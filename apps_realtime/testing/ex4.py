from ..pre_trade.core.trade_model import Order, OrderBookOTC, genOrderID, send_execution_report
import uuid
from microservices_connector.Interservices import timeit

# create a new order
@timeit
def main():
    print('-----------------------Test Cancel order------------------')
    client_orderid1 = uuid.uuid1()
    orderid2 = uuid.uuid1()
    my_order_json = [
        {
            'MsgType': 'D',
            'Account': '000100010001',
            'ClOrdID': str(client_orderid1),
            'OrderQty': 1.2,
            'OrdType': 'LO',
            'Price': 6000.00,
            'Side': 'Buy',  # buy
            'Symbol': 'BTC/USDT',
            'AllocAccount': '000100010002',
            'TimeInForce': 'GTC',
            'SecondaryOrderID': '',
        },
        {
            'MsgType': 'D',
            'Account': '000100020001',
            'ClOrdID': str(orderid2),
            'OrderQty': 1.2,
            'OrdType': 'LO',
            'Price': 6000.00,
            'Side': 'Sell',  # sell
            'Symbol': 'BTC/USDT',
            'AllocAccount': '000100020002',
            'TimeInForce': 'GTC',
            'SecondaryOrderID': genOrderID(str(client_orderid1), '000100010001'),
        }
    ]
    cancel_ClOrdID = uuid.uuid1()
    cancel_order_json ={
        'MsgType': 'F',
        'Account': '000100010001',
        'ClOrdID': str(cancel_ClOrdID),
        'OrigClOrdID': str(client_orderid1),
        'Symbol': 'BTC/USDT',
    }
    order01 = Order(**my_order_json[0])
    # order01.MsgType = 'D'

    # print(order01.to_dict())
    # create order book
    book_OTC_BTCUSDT = OrderBookOTC('BTC/USDT', 0.000001, report=send_execution_report)

    # add to orderbookOTC
    book_OTC_BTCUSDT.add_OTC_order(order01)

    # find order
    res = book_OTC_BTCUSDT.find_order(order01.OrderID)
    print('Find order1:', res)

    # cancel order 1 before order 2
    print('cancel order 1 before order 2')
    cancel_order_json['OrderID'] = res['OrderID'] # assign order ID
    cancel_order1 = Order(**cancel_order_json)
    res_cancel = book_OTC_BTCUSDT.cancel_order(cancel_order1)
    print('Cancel result:', res_cancel)

    # find order
    res = book_OTC_BTCUSDT.find_order(order01.OrderID)
    print('Find order1:', res)

    order02 = Order(**my_order_json[1])

    # add order2 to orderbookOTC
    x = book_OTC_BTCUSDT.add_OTC_order(order02)
    print('Add order2:', x)

    # find order
    res = book_OTC_BTCUSDT.find_order(order01.OrderID)
    print('Find order1:', res)

    # find order
    res = book_OTC_BTCUSDT.find_order(order02.OrderID)
    print('Find order2:', res)


if __name__ == '__main__':
    main()
