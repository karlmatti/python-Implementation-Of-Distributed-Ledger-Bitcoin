class SignedTransactionChain:
    def __init__(self, chain):
        self.chain = chain

    def add_transaction(self, transaction):
        self.chain.append(transaction)

    def is_transaction_in_list(self, new_transaction):
        for transaction in self.chain:
            if transaction.signature == new_transaction.signature:
                return True
        return False

    def to_string(self):
        returned_string = '{"transactions":['
        if self.chain:
            for transaction in self.chain:
                returned_string += transaction.to_string() + ","
            returned_string = returned_string[:-1] + ']}'
            return returned_string
        else:
            return '{"transactions":[]}'

    def chain_to_string(self):
        returned_string = '['
        if self.chain:
            for transaction in self.chain:
                returned_string += transaction.to_string() + ","
            returned_string = returned_string[:-1] + ']'
            return returned_string
        else:
            return '[]'
