# -*- coding: utf-8 -*-
"""
In this module, you can find the Webspider class.
It's a virtual class and shouldn't be used to crawl anything.
"""

import datetime
import hashlib
import os
from urlparse import urlparse

from scrapy.conf import settings
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.utils.url import canonicalize_url

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

    def parse_item(self, response):
        """
        Parse a response into a DocumentItem.
        """
        hxs = Selector(response)
        doc = DocumentItem()
        doc['url'] = canonicalize_url(response.url)
        try:
            doc['meta'] = hxs.xpath('//meta[@name=\'description\']/@content') \
                             .extract()[0]
        except IndexError:
            doc['meta'] = None
        # Add the domain
        doc['domain'] = urlparse(doc['url']).hostname
        try:
            doc['title'] = hxs.xpath('//title/text()').extract()[0]
        except IndexError:
            doc['title'] = None
        encoding = self.detect_encoding(response)
        doc['content'] = response.body.decode(encoding, 'ignore')

        doc['content_type'] = response.headers['Content-type']

        doc["updated_on"] = datetime.datetime.now().strftime(
            "%Y-%m-%dT%H:%M:%S")

        # We store this to avoid computing it each iteration (L100)
        source = hashlib.sha1(doc['url']).hexdigest()

        doc['links'] = []
        # Same code than what is used to follow links, without the seen set
        for rule in self._rules:
            links = rule.link_extractor.extract_links(response)
            if links and rule.process_links:
                links = rule.process_links(links)
            for link in links:
                link_obj = LinkItem()
                link_obj['target'] = \
                    hashlib.sha1(canonicalize_url(link.url)).hexdigest()
                link_obj['source'] = source
                link_obj['anchor'] = link.text
                doc['links'].append(dict(link_obj))

        return doc

    def detect_encoding(self, response):
        """ Detect the encoding of an incoming response. """
        return response.headers.encoding or "utf-8"
