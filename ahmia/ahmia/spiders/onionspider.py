# -*- coding: utf-8 -*-
"""
In this module, you can find the OnionSpider class.
It's a spider to crawl the tor network.
"""
from .base import WebSpider

class OnionSpider(WebSpider):
    """
    Crawls the tor network.
    """
    name = "ahmia-tor"
    default_allowed_domains = ["onion"]
    default_target_sites = \
        ['http://zqktlwi4fecvo6ri.onion/wiki/index.php/Main_Page',
         'http://tt3j2x4k5ycaa5zt.onion/',
         'https://blockchainbdgpzk.onion/',
         'http://7cbqhjnlkivmigxf.onion/']
