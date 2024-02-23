# -*- coding: utf-8 -*-
""" Pipelines """
import hashlib
import logging
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from scrapy.utils.project import get_project_settings
from .items import DocumentItem, LinkItem, AuthorityItem

logger = logging.getLogger(__name__)
settings = get_project_settings()

class CustomElasticSearchPipeline:
    """
    CustomElasticSearchPipeline is responsible for indexing items to Elasticsearch.
    """
    items_buffer = []

    def __init__(self):
        self.es = Elasticsearch(
            [settings.get('ELASTICSEARCH_SERVER')],
            http_auth=(settings.get('ELASTICSEARCH_USERNAME'),
            settings.get('ELASTICSEARCH_PASSWORD')),
            ca_certs=settings.get('ELASTICSEARCH_CA_CERTS', None)
        )
        self.index_name = settings.get('ELASTICSEARCH_INDEX')

    def process_item(self, item, spider):
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
        if item_type != "LinkItem":
            doc_id = hashlib.sha1(item['url'].encode('utf-8')).hexdigest()
        else:
            doc_id = hashlib.sha1(item['target'].encode('utf-8')).hexdigest()

        if isinstance(item, DocumentItem):
            action = {
                "_index": self.index_name,
                "_id": doc_id,
                "_source": dict(item)
            }
        elif isinstance(item, LinkItem):
            # For LinkItem, consider implementing logic to update or add links
            action = {
                "_index": self.index_name,
                "_id": doc_id,
                "_source": dict(item)
            }
        elif isinstance(item, AuthorityItem):
            # For AuthorityItem, you might want to update existing documents
            action = {
                "_op_type": "update",
                "_index": self.index_name,
                "_id": doc_id,
                "doc": {
                    "authority": item['score']
                },
                "doc_as_upsert": True
            }
        else:
            logger.error(f"Unknown item type: {item_type}")
            return

        self.items_buffer.append(action)

        if len(self.items_buffer) >= settings.get('ELASTICSEARCH_BUFFER_LENGTH', 500):
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

    def close_spider(self, spider):
        """
        Called when the spider is closed. Flushes remaining items to Elasticsearch.
        """
        if self.items_buffer:
            self.send_items()
