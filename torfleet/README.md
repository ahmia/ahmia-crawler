# Torfleet and Python load balancer proxy

Several Tor clients and a load balancer Python3 proxy that keeps the same client for the same domain.

# Installation and utilization

Python2

```sh
virtualenv venv
source venv/bin/activate
pip install socksipy-branch
pip install PySocks
```

Python3

```sh
virtualenv -p python3 venv
source venv/bin/activate
pip install socksipy-branch
```

Run

```sh
bash runfleet.sh
```

Wait at least a minute and you can test the HTTP proxies

```sh
curl -x http://localhost:15000 http://msydqstlz2kzerdg.onion/
bash testall.sh
```

```sh
kill $(ps aux | grep 'NewCircuitPeriod' | awk '{print $2}')
kill $(ps aux | grep 'http_tor_proxy' | awk '{print $2}')
rm *.log
```
