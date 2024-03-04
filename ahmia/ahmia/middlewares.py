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

def extract_domains(request):
    """Extract the main domain, xyz.onion, from the URL address"""
    parsed_uri = urlparse(request.url)
    domain = parsed_uri.netloc # abc.xyz.onion
    main_domain = '.'.join(domain.split('.')[-2:]) # xyz.onion
    return main_domain, domain # Return xyz.onion, abc.xyz.onion

class ProxyMiddleware:
    """Middleware for .onion addresses."""
    def process_request(self, request, spider):
        """Process incoming request."""
        main_domain, _ = extract_domains(request)
        if not main_domain.endswith('.onion') or len(main_domain) != 62:
            logger.debug(f'Ignoring request {main_domain}, not v3 onion domain.')
            raise IgnoreRequest("Not a valid onion v3 address")
        # Always select the same proxy for the same onion domain
        # This will keep only one underlining Tor circuit to the onion service
        # Onion addresses form an uniform distribution
        # Therefore this address can be used as a seed for random
        random.seed(main_domain) # A seed for randomness is the onion domain
        # Always select the same proxy for the same onion address
        request.meta['proxy'] = random.choice(settings.get('HTTP_PROXY_TOR_PROXIES'))

class FilterBannedDomains:
    """Middleware to filter requests to banned domains."""
    def process_request(self, request, spider):
        main_domain, domain = extract_domains(request)
        hash_main_domain = hashlib.md5(main_domain.encode('utf-8')).hexdigest()
        hash_domain = hashlib.md5(domain.encode('utf-8')).hexdigest()
        seed_domain_list = [urlparse(url).netloc for url in settings.get('SEEDLIST', [])]
        banned_domains = settings.get('BANNED_DOMAINS', [])
        if not domain in seed_domain_list and not main_domain in seed_domain_list:
            if hash_domain in banned_domains or hash_main_domain in banned_domains:
                logger.info(f"Ignoring request {request.url}, domain is banned.")
                raise IgnoreRequest("Domain is banned")

class SubDomainLimit:
    """Ignore weird sub domain loops."""
    def process_request(self, request, spider):
        _, domain = extract_domains(request)
        if domain.count('.') > 3: # abc.abc.someonion.onion -> 3
            logger.debug(f"Ignoring request {request.url}, too many sub domains.")
            raise IgnoreRequest("Too many sub domains")

class FilterResponses:
    """Limit the HTTP response types that Scrapy downloads."""
    def process_response(self, request, response, spider):
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

    def process_request(self, request, spider):
        """ Limit per domain or, otherwise, let Scrapy process the request """
        if self.max_requests > 0:
            main_domain, _ = extract_domains(request)
            # Increment the request count for the domain
            self.domains_count[main_domain] = self.domains_count.get(main_domain, 0) + 1
            # Block the request if the domain has reached its limit
            if self.domains_count[main_domain] > self.max_requests:
                raise IgnoreRequest(f"Reached max requests for {main_domain}")
