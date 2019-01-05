#!/bin/bash
test=`ps aux | grep "tradecore" | grep -v grep -c`
if [ $test == 0 ]; then
        echo "[INFO] Service is already stop"
        exit
else
        ps aux | grep "tradecore" | grep -v grep | awk '{print $2}' |  /usr/bin/xargs /bin/kill -9
        echo "[WARN] Service is stoping"
        exit
fi