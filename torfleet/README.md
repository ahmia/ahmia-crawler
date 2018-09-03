# Torfleet and Python load balancer proxy

Several Tor clients and Python2 proxy.
Crawler already has a load balancing that keeps the same client for the same domain.

# Installation and utilization

Python2

```sh
virtualenv venv
source venv/bin/activate
pip install SocksiPy-branch==1.1
pip install PySocks==1.6.8
```

Shortcut testing

```sh
$ python torproxy.py 15000 9050
$ curl -x http://localhost:15000 http://msydqstlz2kzerdg.onion/
```

Install Polipo for HTTPS connections

```sh
$ sudo apt-get install polipo
$ sudo cp config /etc/polipo/config
# Set limits
# Show limits
$ ulimit -a -H
# Add line
# * - nofile 16384
$ nano /etc/security/limits.conf
$ ulimit -n 16384
$ service polipo restart
$ ps aux | grep polipo
$ cat /proc/<POLIPO PID>/limits
$ sudo service polipo restart
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
kill $(ps aux | grep 'torproxy' | awk '{print $2}')
rm *.log
```
