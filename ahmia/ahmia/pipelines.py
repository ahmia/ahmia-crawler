# -*- coding: utf-8 -*-
""" Pipelines """
import hashlib
import logging
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from .items import DocumentItem

logger = logging.getLogger(__name__)

class CustomElasticSearchPipeline:
    """
    CustomElasticSearchPipeline is responsible for indexing items to Elasticsearch.
    """
    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def __init__(self, settings):
        self.settings = settings
        self.items_buffer = []

        self.es = Elasticsearch(
            [settings.get('ELASTICSEARCH_SERVER')],
            basic_auth=(settings.get('ELASTICSEARCH_USERNAME'), settings.get('ELASTICSEARCH_PASSWORD')),
            verify_certs=False,
            ssl_show_warn=False,
            max_retries=5,
            request_timeout=30,
        )

        self.index_name = self.settings.get('ELASTICSEARCH_INDEX')

        logger.info(f"Elasticsearch available: {self.es.info()}")

    def process_item(self, item):
        """
        This is the function Scrapy calls for the each pipeline
        """
        self.index_item(item)
        return item  # To continue passing items through other pipelines

    def index_item(self, item):
        """
        Items are indexed here.
        This method handles different types of items.
        """
        item_type = item.__class__.__name__
        doc_id = hashlib.sha1(item['url'].encode('utf-8')).hexdigest()

        if isinstance(item, DocumentItem):
            action = {
                "_index": self.index_name,
                "_id": doc_id,
                "_source": dict(item)
            }
        else:
            logger.error(f"Unknown item type: {item_type}")
            return

        self.items_buffer.append(action)

        if len(self.items_buffer) >= self.settings.get('ELASTICSEARCH_BUFFER_LENGTH', 500):
            self.send_items()

    def send_items(self):
        """
        Send buffered items to Elasticsearch using the bulk API.
        """
        try:
            success, _ = bulk(self.es, self.items_buffer,
                              index=self.index_name,
                              raise_on_error=True)
            logger.info(f"Successfully indexed {success} items.")
        except Exception as e:
            logger.error(f"Error indexing items: {e}")
        finally:
            self.items_buffer = []

    def close_spider(self):
        """
        Called when the spider is closed. Flushes remaining items to Elasticsearch.
        """
        if self.items_buffer:
            self.send_items()
