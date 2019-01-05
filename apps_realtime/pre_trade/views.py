from . import Micro
import traceback

# open account
import uuid, random
from sqlalchemy import func
from sqlalchemy.sql import label
import sys
from .process import write_to_file, load_from_file, gen_orderID,check_balance_account,cancel_order
import datetime

# 1. check data
# 2. check order is exist?
# 3. send request to trade_app

@Micro.route('/pre-trade/real-time-market/process-order')
@Micro.json
def process_order(MsgType=None, Account=None, OrderQty=None, OrdType=None, Price=None, Side=None, Symbol=None, AllocAccount=None, TimeInForce=None, SecondaryOrderID=None):
    data={
        'MsgType': MsgType,
        'Account': Account,
        'OrderQty': OrderQty,
        'OrdType': OrdType,
        'Price': Price,
        'Side': Side,  # buy
        'Symbol': Symbol,
        'AllocAccount': AllocAccount,
        'TimeInForce': TimeInForce,
        'SecondaryOrderID': SecondaryOrderID,
        'ClOrdID': gen_orderID()
    } 
    print(data)
    check_balance_account(data)


@Micro.route('/pre-trade/real-time-market/process-cancel-order',methods=['PUT'])
@Micro.json
def process_cancel_order(order_id=None, type_order= None, direction="buy_sell",account_no=None,user_id=None):
    data={
        "order_id": order_id,
        "type_order": type_order,
        "direction": direction,
        "account_no": account_no,
        "user_id": user_id
    }
    print(data)
    # process
    cancel_order(data)
