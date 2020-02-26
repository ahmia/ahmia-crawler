# -*- coding: utf-8 -*-
"""
In this module, you can find the OnionSpider class.
It's a spider to crawl the tor network.
"""
import datetime

from scrapy.conf import settings
from scrapy.linkextractors import LinkExtractor

from .base import WebSpider


class OnionSpider(WebSpider):
    """
    Crawls the tor network.
    """
    name = "ahmia-tor"
    es_index = settings['ELASTICSEARCH_TOR_INDEX']
    custom_settings = {
        'ITEM_PIPELINES': {
            'ahmia.pipelines.OnionPipeline': 200
        },
        # Automatic index name selection according to YEAR-MONTH, i.e. tor-2017-12
        'ELASTICSEARCH_INDEX': datetime.datetime.now().strftime("tor-%Y-%m")
    }
    if settings['RESEARCH_GATHER']:
        custom_settings['ITEM_PIPELINES']['ahmia.pipelines.HistoricalElasticSearchPipeline'] = 300
    default_start_url = settings['SEEDLIST']

    def get_link_extractor(self):
        return LinkExtractor(allow=[r'^http://[a-z2-7]{16}.onion', r'^http://[a-z2-7]{56}.onion'],
                             deny=[r'^https://blockchainbdgpzk.onion/address/',
                                   r'^https://blockchainbdgpzk.onion/tx/'],
                             deny_domains=settings.get('FAKE_DOMAINS'))
