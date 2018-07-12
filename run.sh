#!/bin/bash

cd ahmia

# One day in seconds
sleeptime=86400 # A day
MAX_TIME=604800 # A week
FINAL_MAX_TIME=605400 # Finally, wait 10mins more

while true; do
    echo ""
    echo "Running forever 'scrapy crawl ahmia-tor' (timeout $MAX_TIME seconds)"
    echo "Sleep $sleeptime seconds between re-call"
    echo ""
    # Max execution time is two days
    timeout --signal=SIGKILL $FINAL_MAX_TIME timeout --kill-after=120 --signal=SIGINT $MAX_TIME scrapy crawl ahmia-tor -s DEPTH_LIMIT=3 -s ROBOTSTXT_OBEY=0 -s FULL_PAGERANK_COMPUTE=True
    # Sleep and run again
    echo ""
    echo "Sleeping $sleeptime seconds..."
    echo ""
    sleep $sleeptime
done

# todo add command to run ahmia-i2p spider in parallel
# todo add SIGKILL handler/trap for the child (scrapy) processes?