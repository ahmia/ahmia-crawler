# -*- coding: utf-8 -*-

import re
from urlparse import urlparse
import os
import datetime
'''import html2text
from langdetect import detect'''
import hashlib

from six.moves.urllib.parse import urljoin

from scrapy.conf import settings
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.linkextractors import LinkExtractor
from scrapy.utils.url import canonicalize_url
from scrapy.utils.response import get_base_url

from onionElasticBot.items import CrawledWebsiteItem

class WebSpider(CrawlSpider):
    name = None

    DEFAULT_ALLOWED_DOMAINS = None
    DEFAULT_TARGET_SITES = None

    def __init__(self, *args, **kwargs):
        super(WebSpider, self).__init__(*args, **kwargs)

        ALLOWED_DOMAINS = settings.get('ALLOWED_DOMAINS')
        if ALLOWED_DOMAINS and os.path.isfile(ALLOWED_DOMAINS):
            # Read a list of URLs from file
            # Create the target file list
            with open(ALLOWED_DOMAINS) as f:
                self.allowed_domains = f.read().splitlines() # Make it to Python list
                # Remove empty strings
                self.allowed_domains = [d for d in self.allowed_domains if d]
        else:
            self.allowed_domains = self.DEFAULT_ALLOWED_DOMAINS

        TARGET_SITES = settings.get('TARGET_SITES')
        if TARGET_SITES and os.path.isfile(TARGET_SITES):
            # Read a list of URLs from file
            # Create the target file list
            with open(TARGET_SITES) as f:
                self.start_urls = f.read().splitlines() # Make it to Python list
                # Remove empty strings
                self.start_urls = [u for u in self.start_urls if u]
        else:
            self.start_urls = self.DEFAULT_TARGET_SITES

        self._rules = (Rule(LinkExtractor(), callback=self.parse_item, follow=True), )

    def parse_item(self, response):
        hxs = Selector(response)
        item = CrawledWebsiteItem()
        item['anchors'] = []
        item['url'] = canonicalize_url(response.url)
        try:
            item['meta'] = hxs.xpath('//meta[@name=\'description\']/@content').extract()[0]
        except IndexError:
            item['meta'] = None
        # Add the domain
        item['domain'] = urlparse(item['url']).hostname
        try:
            item['title'] = hxs.xpath('//title/text()').extract()[0]
        except IndexError:
            item['title'] = None
        encoding = self.detect_encoding(response)
        item['content'] = response.body.decode(encoding, 'ignore')

        item['content_type'] = response.headers['Content-type']

        item["updated_on"] = datetime.datetime.now().strftime(
            "%Y-%m-%dT%H:%M:%S")


        # TODO: Is fake
        # TODO: Is banned

        item['links'] = []
        links = hxs.xpath('//a')
        for link in links:
            link_obj = {}
            # Extract the link's URL
            link_str = " ".join(link.xpath('@href').extract()).replace("\n", "")
            link_str = urljoin(get_base_url(response), link_str)
            link_obj['link'] = hashlib.sha1(link_str).hexdigest()
            # Extract the links value
            link_name_str = " ".join(link.xpath('text()').extract())
            link_name_str = link_name_str.replace("\n", "")
            link_name_str = link_name_str.lstrip()
            link_name_str = link_name_str.rstrip()
            link_obj['link_name'] = link_name_str
            item['links'].append(link_obj)
        return item

    def detect_encoding(self, response):
        return response.headers.encoding or "utf-8"

    def detect_lang(self, decoded_html):
        """HTML 2 string converter. Returns a string."""
        converter = html2text.HTML2Text()
        converter.ignore_links = True
        string = converter.handle(decoded_html)
        return detect(string)
