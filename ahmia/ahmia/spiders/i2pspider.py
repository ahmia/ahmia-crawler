# -*- coding: utf-8 -*-
"""
In this module, you can find the i2pSpider class.
It's a spider to crawl the i2p network.
"""
from .base import WebSpider

class InvisibleInternetSpider(WebSpider):
    """
    Crawls the i2p network.
    """
    name = "ahmia-i2p"
    default_allowed_domains = ["i2p"]
    default_target_sites = ['http://nekhbet.com/i2p_links.shtml',]

    def is_url_valid(self, url):
        """
        Should we crawl the following url?
        """
        return True
