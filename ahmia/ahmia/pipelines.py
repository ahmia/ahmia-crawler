# -*- coding: utf-8 -*-
"""
In this module, you can find pipelines.
AnchorTextPipeline is responsible to index an anchor text with the target
document.
AuthorityPipeline stores links until the spider is closed. Then it creates a
graph and compute the pagerank algorithm on it.
"""
from datetime import datetime
import hashlib
from urlparse import urlparse

from scrapyelasticsearch.scrapyelasticsearch import ElasticSearchPipeline

from .items import DocumentItem, LinkItem, AuthorityItem
from simhash import Simhash

def simhash(s):
        width = 3
        sim = s.strip()
        sim = sim.lower()
        sim.replace(",","")
        sim.replace("\n","")
        sim = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', sim, flags=re.MULTILINE)
        sim = re.sub('mailto://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', sim, flags=re.MULTILINE)
        sim = re.sub(r'[^\w]+', '', sim)
        sim = re.sub('^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$', '',sim, flags = re.MULTILINE)
        features =  [sim[i:i + width] for i in range(max(len(sim) - width + 1, 1))]
        shash = Simhash(features)
        return shash


class HistoricalElasticSearchPipeline(ElasticSearchPipeline):
    """
    HistoricalElasticSearchPipeline indexes new DocumentItems to ES, if they do 
    not already exist. It also indexes a crawl record
    """
    def index_item(self, item):
        index_name = self.settings['ELASTICSEARCH_RESEARCH_INDEX']
        index_suffix_format = self.settings.get(
            'ELASTICSEARCH_INDEX_DATE_FORMAT', None)

        if index_suffix_format:
            index_name += "-" + datetime.strftime(datetime.now(),
                                                  index_suffix_format)

        if isinstance(item, DocumentItem):
            content_index_action = {
                '_index': index_name,
                '_type': self.settings['ELASTICSEARCH_CONTENT_TYPE'],
                '_id': simhash(item['content']),
                'title': item['title'],
                'content': item['content']
            }
            self.items_buffer.append(content_index_action)
            crawl_index_action = {
                '_index': index_name,
                '_type': self.settings['ELASTICSEARCH_CRAWL_TYPE'],
                'crawl_time': datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                'content_id': simhash(item['content'])
             }
             self.items_buffer.append(crawl_index_action)              

        else:
            return


        if len(self.items_buffer) >= \
          self.settings.get('ELASTICSEARCH_BUFFER_LENGTH', 500):
            self.send_items()
            self.items_buffer = []

class CustomElasticSearchPipeline(ElasticSearchPipeline):
    """
    CustomElasticSearchPipeline is responsible to index items to ES.
    In this version, the index_item method is different because to it needs to
    handle different type of items.
    """
    items_buffer = []

    def index_item(self, item):
        """
        Item are indexed here.
        This method receives an item which can be of type DocumentItem,
        LinkItem or AuthorityItem.
        Note: You should add the following line to your elasticsearch.yml file
        script.engine.groovy.inline.update: on
        """
        index_name = self.settings['ELASTICSEARCH_INDEX']
        index_suffix_format = self.settings.get(
            'ELASTICSEARCH_INDEX_DATE_FORMAT', None)

//LAE - ask Juha what's up with this?
        if index_suffix_format:
            index_name += "-" + datetime.strftime(datetime.now(),
                                                  index_suffix_format)

        if isinstance(item, DocumentItem):
            index_action = {
                '_index': index_name,
                '_type': self.settings['ELASTICSEARCH_TYPE'],
                '_id': hashlib.sha1(item['url']).hexdigest(),
                '_source': dict(item)
            }
        elif isinstance(item, LinkItem):
            index_action = {
                "_op_type": "update",
                "_index": index_name,
                "_type": self.settings['ELASTICSEARCH_TYPE'],
                "_id": hashlib.sha1(item['target']).hexdigest(),
                "script": {
                    "inline": """ctx._source.anchors = ctx._source.anchors ?
                              (ctx._source.anchors + [anchor]).unique{it}
                              : [anchor]""",
                    "params" : {
                        "anchor" : item["anchor"]
                    }
                },
                "upsert": {
                    "anchors": [item["anchor"]],
                    "url": item['target'],
                    "domain": urlparse(item['target']).hostname,
                    "updated_on": datetime.now().strftime(
                        "%Y-%m-%dT%H:%M:%S")
                }
            }
        elif isinstance(item, AuthorityItem):
            index_action = {
                "_op_type": "update",
                "_index": index_name,
                "_type": self.settings['ELASTICSEARCH_TYPE'],
                "_id": item['url'],
                "doc": {
                    "authority": item['score']
                }
            }
        else:
            return

        self.items_buffer.append(index_action)

        if len(self.items_buffer) >= \
          self.settings.get('ELASTICSEARCH_BUFFER_LENGTH', 500):
            self.send_items()
            self.items_buffer = []
