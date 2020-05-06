import hashlib

class Block:
    def __init__(self, index, timestamp, data, previous_hash=""):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        unhashed_string = str(self.index) + self.previous_hash + \
                          self.timestamp + str(self.data)
        return hashlib.sha256(unhashed_string.encode('utf-8')).hexdigest()

    def to_string(self):
        return '{"index": ' + str(self.index) + ',' + \
               '"previous hash": "' + self.previous_hash + '",' + \
               '"timestamp": "' + self.timestamp + '",' + \
               '"data": ' + str(self.data) + ',' + \
               '"hash": "' + self.hash + \
               '"}'