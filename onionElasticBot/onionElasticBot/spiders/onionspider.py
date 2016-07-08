# -*- coding: utf-8 -*-

from onionElasticBot.spiders.base import WebSpider

class OnionSpider(WebSpider):
    NAME = "OnionSpider"
    DEFAULT_ALLOWED_DOMAINS = ["onion"]
    DEFAULT_TARGET_SITES = ['https://ahmia.fi/address/', 'http://torlinks6ob7o7zq.onion/', 'http://tt3j2x4k5ycaa5zt.onion/onions.php',]
