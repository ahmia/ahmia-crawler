#!/bin/bash
base_socks_port=19050
base_http_port=15000
privoxy_base_config="privoxy_configs/config"

# Create data and log directories if they don't exist
mkdir -p "data/tor"
mkdir -p "pids"
mkdir -p "log"

for i in {0..49}
do
	socks_port=$((base_socks_port+i))
	http_port=$((base_http_port+i))

	# Create a directory for each Tor instance if it doesn't exist
	mkdir -p "data/tor/tor$i"
	nohup tor --CookieAuthentication 0 --HashedControlPassword "" --ControlPort 0 --ControlSocket 0 --ClientOnly 1 --NewCircuitPeriod 15 --MaxCircuitDirtiness 15 --NumEntryGuards 8 --PidFile ./pids/tor$i.pid --SocksPort 127.0.0.1:$socks_port --Log "warn file ./log/warnings.log" --Log "err file ./log/errors.log" --DataDirectory data/tor/tor$i > ./log/tor_$i.log 2>&1 &
	sleep 1

	# Prepare Privoxy configuration for this instance
	privoxy_conf="privoxy_configs/config_$http_port"
	cp $privoxy_base_config $privoxy_conf
	echo "forward-socks5t / 127.0.0.1:$socks_port ." >> $privoxy_conf
	echo "listen-address 127.0.0.1:$http_port" >> $privoxy_conf
	echo "Running Privoxy with config $privoxy_conf..."
	privoxy $privoxy_conf > $PWD/log/privoxy_$i.log 2>&1 &
	sleep 1

done

sleep 3

echo "HTTP proxy processes (Privoxy):"
ps aux | grep "privoxy privoxy_configs" | grep -v grep | wc -l
echo "Tor processes:"
ps aux | grep tor | grep DataDirec | grep -v grep | wc -l
