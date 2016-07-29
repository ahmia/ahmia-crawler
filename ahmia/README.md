# onionElasticBot
Crawl .onion and .i2p websites from the Tor network

## Prerequisistes
Please follow [installation guide](https://github.com/iriahi/ahmia-crawler)

## Usage
```sh
$ scrapy crawl OnionSpider -s DEPTH_LIMIT=2 -s ROBOTSTXT_OBEY=0
or
$ scrapy crawl OnionSpider -s DEPTH_LIMIT=5 -s LOG_LEVEL=INFO
or
$ scrapy crawl i2pSpider -s DEPTH_LIMIT=100 -s LOG_LEVEL=DEBUG -s ELASTICSEARCH_TYPE=i2p
or
$ scrapy crawl i2pSpider -s DEPTH_LIMIT=1 -s ROBOTSTXT_OBEY=0 -s ELASTICSEARCH_TYPE=i2p
or
$ scrapy crawl OnionSpider -o items.json -t json
or
$ scrapy crawl OnionSpider -s DEPTH_LIMIT=1 -s ALLOWED_DOMAINS=/home/juha/allowed_domains.txt -s TARGET_SITES=/home/juha/seed_list.txt -s ELASTICSEARCH_TYPE=targetitemtype
```
