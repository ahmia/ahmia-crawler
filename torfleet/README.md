# Torfleet and Python3 load balancer proxy

Several Tor clients and a load balancer Python3 proxy that keeps the same client for the same domain.

# Installation and utilization

```sh
pip3 install socksipy-branch
bash runfleet.sh
```

Wait at least a minute and you can test the HTTP proxies

```sh
curl -x http://localhost:15000 http://msydqstlz2kzerdg.onion/
bash testall.sh
```

```sh
killall tor
kill $(ps aux | grep 'http_tor_proxy' | awk '{print $2}')
rm *.log
```
