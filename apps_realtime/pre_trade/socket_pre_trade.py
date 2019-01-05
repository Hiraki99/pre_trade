import traceback
from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit
from .process import getInfoBalanceAccount,gen_orderID,check_balance_account,\
                    cancel_order,CollectData,mem,getCancelOrder,UpdateMemAfterCancel,\
                    updateItem,checkBalanceAccountDB,convertNewStyleExecutionReport
from .response import send_execution_report
from .core.trade_model import OrderBookOTC, Order,genOrderID
from ..ulib import add_Decimal,sub_Decimal,div_Decimal,mul_Decimal,toDecimal
from ..pre_trade.models import ExecutionReport,TransactionTrading,User

from celery import Celery
from ..initdb import db_session
from .my_redis import MyRedis
import json
from .kafka.producer import Producer
from threading import Lock
import requests
# from .process import data
from configparser import ConfigParser
config = ConfigParser()
config.read('config.env')
TOPIC_IN = config["ENV"]["TOPIC_IN"]
TOPIC_OUT = config["ENV"]["TOPIC_OUT"]
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['CELERY_BROKER_URL'] = config["ENV"]['CELERY_BROKER_URL']
app.config['result_backend'] = config["ENV"]['result_backend']
app.config['SQLALCHEMY_DATABASE_URI'] = config["ENV"]['database']

celery = Celery(app.name, backend=app.config['result_backend'], broker = app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
async_mode = None

socketio = SocketIO(app)

# data = CollectData()
# create order book
book_OTC = {}
book_OTC['BTC/USDT'] = OrderBookOTC('BTC/USDT', 0.000001, report=send_execution_report)
book_OTC['ETH/USDT'] = OrderBookOTC('ETH/USDT', 0.000001, report=send_execution_report)
book_OTC['ETH/BTC'] = OrderBookOTC('ETH/BTC', 0.000001, report=send_execution_report)
book_OTC['BTC/ETH'] = OrderBookOTC('BTC/ETH', 0.000001, report=send_execution_report)
book_OTC['BTC/VND'] = OrderBookOTC('BTC/VND', 0.000001, report=send_execution_report)
book_OTC['ETH/VND'] = OrderBookOTC('ETH/VND', 0.000001, report=send_execution_report)
book_OTC['USDT/VND'] = OrderBookOTC('USDT/VND', 0.000001, report=send_execution_report)

redis_book_OTC = {}
redis_book_OTC['BTC/USDT'] = MyRedis("BTC/USDT",{"bid":[],"ask":[]})
redis_book_OTC['ETH/USDT'] = MyRedis("ETH/USDT",{"bid":[],"ask":[]})
redis_book_OTC['ETH/BTC'] = MyRedis("ETH/BTC",{"bid":[],"ask":[]})
redis_book_OTC['BTC/ETH'] = MyRedis("BTC/ETH",{"bid":[],"ask":[]})
redis_book_OTC['BTC/VND'] = MyRedis("BTC/VND",{"bid":[],"ask":[]})
redis_book_OTC['ETH/VND'] = MyRedis("ETH/VND",{"bid":[],"ask":[]})
redis_book_OTC['USDT/VND'] = MyRedis("USDT/VND",{"bid":[],"ask":[]})

def updateBidAskFromDB(book_OTC):
    try:
        with db_session() as session:
            all_order = session.query(ExecutionReport).filter(ExecutionReport.live == True, ExecutionReport.OrdStatus == 'New',ExecutionReport.execution_style == 'ECN').all()
            print(len(all_order))
            for order in all_order:
                order_json = convertNewStyleExecutionReport(order)
                print(order_json)
                try:
                    book_OTC[order_json["Symbol"]].load_order_from_json(json.dumps(order_json))
                except:
                    traceback.print_exc()
                    pass
                   
                
    except:
        traceback.print_exc()
@socketio.on('order-new', namespace='/pre_trade/order')
def socket_new_order(data):
    try:
        print("order: ",data)
        checked = checkBalanceAccountDB(data)
        print(checked)
        if checked['status'] == 1:
            order = {
                'MsgType': 'D',
                "UserID" : data['userID'],
                'Account': checked['data']['Account'],
                'ClOrdID': gen_orderID(),
                'OrderQty': toDecimal(data['OrderQty']),
                'OrdType': 'LO',
                'Price': toDecimal(data['Price']),
                'Side': data['Side'],  
                'Symbol': data['Symbol'],
                'AllocAccount': checked['data']['AllocAccount'],
                'TimeInForce': 'GTC',
                'SecondaryOrderID': '',
            }
            try:
                order['SecondaryOrderID'] = data['SecondaryOrderID']
            except:
                pass
            # print('received data data-order: ' + str(order))

            # check symbol of order
        
            # accept new order
            order_object = Order(**order)
            if(order_object.MsgType == 'D'):
                order_object.OrdStatus = 'New'
            order_object.ExecStyle = 'ECN'
            report = order_object.execution_report()
            print(order_object.to_dict())
            if(report["OrdStatus"] == "New"):
                mem["data"] = updateItem(mem["data"], report)
            with db_session() as session:
                try:
                    user = session.query(User).filter(User.id == report["UserID"]).first()
                    report["DisplayName"] = user.username
                except:
                    traceback.print_exc()
                    pass
            # consumer.start(kwargs=dict(topic=TOPIC_IN))
            producer = Producer(kwargs={"topic":TOPIC_IN , "message" : bytes(json.dumps(order_object.to_dict()).encode("utf-8"))})
            producer.start()
            producer.join()
            
            if(report['OrdStatus'] == "New"):
                return {
                    "status":1,
                    "message": "Order is successful",
                    "report":report
                }
            elif(report['OrdStatus'] == "Filled"):
                report["AllocQty"] = sub_Decimal(mul_Decimal(report["OrderQty"],report["Price"]) , report["Commission"])

                emit('response-list-order-matching-realtime', {'status':2, 'message':"Order execution completed","order":report}, broadcast=True)
                return {
                    "status": 2,
                    "message": "Order execution complete",
                    "report":report
                }           
        else:
            return {
                    "status": 0,
                    "message": checked['message'],
                    "report":""
                }
    except:
        traceback.print_exc()
        return {
                "status": 0,
                "message": 'Fault Server',
                "report":""
            }

@socketio.on('order-cancel', namespace='/pre_trade/order')
def socket_cancel_order(json):
    try:
        print('received json data-cancel-order: ' + str(json))
        if book_OTC[json['Symbol']] is not None:
            # print('mem["data"] = ',mem["data"])
            old_report,cancel_order_json = getCancelOrder(json)
            print("cancel_order_json_before = ",cancel_order_json)
            cancel_order = Order(**cancel_order_json)
            cancel_order.ExecStyle = 'ECN'
            
            producer = Producer(kwargs={"topic":TOPIC_IN , "message" : bytes(json.dumps(cancel_order.to_dict()).encode("utf-8"))})
            producer.start()
            producer.join()   
            return {
                "status":1,
                "message":"Cancel order is completed",
                "report": cancel_order.execution_report(),
                "cancel_report": old_report
            }
            
    except:
        traceback.print_exc()
        return {
            "status":0,
            "message":"Cancel order is failed",
        }


@socketio.on('order-view', namespace='/pre_trade/order')
def socket_view_order(data):
    print("bid ask",data)
    try:
        if(data['Symbol'] is not None):
            # find all bid and ask order
            link = config["ENV"]["TRADE_CORE"] + "/books?pair="+ data['Symbol']
            print(link)
            result = requests.get(link)

            data = result.json()

            bid = data["Bid"]
            
            ask = data["Ask"]
            
            with db_session() as session:
                if(ask != None):
                    for item in ask:
                        user = session.query(User).filter(User.id == int(item["UserID"])).first()
                        item["DisplayName"] = user.username
                else: ask = []
                if(bid != None):
                    for item in bid:
                        user = session.query(User).filter(User.id == int(item["UserID"])).first()
                        item["DisplayName"] = user.username
                else: bid = []
            
            return {
                    'status':1,
                    "bid":bid,
                    "ask":ask
                }
    except:
        traceback.print_exc()
        return {
            'bid':[],
            'ask':[],
            'status':0,
            'message':"get bid ask error"
        }
        pass
@socketio.on('balance-view', namespace='/pre_trade/order')
def socket_balance_order(json):
    print("bid ask",json)
    # print(mem["data"])
    res = {}
    try:
        pair = json["Symbol"].split('-')
        for currency in pair:
            res[currency.upper()] = getInfoBalanceAccount(json["UserID"],currency.upper())
    except:
        traceback.print_exc()
        res["status"] =0
    return res        

@socketio.on('update-mem', namespace='/pre_trade/order')
def update_mem(json):
    print("update-mem",json)
    # print(mem["data"])
    res = {}
    try:
        currency = json["currency"]
        amount = json["amount"]
        for id in mem["data"]:
            balance_user = mem["data"][id]
            if(int(json["UserID"]) == int(id)):
                print("-------------BEFORE--------------")
                print(balance_user[currency]["balance"])
                print(balance_user[currency]["avaiable"])
                
                balance_user[currency]["balance"] = add_Decimal(balance_user[currency]["balance"], amount)
                balance_user[currency]["avaiable"] = add_Decimal(balance_user[currency]["avaiable"], amount)
                print("-------------AFTER--------------")
                print(balance_user[currency]["balance"])
                print(balance_user[currency]["avaiable"])
        res["status"] =1
    except:
        traceback.print_exc()
        res["status"] =0
    return res        
@socketio.on('update-order-realtime', namespace='/pre_trade/order')
def real_time_order(json):
    print("update-order-realtime",json)
    try:
        if(json["type"] == 'order'):
            emit('response-list-order-realtime',json, broadcast=True)   
        else:
            emit('response-list-order-after-cancel-realtime', json, broadcast=True)

    except:
        pass    

def run_socket_pre_trade():
    print('Run socket server, Flask server run at port 5041')
    updateBidAskFromDB(book_OTC)
    socketio.run(app, host="0.0.0.0",port=config["pre_trade"]["port"])
# ------------------------------------- Unused route ---------------------------------------

@socketio.on_error()        # Handles the default namespace
def error_handler(e):
    pass

@socketio.on_error_default  # handles all namespaces without an explicit error handler
def default_error_handler(e):
    pass



    
