# -*- coding: utf-8 -*-
"""
In this module, you can find the i2pSpider class.
It's a spider to crawl the i2p network.
"""
from scrapy.linkextractors import LinkExtractor

from .base import WebSpider


class InvisibleInternetSpider(WebSpider):
    """
    Crawls the i2p network.
    """
    name = "ahmia-i2p"
    default_start_url = ['http://nekhbet.com/i2p_links.shtml', ]

    def get_link_extractor(self):
        return LinkExtractor(allow=r'.i2p',)
