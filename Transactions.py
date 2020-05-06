class Transactions:
    def __init__(self, list):
        self.list = list

    def add_transaction(self, transaction):
        self.list.append(transaction)

    def is_transaction_in_list(self, new_transaction):
        for transaction in self.list:
            if transaction.hash == new_transaction.hash:
                return True
        return False

    def to_string(self):
        returned_string = '{"transactions":['
        if self.list:
            for transaction in self.list:
                returned_string += transaction.to_string() + ","
            returned_string = returned_string[:-1] + ']}'
            return returned_string
        else:
            return '{"transactions":[]}'
