#!/bin/bash
base_socks_port=19050
base_http_port=15000
base_control_port=38118

# Create data directory if it doesn't exist
if [ ! -d "data" ]; then
	mkdir "data"
fi
if [ ! -d "data/tor" ]; then
	mkdir "data/tor"
fi

for i in {0..9}
do
	socks_port=$((base_socks_port+i))
	control_port=$((base_control_port+i))
	http_port=$((base_http_port+i))

	if [ ! -d "data/tor/tor$i" ]; then
		echo "Creating directory data/tor/tor$i"
		mkdir "data/tor/tor$i"
	fi

	echo "Running: tor --CookieAuthentication 0 --HashedControlPassword '' --ClientOnly 1 --NewCircuitPeriod 15 --MaxCircuitDirtiness 15 --NumEntryGuards 8 --SocksBindAddress 127.0.0.1 --ControlPort $control_port --PidFile tor$i.pid --SocksPort $socks_port --DataDirectory data/tor$i > tor_$i.log 2>&1 &"
	nohup tor --CookieAuthentication 0 --HashedControlPassword "" --ClientOnly 1 --NewCircuitPeriod 15 --MaxCircuitDirtiness 15 --NumEntryGuards 8 --SocksBindAddress 127.0.0.1 --ControlPort $control_port --PidFile tor$i.pid --SocksPort $socks_port --DataDirectory data/tor$i > tor_$i.log 2>&1 &

	echo "Running: nohup python3 http_tor_proxy.py http_port socks_port > http_proxy_$i.log 2>&1 &"
	nohup python3 http_tor_proxy.py $http_port $socks_port > http_proxy_$i.log 2>&1 &
done

echo "HTTP proxy processes:"
ps aux | grep http_tor_proxy | grep python3 | wc -l
echo "Tor processes:"
ps aux | grep tor | grep DataDirec | wc -l
