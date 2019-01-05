import threading, time,json
from kafka import KafkaProducer

class Producer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()
        
    def stop(self):
        self.stop_event.set()

    def run(self, data):
        producer = KafkaProducer(bootstrap_servers='54.169.58.227:9094')
        print("producer: ",data)
        producer.send('trade-event-in',  bytearray(data, "utf8"))
        producer.close()

def run_producer(data):
    Producer().run(data)
    