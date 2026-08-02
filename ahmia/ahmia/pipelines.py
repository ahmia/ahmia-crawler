# -*- coding: utf-8 -*-
""" Pipelines """
import hashlib
import logging
import re
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
            request_timeout=60,
        )

        self.index_name = self.settings.get('ELASTICSEARCH_INDEX')

        logger.info(f"Elasticsearch available: {self.es.info()}")

    def process_item(self, item):
        """
        This is the function Scrapy calls for the each pipeline
        """
        self.index_item(item)
        return item  # To continue passing items through other pipelines

    def preprocess(self, text):

        # 小文字化（大文字・小文字の違いを統一）
        text = text.lower()

        # 改行・タブ・複数スペースを1つの空白に統一
        text = re.sub(r'\s+', ' ', text)

        # onionアドレスを削除（サイト固有の識別情報を除去）
        text = re.sub(
            r'[a-z2-7]{56}\.onion',
            '',
            text
        )

        # URLを削除（リンク先の違いによる差を除去）
        text = re.sub(
            r'https?://\S+',
            '',
            text
        )

        # Bitcoinアドレスを削除（決済情報などサイト固有情報を除去）
        text = re.sub(
            r'\b(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,62}\b',
            '',
            text
        )

        # メールアドレスを削除（連絡先情報を除去）
        text = re.sub(
            r'\S+@\S+\.\S+',
            '',
            text
        )

        # 本文と無関係なテンプレート由来の脚注・用語集ノイズを除去
        text = re.sub(
            r'\*\[[^\]]+\]:\s*[^*]*',
            '',
            text
        )

        # 連続する特殊文字を削除（Markdown記号などのノイズ除去）
        text = re.sub(
            r'[*#|_\-]{2,}',
            '',
            text
        )

        # 再度、余分な空白を整理
        text = re.sub(
            r'\s+',
            ' ',
            text
        )

        # 前後の空白を削除
        text = text.strip()

        return text

    def index_item(self, item):
        """
        Items are indexed here.
        This method handles different types of items.
        """
        item_type = item.__class__.__name__
        doc_id = hashlib.sha1(item['url'].encode('utf-8')).hexdigest()

        if isinstance(item, DocumentItem):

            content = item.get('content', '')

            if content:
                # 前処理
                clean_content = self.preprocess(content)
                item['clean_content'] = clean_content
                # ハッシュ値の生成
                item['content_hash'] = hashlib.sha256(
                    clean_content.encode('utf-8')
                ).hexdigest()
            
            action = {
                "_index": self.index_name,
                "_id": doc_id,
                "_source": dict(item)
            }
        else:
            logger.error(f"Unknown item type: {item_type}")
            return

        self.items_buffer.append(action)

        if len(self.items_buffer) >= self.settings.get('ELASTICSEARCH_BUFFER_LENGTH', 100):
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
