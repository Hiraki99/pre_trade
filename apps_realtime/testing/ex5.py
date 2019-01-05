from ..pre_trade.core.trade_model import Order, OrderBookOTC, genOrderID, send_execution_report
import uuid
from microservices_connector.Interservices import timeit

# create a new order


@timeit
def main():
    print('-----------------------Test New Order and matching order------------------')
    orderid1 = uuid.uuid1()
    orderid2 = uuid.uuid1()
    my_order_json = [
        {
            'MsgType': 'D',
            'Account': '000100010001',
            'ClOrdID': str(orderid1),
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
            'OrderQty': 1.200000000000000000001,
            'OrdType': 'LO',
            'Price': 5000.00,
            'Side': 'Sell',  # sell
            'Symbol': 'BTC/USDT',
            'AllocAccount': '000100020002',
            'TimeInForce': 'GTC',
            'SecondaryOrderID': genOrderID(str(orderid1), '000100010001'),
        }
    ]
    order01 = my_order_json[0]
    # order01.MsgType = 'D'

    # print(order01.to_dict())
    # create order book
    book_OTC_BTCUSDT = OrderBookOTC(
        'BTC/USDT', 0.000001, report=send_execution_report)

    # add to orderbookOTC
    book_OTC_BTCUSDT.add_OTC_order(order01)

    order02 = my_order_json[1]

    # add order2 to orderbookOTC
    x = book_OTC_BTCUSDT.add_OTC_order(order02)
    print('Add order2:', x)

    # find all bid and ask order
    o1 = book_OTC_BTCUSDT.view_bid_order()
    print('View Bid Orders: \n', o1)
    o2 = book_OTC_BTCUSDT.view_ask_order()
    print('View Ask Orders: \n', o2)


if __name__ == '__main__':
    main()
