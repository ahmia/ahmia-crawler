# -*- coding: utf-8 -*-
"""
In this module, you can find the OnionSpider class.
It's a spider to crawl the tor network.
"""
import re
from urlparse import urlparse

from .base import WebSpider

class OnionSpider(WebSpider):
    """
    Crawls the tor network.
    """
    name = "ahmia-tor"
    default_allowed_domains = ["onion"]
    default_target_sites = ['https://ahmia.fi/address/',
                            'http://torlinks6ob7o7zq.onion/',
                            'http://tt3j2x4k5ycaa5zt.onion/onions.php',]

    def is_url_valid(self, url):
        """
        Should we crawl the following url?
        With this implementation, only .onion urls are followed.
        """
        try:
            return re.match(r"^[a-z2-7]{16}(\.onion)", urlparse(url).hostname)
        except TypeError:
            return False
