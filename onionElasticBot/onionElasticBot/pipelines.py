# -*- coding: utf-8 -*-
"""Pipelines"""
# Define your item pipelines here
#
import datetime

class AddTimestampPipeline(object):
    """Add timestamp to item"""
    def process_item(self, item, spider):
        """Process an item"""
        item["timestamp"] = datetime.datetime.now().strftime(
            "%Y-%m-%dT%H:%M:%S")
        return item
