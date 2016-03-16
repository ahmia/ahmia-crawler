# -*- coding: utf-8 -*-

# Scrapy settings for monitor project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

from scrapy import log
import requests  # To fetch the list of banned domains

BOT_NAME = 'onionElasticBot'

SPIDER_MODULES = ['onionElasticBot.spiders']
NEWSPIDER_MODULE = 'onionElasticBot.spiders'

ELASTICSEARCH_SERVER = 'localhost' # If not 'localhost' prepend 'http://'
ELASTICSEARCH_PORT = 9200 # If port 80 leave blank
ELASTICSEARCH_USERNAME = ''
ELASTICSEARCH_PASSWORD = ''
ELASTICSEARCH_INDEX = 'crawl'
ELASTICSEARCH_TYPE = 'tor'
ELASTICSEARCH_UNIQ_KEY = 'url'
ELASTICSEARCH_LOG_LEVEL= log.DEBUG

# Read domain area from a file, give path
ALLOWED_DOMAINS = ""
# Read seed list from a file, give path
TARGET_SITES = ""

# Identify as normal Tor Browser
USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; rv:24.0) Gecko/20100101 Firefox/24.0"

DOWNLOAD_TIMEOUT = 60 # 60s

# Search engine point of view
CONCURRENT_REQUESTS = 50
LOG_LEVEL = 'INFO'
COOKIES_ENABLED = False
RETRY_ENABLED = False
DOWNLOAD_MAXSIZE = 1000000 #Max-limit in bytes

# Crawling depth
DEPTH_LIMIT=1

ROBOTSTXT_OBEY=True

# Middlewares
DOWNLOADER_MIDDLEWARES = {
    'onionElasticBot.middleware.ProxyMiddleware': 100,
    'onionElasticBot.middleware.FilterBannedDomains': 200,
    'onionElasticBot.middleware.FilterFakeDomains': 300,
    'onionElasticBot.middleware.FilterResponses': 400,
    'onionElasticBot.middleware.SubDomainLimit': 500,
}

# Pipelines
ITEM_PIPELINES = {
    'onionElasticBot.pipelines.AddTimestampPipeline': 100,
    'scrapyelasticsearch.scrapyelasticsearch.ElasticSearchPipeline': 1000,
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
        FAKE_DOMAINS.append(onion)

# HTTP proxy settings
# port X8123 is for polipo (Tor)
# port 8118 is for privoxy (Tor)
# port 4444 and 4445 is for i2p HTTP/HTTPS proxy
HTTP_PROXY_TOR_PROXIES = ["http://localhost:8123/", "http://localhost:8123/", "http://localhost:8123/"]
HTTP_PROXY_I2P = "http://localhost:4444/" # HTTP i2p proxy in localhost
HTTPS_PROXY_I2P = "http://localhost:4445/" # HTTPS i2p proxy in localhost
