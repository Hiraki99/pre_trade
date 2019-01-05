from ..pre_trade.core.trade_model import Order, OrderBookOTC, genOrderID, send_execution_report
import uuid
from microservices_connector.Interservices import timeit
from ..pre_trade.models import ExecutionReport,TransactionTrading
from ..initdb import db_session
from ..pre_trade.process import updateDataInMem,CollectData,mem,check_balance_account,getCancelOrder,UpdateMemAfterCancel

# create a new order
print("Testing data")
print(mem["data"])
# @timeit
def main():
    print('-----------------------Test New Order and matching order------------------')

    Execution_report = [
        {'Account': '084-01-01-01-8747446',
            'ClOrdID': 'a5747371-8cdb-11e8-8116-28c2dd43f18d',
            'OrderID': 'dbeebb6f-408b-54b8-a390-d901a01057b3',
            'OrigClOrdID': '',
            'OrderQty': 1.2,
            'LeavesQty': 0.0,
            'CumQty': 1.2,
            'OrdType': 'LO',
            'OrdStatus': 'Filled',
            'Price': 6000.0,
            'Symbol': 'BTC/USDT',
            'Side': 'Sell',
            'Currency': 'BTC',
            'AllocSettlCurrency': 'USDT',
            'TimeInForce': 'GTC',
            'TransactTime': '2018-07-21 11:46:03.640888',
            'Commission': 14.4,
            'AllocAccount': '084-01-01-01-2142523',
            'SecondaryOrderID': '27ce0f99-8650-57ab-9c92-91c366fa65a8',
            'execution_style': 'OTC'
         }
    ]
    Transaction_trading = [
        {
            'TradeReportID': '021edad8-cc42-54dc-847c-ce8b33f1f747',
            'Commission': 14.4,
            'LastQty': 1.2,
            'LastPx': 6000.0,
            'TransactTime': '2018-07-20 03:27:52.836594',
            'Side': 'Sell',
            'Symbol': 'BTC/USDT',
            'OrderID': 'dbeebb6f-408b-54b8-a390-d901a01057b3',
            'SecondaryOrderID': 'a4ec3c0d-e308-523c-bb32-6a2002988e75',
            'Account': '084-01-01-01-8747446',
            'Currency': 'USDT',
            'Quantity': 7200.0,
            'AllocAccount': '084-01-01-01-2142523',
            'AllocSettlCurrency': 'USDT',
            'AllocQty': 7185.6}]
    order = {'userID': 1, 'OrderQty': '2', 'OrdType': 'LO', 'Price': '211211', 'Side': 'Sell', 'Symbol': 'ETH/VND'}
    print("Before Data In Memmory")
    print(mem["data"])
    print(check_balance_account(order,mem["data"]))
    with db_session() as session:
        print(Execution_report[0])
    
        excution_report = ExecutionReport(**Execution_report[0])
        session.add(excution_report)
    
    cancel_request = {
        'userID': 1,
        'ClOrdID': 'a5747371-8cdb-11e8-8116-28c2dd43f18d',
        'OrderID': 'dbeebb6f-408b-54b8-a390-d901a01057b3',
        'Symbol': 'BTC/USDT'
    }
    print("Get excution cancel from request client") 
    it = getCancelOrder(cancel_request)
    print(it)
    print("Add User Id to cancel request to update memory")
    it["userID"] = cancel_request["userID"]
    print("Update memory after cancel request")

    print(UpdateMemAfterCancel(it, mem["data"]))

if __name__ == '__main__':
    main()

# acc = {
#   'ETH':{}
# }

# if 'BTC' in acc:
#   print('not None BTC')
# else:
#   print('None')
  
# if 'ETH' in acc:
#   print('not None ETH ')
# else:
#   print('None')