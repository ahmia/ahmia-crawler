# -*- coding: utf-8 -*-
"""Pipelines"""
# Define your item pipelines here
#
import hashlib
from elasticsearch import Elasticsearch, helpers
import logging
import gc
import igraph as ig

class AnchorTextPipeline(object):
    def __init__(self):
        self.items_buffer = []
        self.es = Elasticsearch()

    def send_items(self):
        logging.debug("Send anchors texts to ES")
        helpers.bulk(self.es, self.items_buffer)
        self.items_buffer = []

    def close_spider(self, spider):
        if len(self.items_buffer):
            self.send_items()

    def process_item(self, item, spider):
        for link in item['links']:
            if link['link_name'] is None or len(link['link_name']) == 0:
                continue
            action = {
                "_op_type": "update",
                "_index": "crawl",
                "_type": "tor",
                "_id": link['link'],
                "script": {
                    "inline": "ctx._source.anchors += anchor",
                    "params" : {
                        "anchor" : link["link_name"]
                    }
                },
                "upsert": {
                    "anchors": [link["link_name"]]
                }
            }
            self.items_buffer.append(action)

        if len(self.items_buffer) >= 500:
            self.send_items()

        return item


class AuthorityPipeline(object):
    def __init__(self):
        self.links = []
        self.es = Elasticsearch()
        self.items_buffer = []

    def send_items(self):
        logging.debug("Send anchors texts to ES")
        helpers.bulk(self.es, self.items_buffer)
        self.items_buffer = []

    def close_spider(self, spider):
        logging.info("Creating link graph")
        nodes = set()
        url_to_idx = {}
        idx_to_url = []
        edges = []
        for link in self.links:
            for url in link:
                if url in nodes:
                    continue
                n = len(nodes)
                url_to_idx[url] = n
                idx_to_url.append(url)
                nodes.add(url)
        n = len(nodes)

        edges = [(url_to_idx[link[0]], url_to_idx[link[1]])
                 for link in self.links]
        g = ig.Graph(n, edges)

        del edges
        gc.collect()
        logging.debug("Freeing edges list")

        logging.info("Graph created. Computing pagerank")
        pr = g.pagerank()

        del g
        gc.collect()
        logging.debug("Freeing graph")

        logging.info("Pagerank computed. Now sending authority scores to ES")
        for i in xrange(n):
            url = idx_to_url[i]
            action = {
                "_op_type": "update",
                "_index": "crawl",
                "_type": "tor",
                "_id": url,
                "doc": {
                    "authority": pr[i]
                },
                "doc_as_upsert" : True
            }
            self.items_buffer.append(action)

            if len(self.items_buffer) >= 500:
                self.send_items()

        if len(self.items_buffer):
            self.send_items()

        logging.info("Scores successfully sent to ES")

    def process_item(self, item, spider):
        for link in item['links']:
            self.links.append((hashlib.sha1(item['url']).hexdigest(),
                               link['link']))
        del item['links']
        return item
