import json
import uuid
import datetime
import requests,traceback
from .kafka.producer import Producer
from decimal import *
from flask_socketio import emit
from ..initdb import db_session
from configparser import ConfigParser
from ..pre_trade.models import ExecutionReport,TransactionTrading, Account
from ..ulib import div_Decimal,sub_Decimal, add_Decimal,toDecimal,mul_Decimal
config = ConfigParser()
config.read('config.env')

API_INFO_ACCOUNT = "/account/info/view"

def write_to_file(content, filename='data.txt'):
    with open(filename, 'w') as outfile:
        json.dump(content, outfile)

def load_from_file(filename='data.txt'):
    with open(filename) as f:
        data = json.load(f)
    return data

def gen_orderID():
    x = uuid.uuid1()
    # print(x)
    return str(x)

def main():
    print(gen_orderID())

def check_data(data):
    # maybe need to check user_id???
    if(data['Account']is not None):
        return True
    return False
# Update Balance Account
def CollectData():
    # get all info of all account
    payload = {}
    print("Call Data")
    response = requests.post(config["ENV"]["HOST_DEPOSIT_APP"] + "/getAll/balance/view", json=payload )
    
    result = response.json()[0]
    print(result)
    #update Data
    if(result != 0):
        res = updateAll(result["arr"])
        return res
    else:
        CollectData()
        

def updateItem(json, order):
    
    pair = order["Symbol"].split("/")
   
    if(order["Side"] == "Buy"):
        Account = pair[1]
        AllocAccount = pair[0]
        volume_account = mul_Decimal(order["OrderQty"],order["Price"])
    if(order["Side"] == "Sell"):
        Account = pair[0]
        AllocAccount = pair[1]
        volume_account = order["OrderQty"]
    for user_id in json:
        # print(user_id)
        AccountUser = json[user_id]
        
        # Check account currency existed in user id
        if(Account in AccountUser and AllocAccount in AccountUser):
            
            if((AccountUser[Account]["account_no"] == order["Account"] )):
                
                # print(AccountUser[Account]["account_no"] == order["Account"])
 
                # AccountUser[AllocAccount]["avaiable"] = add_Decimal(AccountUser[AllocAccount]["avaiable"] , volume_alloc_account)
                AccountUser[Account]["avaiable"] = sub_Decimal(AccountUser[Account]["avaiable"],volume_account)

                AccountUser[Account]["orderID"].append(order)
                AccountUser[AllocAccount]["orderID"].append(order)

    
    return json
                
def updateAll(json):
    """[summary]
    
    Arguments:
        json {[json]} -- [all info Account, Balance, Avaiable , List Order of Account]
    
    Returns:
        [json] -- [All info Account currency with list order in mem (order dont match) ]
    """
    with db_session() as session:
        # Step1 : Add all order in account, have all order (match and dont't match), update balance
        AllOrder = session.query(ExecutionReport).filter(ExecutionReport.OrdStatus == "New",ExecutionReport.live == True).all()
        for item in AllOrder:
            # print(ExecutionReport.to_dict(item))
            item = ExecutionReport.to_dict(item)
            json = updateItem(json,item)
    
    return json
# Check data cancel
def check_data_cancel(data):
    if(data['Account']is not None and data['ClOrdID'] is not None):
        return True
    return True
def getJson(userId,Symbol,side,alldata):
    """
        Examplate pair: BTC/USDT

        Side:
        + Buy :  Account : USDT , AllocAccount : BTC
        + Sell:  Account : BTC , AllocAccount: USDT
    """
    
    pair = Symbol.split("/")
    if(side == "Buy"):
        Account = pair[1]
        AllocAccount = pair[0]
    if(side == "Sell"):
        Account = pair[0]
        AllocAccount = pair[1]
    for user_id in alldata:
        if(int(user_id) == int(userId)):
            AccountUser = alldata[user_id]
            if(Account in AccountUser and AllocAccount in AccountUser):
                return AccountUser[Account], AccountUser[AllocAccount]
    return None, None
# Check Balance Account
def check_balance_account(data, alldata):
    res = {'status':0 }
    try:
        total = mul_Decimal(data['Price'] , data['OrderQty'])
        balance_currency, balance_alloccurrency = getJson(data["userID"], data["Symbol"],data["Side"],alldata)
        if(balance_alloccurrency is None or balance_currency is None):
            res['message'] ="Can\'t check balance of account or account is not exist!"
        else:
            if(data["Side"] =="Sell"):
                vol_curr = data["OrderQty"]
            else:
                vol_curr = mul_Decimal(data['Price'] , data['OrderQty'])
            vol_alloc = mul_Decimal(data['Price'] , data['OrderQty'])
            print(balance_currency)
            print(data["OrderQty"])
            print(sub_Decimal(balance_currency["avaiable"] ,vol_curr) > 0)
            checked = sub_Decimal(balance_currency["avaiable"] ,vol_curr) > 0
            if(checked) :
                res["status"] =1
                res["message"] = "Order Buy %r success" % data["Symbol"]
                data["Account"] = balance_currency["account_no"]
                data["AllocAccount"] = balance_alloccurrency["account_no"]
                res["data"] = data 
            else: 
                res["status"] =0
                res["message"] = "Order Buy %r error, Balance Account don't enough to order" % data["Symbol"]
            
                
    except:
        traceback.print_exc()
        res['status'] = 0
        res['message'] = 'Can\'t check balance of account or account is not exist!'
    return res

def load_data_account(account):
    try:
        print('link = '+HOST_DEPOSIT_APP+API_INFO_ACCOUNT)
        data = {"account_no":"084-01-01-01-0211291"}
        res = requests.post(HOST_DEPOSIT_APP+API_INFO_ACCOUNT, json = data)
        print(res.json())
        return res.json()
    except:
        traceback.print_exc()
        res = {}
        res['status'] = 4
        res['message'] = "load data account fail"
        return res

def cancel_order(data):
    res = {}
    try:
        if(check_data_cancel(data)):
            # need to filter type request between order and cancel request
            send_order_to_kafka(data)
            res["status"] = 1
            res["message"] = "send request cancal order is completed!"
        else:
            res["status"] = 0
            res["message"] = "data of order is not correct!"
        pass
    except:
        traceback.print_exc()
        res["status"] = 0
        res["message"] = "can't not cancel data!"
        pass


def send_order_to_kafka(data):
    try:
        Producer().run(data)
        print("send_order_to_kafka success")
        pass
    except:
        print("send_order_to_kafka fail")
        pass

def exclude_order_list(json, order_id):
    # Delete order_id in list order
    res =[]
    for item in json:
        if (item["OrderID"] != order_id):
            res.append(item)
    return res
def getItemJson(currency, account_no,alldata,type_account, volume,orderID):
    for user_id in alldata:
        AccountUser = alldata[user_id]
        if(currency in AccountUser):
            if(AccountUser[currency]["account_no"] == account_no):
                print("-----------------------------------ListOrder before-------------------------")
                print(AccountUser[currency]["balance"])
                print(AccountUser[currency]["avaiable"])

                if(type_account == "alloc"):
                    AccountUser[currency]["balance"] = add_Decimal(AccountUser[currency]["balance"], volume)
                    AccountUser[currency]["avaiable"] = add_Decimal(AccountUser[currency]["avaiable"], volume)
                    print("AllocAccount %r" %AccountUser[currency]["account_no"])
                    
                else:
                    print("Account %r" %AccountUser[currency]["account_no"])
                    print(AccountUser[currency]["balance"] == AccountUser[currency]["avaiable"])
                    if( toDecimal(AccountUser[currency]["balance"]) == toDecimal(AccountUser[currency]["avaiable"])):
                        AccountUser[currency]["avaiable"] = sub_Decimal(AccountUser[currency]["avaiable"], volume)
                    AccountUser[currency]["balance"] = sub_Decimal(AccountUser[currency]["balance"], volume)
                AccountUser[currency]["orderID"] = exclude_order_list(AccountUser[currency]["orderID"], orderID)
                print("-----------------------------------ListOrder after-------------------------")
                print(AccountUser[currency]["balance"])
                print(AccountUser[currency]["avaiable"])
                
                return alldata

def updateDataInMem(alldata,transaction_tradding):
    # Update Info User after order success and tranfer currency between account
    # Usage: data: variable save all info account of user
    # mem["data"] = updateDataInMem(mem["data"],transaction_tradding)
    # Note: update info account to mem
    
    alldata = getItemJson(transaction_tradding["Currency"],transaction_tradding["Account"],alldata,"account",transaction_tradding["Quantity"],transaction_tradding["OrderID"])
   
    alldata = getItemJson(transaction_tradding["AllocSettlCurrency"],transaction_tradding["AllocAccount"],alldata,"alloc",transaction_tradding["AllocQty"],transaction_tradding["SecondaryOrderID"])
    return alldata
def getCancelOrder(cancel_order):
    """ GET order cancel from mem
    
    Arguments:
        user_id {[integer]]]} -- [userId]]
        orderId {[string]} -- [orderId]
    """
    print("cancel order: ",cancel_order)
    with db_session() as session:
        report = session.query(ExecutionReport).filter(ExecutionReport.OrderID == cancel_order["OrderID"]).first()
        # test
        # report = {'MsgType': 'D', 'DisplayName': 'thinhphoho01',
        #                  'UserID': 1, 'Account': '000100020001', 
        #                  'ClOrdID': '2d04912f-a101-11e8-aa06-28c2dd43f18d', 'OrderID': 'abb0a508-cae4-51f6-942d-662fe145215d', 'OrigClOrdID': '', 'OrdType': 'LO', 'OrdStatus': 'New', 'Side': 'Sell', 'Symbol': 'ETH/BTC', 'OrderQty': 1.2999, 'LeavesQty': 1.2999,
        #                  'CumQty': 0, 'Price': 1.33, 'LastQty': 0, 'LastPx': 0, 'Currency': 'ETH', 'AllocSettlCurrency': 'BTC', 'TimeInForce': 'GTC', 'Commission': 0, 'AllocAccount': '000100020002', 'SecondaryOrderID': 'daa64a5b-764e-5736-8a93-ade92b002530', 'TransactTime': '2018-08-16 03:05:10.280972', 'TimeZone': 'GMT +0:00', 'ExecStyle': 'ECN'}
    
        if(report is None):
            return None,None
        else:
            # product
            return  ExecutionReport.to_dict(report),{
                'MsgType': 'F',
                'Account': report.Account,
                'ClOrdID': str(uuid.uuid1()),
                'OrigClOrdID': report.ClOrdID,
                'Symbol': report.Symbol,
                "OrderID": report.OrderID,
                "UserID" : cancel_order["userID"]
            }
            # test
            # return  None,{
            #     'MsgType': 'F',
            #     'Account': report["Account"],
            #     'ClOrdID': str(uuid.uuid1()),
            #     'OrigClOrdID': report["ClOrdID"],
            #     'Symbol': report["Symbol"],
            #     "OrderID": report["OrderID"],
            #     "Side" : cancel_order["Side"],
            #     "UserID" : cancel_order["userID"]
            # }

def UpdateMemAfterCancel(cancel_order,Side, allData):
    """[summary]
    
    Arguments:
        cancel_order {[type]} -- [description]
        UserID {[type]} -- [description]
        Side {[type]} -- [description]
        allData {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """
    pair = cancel_order["Symbol"].split("/")
    if(Side == "Buy"):
        Account = pair[1]
        AllocAccount = pair[0]
    if(Side == "Sell"):
        Account = pair[0]
        AllocAccount = pair[1]
    for user_id in allData:
        if(int(user_id) == int(cancel_order["UserID"])):
            item = allData[user_id]
            
            
            if(Account in item and AllocAccount in item):
              
                item_Account, item_AllocAccount = updateItemAndOrder(item[Account], item[AllocAccount],cancel_order["OrderID"])
                item[Account] = item_Account
                item[AllocAccount] = item_AllocAccount
                

    return allData

def updateItemAndOrder(item_Account,item_AllocAccount, order_id):
    """ Update Account and AllocAccount in mem
    
    Arguments:
        item_Account {[type]} -- [description]
        item_AllocAccount {[type]} -- [description]
        order_id {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """
    order_cancel = {}
    for order in item_Account["orderID"]:
        if(order["OrderID"] == order_id):
            order_cancel = order
            break
    # update balance
    print("----------------Order In List---------")
    print(order_cancel)
    # item_Account["balance"] = add_Decimal(item_Account["balance"], order_cancel["OrderQty"])
    if(order_cancel["Side"] == "Sell"):
        item_Account["avaiable"] = add_Decimal(item_Account["avaiable"], order_cancel["OrderQty"])
    else:
        item_Account["avaiable"] = add_Decimal(item_Account["avaiable"], mul_Decimal(order_cancel["OrderQty"], order_cancel["Price"]))
    item_Account["orderID"]= exclude_order_list(item_Account["orderID"],order_id)
    item_AllocAccount["orderID"]= exclude_order_list(item_AllocAccount["orderID"],order_id)

    return item_Account, item_AllocAccount

def getInfoBalanceAccount(userId, currency):
    res={}
    try:
        with db_session() as session:
            account = session.query(Account).filter(Account.user_id == userId,Account.currency == currency).first()
            # alloc_account = session.query(Account).filter(Account.user_id == userId,Account.currency == alloc_currency).first()
            in_order = 0
            all_excution_account = session.query(ExecutionReport).filter(ExecutionReport.live== True,ExecutionReport.Account == account.account_no, ExecutionReport.OrdStatus == 'New').all()
            for item in all_excution_account:
                # print(ExecutionReport.to_dict(item))
                if(item.Side== "Buy"):
                    in_order = add_Decimal(in_order, mul_Decimal(item.OrderQty,item.Price))
                else:
                    in_order = add_Decimal(in_order, item.OrderQty)
            res["balance"] = account.balance
            res["avaiable"]= sub_Decimal(account.balance,in_order)
    except:
        traceback.print_exc()
        res["status"] =0
    return res
    

def checkBalanceAccountDB(data):
    res= {}
    try:
        pair = data["Symbol"].split('/')
        if(data["Side"]=="Sell"):
            currency = pair[0]
            alloc_currency = pair[1]
        else:
            currency = pair[1]
            alloc_currency = pair[0]
        print(currency)
        print(alloc_currency)
        time = datetime.datetime.now()
        with db_session() as session:
            account = session.query(Account).filter(Account.user_id == data["userID"],Account.currency == currency).first()
            alloc_account = session.query(Account).filter(Account.user_id == data["userID"],Account.currency == alloc_currency).first()
            in_order = 0
            all_excution_account = session.query(ExecutionReport).filter(ExecutionReport.live== True,ExecutionReport.Account == account.account_no, ExecutionReport.OrdStatus == 'New').all()
            for item in all_excution_account:
                # print(ExecutionReport.to_dict(item))
                if(item.Side== "Buy"):
                    in_order = add_Decimal(in_order, mul_Decimal(item.OrderQty,item.Price))
                else:
                    in_order += add_Decimal(in_order, item.OrderQty)
            if(data["Side"] =="Sell"):
                vol_curr = data["OrderQty"]
            else:
                vol_curr = mul_Decimal(data['Price'] , data['OrderQty'])

            avaiable = sub_Decimal(account.balance ,in_order)
            if(sub_Decimal(avaiable, vol_curr) > 0):
                res["status"] =1
                res["message"] = "Order Buy %r success" % data["Symbol"]
                data["Account"] = account.account_no
                data["AllocAccount"] = alloc_account.account_no
                res["data"] = data 
            else:
                res["status"] =0
                res["message"] = "Order Buy %r error, Balance Account don't enough to order" % data["Symbol"]
    except:
        traceback.print_exc()
        res['status'] = 0
        res['message'] = 'Can\'t check balance of account or account is not exist!'\
    
    return res
def convertNewStyleExecutionReport(order):
    order_convert = {
        'MsgType': '8',
        'DisplayName': order.DisplayName, 
        'UserID': order.UserID, 
        'Account': order.Account, 
        'ClOrdID': order.ClOrdID, 
        'OrderID': order.OrderID, 
        'OrigClOrdID': order.OrigClOrdID, 
        'OrderQty': order.OrderQty, 
        'LeavesQty': order.LeavesQty, 
        'CumQty': order.CumQty, 
        'OrdType': order.OrdType, 
        'OrdStatus': order.OrdStatus, 
        'Price': order.Price, 
        'Side': order.Side, 
        'Symbol': order.Symbol, 
        'Currency': order.Currency, 
        'AllocSettlCurrency': order.AllocSettlCurrency, 
        'TimeInForce': order.TimeInForce, 
        'TransactTime': order.TransactTime.strftime("%c"), 
        'Commission': order.Commission, 
        'AllocAccount': order.AllocAccount, 
        'SecondaryOrderID': order.SecondaryOrderID, 
        'TimeZone': 'GMT +0:00', 
        'ExecStyle': order.execution_style}
    return order_convert


mem = {}
mem["data"] = CollectData()

if __name__ == '__main__':
    main()

