import requests, traceback
from .core.trade_model import Order
from .logger import create_logger
from flask_socketio import emit
from configparser import ConfigParser
import json
config = ConfigParser()
config.read('config.env')
from ..initdb import db_session
from ..pre_trade.models import ExecutionReport,TransactionTrading,User
from ..ulib import add_Decimal,sub_Decimal,div_Decimal,mul_Decimal,toDecimal
logger = create_logger()
# logging rotation-log, co tren python-snippet 
# folder logging: log-preTrade (de ngoai thu muc du an, json)
# push data to trade-data: insert report to database
# push status request to deposi_app(transaction_report)
# push data via socketio -> nodejs api -> client
import redis

# Redis configuration
myredis = redis.StrictRedis(host='localhost', port=6379, db=4)



def send_execution_report(order_obj_or_dict):
    flag = False
    
    try:
        report = order_obj_or_dict.execution_report()
        order = order_obj_or_dict.to_dict()
    except:
        order = order_obj_or_dict
        report = order
        flag= True

    if(bool(myredis.get(json.dumps(report))) == True):
        return None, None
    else: myredis.set(json.dumps(report), True)
    
    try:
        if(report['MsgType'] == "8"):
            # push database
            try:
                with db_session() as session:
                    try:
                        user = session.query(User).filter(User.id == report["UserID"]).first()
                        report["DisplayName"] = user.username
                    except:
                        traceback.print_exc()
                        pass
                requests.post(config["ENV"]['HOST_TRADE_DATA'] + '/add-execution-report', json = report)
                print("push Excution Report")
            except:
                traceback.print_exc()
                logger.error(traceback.print_exc())
            # push socket 
                        


        elif(report['MsgType'] == "AE"):
            # add transactionTrading To Db
            with  db_session() as session:
                transaction_trading = session.query(TransactionTrading).filter(TransactionTrading.OrderID == report["OrderID"],
                                                                        TransactionTrading.live == True).first()
                if(transaction_trading is None):
                    requests.post(config["ENV"]['HOST_TRADE_DATA'] + '/add-transaction-trading', json = report)
                    print("push TRADING-TRANSACTION-AE")
                    
                    # push HOST_DEPOSIT_APP
                    requests.post(config["ENV"]['HOST_DEPOSIT_APP']+'/transaction_reports', json = {"Account_no":report['Account'],"AllocAccount_no":report['AllocAccount'],"AllocQty":report['AllocQty'],"Quantity":report['Quantity']})
                    print("push DEPOSIT_APP")
        # logger.info(report)
        return report, order
    except:
        traceback.print_exc()
        return None , None
        # logger.error(traceback.print_exc())
        # pass
