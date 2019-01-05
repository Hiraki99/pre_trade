from ..pre_trade.core.trade_model import Order, OrderBookOTC, genOrderID, send_execution_report
import uuid
import json
from microservices_connector.Interservices import timeit
from ..pre_trade.kafka.consumer import Consumer
from ..pre_trade.kafka.producer import Producer
import requests
# from .process import data
from configparser import ConfigParser
config = ConfigParser()
config.read('config.env')
from kafka import KafkaConsumer, KafkaProducer
from ..initdb import db_session
from ..pre_trade.models import ExecutionReport, TransactionTrading, User
from ..pre_trade.process import getCancelOrder
from ..pre_trade.process import checkBalanceAccountDB
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
            'OrderQty': 100000,
            'OrdType': 'LO',
            'Price': 0.0656,
            'Side': 'Buy',  # buy
            'Symbol': 'ETH/BTC',
            'AllocAccount': '000100010002',
            'TimeInForce': 'GTC',
            'SecondaryOrderID': '',
            'DisplayName': 'Thinh KAKA',
            'userID': 1
        },
        {
            'MsgType': 'D',
            'Account': '000100020001',
            'ClOrdID': str(orderid2),
            'OrderQty': 1.2999,
            'OrdType': 'LO',
            'Price': 1.33,
            'Side': 'Sell',  # sell
            'Symbol': 'ETH/BTC',
            'AllocAccount': '000100020002',
            'TimeInForce': 'GTC',
            'SecondaryOrderID': genOrderID(str(orderid1), '000100010001'),
            'DisplayName': 'Thinh KAKA',
            'UserID': 1
        }
    ]

    # tạo đối tượng Order từ dict của python
    # Quá trình khởi tạo này đã check tất cả các kiểu và độ dài của dữ liệu
    TOPIC_IN = config["ENV"]["TOPIC_IN"]
    TOPIC_OUT = config["ENV"]["TOPIC_OUT"]
    # for i in range(10):
    print("--------------Order----------------")
    print(checkBalanceAccountDB(my_order_json[0]))

    my_order_json[1]['ClOrdID'] = str(uuid.uuid1())
    order01 = Order(**my_order_json[0])
    order01.OrdStatus = 'New'
    order01.ExecStyle = 'ECN'
    # if(checkBalanceAccountDB(my_order_json[1])):
    #     print(json.dumps(order01.to_dict()).encode("utf-8"))
    #     producer = Producer(kwargs={"topic":TOPIC_IN , "message" : bytes(json.dumps(order01.to_dict()).encode("utf-8"))})
    #     producer.start()
    # else:
    
    
    result = requests.get("http://localhost:3000/books?pair=ETH/BTC")
    
    data = result.json()
    bid = data["Bid"]

    ask = data["Ask"]
    with db_session() as session:
        if(ask != None):
            for item in ask:
                user = session.query(User).filter(
                    User.id == int(item["UserID"])).first()
                item["DisplayName"] = user.username
        else:
            ask = []
        if(bid != None):
            for item in bid:
                user = session.query(User).filter(
                    User.id == int(item["UserID"])).first()
                item["DisplayName"] = user.username
        else:
            bid = []

    print("------------------SHOW BID---------------")
    print(bid)
    # print("------------------SHOW ASK---------------")
    # print(ask)


if __name__ == '__main__':
    main()
