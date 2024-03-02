# Torfleet: Tor and Privoxy load balance HTTP proxies

Several Tor clients and HTTP proxies.
Crawler already has a load balancing that keeps the same client for the same domain.

Install Privoxy.

I.e, on Ubuntu, adjust the AppArmor profile for Privoxy to allow it access to the configuration files:

```sh
sudo nano /etc/apparmor.d/usr.sbin.privoxy

# Add the Necessary Permissions: allow Privoxy to read torfleet configuration files:
/yourpath/ahmia-crawler/torfleet/** r,

sudo apparmor_parser -r /etc/apparmor.d/usr.sbin.privoxy
```

Run

```sh
bash runfleet.sh
```

Wait at least a minute and you can test the HTTP proxies.

```sh
curl -x http://localhost:15000 http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/robots.txt

and

bash testall.sh
```

```sh
kill $(ps aux | grep 'NewCircuitPeriod' | grep -v grep | awk '{print $2}')
kill $(ps aux | grep 'privoxy privoxy_configs' | grep -v grep | awk '{print $2}')
```
