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
            'SecondaryOrderID': '', 'DisplayName':'Thinh KAKA',
        'UserID': 1
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
            'SecondaryOrderID': genOrderID(str(orderid1), '000100010001'),'DisplayName':'Thinh KAKA',
        'UserID': 1
        }
    ]
    # tạo đối tượng Order từ dict của python
    # Quá trình khởi tạo này đã check tất cả các kiểu và độ dài của dữ liệu
    order01 = Order(**my_order_json[0])
    # order01.MsgType = 'D'

    # print(order01.to_dict())
    # create order book
    book_OTC_BTCUSDT = OrderBookOTC(
        'BTC/USDT', 0.000001, report=send_execution_report)

    # add to orderbookOTC
    book_OTC_BTCUSDT.add_OTC_order(order01)

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

    # find all bid ask
    # find all bid and ask order
    o1 = book_OTC_BTCUSDT.view_bid_order()
    print('View Bid Orders: \n', o1)
    o2 = book_OTC_BTCUSDT.view_ask_order()
    print('View Ask Orders: \n', o2)

    expected_execution_report = {
        'MsgType': '8', 
        'Account': '000100010001', 
        'ClOrdID': 'f89333e6-8602-11e8-8f1c-f40f24228a51', 
        'OrderID': 'a3ff8675-d32d-55cd-9739-b4dcbfc3f7ec', 
        'OrigClOrdID': '', 
        'OrderQty': 1.2, 
        'LeavesQty': 0.0, 
        'CumQty': 1.2, 
        'OrdType': 'LO', 
        'OrdStatus': 'Filled',
        'Price': 6000.0, 
        'Side': 'Buy', 
        'Symbol': 'BTC/USDT', 
        'TimeInForce': 'GTC', 
        'ExecType': 'Complete', 
        'TransactTime': '2018-07-13 01:39:55.337783', 
        'Commission': 0.0024, 
        'AllocAccount': '000100010002', 
        'SecondaryOrderID': '', 
        'time_zone': 'GMT +7:00', 
        'execution_style': 'OTC',
        'DisplayName':'Thinh KAKA',
        'UserId': 1
        }


if __name__ == '__main__':
    main()
