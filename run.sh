#!/bin/bash

cd ahmia

sleeptime=60 # One minute
MAX_TIME=604800 # A week
FINAL_MAX_TIME=605400 # Finally, wait 10mins more

while true; do
    echo "Running crawlers..."
    echo ""
    # depth = 1
    timeout --signal=SIGKILL $FINAL_MAX_TIME timeout --kill-after=120 --signal=SIGINT $MAX_TIME scrapy crawl ahmia-tor -s DEPTH_LIMIT=1
    sleep $sleeptime
    # depth = 2
    timeout --signal=SIGKILL $FINAL_MAX_TIME timeout --kill-after=120 --signal=SIGINT $MAX_TIME scrapy crawl ahmia-tor -s DEPTH_LIMIT=2
    sleep $sleeptime
    # depth = 3
    timeout --signal=SIGKILL $FINAL_MAX_TIME timeout --kill-after=120 --signal=SIGINT $MAX_TIME scrapy crawl ahmia-tor -s DEPTH_LIMIT=3
    # Sleep and run again
    echo ""
    echo "Sleeping $sleeptime seconds..."
    echo ""
    sleep $sleeptime
done
