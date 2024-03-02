# onionElasticBot
Crawl .onion websites from the Tor network

## Usage
```sh
scrapy crawl ahmia-tor -s DEPTH_LIMIT=1 -s LOG_LEVEL=DEBUG
or
scrapy crawl ahmia-tor -s DEPTH_LIMIT=1 -O items.json:json
or
scrapy crawl ahmia-tor -s DEPTH_LIMIT=3
```
