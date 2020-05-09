from TransactionV2 import TransactionV2


class SignedTransaction:
    def __init__(self, signature, transaction):
        self.transaction = transaction
        self.signature = signature

    def to_string(self):
        return '{"signature": "' + self.signature + '",' + \
               '"transaction": ' + self.transaction.to_string() + \
               '}'
