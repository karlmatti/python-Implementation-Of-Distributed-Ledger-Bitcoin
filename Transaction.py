import hashlib
import json


class Transaction:
    def __init__(self, index, timestamp, data):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        unhashed_string = str(self.index) + \
                          self.timestamp + json.dumps(self.data, separators=(',', ':'))
        return hashlib.sha256(unhashed_string.encode('utf-8')).hexdigest()

    def to_string(self):
        return '{"index": ' + str(self.index) + ',' + \
               '"timestamp": "' + self.timestamp + '",' + \
               '"data": ' + json.dumps(self.data, separators=(',', ':')) + ',' + \
               '"hash": "' + self.hash + \
               '"}'
