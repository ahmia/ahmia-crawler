# -*- coding: utf-8 -*-
"""
In this module, you can find items.
DocumentItem contains information about a Document (or Webpage).
LinkItem contains information about a Link between two Documents.
"""
import re
import unicodedata

from scrapy.item import Field, Item
from scrapy.loader.processors import MapCompose, TakeFirst

all_chars = (unichr(i) for i in xrange(0x110000))
control_chars = ''.join(c for c in all_chars if unicodedata.category(c) == 'Cc')
control_char_re = re.compile('[%s]' % re.escape(control_chars))

def remove_control_chars(s):
    """ Returns a string without non-printable characters like \n \r \t """
    return control_char_re.sub(' ', s)

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
    url = Field(output_processor=TakeFirst())
    h1 = Field(output_processor=TakeFirst())
    raw_title = Field(output_processor=TakeFirst())
    raw_url = Field(output_processor=TakeFirst())
    raw_text = Field(output_processor=TakeFirst())
    title = Field(input_processor=MapCompose(remove_control_chars),
                  output_processor=TakeFirst())
    meta = Field(input_processor=MapCompose(remove_control_chars),
                 output_processor=TakeFirst())
    content = Field(input_processor=MapCompose(remove_control_chars),
                    output_processor=TakeFirst())
    domain = Field(output_processor=TakeFirst())
    content_type = Field(output_processor=TakeFirst())
    updated_on = Field(output_processor=TakeFirst())
    links = Field()

class LinkItem(Item):
    """
    Informations about a Link.
    Source is the absolute url of the source document.
    Target is the absolute url of the target document.
    Anchor is the text used to describe the target document and can be empty.
    """
    source = Field()
    target = Field()
    anchor = Field()

class AuthorityItem(Item):
    """
    Authority score of a page
    Url is the _id of the document (an SHA1 hash of its url).
    Score is the pagerank score computed.
    """
    url = Field()
    score = Field()
