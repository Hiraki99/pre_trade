import threading
import logging
import time
import multiprocessing

from kafka import KafkaConsumer, KafkaProducer
from ..response import send_execution_report
from configparser import ConfigParser
import json
config = ConfigParser()
config.read('config.env')
TOPIC_OUT = config["ENV"]["TOPIC_OUT"]

class Producer(threading.Thread):
    def __init__(self,**kwargs):
        threading.Thread.__init__(self,**kwargs)
        self.stop_event = threading.Event()
    def stop(self):
        self.stop_event.set()

    def run(self):
        
        producer = KafkaProducer(bootstrap_servers=config["ENV"]["server"])
        
        producer.send(self._kwargs['topic'], self._kwargs['message'] )    
        print("Send success")
        producer.close()