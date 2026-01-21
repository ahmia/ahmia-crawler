# -*- coding: utf-8 -*-
""" OnionSpider class to crawl onion websites through the Tor network """
import datetime
from urllib.parse import urlparse
import html2text
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from ahmia.items import DocumentItem

class OnionSpider(CrawlSpider):
    """ The base to crawl onion webpages """
    name = "ahmia-tor"

    rules = (
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

    def __init__(self, *args, seedlist=None, **kwargs):
        """ Init """
        super().__init__(*args, **kwargs)  # Python 3 style super()

        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = True
        self.html_converter.ignore_images = True

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
        return self.html_converter.handle(response.text)

    def parse_item(self, response):
        """ Parse items  """
        title = " ".join(response.xpath("//title/text()").getall()).strip()
        h1 = " ".join(response.xpath("//h1/text()").getall()).strip()
        meta_desc = response.xpath("//meta[@name='description']/@content").get()
        body_text = self.html_converter.handle(response.text)

        item = DocumentItem()
        item["url"] = response.url
        item["domain"] = urlparse(response.url).hostname.lower()
        item["title"] = title[:200]
        item["h1"] = h1[:200]
        item["meta"] = (meta_desc or "")[:1000]
        item["content"] = f"{title} {body_text}"[:1500000]
        item["content_type"] = response.headers.get("Content-Type", b"").decode("utf-8")
        item["updated_on"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        del response

        return item
