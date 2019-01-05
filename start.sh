#!/bin/bash
# $app1 = "runDeposit.py"
# $app2 = "runGateway.py"
# $app3 = "runTrade.py"
test=`ps aux | grep "runPreTrade" | grep -v grep -c`
if [ $test == 0 ]; then
        #pip install -r requirements.txt
        python runPreTrade.py --env=pre_trade >> logs-pre-trade.log  &
        echo "[INFO] Service is starting"
        exit
else
        echo "[WARN] Service is already running"
        exit
fi

test=`ps aux | grep "runPreTradeRealTime" | grep -v grep -c`
if [ $test == 0 ]; then
        #pip install -r requirements.txt
        python3 runPreTradeRealTime.py --env=pre_trade_realtime &
        python3 runPreTradeRealTime.py --env=consumer &
        echo "[INFO] Service RealTimeTrading is starting"
        exit
else
        echo "[WARN] Service is already running"
        exit
fi