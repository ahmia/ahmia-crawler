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

ELASTICSEARCH_SERVERS = ['http://localhost:9200']  # For scrapy-elasticsearch
ELASTICSEARCH_SERVER = ELASTICSEARCH_SERVERS[0]  # For special update
ELASTICSEARCH_TOR_INDEX = datetime.datetime.now().strftime("tor-%Y-%m")
ELASTICSEARCH_I2P_INDEX = datetime.datetime.now().strftime("i2p-%Y-%m")
ELASTICSEARCH_TYPE = 'doc'

# For the optional research pipeline
ELASTICSEARCH_RESEARCH_INDEX = 'research'
ELASTICSEARCH_CONTENT_TYPE = 'content'
ELASTICSEARCH_CRAWL_TYPE = 'crawl'
RESEARCH_GATHERING = False

ELASTICSEARCH_UNIQ_KEY = 'url'
ELASTICSEARCH_LOG_LEVEL = logging.INFO

# Read domain area from a file, give path
ALLOWED_DOMAINS = ""
# Read seed list from a file, give path
TARGET_SITES = ""

# Identify as normal Tor Browser
USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; rv:45.0) Gecko/20100101 Firefox/45.0"

DOWNLOAD_TIMEOUT = 80  # seconds
DOWNLOAD_DELAY = 1

# Search engine point of view
CONCURRENT_REQUESTS = 100
LOG_LEVEL = 'INFO'
COOKIES_ENABLED = False
RETRY_ENABLED = False
DOWNLOAD_MAXSIZE = 1000000  # Max-limit in bytes
REACTOR_THREADPOOL_MAXSIZE = 20
REDIRECT_ENABLED = False
AJAXCRAWL_ENABLED = True

# Crawling depth
DEPTH_LIMIT = 1

ROBOTSTXT_OBEY = True

# Middlewares
DOWNLOADER_MIDDLEWARES = {
    'ahmia.middleware.ProxyMiddleware': 100,
    'ahmia.middleware.FilterBannedDomains': 200,
    'ahmia.middleware.FilterResponses': 400,
    'ahmia.middleware.SubDomainLimit': 500,
}

SEEDLIST = ['http://zqktlwiuavvvqqt4ybvgvi7tyo4hjl5xgfuvpdf6otjiycgwqbym2qad.onion/wiki/index.php/Main_Page',
         'http://3bbad7fauom4d6sgppalyqddsqbf5u5p56b5k5uk2zxsy3d6ey2jobad.onion/discover',
         'http://tt3j2x4k5ycaa5zt.onion/',
         'http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/address/',
         'http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/add/onionsadded/',
         'http://donionsixbjtiohce24abfgsffo2l4tk26qx464zylumgejukfq2vead.onion/?cat=20&pg=1&lang=en',
         'http://donionsixbjtiohce24abfgsffo2l4tk26qx464zylumgejukfq2vead.onion/?cat=7&pg=1&lang=en',
         'https://github.com/alecmuffett/real-world-onion-sites']

url = "http://donionsixbjtiohce24abfgsffo2l4tk26qx464zylumgejukfq2vead.onion/?cat=19&pg="
for i in range(1, 500):
    SEEDLIST.append(url + str(i))

BANNED_DOMAINS = []
response = requests.get('https://ahmia.fi/banned/?987654321')
for md5 in response.text.split("\n"):
    md5 = md5.strip().replace(" ", "")
    if len(md5) is 32:
        BANNED_DOMAINS.append(md5)

FAKE_DOMAINS = []
response = requests.get('https://ahmia.fi/static/fakelist.txt')
for onion in response.text.split("\n"):
    onion = onion.strip().replace(" ", "")
    if len(onion) is 16:
        FAKE_DOMAINS.append('%s.onion' % onion)

# Tor proxy settings
HTTPS_PROXY_TOR_PROXIES = ["http://localhost:8123/"]  # Tor HTTPS Polipo proxy
# Tor HTTP Python proxies localhost:15000 ... localhost:15029
HTTP_PROXY_TOR_PROXIES = ["http://localhost:150%02d" % i for i in range(0,30)]
# i2p proxy settings
HTTP_PROXY_I2P = "http://localhost:4444/" # HTTP i2p proxy in localhost
HTTPS_PROXY_I2P = "http://localhost:4445/" # HTTPS i2p proxy in localhost
