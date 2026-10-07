# -*- coding: utf-8 -*-
"""Proxy middleware and other middlewares to support special handling."""
import hashlib
import logging
import re
from urllib.parse import urlparse

from scrapy.exceptions import IgnoreRequest

from scrapy.exceptions import (
    IgnoreRequest,
    DownloadTimeoutError,
    DownloadConnectionRefusedError,
)

# Get a logger instance for this module
logger = logging.getLogger(__name__)

def extract_domains(request):
    """Extract the main domain, xyz.onion, from the URL address"""
    parsed_uri = urlparse(request.url)
    domain = parsed_uri.netloc # abc.xyz.onion
    main_domain = '.'.join(domain.split('.')[-2:]) # xyz.onion
    return main_domain, domain # Return xyz.onion, abc.xyz.onion

class ProxyMiddleware:
    """Middleware for .onion addresses."""

    @classmethod
    def from_crawler(cls, crawler):
        mw = cls()
        mw.crawler = crawler
        mw.settings = crawler.settings
        return mw

    def process_request(self, request):
        """Process incoming request."""
        main_domain, _ = extract_domains(request)
        if not main_domain.endswith('.onion') or len(main_domain) != 62:
            logger.debug(f'Ignoring request {main_domain}, not v3 onion domain.')
            raise IgnoreRequest("Not a valid onion v3 address")
        proxies = self.settings.get('HTTP_PROXY_TOR_PROXIES', [])
        if not proxies:
            raise IgnoreRequest("No Tor proxies configured")
        # Always select the same proxy for the same onion domain
        # This will keep only one underlining Tor circuit to the onion service
        # Onion addresses form an uniform distribution
        # Deterministic, side-effect-free selection
        h = hashlib.blake2b(main_domain.encode('utf-8'), digest_size=8).digest()
        index = int.from_bytes(h, 'big') % len(proxies)
        # Always select the same proxy for the same onion address
        request.meta['proxy'] = proxies[index]

class FilterBannedDomains:
    """Middleware to filter requests to banned domains."""

    @classmethod
    def from_crawler(cls, crawler):
        mw = cls()
        mw.settings = crawler.settings
        return mw

    def process_request(self, request):
        main_domain, domain = extract_domains(request)
        hash_main_domain = hashlib.md5(main_domain.encode('utf-8')).hexdigest()
        hash_domain = hashlib.md5(domain.encode('utf-8')).hexdigest()
        seed_domain_list = [urlparse(url).netloc for url in self.settings.get('SEEDLIST', [])]
        banned_domains = self.settings.get('BANNED_DOMAINS', [])
        if not domain in seed_domain_list and not main_domain in seed_domain_list:
            if hash_domain in banned_domains or hash_main_domain in banned_domains:
                logger.debug(f"Ignoring request {request.url}, domain is banned.")
                raise IgnoreRequest("Domain is banned")

class SubDomainLimit:
    """Ignore weird sub domain loops."""
    def process_request(self, request):
        _, domain = extract_domains(request)
        if domain.count('.') > 3: # abc.abc.someonion.onion -> 3
            logger.debug(f"Ignoring request {request.url}, too many sub domains.")
            raise IgnoreRequest("Too many sub domains")

class FilterResponses:
    """Limit the HTTP response types that Scrapy downloads."""
    def process_response(self, request, response):
        type_whitelist = (r'text', )
        content_type_header = response.headers.get('content-type', b'').decode('utf-8')
        if not self.is_valid_response(type_whitelist, content_type_header):
            logger.debug(f"Ignoring response from {response.url}, content-type not in whitelist")
            raise IgnoreRequest("Content-type not in whitelist")
        return response

    @staticmethod
    def is_valid_response(type_whitelist, content_type_header):
        """ Check if some whitelist type in content_type_header """
        for type_regex in type_whitelist:
            if re.search(type_regex, content_type_header):
                return True
        return False

class DomainLimitMiddleware:
    """A request counter for each domain and a limit the number of requests"""
    def __init__(self, max_requests):
        self.max_requests = max_requests
        self.domains_count = {}

    @classmethod
    def from_crawler(cls, crawler):
        """ This method is used by Scrapy to create your middleware instance """
        return cls(max_requests=crawler.settings.getint('DOMAIN_MAX_REQUESTS', 0))

    def process_request(self, request):
        """ Limit per domain or, otherwise, let Scrapy process the request """
        if self.max_requests > 0:
            main_domain, _ = extract_domains(request)
            # Increment the request count for the domain
            self.domains_count[main_domain] = self.domains_count.get(main_domain, 0) + 1
            # Block the request if the domain has reached its limit
            if self.domains_count[main_domain] > self.max_requests:
                raise IgnoreRequest(f"Reached max requests for {main_domain}")

class DeadSiteTracker:
    """
    ダウンロード失敗（タイムアウト・接続拒否など、
    "サイトが死んでいる"ことを示す真のネットワークエラー）だけを検知する。

    IgnoreRequest（他ミドルウェアによる意図的なフィルタリング：
    BAN・サブドメイン過多・上限到達・非テキストレスポンス等）は、
    サイトの生死とは無関係なので、明示的に除外する。

    実測（2026-08-20時点、DEPTH_LIMIT=1でのテストクロール）により、
    以下の2種類が実際に発生することを確認済み:
      - DownloadTimeoutError（313件、60秒応答なし）
      - DownloadConnectionRefusedError（torfleet未起動時に大量発生。
        本番では稀だが、Tor回線の一時的な不調で今後も起こりうるため対象に含める）
    """

    # サイトが本当に死んでいることを示唆する例外の種類
    DEATH_SIGNAL_EXCEPTIONS = (
        DownloadTimeoutError,
        DownloadConnectionRefusedError,
    )

    @classmethod
    def from_crawler(cls, crawler):
        mw = cls()
        mw.settings = crawler.settings
        from elasticsearch import Elasticsearch
        mw.es = Elasticsearch(
            [mw.settings.get('ELASTICSEARCH_SERVER')],
            basic_auth=(
                mw.settings.get('ELASTICSEARCH_USERNAME'),
                mw.settings.get('ELASTICSEARCH_PASSWORD'),
            ),
            verify_certs=False,
            ssl_show_warn=False,
        )
        mw.index_name = mw.settings.get('ELASTICSEARCH_INDEX')
        return mw

    def process_exception(self, request, exception, spider):
        if isinstance(exception, IgnoreRequest):
            return None  # 意図的なスキップ。死活判定には関係ない

        if not isinstance(exception, self.DEATH_SIGNAL_EXCEPTIONS):
            logger.debug(
                f"未分類の例外のためスキップ: {request.url} "
                f"({type(exception).__name__})"
            )
            return None

        from .liveness_utils import record_crawl_failure, compute_doc_id
        doc_id = compute_doc_id(request.url)
        record_crawl_failure(self.es, self.index_name, doc_id, request.url)

        return None