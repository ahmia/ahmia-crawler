#!/bin/bash

cd ahmia

rm -rf jobdir

# One day
MAX_TIME=85200
FINAL_MAX_TIME=86400

echo ""
time timeout --signal=SIGKILL $FINAL_MAX_TIME timeout --kill-after=120 --signal=SIGINT $MAX_TIME scrapy crawl ahmia-tor -s DEPTH_LIMIT=3 -a seedlist='http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/add/onionsadded/'
echo ""
