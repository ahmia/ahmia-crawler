[![Code Health](https://landscape.io/github/iriahi/ahmia-crawler/master/landscape.svg?style=flat)](https://landscape.io/github/iriahi/ahmia-crawler/master)
[![Requirements Status](https://requires.io/github/iriahi/ahmia-crawler/requirements.svg?branch=master)](https://requires.io/github/iriahi/ahmia-crawler/requirements/?branch=master)

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
# apt-get install build-essential python-pip python-virtualenv
# apt-get install libxml2-dev libxslt1-dev python-dev libffi-dev libssl-dev
# apt-get install tor polipo
```

### Fedora 23
```sh
# dnf install @development-tools redhat-rpm-config python-pip python-virtualenv
# dnf install libxml-devel libxslt-devel python-devel libffi-devel openssl-devel
# dnf install tor polipo
```

## Install requirements in a virtual environment

```sh
$ virtualenv /path/to/venv
$ source /path/to/venv/bin/activate
(venv)$ pip install -r requirements.txt
```

## Proxy configuration
Please use polipo config sample [here](https://github.com/ahmia/ahmia-crawler/blob/master/conf/polipo/config).

## Start tor and polipo
```sh
# systemctl start tor
# systemctl start polipo
```

# Usage
Each crawler has its own guide.
- [onionElasticBot](https://github.com/ahmia/ahmia-crawler/tree/master/onionElasticBot)

# How to use multiple Tor clients ?
You can setup [TorBalancer](https://github.com/ahmia/TorBalancer) to do this.
Don't forget to update the bot settings.py
