from . import Micro
import traceback

# open account
import uuid
import random
from sqlalchemy import func
from sqlalchemy.sql import label
import sys
from .process import write_to_file, load_from_file, gen_orderID, check_balance_account, cancel_order
import datetime

# create Orders dictionaries
ORDERS = {
    'Buyer': {},
    'Seller': {},
}

ORDERS_MATCHED = {

}
# demo
# 1. Generate order-ID

# 2. Add orderID to ORDERS
# 3. Add orders to dictionaries of buy-order with key = orderID, user = anonymous
# 5. Remove matched orders from buy and sell side
# 6. Add matched orders to ORDER_HISTORY

# real
# 1. check data is correct
# 2. get data of account from server (HOST_DEPOSIT_APP)
# 3. check balance of account
# 4. send request to trade_app and return notify

# ------------------------------------- Old depreciated API --------------------------------


@Micro.typing('/api/pre-trade/order-book/view-order')
@Micro.json
def view_order_by_name(username=None):
    print(ORDERS_MATCHED)
    return ORDERS_MATCHED[username]


@Micro.typing('/api/pre-trade/order-book/view-bid-ask', methods=['POST', 'GET'])
@Micro.json
def view_order_bid_ask():
    print(ORDERS)
    return ORDERS


@Micro.typing('/api/pre-trade/order-book/process-order-buy-coin')
@Micro.json
def process_order_buy_coin(account_no=None, status=None, symbol='BTC', side='', type='Buyer', time_in_force="Null", price='0', order_qty='0', fee='0', is_from_market_maker='false', target_order="false", username=None):
    data = {
        "account_no": account_no,
        "status": status,
        "symbol": symbol,
        "side": side,
        "type": type,
        "time_in_force": 1,
        "price": price,
        "order_qty": order_qty,
        "fee": fee,
        "is_from_market_maker": is_from_market_maker,
        "target_order": target_order, "user": username
    }
    # format order:
    data['Description'] = 'Wait for matching'
    data['Status'] = 'Waiting'
    data['time'] = str(datetime.datetime.now())

    # Seller
    # generate orderID for data
    data['orderID'] = gen_orderID()
    if username:
        data['user'] = username
    else:
        data['user'] = 'anonymous'
    print(data)
    if data['side'] not in ['Buyer', 'Seller']:
        return {
            "is_ok": False,
            "log": "Order type out of Buyer or Seller"
        }
    if target_order == 'false':
        # Add orderID to ORDERS
        ORDERS[data['side']] = data
        # add order matched to ORDERS_MATCHED
        if not username in ORDERS_MATCHED:
            ORDERS_MATCHED[username] = {}
        ORDERS_MATCHED[username][data['orderID']] = data
        print(ORDERS)
        print(ORDERS_MATCHED)
    else:
        # process matching
        # process matching
        for orderID in ORDERS[data['side']]:
            user_of_order = data['user']
            if orderID == data['target_order']:
                # Order is matched:
                matched_order = ORDERS[data['side']][orderID]
                matched_order['time'] = str(datetime.datetime.now())
                matched_order['Description'] = "Done for %s %s" % (
                    data['symbol'], data['order_qty'])
                matched_order['Status'] = 'Done'
                # add order matched to ORDERS_MATCHED
                if not user_of_order in ORDERS_MATCHED:
                    ORDERS_MATCHED[user_of_order] = {}
                ORDERS_MATCHED[user_of_order][orderID] = matched_order
                # remove done order from ORDERS
                del ORDERS[data['side']][orderID]
                print(ORDERS)
                print(ORDERS_MATCHED)
                return True

    return {
        "is_ok": True,
        "log": "pre-trade process-buy-coin ok"
    }


@Micro.typing('api/pre-trade/order-book/process-order-sell-coin')
@Micro.json
def process_order_sell_coin(account_no=None, status=None, symbol='BTC', side='', type='Buyer', time_in_force="Null", price='0', order_qty='0', fee='0', is_from_market_maker='false', target_order="false", username=None):
    data = {
        "account_no": account_no,
        "status": status,
        "symbol": symbol,
        "side": side,
        "type": type,
        "time_in_force": 1,
        "price": price,
        "order_qty": order_qty,
        "fee": fee,
        "is_from_market_maker": is_from_market_maker,
        "target_order": target_order
    }
    print(data)
    # processing
    # format order:
    data['Description'] = 'Wait for matching'
    data['Status'] = 'Waiting'
    data['time'] = str(datetime.datetime.now())
    print(data)
    # Seller
    # generate orderID for data
    data['orderID'] = gen_orderID()
    if username:
        data['user'] = username
    else:
        data['user'] = 'anonymous'
    if data['side'] not in ['Buyer', 'Seller']:
        return {
            "is_ok": False,
            "log": "Order type out of Buyer or Seller"
        }
    if target_order == 'false':
        # Add orderID to ORDERS
        ORDERS[data['side']] = data
        # add order matched to ORDERS_MATCHED
        if not username in ORDERS_MATCHED:
            ORDERS_MATCHED[username] = {}
        ORDERS_MATCHED[username][data['user']] = data
    else:
        # process matching
        for orderID in ORDERS[data['side']]:
            user_of_order = data['user']
            if orderID == data['target_order']:
                # Order is matched:
                matched_order = ORDERS[data['side']][orderID]
                matched_order['time'] = str(datetime.datetime.now())
                matched_order['Description'] = "Done for %s %s" % (
                    data['symbol'], data['order_qty'])
                matched_order['Status'] = 'Done'
                # add order matched to ORDERS_MATCHED
                if not user_of_order in ORDERS_MATCHED:
                    ORDERS_MATCHED[user_of_order] = {}
                ORDERS_MATCHED[user_of_order][orderID] = matched_order
                # remove done order from ORDERS
                del ORDERS[data['side']][orderID]
                return True
    return {
        "is_ok": True,
        "log": "pre-trade process-sell-coin ok"
    }


@Micro.typing('/api/pre-trade/order-book/process-cancel-order-book')
@Micro.json
def process_cancel_order_book(account_no=None, order_id=None, type_order="order", target_order="false", username=None):

    data = {
        "account_no": account_no,
        "order_id": order_id,
        "type_order": type_order,
        "target_order": target_order
    }
    print(data)
    del ORDERS[data['side']][order_id]
    del ORDERS_MATCHED[username][order_id]
    return {
        "is_ok": True,
        "log": "pre-trade process-cancel-order-book ok"
    }
