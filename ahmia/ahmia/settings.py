# -*- coding: utf-8 -*-
""" Settings """
import re
import hashlib
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

ELASTICSEARCH_BUFFER_LENGTH = 500

# Identify as normal Tor Browser
#USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0"
HEADERS = {'User-Agent': USER_AGENT}

# Main settings for crawling speed and performance
DOWNLOAD_TIMEOUT = 60 # seconds
DOWNLOAD_DELAY = 1
AUTOTHROTTLE_ENABLED = False
#AUTOTHROTTLE_ENABLED = True
#AUTOTHROTTLE_START_DELAY = 2
#AUTOTHROTTLE_MAX_DELAY = 60
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0  # Adjust based on performance

# Crawl in breadth-first order (BFO)
DEPTH_PRIORITY = 1
DOMAIN_MAX_REQUESTS = 100 # Spider does not over-focus on large websites, set 0 for unlimited

SCHEDULER_DISK_QUEUE = "scrapy.squeues.PickleFifoDiskQueue"
SCHEDULER_MEMORY_QUEUE = "scrapy.squeues.FifoMemoryQueue"

#JOBDIR = "jobdir" # disk-backed to avoid memory growth

# Broad Crawls
# https://docs.scrapy.org/en/latest/topics/broad-crawls.html
SCHEDULER_PRIORITY_QUEUE = "scrapy.pqueues.ScrapyPriorityQueue"
#SCHEDULER_PRIORITY_QUEUE = "scrapy.pqueues.DownloaderAwarePriorityQueue"
CONCURRENT_REQUESTS = 100
CONCURRENT_REQUESTS_PER_DOMAIN = 10
REACTOR_THREADPOOL_MAXSIZE = CONCURRENT_REQUESTS
DOWNLOAD_MAXSIZE = 5242880 # Max-limit in bytes, 5 MB, 5*1024*1024 = 5,242,880 bytes
COOKIES_ENABLED = False
RETRY_ENABLED = False

REDIRECT_ENABLED = True
REDIRECT_MAX_TIMES = 3
AJAXCRAWL_ENABLED = False
DEPTH_LIMIT = 5 # Crawling depth, default is 5
DEPTH_STATS_VERBOSE = True # Output per-depth request counts
ROBOTSTXT_OBEY = False

EXTENSIONS = {
    'scrapy.extensions.memusage.MemoryUsage': 500,
    'scrapy.extensions.closespider.CloseSpider': 600,
}

MEMUSAGE_CHECK_INTERVAL_SECONDS = 5.0
MEMUSAGE_LIMIT_MB = 35000
MEMUSAGE_WARNING_MB = 30000

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

# Tor proxy settings: http://localhost:15000 - http://localhost:15099
HTTP_PROXY_TOR_PROXIES = [f"http://localhost:150{i:02}" for i in range(0, 100)]

def extract_onions_from_url(url, timeout=120):
    """ Helper function to extract unique onion base URLs """
    onions = set()
    try:
        resp = requests.get(url, timeout=timeout, headers=HEADERS)
        resp.raise_for_status()
        # Match full http://xyz.onion/ links
        matches = re.findall(r'http://[a-z2-7]{56}\.onion/?', resp.text)
        for match in matches:
            # Normalize: ensure trailing slash
            normalized = match.rstrip("/") + "/"
            onions.add(normalized)
    except requests.exceptions.Timeout:
        print(f"\nsettings.py: Timed out fetching {url}\n")
    except requests.exceptions.RequestException as e:
        print(f"\nsettings.py: Error fetching {url} -> {e}\n")
    return onions

SEEDLIST_SET = set([
    'http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/',
])

# Fetch additional seeds
SEEDLIST_SET.update(extract_onions_from_url(
    'https://ahmia.fi/add/onionsadded/?1234'
))

SEEDLIST_SET.update(extract_onions_from_url(
    'https://ahmia.fi/address/?1234'
))

BANNED_DOMAINS = []
try:
    response = requests.get('https://ahmia.fi/banned/?987654321', timeout=120, headers=HEADERS)
    for md5 in response.text.split("\n"):
        md5 = md5.strip().replace(" ", "")
        if len(md5) == 32:
            BANNED_DOMAINS.append(md5)
except requests.exceptions.Timeout:
    print("\nsettings.py: Timed out fetching BANNED_DOMAINS\n")

SEEDLIST = []

for domain_url in SEEDLIST_SET:
    if "://" in domain_url and ".onion" in domain_url:
        onion_domain = domain_url.split("/")[2]
        if onion_domain.endswith(".onion"):
            main_domain = onion_domain.split(".")[0] + ".onion"
            if hashlib.md5(main_domain.encode('utf-8')).hexdigest() in BANNED_DOMAINS:
                continue
        SEEDLIST.append(domain_url)

print(f"\n settings.py loaded: SEEDLIST with {len(SEEDLIST)} onion addresses\n")
