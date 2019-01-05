import traceback
import json
import redis

# Redis configuration
myredis = redis.StrictRedis(host='localhost', port=6379, db=4)
# print("redis = ",myredis.st)

class MyRedis:
    def __init__(self, arg, default={}):
        self.name = arg
        try:
            self.value = self.query()
        except:
            self.value = default
            self.commit()

    def commit(self):
        json_value = json.dumps(self.value)
        myredis.set(self.name, json_value)

    def update(self, new_value):
        self.value = new_value
        self.commit()

    def query(self):
        self.value = json.loads(myredis.get(self.name).decode('utf-8'))
        return self.value
    
    def getKeyName(self):
        return self.name

    def __str__(self):
        return repr(self) + self.name




