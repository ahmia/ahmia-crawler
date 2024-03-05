#!/bin/bash

cd ahmia

MAX_TIME=2160000 # 25 days
FINAL_MAX_TIME=2163600 # Finally, wait 60 mins more

echo ""
timeout --signal=SIGKILL $FINAL_MAX_TIME timeout --kill-after=120 --signal=SIGINT $MAX_TIME scrapy crawl ahmia-tor
echo ""
