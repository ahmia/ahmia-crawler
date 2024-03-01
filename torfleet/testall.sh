#!/bin/bash
base_http_port=15000

for i in {0..49}
do
	http_port=$((base_http_port+i))

	echo "Testing HTTP proxy localhost:$http_port"
	curl --proxy http://localhost:$http_port "http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/robots.txt"
done
