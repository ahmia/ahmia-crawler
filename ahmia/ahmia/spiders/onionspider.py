# -*- coding: utf-8 -*-
"""
In this module, you can find the OnionSpider class.
It's a spider to crawl the tor network.
"""
from scrapy.linkextractors import LinkExtractor
from scrapy.conf import settings

from .base import WebSpider

class OnionSpider(WebSpider):
    """
    Crawls the tor network.
    """
    name = "ahmia-tor"

    default_start_url = \
    ['http://zqktlwi4fecvo6ri.onion/wiki/index.php/Main_Page',
     'http://tt3j2x4k5ycaa5zt.onion/',
     'http://msydqstlz2kzerdg.onion/address/',
     'http://msydqstlz2kzerdg.onion/add/onionsadded/',
     'https://blockchainbdgpzk.onion/',
     'http://7cbqhjnlkivmigxf.onion/']

    url = "http://zlal32teyptf4tvi.onion/?search=&rep=n%2Fa&page="
    for index in range(1,100):
        default_start_url.append( url + str(index) )

    def get_link_extractor(self):
        return LinkExtractor(allow=[r'^http://[a-z2-7]{16}.onion', r'^http://[a-z2-7]{56}.onion'],
                             deny=[r'^https://blockchainbdgpzk.onion/address/',
                                   r'^https://blockchainbdgpzk.onion/tx/'],
                             deny_domains=settings.get('FAKE_DOMAINS'))
