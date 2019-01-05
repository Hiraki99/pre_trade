# T-REX-CORE
CORE application of T-REX trading system

## Hướng dẫn sử dụng thư viện trading core 

### 1. Đặt lệnh OTC mới:
Lệnh đặt 1 giao dịch OTC mới được truyền dưới dạng json có cấu trúc như sau:
```
orderid1 = uuid.uuid1()
order1 = {
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
}
```
Trong đó:

- MsgType : là 'D' đối với loại message là đặt lệnh mới
- Account: là Account của khách hàng mà từ đó tiền sẽ chuyển đi. Ví dụ: Buy BTC/USDT thì Account là USDT, Sell BTC/USDT thì Account là Account là BTC
- AllocAccount: là Account của khách hàng mà từ đó tiền sẽ chuyển vào. Ví dụ: Buy BTC/USDT => AllocAccount là BTC, Sell BTC/USDT => AllocAccount là USDT
- ClOrdID là số id mà pretrade sinh ra, nếu pretrade chạy thành cụm thì đây là số id do cụm sinh ra. Số này = str(uuid.uuid1())
- OrderQty: khối lượng giao dịch tính bằng số lượng tiền tệ đứng trước trong tỷ giá. Ví dụ BTC/USDT thì khối lượng để chỉ số lượng BTC, ETH/USDT thì khối lượng chỉ lượng ETH
- OrdType: luôn là 'LO' với giao dịch OTC
- Side: là 'Buy' hoặc 'Sell' (lưu ý viết hoa chữ đầu)
- Price: là tỷ giá của 2 đồng tiền. Ví dụ: BTC/USDT = 6000 => BTC = 6000 USDT
- TimeInForce:mặc định là 'GTC'
- SecondaryOrderID: dùng để khớp lệnh trong giao dịch OTC, trong đó lệnh chỉ rõ là sẽ khớp với Order có orderID là bao nhiêu

Quy trình đặt lệnh như sau:
```
# khởi Tạo sổ lệnh. Sổ lệnh sẽ tồn tại trong suốt quá trình trading và được khởi tạo ngay khi application start
# create order book
book_OTC_BTCUSDT = OrderBookOTC(
    'BTC/USDT', 0.000001, report=send_execution_report)
# function send_execution_report là hàm chuyển dữ liệu dạng json ra ngoài. Hàm này có dạng F(Order), trong đó Order là class Order, có thuộc tính execution_report() => trả ra kết quả giao dịch dạng dict. Hàm này sau đó sẽ phân tích kết quả giao dịch và gửi dữ liệu đến client, database...
# Example về send_execution_report:
def send_execution_report(order):
    """Use for test only. Just print result to console
    
    Arguments:
        order {Order} -- [description]
    """

    # send Execution Report to queue of resulting trade
    print('Send Execution Report: %s' % order.execution_report())

# Sau khi nhận dữ liệu từ client => chuyển dữ liệu thành dạng dict => check dữ liệu xem các tài khoản có đủ khả năng thực hiện giao dịch hay không, có valid hay không...

# Sau quá trình check thành công => dtạo đối tượng Order từ dict của python
# Quá trình khởi tạo này đã check tất cả các kiểu và độ dài của dữ liệu
order01 = Order(**order1)
# Qúa trình khởi tạo này cũng đồng thời sinh ra orderID
# quá trình tạo lệnh sai sẽ raise error

# Thử in ra các thông tin trong lệnh mới
pritn(order01.execution_report())

# Add thêm lệnh mới vào sổ lệnh
# add to orderbookOTC
book_OTC_BTCUSDT.add_OTC_order(order01)
# find order => thử tìm Order theo OrderID
res = book_OTC_BTCUSDT.find_order(order01.OrderID)
print('Find order1:', res)
```
Trên đây là cách đặt 1 lệnh chào giá OTC, để thực hiện giao dịch với lệnh này cần 1 lệnh khớp giao dịch

### 2. Đặt lệnh Khớp giao dịch: Khớp 1 lệnh OTC đã quote sẵn trên thị trường

Một lệnh Khớp giao dịch có dạng như sau:

```
order2 = {
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
        'SecondaryOrderID': genOrderID(str(orderid1), '000100010001'),
    }
}
```

Lệnh khớp (order2) có thông tin giao dịch về giá, khối lượng, loại Symbol bằng với order quote (order1), các thông tin còn lại là của Account thực hiện giao dịch order2. Điểm quan trọng ở SecondaryOrderID ko để trống mà điền OrderID của order1

Quá trình truyền và add lệnh vào orderbook như đặt lệnh mới:

```
order02 = Order(**order2)

# add order2 to orderbookOTC
x = book_OTC_BTCUSDT.add_OTC_order(order02)
print('Add order2:', x)
```

Sau khi add vào thì order 2 tự động matching với order 1 đã được chỉ định trong SecondaryOrderID. 2 lệnh sau đó được hàm send_execution_report đẩy dữ liệu ra ngoài. 

Dùng đoạn code sau để show tất cả các lệnh bid-ask sẽ ko tìm thấy 2 lệnh order 1 và 2 nữa:
```
# find all bid and ask order
o1 = book_OTC_BTCUSDT.view_bid_order()
print('View Bid Orders: \n', o1)
o2 = book_OTC_BTCUSDT.view_ask_order()
print('View Ask Orders: \n', o2)
```
Trong trường hợp, lệnh order 2 ko khớp dc với order1 vì bất kỳ lý do gì thì order 2 sẽ trở thành 1 lệnh quote khác như order 1

### 3. Cancel một lệnh đã đặt:

Cú pháp lệnh sau đây để cancel một lệnh:
```
cancel_order_json ={
        'MsgType': 'F',
        'Account': '000100010001',
        'ClOrdID': str(cancel_ClOrdID),
        'OrigClOrdID': str(client_orderid1),
        'Symbol': 'BTC/USDT',
        'OrderID': order1.OrderID
    }
```

Muốn cancel lệnh nào thì cần orderID và ClOrdID của lệnh đó. Sau đó add lệnh này vào như đối với order mới (lưu ý, MsgType là 'F'):
```
cancel_order1 = Order(**cancel_order_json)
res_cancel = book_OTC_BTCUSDT.cancel_order(cancel_order1)
print('Cancel result:', res_cancel)
```
Full example của phần 1,2,3 được để trong thư mực testing. Chạy test bằng cú pháp `python runPreTrade.py --env=test`

### 4. Execution report:

Execution report là tổng hợp các message trả ra từ hàm send_execution_report. Hàm này có thể customize và truyền vào order book ở biến report. Các loại message như sau:

```
Examples:
        my_order_json = [
            # đây là lệnh đặt mới
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
            # lệnh khớp 1 lệnh đã có`
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
                'SecondaryOrderID': genOrderID(str(orderid1), '000100010001'),
            }
        ]
        # loại message trả ra mỗi lần đặt lệnh mới, khớp lệnh hoặc cancel lệnh
        expected_execution_report = {'MsgType': '8', 'Account': '000100010001', 'ClOrdID': 'e2b9f268-8bcc-11e8-a136-f40f24228a51', 'OrderID': 'a4ec3c0d-e308-523c-bb32-6a2002988e75', 'OrigClOrdID': '', 'OrderQty': 1.2, 'LeavesQty': 0.0, 'CumQty': 1.2,'OrdType': 'LO', 'OrdStatus': 'Filled', 'Price': 6000.0, 'Side': 'Buy', 'Symbol': 'BTC/USDT', 'Currency': 'BTC', 'AllocSettlCurrency': 'USDT', 'TimeInForce': 'GTC', 'TransactTime': '2018-07-20 03:27:52.835766', 'Commission': 0.0024, 'AllocAccount': '000100010002', 'SecondaryOrderID': '', 'time_zone': 'GMT +7:00', 'execution_style': 'OTC'}
        loại message trả ra trong trường hợp lệnh khớp, dùng để chuyển tiền
        Transaction = {'MsgType': 'AE', 'TradeReportID': '021edad8-cc42-54dc-847c-ce8b33f1f747', 'Commission': 14.4, 'LastQty': 1.2, 'LastPx': 6000.0, 'TransactTime': '2018-07-20 03:27:52.836594', 'Side': 'Sell', 'Symbol': 'BTC/USDT', 'OrderID': 'f81eb87f-c4eb-5d06-8b11-a4d4a0dffe9d', 'SecondaryOrderID': 'a4ec3c0d-e308-523c-bb32-6a2002988e75', 'Account': '000100020001', 'Currency': 'USDT', 'Quantity': 7200.0, 'AllocAccount': '000100010002', 'AllocSettlCurrency': 'USDT','AllocQty': 7185.6}
```

Giải thích thêm 1 số trường:

- Msgtype: nhận giá trị '8' hoặc 'AE'
- Commission: phí giao dịch, tính trên số tiền của Account và loại tiền quy định trong Currency
- Account: tài khoản chuyển tiền đi
- Currency: Loại tiền của tài khoản đi
- AllocQty: Số lượng tiền chuyển vào tài khoản đích
- AllocSettlCurrency: loại tiền chuyển vào tài khoản đích

Mỗi giao dịch thành công sinh ra 2 transaction report, mỗi lệnh new order, lệnh khớp hay cancel order sinh ra 1 execution report
