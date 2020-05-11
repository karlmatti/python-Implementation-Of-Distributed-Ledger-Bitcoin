import hashlib
from hashlib import *


class BlockV2:
    def __init__(self, nr, timestamp, nonce, creator, transactions, previous_hash=""):
        self.nr = nr
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.nonce = nonce
        self.creator = creator
        self.transactions = transactions
        self.count = len(transactions.chain)
        self.merkle_root = self.calculate_merkle_root()
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        unhashed_string = '{"nr": %d,' \
                          '"previous_hash": "%s",' \
                          '"timestamp": "%s",' \
                          '"nonce": "%s",' \
                          '"creator": "%s",' \
                          '"merkle_root": "%s",' \
                          '"count": %d,' \
                          '"transactions": %s}' % (
            self.nr, self.previous_hash, self.timestamp,
            self.nonce, self.creator,
            self.merkle_root, self.count, self.transactions.chain_to_string())

        return hashlib.sha256(unhashed_string.encode('ascii')).hexdigest()

    def calculate_merkle_root(self):

        old_hash_list = []
        for transaction in self.transactions.chain:
            old_hash_list.append(transaction.calculate_hash())
        if len(old_hash_list) % 2 != 0:
            old_hash_list.append(old_hash_list[-1])

        iteration_counter = 1
        while (len(old_hash_list) > 1):
            # we run the loop till we don't get a single hash
            j = 0
            for i in range(0, len(old_hash_list) - 1):

                old_hash_list[j] = sha256(str(old_hash_list[i] + old_hash_list[i + 1]).encode('ascii')).hexdigest()
                # hash of the i th leaf and i + 1 th leaf are concatenated
                # to find the hash parent to the both

                i += 2
                j += 1

            lastDelete = i - j;
            iteration_counter +=1
            del old_hash_list[-lastDelete:];
        return old_hash_list

        # as we now have the hash to the upper level of the tree, we delete the extra space in the array.
        # in each iteration of this loop the size of the storeHash list is halved.


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
