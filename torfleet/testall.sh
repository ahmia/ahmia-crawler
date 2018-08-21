#!/bin/bash
base_http_port=15000

for i in {0..9}
do
	http_port=$((base_http_port+i))

	echo "Testing HTTP proxy localhost:$http_port"
	curl -x http://localhost:$http_port http://msydqstlz2kzerdg.onion/robots.txt
done
