#!/bin/bash

command=${1:-default}
sleeptime=${2:-5}

cd onionElasticBot/

while true; do
	echo ""
	echo "Running forever 'scrapy crawl $command'" 
        echo "Sleep $sleeptime seconds between re-call"
	echo ""
	scrapy crawl $command
	# Sleep and run again
	echo ""
	echo "Sleeping $sleeptime seconds..."
	echo ""
	sleep $sleeptime
done
