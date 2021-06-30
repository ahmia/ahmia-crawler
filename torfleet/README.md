# Torfleet and Python load balance proxies

Several Tor clients and Python2.7 proxies.
Crawler already has a load balancing that keeps the same client for the same domain.

# Shortcut testing

```sh
$ python2.7 torproxy.py 15000 9050
$ curl -x http://localhost:15000 http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/
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
$ sudo nano /etc/security/limits.conf
$ ulimit -n 16384
$ sudo service polipo restart
$ ps aux | grep polipo
$ cat /proc/<POLIPO PID>/limits
```


Run

```sh
bash runfleet.sh
```

Wait at least a minute and you can test the HTTP proxies

```sh
curl -x http://localhost:15000 http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/
bash testall.sh
```

```sh
kill $(ps aux | grep 'NewCircuitPeriod' | awk '{print $2}')
kill $(ps aux | grep 'torproxy' | awk '{print $2}')
rm *.log
```
