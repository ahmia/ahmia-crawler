# -*- coding: utf-8 -*-
""" Settings """
import warnings
import datetime
import requests
from decouple import config

BOT_NAME = 'ahmia'

SPIDER_MODULES = ['ahmia.spiders']
NEWSPIDER_MODULE = 'ahmia.spiders'

# Log level and ignore useless warnings
LOG_LEVEL = 'INFO'
warnings.filterwarnings("ignore", category=RuntimeWarning,
                        module='scrapy.spidermiddlewares.referer',
                        message="Could not load referrer policy")

# Elasticsearch settings using environment variables for sensitive information
ELASTICSEARCH_SERVER = config('ES_URL', default="https://localhost:9200/")
ELASTICSEARCH_INDEX = datetime.datetime.now().strftime("onions-%Y-%m")
ELASTICSEARCH_USERNAME = config('ES_USERNAME', default='elastic')
ELASTICSEARCH_PASSWORD = config('ES_PASSWORD', default='password12345')
ELASTICSEARCH_CA_CERTS = config('ES_CA_CERTS',
                                default='/etc/elasticsearch/certs/http_ca.crt')
VERIFY_CERTS = config('VERIFY_CERTS', default=True)
SSL_SHOW_WARN = config('SSL_SHOW_WARN', default=True)

# Identify as normal Tor Browser
#USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0"

# Main settings for crawling speed and performance
DOWNLOAD_TIMEOUT = 120  # seconds
DOWNLOAD_DELAY = 1
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 2
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0  # Adjust based on performance

# Crawl in breadth-first order (BFO)
DEPTH_PRIORITY = 1
DOMAIN_MAX_REQUESTS = 1000 # Spider does not over-focus on large websites, set 0 for unlimited

SCHEDULER_DISK_QUEUE = "scrapy.squeues.PickleFifoDiskQueue"
SCHEDULER_MEMORY_QUEUE = "scrapy.squeues.FifoMemoryQueue"

JOBDIR = "jobdir" # disk-backed to avoid memory growth

# Broad Crawls
# https://docs.scrapy.org/en/latest/topics/broad-crawls.html
SCHEDULER_PRIORITY_QUEUE = "scrapy.pqueues.ScrapyPriorityQueue"
CONCURRENT_REQUESTS = 100
CONCURRENT_REQUESTS_PER_DOMAIN = 10
REACTOR_THREADPOOL_MAXSIZE = 100
DOWNLOAD_MAXSIZE = 5242880 # Max-limit in bytes, 5 MB, 5*1024*1024 = 5,242,880 bytes
COOKIES_ENABLED = False
RETRY_ENABLED = False

REDIRECT_ENABLED = True
REDIRECT_MAX_TIMES = 3
AJAXCRAWL_ENABLED = False
DEPTH_LIMIT = 10 # Crawling depth, default is 10
DEPTH_STATS_VERBOSE = True # Output per-depth request counts
ROBOTSTXT_OBEY = False

ITEM_PIPELINES = {
    'ahmia.pipelines.CustomElasticSearchPipeline': 900,
}

DOWNLOADER_MIDDLEWARES = {
    'ahmia.middlewares.ProxyMiddleware': 100,
    'ahmia.middlewares.FilterBannedDomains': 200,
    'ahmia.middlewares.DomainLimitMiddleware': 300,
    'ahmia.middlewares.SubDomainLimit': 400,
    'ahmia.middlewares.FilterResponses': 500, # Finally, filter non-text responses
}

SEEDLIST = [
    'http://3bbad7fauom4d6sgppalyqddsqbf5u5p56b5k5uk2zxsy3d6ey2jobad.onion/discover',
    'http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/address/?1234',
    'http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/add/onionsadded/?1234',
    'http://checkitzh2q35xf42lrtxc6a4o2aqpvvu5dpdophhl44rnqla7ffpkid.onion/',
    'http://jywxh4q4arybssyaxjmfqooknt6skj2qmjhblewrhteeppmusmsfbyqd.onion/'
]

for _i in range(2, 36):
    SEEDLIST.append(f"http://3bbad7fauom4d6sgppalyqddsqbf5u5p56b5k5uk2zxsy3d6ey2jobad.onion/discover?p={_i}")

for _i in range(2, 100):
    SEEDLIST.append(f"http://jywxh4q4arybssyaxjmfqooknt6skj2qmjhblewrhteeppmusmsfbyqd.onion/?page={_i}")

for _i in range(2, 1000):
    SEEDLIST.append(f"http://checkitzh2q35xf42lrtxc6a4o2aqpvvu5dpdophhl44rnqla7ffpkid.onion/search?q=onion&page={_i}")

BANNED_DOMAINS = []
try:
    response = requests.get('https://ahmia.fi/banned/?987654321', timeout=120)
    for md5 in response.text.split("\n"):
        md5 = md5.strip().replace(" ", "")
        if len(md5) == 32:
            BANNED_DOMAINS.append(md5)
except requests.exceptions.Timeout:
    print("\nsettings.py: Timed out fetching BANNED_DOMAINS\n")

# Tor proxy settings: http://localhost:15000 - http://localhost:15099
HTTP_PROXY_TOR_PROXIES = [f"http://localhost:150{i:02}" for i in range(0, 100)]
