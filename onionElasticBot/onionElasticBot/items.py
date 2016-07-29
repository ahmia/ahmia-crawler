# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Field, Item


class CrawledWebsiteItem(Item):
    """A web site"""
    url = Field()
    title = Field()
    meta = Field()
    anchors = Field()
    content = Field()
    domain = Field()
    lang = Field()
    content_type = Field()
    content_checksum = Field()
    code = Field()
    is_fake = Field()
    is_banned = Field()
    updated_on = Field()
    last_seen = Field()
    links = Field()
