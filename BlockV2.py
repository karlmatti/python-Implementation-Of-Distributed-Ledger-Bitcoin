import hashlib


class BlockV2:
    def __init__(self, nr, timestamp, nonce, hash, creator, merkle_root, transactions, previous_hash=""):
        self.nr = nr
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.nonce = nonce
        self.hash = self.calculate_hash()
        self.creator = creator
        self.merkle_root = merkle_root
        self.transactions = transactions
        self.count = len(transactions)

    def calculate_hash(self):
        unhashed_string = '{"nr": {0},' \
                          '"previous_hash": "{1}",' \
                          '"timestamp": "{2}",' \
                          '"nonce": "{3}",' \
                          '"creator": "{4}",' \
                          '"merkle_root": "{5}",' \
                          '"count": {6},' \
                          '"transactions": {7}}'.format(
            self.nr, self.previous_hash, self.timestamp,
            self.nonce, self.creator,
            self.merkle_root, self.count, self.transactions
        )
        return hashlib.sha256(unhashed_string.encode('ascii')).hexdigest()
    def calculate_merkle_root(self):
        leafCount = self.count # 10
        leafs = self.transactions

        old_hash_list = []
        for transaction in self.transactions:
            old_hash_list.append(transaction.calculate_hash())
        while leafCount != 1:
            new_hash_list = []
            #  TODO: calculate merkle root 


    def to_string(self):
        return '{"nr": {0},' \
               '"previous_hash": "{1}",' \
               '"timestamp": "{2}",' \
               '"nonce": "{3}",' \
               '"hash": "{4}",' \
               '"creator": "{5}",' \
               '"merkle_root": "{6}",' \
               '"count": {7},' \
               '"transactions": {8}}'.format(
            self.nr, self.previous_hash, self.timestamp,
            self.nonce, self.hash, self.creator,
            self.merkle_root, self.count, self.transactions
        )
