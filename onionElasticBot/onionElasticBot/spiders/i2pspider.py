# -*- coding: utf-8 -*-

from onionElasticBot.spiders.base import WebSpider

class i2pSpider(WebSpider):
    name = "i2pSpider"
    DEFAULT_ALLOWED_DOMAINS = ["i2p"]
    DEFAULT_TARGET_SITES = ['http://nekhbet.com/i2p_links.shtml',]
