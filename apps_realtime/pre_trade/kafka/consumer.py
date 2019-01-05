#!/usr/bin/env python
import threading
import logging
import time
import multiprocessing
import traceback
from kafka import KafkaConsumer, KafkaProducer
from ..response import send_execution_report
# from ..socket_pre_trade import socketio
from configparser import ConfigParser
import json
config = ConfigParser()
config.read('config.env')
TOPIC_OUT = config["ENV"]["TOPIC_OUT"]
TOPIC_IN = config["ENV"]["TOPIC_IN"]
from socketIO_client import SocketIO, LoggingNamespace,BaseNamespace

class MainNamespace(BaseNamespace):
    def client(self, *args):
        print('client', args)

def create_socket_client():
    socketPreTrade = SocketIO(config["pre_trade"]["host"], config["pre_trade"]["port"])
    socketclient = socketPreTrade.define(MainNamespace, '/pre_trade/order')
    return socketclient
socketclient = create_socket_client()
class Consumer(multiprocessing.Process):
    def __init__(self,**kwargs):
        multiprocessing.Process.__init__(self,**kwargs)
        self.stop_event = multiprocessing.Event()
    def stop(self):
        self.stop_event.set()

    def run(self):
        consumer = KafkaConsumer(bootstrap_servers=config["ENV"]["server"],
                                 auto_offset_reset='latest',
                                 consumer_timeout_ms=1000)
        consumer.subscribe([self._kwargs['topic']])
        while not self.stop_event.is_set():    
            i=0
            for message in consumer:
                # socketio.start_background_task(target = )
                
                report, order = send_execution_report(json.loads(message.value.decode('utf-8')))
                send_quest(report,order)
                i = i+1
                if self.stop_event.is_set():
                    break
            print("number message %d" %i)
        consumer.close()
        print("Done Consumer Order To Kafka")
def send_quest(report, order):
    try:
        if(report is None or order is None or report['MsgType'] == "AE"):
            return
        if(report['OrdStatus']!='Canceled'):
            if(order["SecondaryOrderID"]==""):
                socketclient.emit("update-order-realtime",{'status':1,'type':'order', 'message':"Order is completed","order":report})
        else:
            socketclient.emit("update-order-realtime",{'status':1,'type':'cancel', 'message':"Order cancel is completed","order":report})      
        print("send Success")
    except:
        traceback.print_exc()
        pass
    
def main():
    consumer = Consumer(kwargs={"topic":TOPIC_OUT})
    consumer.start()

if __name__ == "__main__":
    
    logging.basicConfig(
        format='%(asctime)s.%(msecs)s:%(name)s:%(thread)d:%(levelname)s:%(process)d:%(message)s',
        level=logging.INFO
    )
    main()
    
