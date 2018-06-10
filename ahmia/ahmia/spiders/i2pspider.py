# -*- coding: utf-8 -*-
"""
In this module, you can find the i2pSpider class.
It's a spider to crawl the i2p network.
"""
import datetime

from scrapy.conf import settings
from scrapy.linkextractors import LinkExtractor

from .base import WebSpider


class InvisibleInternetSpider(WebSpider):
    """
    Crawls the i2p network.
    """
    name = "ahmia-i2p"
    es_index = settings['ELASTICSEARCH_I2P_INDEX']
    custom_settings = {
        'ITEM_PIPELINES': {
            'ahmia.pipelines.I2PPipeline': 200
        },
        # Automatic index name selection according to YEAR-MONTH, i.e. i2p-2017-12
        'ELASTICSEARCH_INDEX': datetime.datetime.now().strftime("i2p-%Y-%m")
    }
    default_start_url = ['http://nekhbet.com/i2p_links.shtml', ]

    def get_link_extractor(self):
        return LinkExtractor(allow=r'.i2p',)
