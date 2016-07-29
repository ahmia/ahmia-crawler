# -*- coding: utf-8 -*-

import igraph as ig
from elasticsearch import Elasticsearch, helpers
import pdb
import codecs
import logging

links = []
urls = set()

''' Links are loaded here. '''
with codecs.open('graph.txt', 'r', 'utf-8') as f:
    for line in f:
        values = line.split('\t')
        if len(values) == 3:
            source, target, anchor = values
            anchor = anchor.replace('\n', '')
            if len(anchor) == 0:
                anchor = None
        elif len(values) == 2:
            source, target = values
            anchor = None
        else:
            # Unexploitable link
            continue
        links.append({
            "src": source,
            "tgt": target,
            "anchor": anchor
        })
        urls.add(source)
        urls.add(target)

''' Then the graph is computed.
For this we use the python-igraph library. '''
n = len(urls)
url_to_idx = {}
idx_to_url = {}
i = 0
for url in urls:
    url_to_idx[url] = i
    idx_to_url[i] = url
    i += 1

edges = [(url_to_idx[link['src']], url_to_idx[link['tgt']]) for link in links]

print "Making graph"
g = ig.Graph(n, edges)

print "Computing pagerank"
''' The pagerank is computed. After this we have a dictionnary url -> pagerank '''
pr = g.pagerank()

''' Cleaning some memory space '''
del edges
del g

''' Popularity is sent to ES '''
es = Elasticsearch()

print "Sending authority to ES"
items_buffer = []
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
    items_buffer.append(action)
    if len(items_buffer) == 500:
        print "Sending bulk requests"
        helpers.bulk(es, items_buffer)
        items_buffer = []
# At this point, items_buffer might not be empty

if len(items_buffer):
    helpers.bulk(es, items_buffer)
    items_buffer = []
pdb.set_trace()

''' Anchor texts are sent to ES
For this to work, groovy script needs to be enabled in elasticsearch.yml
script.engine.groovy.inline.update: on '''
for link in links:
    if link["anchor"] is None:
        continue
    action = {
        "_op_type": "update",
        "_index": "crawl",
        "_type": "tor",
        "_id": link["tgt"],
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
    items_buffer.append(action)
    if len(items_buffer) == 500:
        helpers.bulk(es, items_buffer)
        items_buffer = []

if len(items_buffer):
    helpers.bulk(es, items_buffer)
    items_buffer = []
