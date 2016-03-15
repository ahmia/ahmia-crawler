onionElasticBot - Crawl .onion and .i2p websites from the Tor network
=====================================================================

This is a Scrapy project to crawl .onion websites from the Tor network. Saves h1, h2, title, domain, url, plain HTML and words to Elasticsearch or plain JSON.

Short guide to the crawler installation
---------------------------------------

-	Install Elasticsearch and Oracle Java
-	Install Python 2.7
-	Install Tor software (use zero-circuit patch)
-	Install Polipo HTTP proxy software
-	Install i2p software

```sh
$ sudo apt-get install git
$ sudo apt-get install python-virtualenv
$ sudo apt-get install python-pip
$ sudo apt-get install libffi-dev
$ sudo apt-get install python-dev libxml2-dev libxslt-dev
$ sudo apt-get install libssl-dev
$ sudo apt-get install python-twisted
$ sudo apt-get install python-simplejson
$ sudo apt-get install gcc
```

```sh
$ cd onionElasticBot
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

Setup Polipo:

```sh
$ sudo apt-get install polipo
$ sudo cp polipo_conf /etc/polipo/config
$ sudo service polipo restart
```

Creating Index Settings:

```sh
$ curl -XPUT -i "localhost:9200/crawl/" -d "@./mappings.json"
```


Run the crawler software
------------------------

```sh
$ scrapy crawl OnionSpider -s DEPTH_LIMIT=100
or
$ scrapy crawl i2pSpider -s DEPTH_LIMIT=100 -s LOG_LEVEL=DEBUG -s ELASTICSEARCH_TYPE=i2p
or
$ scrapy crawl i2pSpider -s DEPTH_LIMIT=1 -s ROBOTSTXT_OBEY=0 -s ELASTICSEARCH_TYPE=i2p
or
$ scrapy crawl OnionSpider -o items.json -t json
or
$ scrapy crawl OnionSpider -s DEPTH_LIMIT=1 -s ALLOWED_DOMAINS=/home/juha/allowed_domains.txt -s TARGET_SITES=/home/juha/seed_list.txt -s ELASTICSEARCH_TYPE=targetitemtype
```

Run crawler forever:

```sh
$ bash runforever.sh OnionSpider 3600
```
