# -*- coding: utf-8 -*-
"""
In this module, you can find the Webspider class.
It's a virtual class and shouldn't be used to crawl anything.
"""

import datetime
import hashlib
import os
from urlparse import urlparse, urljoin

from scrapy.conf import settings
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.utils.url import canonicalize_url
from scrapy.utils.response import get_base_url

from ahmia.items import DocumentItem, LinkItem

class WebSpider(CrawlSpider):
    """
    The base to crawl webpages in a specific network (tor, i2p).
    It uses github.com/ahmia/ahmia-index mappings.
    """
    name = None

    default_allowed_domains = None
    default_target_sites = None

    def __init__(self, *args, **kwargs):
        super(WebSpider, self).__init__(*args, **kwargs)

        allowed_domains = settings.get('ALLOWED_DOMAINS')
        if allowed_domains and os.path.isfile(allowed_domains):
            # Read a list of URLs from file
            # Create the target file list
            with open(allowed_domains) as allowed_domains_file:
                # Make it to Python list
                self.allowed_domains = allowed_domains_file.read().splitlines()
                # Remove empty strings
                self.allowed_domains = [d for d in self.allowed_domains if d]
        else:
            self.allowed_domains = self.default_allowed_domains

        target_sites = settings.get('TARGET_SITES')
        if target_sites and os.path.isfile(target_sites):
            # Read a list of URLs from file
            # Create the target file list
            with open(target_sites) as target_sites_file:
                # Make it to Python list
                self.start_urls = target_sites_file.read().splitlines()
                # Remove empty strings
                self.start_urls = [u for u in self.start_urls if u]
        else:
            self.start_urls = self.default_target_sites

        self._rules = (Rule(LinkExtractor(),
                            callback=self.parse_item,
                            follow=True), )

    def is_url_valid(self, url):
        """
        Should we crawl the following url ?
        """
        raise NotImplementedError

    def parse_item(self, response):
        """
        Parse a response into a DocumentItem.
        """

        # Is it a .onion url ?
        doc_url = canonicalize_url(response.url)
        doc_hostname = urlparse(doc_url).hostname

        if not self.is_url_valid(doc_hostname):
            return None

        hxs = Selector(response)
        doc = DocumentItem()

        # We don't want to reset the array
        # doc['anchors'] = []


        doc['url'] = doc_url
        try:
            doc['meta'] = hxs.xpath('//meta[@name=\'description\']/@content') \
                             .extract()[0]
        except IndexError:
            doc['meta'] = None
        # Add the domain
        doc['domain'] = doc_hostname
        try:
            doc['title'] = hxs.xpath('//title/text()').extract()[0]
        except IndexError:
            doc['title'] = None
        encoding = self.detect_encoding(response)
        doc['content'] = response.body.decode(encoding, 'ignore')

        doc['content_type'] = response.headers['Content-type']

        doc["updated_on"] = datetime.datetime.now().strftime(
            "%Y-%m-%dT%H:%M:%S")

        doc['links'] = []
        links = hxs.xpath('//a')
        for link in links:
            link_obj = LinkItem()

            # Extract the link's URL
            link_url = "".join(link.xpath('@href').extract()).replace("\n", "")
            link_url = canonicalize_url(urljoin(get_base_url(response),
                                                link_url))
            if not self.is_url_valid(link_url):
                continue

            link_obj['target'] = hashlib.sha1(link_url).hexdigest()
            link_obj['source'] = hashlib.sha1(doc_url).hexdigest()
            # Extract the links value
            anchor = " ".join(link.xpath('text()')\
                              .extract()) \
                        .replace("\n", "") \
                        .strip()
            link_obj['anchor'] = anchor
            doc['links'].append(dict(link_obj))

        return doc

    def detect_encoding(self, response):
        """ Detect the encoding of an incoming response. """
        return response.headers.encoding or "utf-8"
