import hashlib


class TransactionV2:
    def __init__(self, trn_from, trn_to, trn_sum, trn_timestamp):
        self.trn_from = trn_from
        self.trn_to = trn_to
        self.trn_sum = trn_sum
        self.trn_timestamp = trn_timestamp

    def calculate_hash(self):
        return hashlib.sha256(self.to_string().encode('utf-8')).hexdigest()

    def to_string(self):
        return '{"from": "' + self.trn_from + '",' + \
               '"to": "' + self.trn_to + '",' + \
               '"sum": ' + str(self.trn_sum) + ',' + \
               '"timestamp": "' + self.trn_timestamp + \
               '"}'
