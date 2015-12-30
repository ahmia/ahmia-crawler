# -*- coding: UTF-8 -*-

import re
from urlparse import urlparse
import os
import html2text
from scrapy.conf import settings

from onionElasticBot.items import CrawledWebsiteItem
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import Selector


class i2pSpider(CrawlSpider):
    name = "i2pSpider"
    ALLOWED_DOMAINS = settings.get('ALLOWED_DOMAINS')

    if ALLOWED_DOMAINS and os.path.isfile(ALLOWED_DOMAINS):
        # Read a list of URLs from file
        # Create the target file list
        with open(ALLOWED_DOMAINS) as f:
            allowed_domains = f.read().splitlines() # Make it to Python list
            allowed_domains = filter(None, allowed_domains) # Remove empty strings
    else:
        allowed_domains = ["i2p"]

    TARGET_SITES = settings.get('TARGET_SITES')

    if TARGET_SITES and os.path.isfile(TARGET_SITES):
        # Read a list of URLs from file
        # Create the target file list
        with open(TARGET_SITES) as f:
            start_urls = f.read().splitlines() # Make it to Python list
            start_urls = filter(None, start_urls) # Remove empty strings
    else:
        start_urls = [ 'http://nekhbet.com/i2p_links.shtml', ]

    rules = (Rule(LinkExtractor(), callback='parse_item', follow=True), )

    def parse_item(self, response):
        hxs = Selector(response)
        item = CrawledWebsiteItem()
        # Also the header
        item['header'] = response.headers
        item['url'] = response.url
        # Add the domain
        domain = urlparse( item['url'] ).hostname
        item['domain'] = domain
        title_list = hxs.xpath('//title/text()').extract()
        h1_list = hxs.xpath("//h1/text()").extract()
        item['h1'] = " ".join(h1_list)
        h2_list = hxs.xpath("//h2/text()").extract()
        item['h2'] = " ".join(h2_list)
        title = ' '.join(title_list)
        item['title'] = title
        encoding = self.detect_encoding(response)
        decoded_html = response.body.decode(encoding, 'ignore')
        html_text = self.html2string(decoded_html)
        words = self.extract_words(html_text)
        item['text'] = title + " " + " ".join(words)
        # For each link on this page
        item['links'] = []
        links = hxs.xpath('//a')
        for link in links:
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
            item['links'].append(link_obj)
        return item

    def detect_encoding(self, response):
        return response.headers.encoding or "utf-8"

    def html2string(self, decoded_html):
        """HTML 2 string converter. Returns a string."""
        converter = html2text.HTML2Text()
        converter.ignore_links = True
        string = converter.handle(decoded_html)
        return string

    def extract_words(self, html_string):
        """Create a word list."""
        string_list = re.split(r' |\n|#|\*', html_string)
        # Cut a word list that is larger than 10000 words
        if len(string_list) > 10000:
            string_list = string_list[0:10000]
        words = []
        for word in string_list:
            # Word must be longer than 0 letter
            # And shorter than 45sudo service polipo restart
            # The longest word in a major English dictionary is
            # Pneumonoultramicroscopicsilicovolcanoconiosis (45 letters)
            if len(word) > 0 and len(word) <= 45:
                words.append(word)
        return words
