#!/bin/bash

test=`ps aux | grep "runPreTrade" | grep -v grep -c`
if [ $test == 0 ]; then
        #pip install -r requirements.txt
        python runTrunPreTraderade.py --env=pre_trade   &
        echo "[INFO] Service is starting"
        exit
else
        echo "[WARN] Service is already running"
        exit
fi