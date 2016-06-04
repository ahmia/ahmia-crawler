![https://ahmia.fi/](https://raw.githubusercontent.com/razorfinger/ahmia/ahmia-redesign/ahmia-logotype.png)

Ahmia is the search engine for `.onion` domains on the Tor anonymity
network. It is led by [Juha Nurmi](//github.com/juhanurmi) and is based
in Finland. This repository contains crawlers used by [Ahmia](https://github.com/ahmia) search engine

# Installation guide

## Install dependencies:

### Ubuntu 16.04
```sh
# apt-get install build-essential python-pip python-virtualenv
# apt-get install libxml2-dev libxslt1-dev python-dev libffi-dev libssl-dev
# apt-get install tor polipo default-jre
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

## Install Elasticsearch

Please install elastic search from the official repository thanks to the [official guide](https://www.elastic.co/guide/en/elasticsearch/reference/current/setup-repositories.html)

# Configuration

## Configure polipo

Please find the config sample [here](https://github.com/iriahi/ahmia-crawler/blob/master/conf/polipo/config).

## Configure elasticsearch

Default configuration is enough to run crawlers in dev mode. You can find a more secure configuration of [/etc/default/elasticsearch]() and [/etc/elasticsearch/elasticsearch.yml]()

# Start services
```sh
# systemctl start tor
# systemctl start polipo
# systemctl start elasticsearch
```


