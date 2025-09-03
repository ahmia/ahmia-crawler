# -*- coding: utf-8 -*-
""" OnionSpider class to crawl onion websites through the Tor network """
import datetime
import hashlib
from urllib.parse import urlparse
import html2text
import igraph as ig
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.http import HtmlResponse, Request
from scrapy.selector import Selector
from scrapy.utils.project import get_project_settings

from ahmia.items import DocumentItem

class OnionSpider(CrawlSpider):
    """ The base to crawl onion webpages """
    name = "ahmia-tor"

    def __init__(self, *args, seedlist=None, **kwargs):
        """ Init """
        super().__init__(*args, **kwargs)  # Python 3 style super()

        settings = get_project_settings()

        self.rules = (
            Rule(LinkExtractor(allow=[r'^https?://[a-z2-7]{56}\.onion(?:/.*)?$']),
                 callback='parse_item', follow=True),
        )

        self._compile_rules()

        if seedlist:  # Override SEEDLIST if `seedlist` argument is provided
            # scrapy crawl ahmia-tor\
            # -a seedlist=\
            # 'http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/add/onionsadded/',\
            # 'http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/add/onionsadded/'
            self.start_urls = [url.strip() for url in seedlist.split(',')]
        else:
            self.start_urls = settings.get('SEEDLIST', [])

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

    def extract_urls_from_response(self, response):
        """ Extract URLs from the given HtmlResponse object """
        # Use Scrapy's selector to extract href attributes from <a> tags
        urls = response.css('a::attr(href)').getall()
        # Filter out URLs that don't start with http:// or https://
        urls = [url for url in urls if url.startswith('http://') or url.startswith('https://')]
        return urls

    def parse(self, response):
        """ Parse a response, yields requests """
        for request_or_item in super().parse(response):
            yield request_or_item

    def html2string(self, response):
        """ Convert HTML content to plain text """
        converter = html2text.HTML2Text()
        converter.ignore_links = True
        return converter.handle(response.text)

    def parse_item(self, response):
        """ Parse a response into a DocumentItem. """
        #self.logger.info(f'Visited {response.url}')
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
