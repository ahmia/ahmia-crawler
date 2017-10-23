# -*- coding: utf-8 -*-
"""Settings"""

# Scrapy settings for monitor project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

import logging
import requests  # To fetch the list of banned domains
import datetime # Index name according to YEAR-MONTH

BOT_NAME = 'ahmia'

SPIDER_MODULES = ['ahmia.spiders']
NEWSPIDER_MODULE = 'ahmia.spiders'

ELASTICSEARCH_SERVERS = ['http://localhost:9200'] # For scrapy-elasticsearch
ELASTICSEARCH_SERVER = ELASTICSEARCH_SERVERS[0] # For special update

# Automatic index name selection according to YEAR-MONTH, i.e. crawl-2017-12
ELASTICSEARCH_INDEX = datetime.datetime.now().strftime("crawl-%Y-%m")
ELASTICSEARCH_RESEARCH_INDEX = 'research'

ELASTICSEARCH_TYPE = 'tor'
ELASTICSEARCH_CONTENT_TYPE = 'content'
ELASTICSEARCH_CRAWL_TYPE = 'crawl'
ELASTICSEARCH_UNIQ_KEY = 'url'
ELASTICSEARCH_LOG_LEVEL = logging.INFO

# Read domain area from a file, give path
ALLOWED_DOMAINS = ""
# Read seed list from a file, give path
TARGET_SITES = ""

# Identify as normal Tor Browser
USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; rv:45.0) Gecko/20100101 Firefox/45.0"

DOWNLOAD_TIMEOUT = 60 # 60s
DOWNLOAD_DELAY = 1

# Search engine point of view
CONCURRENT_REQUESTS = 100
LOG_LEVEL = 'INFO'
COOKIES_ENABLED = False
RETRY_ENABLED = False
DOWNLOAD_MAXSIZE = 1000000 #Max-limit in bytes
REACTOR_THREADPOOL_MAXSIZE = 20
REDIRECT_ENABLED = False
AJAXCRAWL_ENABLED = True

# Crawling depth
DEPTH_LIMIT = 3

ROBOTSTXT_OBEY = True

# Middlewares
DOWNLOADER_MIDDLEWARES = {
    'ahmia.middleware.ProxyMiddleware': 100,
    'ahmia.middleware.FilterBannedDomains': 200,
    'ahmia.middleware.FilterResponses': 400,
    'ahmia.middleware.SubDomainLimit': 500,
}

# Pipelines
ITEM_PIPELINES = {
    'ahmia.pipelines.CustomElasticSearchPipeline': 100,
    'ahmia.pipelines.HistoricalElasticSearchPipeline':200,
}

BANNED_DOMAINS = []
response = requests.get('https://ahmia.fi/banned/')
for md5 in response.text.split("\n"):
    if len(md5) is 32:
        BANNED_DOMAINS.append(md5)

FAKE_DOMAINS = []
response = requests.get('https://ahmia.fi/static/fakelist.txt')
for onion in response.text.split("\n"):
    if len(onion) is 16:
        FAKE_DOMAINS.append('%s.onion' % onion)

# HTTP proxy settings
# port 8123 is for polipo (Tor)
# port 8118 is for privoxy (Tor)
# port 4444 and 4445 is for i2p HTTP/HTTPS proxy
# port 3128 is HAProxy load balancer
# port 14444 pure HTTP socks tor proxy
HTTP_PROXY_TOR_PROXIES = ["http://localhost:8123/"] # Tor HTTP proxy
HTTP_PROXY_I2P = "http://localhost:4444/" # HTTP i2p proxy in localhost
HTTPS_PROXY_I2P = "http://localhost:4445/" # HTTPS i2p proxy in localhost
