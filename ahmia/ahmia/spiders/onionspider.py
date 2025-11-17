# -*- coding: utf-8 -*-
""" OnionSpider class to crawl onion websites through the Tor network """
import datetime
from urllib.parse import urlparse
import html2text
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector

from ahmia.items import DocumentItem

class OnionSpider(CrawlSpider):
    """ The base to crawl onion webpages """
    name = "ahmia-tor"

    def __init__(self, *args, seedlist=None, **kwargs):
        """ Init """
        super().__init__(*args, **kwargs)  # Python 3 style super()

        self.rules = (
            Rule(
                LinkExtractor(
                    allow=[r"^https?://[a-z2-7]{56}\.onion(?:/.*)?$"],
                    deny_extensions=[
                        "7z","apk","bin","bz2","dmg","exe","gif","gz","ico","iso","jar",
                        "jpg","jpeg","mp3","mp4","m4a","ogg","pdf","png","rar","svg",
                        "tar","tgz","webm","webp","xz","zip"
                    ],
                    unique=True,
                    canonicalize=True,
                ),
                callback="parse_item",
                follow=True,
            ),
        )
        self._compile_rules()

        if seedlist:  # Override SEEDLIST if `seedlist` argument is provided
            # scrapy crawl ahmia-tor\
            # -a seedlist=\
            # 'http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/add/onionsadded/',\
            # 'http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/add/onionsadded/'
            self.start_urls = [url.strip() for url in seedlist.split(',') if url.strip()]
        else:
            from scrapy.utils.project import get_project_settings # defer to project settings
            self.start_urls = get_project_settings().get("SEEDLIST", [])

    def html2string(self, response):
        """ Convert HTML content to plain text """
        converter = html2text.HTML2Text()
        converter.ignore_links = True
        converter.ignore_images = True
        return converter.handle(response.text)

    def parse_item(self, response):
        """ Parse items  """
        sel = Selector(response)
        title = " ".join(sel.xpath("//title/text()").getall()).strip()
        h1 = " ".join(sel.xpath("//h1/text()").getall()).strip()
        body_text = self.html2string(response)
        full_content = f"{title} {body_text}"
        item = DocumentItem()
        item["url"] = response.url
        item["domain"] = urlparse(response.url).hostname.lower()
        item["title"] = title[:200]
        item["h1"] = h1[:200]
        meta_desc = sel.xpath("//meta[@name='description']/@content").get()
        item["meta"] = (meta_desc or "")[:1000]
        item["content"] = full_content[:1500000]
        item["content_type"] = response.headers.get("Content-Type", b"").decode("utf-8")
        item["updated_on"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        return item
