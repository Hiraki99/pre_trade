import requests, traceback
from .core.trade_model import Order
from .logger import create_logger
from flask_socketio import emit
from configparser import ConfigParser
config = ConfigParser()
config.read('config.env')
from ..initdb import db_session
from ..pre_trade.models import ExecutionReport,TransactionTrading,User
from ..ulib import add_Decimal,sub_Decimal,div_Decimal,mul_Decimal,toDecimal
from .process import mem,updateDataInMem
logger = create_logger()
# logging rotation-log, co tren python-snippet 
# folder logging: log-preTrade (de ngoai thu muc du an, json)
# push data to trade-data: insert report to database
# push status request to deposi_app(transaction_report)
# push data via socketio -> nodejs api -> client


def send_execution_report(order):
    print("send_execution_report -------")
    """
    # loại message trả ra mỗi lần đặt lệnh mới, khớp lệnh hoặc cancel lệnh
        expected_execution_report = 
        {
            'MsgType': '8',
            'Account': '000100010001', 
            'ClOrdID': 'e2b9f268-8bcc-11e8-a136-f40f24228a51', 
            'OrderID': 'a4ec3c0d-e308-523c-bb32-6a2002988e75', 
            'OrigClOrdID': '',
            'OrderQty': 1.2, 
            'LeavesQty': 0.0, 
            'CumQty': 1.2,
            'OrdType': 'LO', 
            'OrdStatus': 'Filled', 
            'Price': 6000.0, 
            'Side': 'Buy', 
            'Symbol': 'BTC/USDT', 
            'Currency': 'BTC',
            'AllocSettlCurrency': 'USDT', 
            'TimeInForce': 'GTC', 
            'TransactTime': '2018-07-20 03:27:52.835766', 
            'Commission': 0.0024, 
            'AllocAccount': '000100010002', 
            'SecondaryOrderID': '', 
            'time_zone': 'GMT +7:00', 
            'execution_style': 'OTC'
        } => database vs socket
        loại message trả ra trong trường hợp lệnh khớp, dùng để chuyển tiền
        Transaction = 
        {
            'MsgType': 'AE', 
            'TradeReportID': 
            '021edad8-cc42-54dc-847c-ce8b33f1f747', 
            'Commission': 14.4, 
            'LastQty': 1.2, 
            'LastPx': 6000.0, 
            'TransactTime': '2018-07-20 03:27:52.836594',
            'Side': 'Sell', 
            'Symbol': 'BTC/USDT', 
            'OrderID': 'f81eb87f-c4eb-5d06-8b11-a4d4a0dffe9d', 
            'SecondaryOrderID': 'a4ec3c0d-e308-523c-bb32-6a2002988e75', 
            'Account': '000100020001', 
            'Currency': 'USDT', 
            'Quantity': 7200.0, 
            'AllocAccount': '000100010002',
            'AllocSettlCurrency': 'USDT',
            'AllocQty': 7185.6
        } => deposit app 
    """
    report = order.execution_report()    
    print(' 73 Send Execution Report: %s' % report)
    print(' 74 order.MsgType: %s' % order.MsgType)
    

    try:
        if(report['MsgType'] == "8"):
            # push database
            try:
                print("### 80 Report order match ####")
                print(report)
                with db_session() as session:
                    try:
                        user = session.query(User).filter(User.id == report["UserID"]).first()
                        report["DisplayName"] = user.username
                    except:
                        traceback.print_exc()
                        pass
                res = requests.post(config["ENV"]['HOST_TRADE_DATA'] + '/add-execution-report', json = report)
                # print(res)
                print(" 91 push TRADE-DATA")
            except:
                traceback.print_exc()
                logger.error(traceback.print_exc())
            # push socket 
            if(report['OrdStatus']!='Canceled'):
                if(order.SecondaryOrderID==""):
                    emit('response-list-order', {'status':1, 'message':"Order is completed","order":report}, broadcast=True)
                # else:
                #     if(report["Side"] == "Buy"):
                #         report["AllocQty"] = sub_Decimal(mul_Decimal(report["OrderQty"],report["Price"]) , report["Commission"])
                #     else:
                #         report["AllocQty"] = toDecimal(report["OrderQty"])
                #     print("------------------Report Socket-------------------")
                #     print(report)
                #     emit('response-list-order-matching', {'status':2, 'message':"Order execution completed","order":report}, broadcast=True)
                    # report["AllocQty"] = sub_Decimal(mul_Decimal(report["OrderQty"],report["Price"]) , report["Commission"])
                    # emit('response-list-order-matching', {'status':2, 'message':"Order execution completed","order":report}, broadcast=True)
            else:
                res = requests.post(config["ENV"]['HOST_TRADE_DATA'] + '/add-execution-report', json = report)
                print("send_execution_report emit order-cancel")
                emit('response-list-order-after-cancel', {'status':1, 'message':"Cancel order is completed","order":report}, broadcast=True)


        elif(report['MsgType'] == "AE"):
            # add transactionTrading To Db
            res_push_data = requests.post(config["ENV"]['HOST_TRADE_DATA'] + '/add-transaction-trading', json = report)
            print(res_push_data)
            print("push TRADING-TRANSACTION-AE")
            
            # push HOST_DEPOSIT_APP
            res_update_balance = requests.post(config["ENV"]['HOST_DEPOSIT_APP']+'/transaction_reports', json = {"Account_no":report['Account'],"AllocAccount_no":report['AllocAccount'],"AllocQty":report['AllocQty'],"Quantity":report['Quantity']})
            print(res_update_balance)
            print("push DEPOSIT_APP")
            mem["data"] = updateDataInMem(mem["data"], report)
        logger.info(report)
    except:
        logger.error(traceback.print_exc())
        pass
