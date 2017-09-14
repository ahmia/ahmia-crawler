#!/bin/bash

source venv/bin/activate
cd ahmia

# One day in seconds
sleeptime=86400

while true; do
    echo ""
    echo "Running forever 'scrapy crawl ahmia-tor'" 
    echo "Sleep $sleeptime seconds between re-call"
    echo ""
    # Max execution time is two days
    timeout 172800 scrapy crawl ahmia-tor -s DEPTH_LIMIT=3 -s ROBOTSTXT_OBEY=0 -s FULL_PAGERANK_COMPUTE=True
    # Sleep and run again
    echo ""
    echo "Sleeping $sleeptime seconds..."
    echo ""
    sleep $sleeptime
done
