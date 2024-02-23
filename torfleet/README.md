# Torfleet and Python load balance proxies

Several Tor clients and Python proxies.
Crawler already has a load balancing that keeps the same client for the same domain.

# Shortcut testing

```sh
python torproxy.py 19050 9050
curl --proxy http://localhost:19050 http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/robots.txt
```

Install Privoxy for HTTPS connections

```sh
# Add
# forward-socks5t   /               127.0.0.1:9050 .
sudo systemctl start privoxy
curl -v --proxy 127.0.0.1:8118 https://ahmia.fi/robots.txt
curl --proxy 127.0.0.1:8118 http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/robots.txt
```

Run

```sh
bash runfleet.sh
```

Wait at least a minute and you can test the HTTP proxies

```sh
curl -x http://localhost:15000 http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/robots.txt
bash testall.sh
```

```sh
kill $(ps aux | grep 'NewCircuitPeriod' | awk '{print $2}')
kill $(ps aux | grep 'torproxy' | awk '{print $2}')
rm *.log
```
