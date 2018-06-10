# onionElasticBot
Crawl .onion and .i2p websites from the Tor network

## Prerequisistes
Please follow [installation guide](https://github.com/iriahi/ahmia-crawler)

## Usage
```sh
$ scrapy crawl ahmia-tor -s DEPTH_LIMIT=2 -s ROBOTSTXT_OBEY=0
or
$ scrapy crawl ahmia-tor -s DEPTH_LIMIT=5 -s LOG_LEVEL=INFO
or
$ scrapy crawl ahmia-i2p -s DEPTH_LIMIT=100 -s LOG_LEVEL=DEBUG
or
$ scrapy crawl ahmia-i2p -s DEPTH_LIMIT=1 -s ROBOTSTXT_OBEY=0
or
$ scrapy crawl ahmia-tor -o items.json -t json
or
$ scrapy crawl ahmia-tor -s DEPTH_LIMIT=1 -s ALLOWED_DOMAINS=/home/juha/allowed_domains.txt -s TARGET_SITES=/home/juha/seed_list.txt -s ELASTICSEARCH_TYPE=targetitemtype
```

### Run forever

$ ../run.sh