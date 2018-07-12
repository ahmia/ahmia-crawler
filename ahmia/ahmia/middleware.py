"""Proxy middleware to support .onion addresses."""

# Install Polipo
# and setup Polipo http://localhost:8123/

# Install Tor with Tor2web mode

# Direct every request to .onion sites to privoxy that uses Tor

import re
import random
import hashlib
import logging
from urlparse import urlparse
from scrapy.exceptions import IgnoreRequest

from scrapy.conf import settings


class ProxyMiddleware(object):
    """Middleware for .onion/.i2p addresses."""
    def process_request(self, request, spider): # pylint:disable=unused-argument
        """Process incoming request."""
        parsed_uri = urlparse(request.url)
        domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        if ".onion" in domain and ".onion." not in domain:
            # Always select the same proxy for the same onion domain
            # This will keep only one underlining Tor circuit to the onion service
            # Onion addresses form an uniform distribution
            # Therefore this address can be used as a seed for random
            hash = '{uri.netloc}'.format(uri=parsed_uri).replace(".onion", "")
            random.seed( hash ) # A seed for randomness is the onion domain
            # List of proxies available
            tor_proxy_list = settings.get('HTTP_PROXY_TOR_PROXIES')
            # Always select the same proxy for the same onion address
            request.meta['proxy'] = random.choice(tor_proxy_list)
        elif ".i2p" in domain and ".i2p." not in domain:
            if parsed_uri.scheme == "https":
                request.meta['proxy'] = settings.get('HTTPS_PROXY_I2P')
            else:
                request.meta['proxy'] = settings.get('HTTP_PROXY_I2P')

class FilterBannedDomains(object):
    """
    Middleware to filter requests to banned domains.
    """
    def process_request(self, request, spider): # pylint:disable=unused-argument
        """Process incoming request."""
        parsed_uri = urlparse(request.url)
        domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        domain = domain.replace("http://", "").replace("https://", "") \
                                              .replace("/", "")
        banned_domains = settings.get('BANNED_DOMAINS')
        if hashlib.md5(domain).hexdigest() in banned_domains:
            # Do not execute this request
            request.meta['proxy'] = ""
            msg = "Ignoring request {}, This domain is banned." \
                  .format(request.url)
            logging.info(msg)
            raise IgnoreRequest()

class SubDomainLimit(object):
    """
    Ignore weird sub domain loops (for instance, rss..rss.rss.something.onion)
    """
    def process_request(self, request, spider): # pylint:disable=unused-argument
        """Process incoming request."""
        hostname = urlparse(request.url).hostname
        if len(hostname.split(".")) > 4:
            # Do not execute this request
            request.meta['proxy'] = ""
            msg = "Ignoring request {}, too many sub domains." \
                  .format(request.url)
            logging.info(msg)
            raise IgnoreRequest()

class FilterResponses(object):
    """Limit the HTTP response types that Scrapy downloads."""

    @staticmethod
    def is_valid_response(type_whitelist, content_type_header):
        """Is the response valid?"""
        for type_regex in type_whitelist:
            if re.search(type_regex, content_type_header):
                return True
        return False

    def process_response(self, request, response, spider): # pylint:disable=unused-argument
        """
        Only allow HTTP response types that that match the given list of
        filtering regexs
        """
        # to specify on a per-spider basis
        # type_whitelist = getattr(spider, "response_type_whitelist", None)
        type_whitelist = (r'text', )
        content_type_header = response.headers.get('content-type', None)
        if content_type_header and self.is_valid_response(type_whitelist,
                                                          content_type_header):
            return response
        else:
            msg = "Ignoring request {}, content-type was not in whitelist" \
                  .format(response.url)
            logging.info(msg)
            raise IgnoreRequest()
