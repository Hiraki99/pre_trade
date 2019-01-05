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
# from .process import data
from configparser import ConfigParser
config = ConfigParser()
config.read('config.env')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['CELERY_BROKER_URL'] = config["ENV"]['CELERY_BROKER_URL']
app.config['result_backend'] = config["ENV"]['result_backend']
app.config['SQLALCHEMY_DATABASE_URI'] = config["ENV"]['database']

celery = Celery(app.name, backend=app.config['result_backend'], broker = app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

socketio = SocketIO(app)

# data = CollectData()
# create order book
book_OTC = {}
book_OTC['BTC/USDT'] = OrderBookOTC('BTC/USDT', 0.000001, report=send_execution_report)
book_OTC['ETH/USDT'] = OrderBookOTC('ETH/USDT', 0.000001, report=send_execution_report)
book_OTC['ETH/BTC'] = OrderBookOTC('ETH/BTC', 0.000001, report=send_execution_report)
book_OTC['BTC/VND'] = OrderBookOTC('BTC/VND', 0.000001, report=send_execution_report)
book_OTC['ETH/VND'] = OrderBookOTC('ETH/VND', 0.000001, report=send_execution_report)
book_OTC['USDT/VND'] = OrderBookOTC('USDT/VND', 0.000001, report=send_execution_report)

redis_book_OTC = {}
redis_book_OTC['BTC/USDT'] = MyRedis("BTC/USDT",{"bid":[],"ask":[]})
redis_book_OTC['ETH/USDT'] = MyRedis("ETH/USDT",{"bid":[],"ask":[]})
redis_book_OTC['ETH/BTC'] = MyRedis("ETH/BTC",{"bid":[],"ask":[]})
redis_book_OTC['BTC/VND'] = MyRedis("BTC/VND",{"bid":[],"ask":[]})
redis_book_OTC['ETH/VND'] = MyRedis("ETH/VND",{"bid":[],"ask":[]})
redis_book_OTC['USDT/VND'] = MyRedis("USDT/VND",{"bid":[],"ask":[]})

def updateBidAskFromRedis(book_OTC, redis_bookOTC):
    try:
        with db_session() as session:
            all_order = session.query(ExecutionReport).filter(ExecutionReport.live == True, ExecutionReport.OrdStatus == 'New').all()
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

# add to orderbookOTC
# book_OTC_BTCUSDT.add_OTC_order(order01)

@socketio.on('order-new', namespace='/pre_trade/order')
def socket_new_order(json):
    try:
        print("order: ",json)
        checked = checkBalanceAccountDB(json)
        print(checked)
        if checked['status'] == 1:
            order = {
                'MsgType': 'D',
                "UserID" : json['userID'],
                'Account': checked['data']['Account'],
                'ClOrdID': gen_orderID(),
                'OrderQty': toDecimal(json['OrderQty']),
                'OrdType': 'LO',
                'Price': toDecimal(json['Price']),
                'Side': json['Side'],  
                'Symbol': json['Symbol'],
                'AllocAccount': checked['data']['AllocAccount'],
                'TimeInForce': 'GTC',
                'SecondaryOrderID': '',
            }
            try:
                order['SecondaryOrderID'] = json['SecondaryOrderID']
            except:
                pass
            print('received json data-order: ' + str(order))

            # check symbol of order
            if book_OTC[order['Symbol']] is not None:
                # accept new order
                order_object = Order(**order)
                # print("order_object.to_dict() = ",order_object.to_dict())
                x = book_OTC[order['Symbol']].add_OTC_order(order_object)
                # book_OTC[order['Symbol']].find_order(order_object.OrderID)
                
                report = order_object.execution_report()
                print('x = ',x)
                
                if(report["OrdStatus"] == "New"):
                    mem["data"] = updateItem(mem["data"], report)
                with db_session() as session:
                    try:
                        user = session.query(User).filter(User.id == report["UserID"]).first()
                        report["DisplayName"] = user.username
                    except:
                        traceback.print_exc()
                        pass
                print(report)
                bid = book_OTC[report['Symbol']].view_bid_order()
                print('View Bid Orders After new orders or match orders: \n', bid)
                ask = book_OTC[report['Symbol']].view_ask_order()
                print('View Ask Orders: new orders or match orders \n', ask)
                redis_book_OTC[report['Symbol']].update({'bid':bid,'ask':ask})

                if(x[0]):
                    if(report['OrdStatus'] == "New"):
                        return {
                            "status":1,
                            "message": "Order is successful",
                            "report":report
                        }
                    elif(report['OrdStatus'] == "Filled"):
                        report["AllocQty"] = sub_Decimal(mul_Decimal(report["OrderQty"],report["Price"]) , report["Commission"])
                        
                        print("---------------Report http---------------------")
                        print(report)
                        emit('response-list-order-matching', {'status':2, 'message':"Order execution completed","order":report}, broadcast=True)
                        return {
                            "status": 2,
                            "message": "Order execution complete",
                            "report":report
                            # ,"AllocQty" : sub_Decimal(report["OrderQty"],mul_Decimal())
                        }
                else:
                    return {
                        "status": 0,
                        "message": "Order is failed",
                        "report":""
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
            res_cancel = book_OTC[json['Symbol']].cancel_order(cancel_order)
            print("res_cancel = ",res_cancel)
            cancel_order_json["userID"] = json["userID"]
            mem["data"] = UpdateMemAfterCancel(cancel_order_json,json["Side"], mem["data"])
            # update redis_book_OTC
            bid = book_OTC[json['Symbol']].view_bid_order()
            ask = book_OTC[json['Symbol']].view_ask_order()
            redis_book_OTC[json['Symbol']].update({'bid':bid,'ask':ask})

            print("cancel_order_json_after = ",cancel_order.execution_report())
            if(res_cancel[0]):
                return {
                    "status":1,
                    "message":"Cancel order is completed",
                    "report": cancel_order.execution_report(),
                    "cancel_report": old_report
                }
            else:
                return {
                    "status":0,
                    "message":"Cancel order is failed",
                    "report": old_report
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
            bid = book_OTC[data['Symbol']].view_bid_order()
            print('View Bid Orders: \n', bid)
            ask = book_OTC[data['Symbol']].view_ask_order()
            print('View Ask Orders: \n', ask)
            with db_session() as session:
                for item in ask:
                    user = session.query(User).filter(User.id == item["UserID"]).first()
                    item["DisplayName"] = user.username
                for item in bid:
                    user = session.query(User).filter(User.id == item["UserID"]).first()
                    item["DisplayName"] = user.username
                
            redis_book_OTC[data['Symbol']].update({'bid':bid,'ask':ask})
            redis_book_OTC[data['Symbol']].query()
            print("--------------Update Reids--------------")
            print(redis_book_OTC[data['Symbol']].value)
            return {"bid":bid, "ask":ask}
    except:
        traceback.print_exc()
        pass
@socketio.on('balance-view', namespace='/pre_trade/order')
def socket_balance_order(json):
    print("bid ask",json)
    # print(mem["data"])
    res = {}
    try:
        # if(json['Symbol'] is not None):
        #     pair = json["Symbol"].split('-')
        #     for id in mem["data"]:
        #         balance_user = mem["data"][id]
        #         if(int(json["UserID"]) == int(id)):
        #             for item in pair:
        #                 if item.upper() in balance_user:
        #                     res[item.upper()] = {
        #                         "avaiable": balance_user[item.upper()]["avaiable"],
        #                         "balance": balance_user[item.upper()]["balance"]
        #                     }
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



# @socketio.on('transaction-report', namespace='/pre_trade/transaction-report')
# def transaction_report(json):
    
# ------------------------------------- Start socketIO and flask server --------------------------
def run_socket_pre_trade():
    print('Run socket server, Flask server run at port 5000')
    updateBidAskFromRedis(book_OTC, redis_book_OTC)
    socketio.run(app, host="0.0.0.0")

# ------------------------------------- Unused route ---------------------------------------

@socketio.on_error()        # Handles the default namespace
def error_handler(e):
    pass

@socketio.on_error_default  # handles all namespaces without an explicit error handler
def default_error_handler(e):
    pass



    
