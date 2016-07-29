# -*- coding: utf-8 -*-

from onionElasticBot.spiders.base import WebSpider

class OnionSpider(WebSpider):
    name = "OnionSpider"
    DEFAULT_ALLOWED_DOMAINS = ["onion"]
    DEFAULT_TARGET_SITES = ['https://ahmia.fi/address/',]
