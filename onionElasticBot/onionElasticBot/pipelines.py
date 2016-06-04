# -*- coding: utf-8 -*-

# Define your item pipelines here
#
import datetime

class AddTimestampPipeline(object):
    def process_item(self, item, spider):
        item["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        return item
