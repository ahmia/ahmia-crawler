# -*- coding: utf-8 -*-
"""
In this module, you can find the OnionSpider class.
It's a spider to crawl the tor network.
"""
import os
from scrapy.linkextractors import LinkExtractor
from scrapy.conf import settings

from .base import WebSpider

class OnionSpider(WebSpider):
    """
    Crawls the tor network.
    """
    name = "ahmia-tor"

    TARGET_SITES = settings.get('TARGET_SITES')

    if TARGET_SITES and os.path.isfile(TARGET_SITES):
        # Read a list of URLs from file
        # Create the target file list
        with open(TARGET_SITES) as f:
            default_start_url = f.read().splitlines() # Make it to Python list
            default_start_url = filter(None, start_urls) # Remove empty strings
    else:
        default_start_url = \
            ['http://zqktlwi4fecvo6ri.onion/wiki/index.php/Main_Page',
            'http://tt3j2x4k5ycaa5zt.onion/',
            'http://msydqstlz2kzerdg.onion/address/',
            'https://blockchainbdgpzk.onion/',
            'http://7cbqhjnlkivmigxf.onion/']

    def get_link_extractor(self):
        return LinkExtractor(allow=r'^http://[a-z2-7]{16}.onion',
                             deny=[r'^https://blockchainbdgpzk.onion/address/',
                                   r'^https://blockchainbdgpzk.onion/tx/'],
                             deny_domains=settings.get('FAKE_DOMAINS'))
