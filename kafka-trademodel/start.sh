test=`ps aux | grep "tradecore" | grep -v grep -c`
echo 
if [ $test == 0 ]; then
        # python3 runDeposit.py --env=deposit >> logs-deposit.log  
        ./tradecore.linux >> tradecore.log &
        echo "[INFO] Service is starting"
        exit
else
        echo "[WARN] Service is already running"
        exit
fi