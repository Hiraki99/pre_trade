from ..pre_trade.core.trade_model import Order, OrderBookOTC, genOrderID, send_execution_report
import uuid
import json
from microservices_connector.Interservices import timeit
from ..pre_trade.kafka.consumer import Consumer
from ..pre_trade.kafka.producer import Producer

# from .process import data
from configparser import ConfigParser
config = ConfigParser()
config.read('config.env')
from kafka import KafkaConsumer, KafkaProducer

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
            'DisplayName':'thinhphoho01',
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
            'SecondaryOrderID': genOrderID(str(orderid1), '000100010001'),
            'DisplayName':'Thinh KAKA',
            'UserID': 1
        }
    ]

    TOPIC_IN = config["ENV"]["TOPIC_IN"]
    TOPIC_OUT = config["ENV"]["TOPIC_OUT"]
    print("--------------Order1----------------")
    
    # producer = KafkaProducer(bootstrap_servers='54.169.58.227:9092')

    
    print("Done")
    consumer = Consumer()
    consumer.run(TOPIC_IN)
if __name__ == '__main__':
    main()
