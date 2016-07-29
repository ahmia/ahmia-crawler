# -*- coding: utf-8 -*-
"""Pipelines"""
# Define your item pipelines here
#
import hashlib
import codecs

class ExportLinksPipeline(object):
    def open_spider(self, spider):
        self.file = codecs.open('graph.txt', 'w', "utf-8")

    def close_spider(self, spider):
        self.file.close()

    """Export links as graph edges to a json file"""
    def process_item(self, item, spider):
        """Process an item"""
        for link in item['links']:
            res = u"{src}\t{tgt}\t{anchor}\n".format(
                src=hashlib.sha1(item['url']).hexdigest(),
                tgt=hashlib.sha1(link['link']).hexdigest(),
                anchor=link['link_name']
            )
            self.file.write(res)
        del item['links']
        return item
