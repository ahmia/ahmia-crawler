# -*- coding: utf-8 -*-
"""Proxy middleware and other middlewares to support special handling."""
import hashlib
import logging
import random
import re
from urllib.parse import urlparse

from scrapy.utils.project import get_project_settings
from scrapy.exceptions import IgnoreRequest

# Get a logger instance for this module
logger = logging.getLogger(__name__)

settings = get_project_settings()

class ProxyMiddleware(object):
    """Middleware for .onion/.i2p addresses."""
    def process_request(self, request, spider):
        """Process incoming request."""
        parsed_uri = urlparse(request.url)
        domain = parsed_uri.netloc
        scheme = parsed_uri.scheme
        if not domain.endswith('.onion') or len(domain) != 62:
            logger.info(f'Ignoring request {domain}, not v3 onion domain.')
            raise IgnoreRequest("Not a valid onion v3 address")
        tor_proxy_list = settings.get('HTTPS_PROXY_TOR_PROXIES') if scheme == "https" else settings.get('HTTP_PROXY_TOR_PROXIES')
        # Always select the same proxy for the same onion domain
        # This will keep only one underlining Tor circuit to the onion service
        # Onion addresses form an uniform distribution
        # Therefore this address can be used as a seed for random
        random.seed(domain) # A seed for randomness is the onion domain
        # Always select the same proxy for the same onion address
        request.meta['proxy'] = random.choice(tor_proxy_list)

class FilterBannedDomains(object):
    """Middleware to filter requests to banned domains."""
    def process_request(self, request, spider):
        domain = urlparse(request.url).netloc
        maindomain = ".".join(domain.split(".")[-2:])
        hash_maindomain = hashlib.md5(f"{maindomain}\n".encode('utf-8')).hexdigest()
        hash_domain = hashlib.md5(f"{domain}\n".encode('utf-8')).hexdigest()
        seed_domain_list = [urlparse(url).netloc for url in settings.get('SEEDLIST', [])]
        banned_domains = settings.get('BANNED_DOMAINS', [])
        if not domain in seed_domain_list and not maindomain in seed_domain_list:
            if hash_domain in banned_domains or hash_maindomain in banned_domains:
                logger.info(f"Ignoring request {request.url}, domain is banned.")
                raise IgnoreRequest("Domain is banned")

class SubDomainLimit(object):
    """Ignore weird sub domain loops."""
    def process_request(self, request, spider):
        hostname = urlparse(request.url).hostname
        if hostname.count('.') > 3: # abc.abc.someonion.onion -> 3
            logger.info(f"Ignoring request {request.url}, too many sub domains.")
            raise IgnoreRequest("Too many sub domains")

class FilterResponses(object):
    """Limit the HTTP response types that Scrapy downloads."""
    def process_response(self, request, response, spider):
        type_whitelist = (r'text', )
        content_type_header = response.headers.get('content-type', b'').decode('utf-8')
        if not self.is_valid_response(type_whitelist, content_type_header):
            logger.info(f"Ignoring response from {response.url}, content-type not in whitelist")
            raise IgnoreRequest("Content-type not in whitelist")
        return response

    @staticmethod
    def is_valid_response(type_whitelist, content_type_header):
        for type_regex in type_whitelist:
            if re.search(type_regex, content_type_header):
                return True
        return False
