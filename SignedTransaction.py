from TransactionV2 import TransactionV2
import hashlib

class SignedTransaction:
    def __init__(self, signature, transaction):
        self.transaction = transaction
        self.signature = signature

    def calculate_hash(self):
        return hashlib.sha256(self.to_string().encode('utf-8')).hexdigest()
    def to_string(self):
        return '{"signature": "' + self.signature + '",' + \
               '"transaction": ' + self.transaction.to_string() + \
               '}'
