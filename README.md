[![Build Status](https://travis-ci.org/ahmia/ahmia-crawler.svg?branch=master)](https://travis-ci.org/ahmia/ahmia-crawler)
[![Code Health](https://landscape.io/github/ahmia/ahmia-crawler/master/landscape.svg?style=flat)](https://landscape.io/github/ahmia/ahmia-crawler/master)
[![Requirements Status](https://requires.io/github/ahmia/ahmia-crawler/requirements.svg?branch=master)](https://requires.io/github/ahmia/ahmia-crawler/requirements/?branch=master)

![https://ahmia.fi/](https://raw.githubusercontent.com/razorfinger/ahmia/ahmia-redesign/ahmia-logotype.png)

Ahmia is the search engine for `.onion` domains on the Tor anonymity
network. It is led by [Juha Nurmi](//github.com/juhanurmi) and is based
in Finland. This repository contains crawlers used by [Ahmia](https://github.com/ahmia) search engine

# Prerequisites
[Ahmia-index](https://github.com/ahmia/ahmia-index) should be installed and running

# Installation guide

## Install dependencies:

### Ubuntu 16.04
```sh
apt-get install build-essential python-pip python-virtualenv
apt-get install libxml2-dev libxslt1-dev python-dev libffi-dev libssl-dev
apt-get install tor polipo
```

### Fedora 23
```sh
dnf install @development-tools redhat-rpm-config python-pip python-virtualenv
dnf install libxml-devel libxslt-devel python-devel libffi-devel openssl-devel
dnf install tor polipo
```

## Install requirements in a virtual environment

```sh
python3 -m virtualenv venv3
source venv3/bin/activate
python3 -m pip install -r requirements/prod.txt
```

## Prefer own python HTTP proxy

Look fleet installation
[here](https://github.com/ahmia/ahmia-crawler/tree/master/torfleet).

# Usage

In order to execute the crawler to run permanently:
```
source venv/bin/activate
./run.sh &> crawler.log
```

# Specific run examples

```sh
Primary
scrapy crawl ahmia-tor -s DEPTH_LIMIT=3 -s ROBOTSTXT_OBEY=0 -s FULL_PAGERANK_COMPUTE=True
or
scrapy crawl ahmia-tor -s DEPTH_LIMIT=5 -s LOG_LEVEL=INFO
or
scrapy crawl ahmia-i2p -s DEPTH_LIMIT=100 -s LOG_LEVEL=DEBUG
or
scrapy crawl ahmia-i2p -s DEPTH_LIMIT=1 -s ROBOTSTXT_OBEY=0
or
scrapy crawl ahmia-tor -o items.json -t json
or
scrapy crawl ahmia-tor -s DEPTH_LIMIT=1 -s ALLOWED_DOMAINS=/home/juha/allowed_domains.txt -s TARGET_SITES=/home/juha/seed_list.txt -s ELASTICSEARCH_TYPE=targetitemtype
```
