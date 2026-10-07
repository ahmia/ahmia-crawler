# -*- coding: utf-8 -*-
""" OnionSpider class to crawl onion webpages through the Tor network """
import datetime
from collections import Counter, defaultdict
from urllib.parse import urlparse

import html2text
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from ahmia.items import DocumentItem


class OnionSpider(CrawlSpider):
    """ The base to crawl onion webpages """
    name = "ahmia-tor"

    # Debug thresholds only, not enforcement limits.
    LARGE_RESPONSE_BYTES = 2 * 1024 * 1024
    LARGE_TEXT_BYTES = 2 * 1024 * 1024

    MAX_EXTRACTED_LINKS_PER_DOMAIN = 50000
    # 集めるサイトの条件指定
    rules = (
        Rule(
            LinkExtractor(
                allow=[r"^https?://[a-z2-7]{56}\.onion(?:/.*)?$"],
                deny_extensions=[
                    "7z", "apk", "bin", "bz2", "dmg", "exe", "gif", "gz", "ico", "iso", "jar",
                    "jpg", "jpeg", "mp3", "mp4", "m4a", "ogg", "pdf", "png", "rar", "svg",
                    "tar", "tgz", "webm", "webp", "xz", "zip"
                ],
                unique=True, # 同一リンクは排除
                canonicalize=True,
            ),
            callback="parse_item",
            follow=True,
            process_links="limit_links_per_domain",
        ),
    )

    # 初期設定
    def __init__(self, *args, seedlist=None, **kwargs):
        """ Init """
        super().__init__(*args, **kwargs)

        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = True
        self.html_converter.ignore_images = True

        self._extracted_links_per_domain = defaultdict(int) # リンク内にあったリンク数を保存する変数
        self._current_response_host = None

        if seedlist:
            self.start_urls = [url.strip() for url in seedlist.split(',') if url.strip()]
            self.logger.info("Using 'seedlist' argument with %d URLs.", len(self.start_urls))
        else:
            from scrapy.utils.project import get_project_settings
            self.start_urls = get_project_settings().get("SEEDLIST", [])
            self.logger.info("Using SEEDLIST from settings.py with %d URLs.", len(self.start_urls))

    # 1ドメインから取得するリンク数の制限
    def limit_links_per_domain(self, links):
        """Limit extracted links to 50,000 per one domain."""
        kept = []

        host = (self._current_response_host or "").lower()
        if not host:
            return links

        original_count = len(links)
        remaining = self.MAX_EXTRACTED_LINKS_PER_DOMAIN - self._extracted_links_per_domain[host]

        if original_count >= 1000:
            self.logger.warning(
                "Large link extraction batch: response_host=%s extracted_links=%d already_seen_for_host=%d remaining_budget=%d",
                host,
                original_count,
                self._extracted_links_per_domain[host],
                max(0, remaining),
            )

        if remaining <= 0:
            self.logger.info(
                "Per-domain extracted link budget exhausted: response_host=%s limit=%d",
                host,
                self.MAX_EXTRACTED_LINKS_PER_DOMAIN,
            )
            return kept

        for link in links:
            if remaining <= 0:
                break
            self._extracted_links_per_domain[host] += 1
            kept.append(link)
            remaining -= 1

        kept_count = len(kept)
        dropped_count = original_count - kept_count
        if dropped_count > 0:
            self.logger.warning(
                "Dropped links due to per-domain extraction budget: response_host=%s kept=%d dropped=%d total_for_host=%d",
                host,
                kept_count,
                dropped_count,
                self._extracted_links_per_domain[host],
            )

        return kept

    def html2string(self, response):
        """Convert HTML content to plain text."""
        return self.html_converter.handle(response.text)

    def parse_start_url(self, response):
        self._current_response_host = (urlparse(response.url).hostname or "").lower()
        return self.parse_item(response)

    def _debug_log_page_characteristics(self, response, body_text):
        response_size = len(response.body or b"")
        text_size = len(body_text.encode("utf-8", errors="ignore")) if body_text else 0
        hostname = (urlparse(response.url).hostname or "").lower()
        content_type = response.headers.get("Content-Type", b"").decode("utf-8", errors="ignore")

        stats = self.crawler.stats
        stats.max_value("debug/max_response_bytes", response_size)
        stats.max_value("debug/max_text_bytes", text_size)

        if content_type:
            content_type_base = content_type.split(";")[0].strip()
            stats.inc_value(f"debug/content_type/{content_type_base}")

        if response_size >= self.LARGE_RESPONSE_BYTES or text_size >= self.LARGE_TEXT_BYTES:
            self.logger.warning(
                "LARGE_PAGE url=%s domain=%s response_bytes=%d text_bytes=%d content_type=%s",
                response.url,
                hostname,
                response_size,
                text_size,
                content_type,
            )

    def _safe_html2text(self, response):
        """
        Convert HTML to text, but suppress noisy html2text/parser tracebacks caused by broken HTML.
        Return an empty string on failure and log a compact warning instead.
        """
        try:
            return self.html_converter.handle(response.text)
        except Exception as exc:
            self.crawler.stats.inc_value("debug/html2text_errors")
            self.logger.warning(
                "html2text failed for url=%s domain=%s exc=%s: %s",
                response.url,
                (urlparse(response.url).hostname or "").lower(),
                exc.__class__.__name__,
                exc,
            )
            return ""

    # 取得したHTMLをparseItemに変換
    def parse_item(self, response):
        """Parse items."""
        self._current_response_host = (urlparse(response.url).hostname or "").lower()

        response_size = len(response.body or b"")
        if response_size >= self.LARGE_RESPONSE_BYTES:
            self.logger.warning(
                "Large raw response before parsing: url=%s bytes=%d",
                response.url,
                response_size,
            )

        title = " ".join(response.xpath("//title/text()").getall()).strip()
        h1 = " ".join(response.xpath("//h1/text()").getall()).strip()
        meta_desc = response.xpath("//meta[@name='description']/@content").get()

        body_text = self._safe_html2text(response)

        self._debug_log_page_characteristics(response, body_text)

        item = DocumentItem()
        item["url"] = response.url
        item["domain"] = urlparse(response.url).hostname.lower()
        item["title"] = title[:200]
        item["h1"] = h1[:200]
        item["meta"] = (meta_desc or "")[:1000]
        item["content"] = f"{title} {body_text}"[:1500000]
        item["content_type"] = response.headers.get("Content-Type", b"").decode("utf-8")
        item["updated_on"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        content_size = len(item["content"].encode("utf-8", errors="ignore"))
        self.crawler.stats.max_value("debug/max_indexed_content_bytes", content_size)

        del response

        return item

    def closed(self, reason):
        counts = Counter(self._extracted_links_per_domain)
        self.logger.info(
            "Spider closed: reason=%s extracted_domains=%d extracted_total=%d top_domains=%s",
            reason,
            len(self._extracted_links_per_domain),
            sum(self._extracted_links_per_domain.values()),
            counts.most_common(20),
        )
