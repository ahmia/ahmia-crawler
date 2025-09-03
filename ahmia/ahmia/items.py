# -*- coding: utf-8 -*-
"""
Defines Scrapy Items for Document, Link, and Authority data.
"""
import re
import unicodedata
from scrapy.item import Field, Item
from itemloaders.processors import TakeFirst, MapCompose

# Compile a regex for control characters for efficiency
all_chars = (chr(i) for i in range(0x110000))
CHARS = ''.join(c for c in all_chars if unicodedata.category(c) == 'Cc')
CHARS_RE = re.compile(f'[{re.escape(CHARS)}]')

def remove_control_chars(s):
    """Remove control characters from a string."""
    return CHARS_RE.sub(' ', s)

def to_float(s):
    """Convert a string to float if possible, else return None."""
    try:
        return float(s)
    except ValueError:
        return None

class DocumentItem(Item):
    """Represents a webpage document."""
    url = Field(output_processor=TakeFirst())
    h1 = Field(output_processor=TakeFirst())
    title = Field(input_processor=MapCompose(remove_control_chars), output_processor=TakeFirst())
    meta = Field(input_processor=MapCompose(remove_control_chars), output_processor=TakeFirst())
    content = Field(input_processor=MapCompose(remove_control_chars), output_processor=TakeFirst())
    domain = Field(output_processor=TakeFirst())
    content_type = Field(output_processor=TakeFirst())
    updated_on = Field(output_processor=TakeFirst())
    links = Field()
