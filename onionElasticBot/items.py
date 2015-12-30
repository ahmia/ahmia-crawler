# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Field, Item


class CrawledWebsiteItem(Item):
    """A web site"""
    domain = Field()
    url = Field()
    title = Field()
    h1 = Field()
    h2 = Field()
    text = Field()
    header = Field()
    links = Field()
    timestamp = Field()
