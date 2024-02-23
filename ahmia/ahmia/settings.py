# -*- coding: utf-8 -*-
""" Settings """
import datetime
import requests
from decouple import config

BOT_NAME = 'ahmia'

SPIDER_MODULES = ['ahmia.spiders']
NEWSPIDER_MODULE = 'ahmia.spiders'

# Elasticsearch settings using environment variables for sensitive information
ELASTICSEARCH_SERVER = config('ES_URL', default="https://localhost:9200/")
ELASTICSEARCH_INDEX = datetime.datetime.now().strftime("tor-%Y-%m")
ELASTICSEARCH_USERNAME = config('ES_USERNAME', default='elastic')
ELASTICSEARCH_PASSWORD = config('ES_PASSWORD', default='password12345')
ELASTICSEARCH_CA_CERTS = config('ES_CA_CERTS', default='/etc/elasticsearch/certs/http_ca.crt')

# Identify as normal Tor Browser
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0"

DOWNLOAD_TIMEOUT = 80  # seconds
DOWNLOAD_DELAY = 1
CONCURRENT_REQUESTS = 100
LOG_LEVEL = 'INFO'
COOKIES_ENABLED = False
RETRY_ENABLED = False
DOWNLOAD_MAXSIZE = 1024000  # Max-limit in bytes, 1MB
REACTOR_THREADPOOL_MAXSIZE = 20
REDIRECT_MAX_TIMES = 3
AJAXCRAWL_ENABLED = True
DEPTH_LIMIT = 1  # Crawling depth
ROBOTSTXT_OBEY = False

ITEM_PIPELINES = {
    'ahmia.pipelines.CustomElasticSearchPipeline': 900,
}

DOWNLOADER_MIDDLEWARES = {
    'ahmia.middlewares.ProxyMiddleware': 100,
    'ahmia.middlewares.FilterBannedDomains': 200,
    'ahmia.middlewares.FilterResponses': 300,
    'ahmia.middlewares.SubDomainLimit': 400,
}

SEEDLIST = ['http://torlinkv7cft5zhegrokjrxj2st4hcimgidaxdmcmdpcrnwfxrr2zxqd.onion/',
         'http://zqktlwiuavvvqqt4ybvgvi7tyo4hjl5xgfuvpdf6otjiycgwqbym2qad.onion/wiki/index.php/Main_Page',
         'http://3bbad7fauom4d6sgppalyqddsqbf5u5p56b5k5uk2zxsy3d6ey2jobad.onion/discover',
         'http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/address/',
         'http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/add/onionsadded/']

BANNED_DOMAINS = []
try:
    response = requests.get('https://ahmia.fi/banned/?987654321', timeout=60)
    for md5 in response.text.split("\n"):
        md5 = md5.strip().replace(" ", "")
        if len(md5) == 32:
            BANNED_DOMAINS.append(md5)
except requests.exceptions.Timeout:
    print("\nsettings.py: Timed out fetching BANNED_DOMAINS\n")

# Tor proxy settings
HTTPS_PROXY_TOR_PROXIES = ["http://localhost:8118/"]  # Tor HTTPS Privoxy proxy
# Tor HTTP Python proxies localhost:15000 ... localhost:15029
HTTP_PROXY_TOR_PROXIES = ["http://localhost:150%02d" % i for i in range(0,30)]
