# -*- coding: utf-8 -*-
"""
In this module, you can find pipelines.
AnchorTextPipeline is responsible to index an anchor text with the target
document.
AuthorityPipeline stores links until the spider is closed. Then it creates a
graph and compute the pagerank algorithm on it.
"""
from datetime import datetime

import logging
import time
import types

import igraph as ig

from scrapyelasticsearch.scrapyelasticsearch import ElasticSearchPipeline

class AnchorTextPipeline(ElasticSearchPipeline):
    """
    AnchorTextPipeline is responsible to index an anchor text with the target
    document. It is a subclass of ElasticSearchPipeline which index items to ES.
    Use of the settings dict is already done by the parent class.
    Only the index_item method is different because the item is not sent
    directly to ES and the _index endpoint.
    """
    def index_item(self, item):
        """
        Item are indexed here.
        This method receives a DocumentItem and uses the links field which is a
        list of LinkItem.
        Each LinkItem's anchor is appended to the document identified by the
        target field. This is done by using ES's update api with a script.
        In case we update a document that is not yet indexed, an upsert dict
        is sent to ES.
        Note: You should add the following line to your elasticsearch.yml file
        script.engine.groovy.inline.update: on
        """
        index_name = self.settings['ELASTICSEARCH_INDEX']
        index_suffix_format = self.settings.get(
            'ELASTICSEARCH_INDEX_DATE_FORMAT', None)

        if index_suffix_format:
            index_name += "-" + datetime.strftime(datetime.now(),
                                                  index_suffix_format)

        for link in item['links']:
            if link['anchor'] is None or len(link['anchor']) == 0:
                continue
            index_action = {
                "_op_type": "update",
                "_index": index_name,
                "_type": self.settings['ELASTICSEARCH_TYPE'],
                "_id": link['target'],
                "script": {
                    "inline": "ctx._source.anchors += anchor",
                    "params" : {
                        "anchor" : link["anchor"]
                    }
                },
                "upsert": {
                    "anchors": [link["anchor"]]
                }
            }

            self.items_buffer.append(index_action)

            if len(self.items_buffer) == \
              self.settings.get('ELASTICSEARCH_BUFFER_LENGTH', 500):
                self.send_items()
                self.items_buffer = []


class AuthorityPipeline(ElasticSearchPipeline):
    """
    AuthorityPipeline is responsible to index the authority score of a document.
    It is a subclass of ElasticSearchPipeline which index items to ES.
    Use of the settings dict is already done by the parent class.
    Indexing authority score is done in two steps:
    - During crawling, links are stored to being used later.
    - After crawling, links are used to make a graph and compute authority
    scores.
    Because of this, this class is different than it's parent.
    """
    def __init__(self):
        super(AuthorityPipeline, self).__init__()
        self.links = []

    def close_spider(self, spider):
        """
        Called when the crawling is finished (graceful stop or no more urls).
        It computes authority scores and index it to ES.
        """
        logging.info("Creating link graph")
        nodes = set()
        url_to_idx = {}
        idx_to_url = []
        edges = []
        for link in self.links:
            for url in link:
                if url in nodes:
                    continue
                url_to_idx[url] = len(nodes)
                idx_to_url.append(url)
                nodes.add(url)
        total_nodes = len(nodes)

        edges = [(url_to_idx[link[0]], url_to_idx[link[1]])
                 for link in self.links]
        links_graph = ig.Graph(total_nodes, edges)

        del edges
        logging.debug("Freeing edges list")

        logging.info("Graph created with %d nodes and %d edges.",
                     total_nodes,
                     len(self.links))
        logging.info("Computing pagerank")
        start = time.time()
        idx_to_pageranks = links_graph.pagerank()
        end = time.time()
        logging.info("Pagerank computed in %.2fs",
                     round(end - start, 2))

        del links_graph
        logging.debug("Freeing graph")

        for i in xrange(total_nodes):
            self.index_item((idx_to_url[i], idx_to_pageranks[i]))

    def index_item(self, item):
        """
        Item are indexed here.
        This method receives an item which is a list of two values:
        - The first one is the _id of the document (sha1 hash of its url).
        - The second one is the authority score.
        In case we update a document that is not yet indexed, ES will use the
        doc dict instead of the upsert dict (thanks to doc_as_upsert).
        """
        index_name = self.settings['ELASTICSEARCH_INDEX']
        index_suffix_format = self.settings.get(
            'ELASTICSEARCH_INDEX_DATE_FORMAT', None)

        if index_suffix_format:
            index_name += "-" + datetime.strftime(datetime.now(),
                                                  index_suffix_format)

        index_action = {
            "_op_type": "update",
            "_index": index_name,
            "_type": self.settings['ELASTICSEARCH_TYPE'],
            "_id": item[0],
            "doc": {
                "authority": item[1]
            },
            "doc_as_upsert" : True
        }
        self.items_buffer.append(index_action)

        if len(self.items_buffer) == \
          self.settings.get('ELASTICSEARCH_BUFFER_LENGTH', 500):
            self.send_items()
            self.items_buffer = []

    def process_item(self, item, spider):
        """
        Items are processed just as the parent class, but not indexed.
        The links field of the item is deleted to being ignored by the main
        ElasticSearchPipeline.
        """
        if isinstance(item, types.GeneratorType) or isinstance(item,
                                                               types.ListType):
            for each in item:
                self.process_item(each, spider)
        else:
            for link in item['links']:
                self.links.append((link['source'], link['target']))
            del item['links']
        return item
