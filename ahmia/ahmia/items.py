# -*- coding: utf-8 -*-
"""
In this module, you can find items.
DocumentItem contains information about a Document (or Webpage).
LinkItem contains information about a Link between two Documents.
"""
from scrapy.item import Field, Item

class DocumentItem(Item):
    """
    Informations about a Document.
    A Document is a webpage that will be indexed by Elasticsearch.
    Its id will be the SHA1 hash of its url.
    Url, title, meta are all text fields that will be searchable.
    Anchors is an array of searchable text.
    Content is the full HTML source code of the page.
    Domain is the domain of the document, and is not analyzed.
    Content_type is the MIME of the document.
    Is_fake and is_banned are booleans to mask specific documents.
    Updated_on is the datetime of the last update.
    """
    url = Field()
    title = Field()
    meta = Field()
    anchors = Field()
    content = Field()
    domain = Field()
    content_type = Field()
    is_fake = Field()
    is_banned = Field()
    updated_on = Field()
    links = Field()

class LinkItem(Item):
    """
    Informations about a Link.
    Source is the _id of the source document (an SHA1 hash of its url).
    Target is the _id of the target document (an SHA1 hash of its url).
    Anchor is the text used to describe the target document and can be empty.
    """
    source = Field()
    target = Field()
    anchor = Field()
