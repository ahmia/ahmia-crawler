#!/bin/bash

cd ahmia

#rm -rf jobdir_monthly # add "-s JOBDIR=jobdir_monthly" for scrapy

MAX_TIME=865200 # 10 days + 1200 seconds
FINAL_MAX_TIME=866400 # Finally, wait 1200 seconds more

echo ""
time timeout --signal=SIGKILL $FINAL_MAX_TIME timeout --kill-after=120 --signal=SIGINT $MAX_TIME scrapy crawl ahmia-tor
echo ""
