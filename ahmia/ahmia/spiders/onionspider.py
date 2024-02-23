# -*- coding: utf-8 -*-
""" OnionSpider class to crawl onion websites through the Tor network """
import datetime
import hashlib
from urllib.parse import urlparse
import html2text
import igraph as ig
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.http import HtmlResponse, Request
from scrapy.selector import Selector
from scrapy.utils.project import get_project_settings

from ahmia.items import DocumentItem, LinkItem, AuthorityItem

class OnionSpider(CrawlSpider):
    """ The base to crawl onion webpages """
    name = "ahmia-tor"
    settings = get_project_settings()
    es_index = settings.get('ELASTICSEARCH_INDEX')
    start_urls = settings.get('SEEDLIST', [])
    rules = (Rule(LinkExtractor(allow=[r'^https?://[a-z2-7]{56}\.onion(?:/.*)?$']), callback='parse_item', follow=True),)

    es = Elasticsearch(
        [settings.get('ELASTICSEARCH_SERVER')],
        http_auth=(settings.get('ELASTICSEARCH_USERNAME'), settings.get('ELASTICSEARCH_PASSWORD')),
        ca_certs=settings.get('ELASTICSEARCH_CA_CERTS', None)
    )

    def binary_search(self, array, key, low, high):
        """ Fast search in a sorted array """
        if low > high:
            return -1
        middle = (low + high) // 2  # Use floor division for Python 3 compatibility
        if array[middle] == key:
            return middle
        if key < array[middle]:
            return self.binary_search(array, key, low, middle - 1)
        return self.binary_search(array, key, middle + 1, high)

    def build_links(self):
        """ Build a complete list of links from HTML in Elasticsearch """
        new_links = []
        # Scan through documents in Elasticsearch that have a 'url' field
        hashes = sorted([
            doc['_id'] for doc in scan(
                self.es,
                query={"query": {"exists": {"field": "url"}}},
                index=self.es_index,
                _source_includes=[]
            )
        ])
        # Scan through documents that have a 'content' field
        content_hits = scan(
            self.es,
            query={"query": {"exists": {"field": "content"}}},
            index=self.es_index,
            _source_includes=["content", "url"]
        )
        for hit in content_hits:
            id_ = hit['_id']
            url = hit['_source']['url']
            content = hit['_source']['content'].encode('utf-8')
            # Generate a Scrapy HtmlResponse object from the content
            response = HtmlResponse(url=url, body=content, encoding='utf-8')
            # Extract and process links from the response
            for extracted_url in self.extract_urls_from_response(response):
                # Generate a hash for each extracted URL
                hash_target = hashlib.sha1(extracted_url.encode('utf-8')).hexdigest()
                # Use a binary search to check if the hash exists in the sorted list of hashes
                if self.binary_search(hashes, hash_target, 0, len(hashes) - 1) < 0:
                    continue
                new_links.append((id_, hash_target))
        return new_links

    def extract_urls_from_response(self, response):
        """ Extract URLs from the given HtmlResponse object """
        # Use Scrapy's selector to extract href attributes from <a> tags
        urls = response.css('a::attr(href)').getall()
        # Filter out URLs that don't start with http:// or https://
        urls = [url for url in urls if url.startswith('http://') or url.startswith('https://')]
        return urls

    def compute_pagerank(self):
        """ Compute the pagerank dict """
        new_links = self.build_links()
        nodes = set([url_hash for link in new_links for url_hash in link])
        links_graph = ig.Graph(len(nodes))
        links_graph.vs["name"] = list(nodes)
        links_graph.add_edges(new_links)
        itemproc = self.crawler.engine.scraper.itemproc
        for i, score in enumerate(links_graph.pagerank()):
            itemproc.process_item(AuthorityItem(url=links_graph.vs["name"][i],
                                                score=score), self)

    def parse(self, response):
        """ Parse a response, yields requests """
        for request_or_item in super(OnionSpider, self).parse(response):
            if isinstance(request_or_item, Request):
                yield LinkItem(target=request_or_item.url,
                               source=response.url,
                               anchor=request_or_item.meta['link_text'])
            yield request_or_item

    def on_idle(self):
        """ Called when the spider is idle """
        self.compute_pagerank()

    def html2string(self, response):
        """ Convert HTML content to plain text """
        converter = html2text.HTML2Text()
        converter.ignore_links = True
        return converter.handle(response.text)

    def parse_item(self, response):
        """ Parse a response into a DocumentItem. """
        self.logger.info(f'Visited {response.url}')
        doc_loader = ItemLoader(item=DocumentItem(), response=response)
        doc_loader.add_value('url', response.url)
        doc_loader.add_xpath('meta', '//meta[@name=\'description\']/@content')
        doc_loader.add_value('domain', urlparse(response.url).hostname)
        doc_loader.add_xpath('title', '//title/text()')
        hxs = Selector(response)  # For HTML extractions
        # Extract links on this page
        links = []
        a_links = hxs.xpath('//a')
        for link in a_links[0:250]: # limit to 250
            link_obj = {}
            # Extract the link's URL
            link_str = " ".join(link.xpath('@href').extract())
            link_obj['link'] = link_str.replace("\n", "")
            # Extract the links value
            link_name_str = " ".join(link.xpath('text()').extract())
            link_name_str = link_name_str.replace("\n", "")
            link_name_str = link_name_str.lstrip()
            link_name_str = link_name_str.rstrip()
            link_obj['link_name'] = link_name_str
            # Skip extremely long "links" and link names (non-sense, broken HTML)
            if len(link_obj['link']) >= 500 or len(link_obj['link_name']) >= 500:
                continue # Skip, cannot be right link name or link URL
            links.append(link_obj)
        doc_loader.add_value('links', links)

        # Populate text field
        title_list = hxs.xpath('//title/text()').extract()
        title = ' '.join(title_list)
        body_text = self.html2string(response)
        text = title + " " + body_text
        doc_loader.add_value('content', text)

        doc_loader.add_value('title', title)
        doc_loader.add_value('url', response.url)

        h1_list = hxs.xpath("//h1/text()").extract()
        doc_loader.add_value('h1', " ".join(h1_list))

        doc_loader.add_value('content_type', response.headers['Content-type'].decode("utf-8"))
        doc_loader.add_value('updated_on', datetime.datetime.now().strftime(
            "%Y-%m-%dT%H:%M:%S"))
        item = doc_loader.load_item()
        # url, h1, title, meta, content, domain, content_type, updated_on, links
        # Clean extremy long weird text content from the item
        item["url"] = item.get("url", "")
        item["h1"] = item.get("h1", "")[0:100]
        item["title"] = item.get("title", "")[0:100]
        item["meta"] = item.get("meta", "")[0:1000]
        item["content"] = item.get("content", "")[0:500000]
        item["domain"] = item.get("domain", "")
        item["content_type"] = item.get("content_type", "")
        item["updated_on"] = item.get("updated_on", "")
        item["links"] = item.get("links", [])
        return item
