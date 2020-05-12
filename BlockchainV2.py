import json

from BlockV2 import BlockV2
from SignedTransaction import SignedTransaction
from SignedTransactionChain import SignedTransactionChain
from TransactionV2 import TransactionV2
from datetime import datetime


class Blockchain:
    def __init__(self):
        self.chain = [[self.create_genesis_block()]]

    def create_genesis_block(self):
        genesis_transaction = TransactionV2("System",
                                            "Satoshi Nakamoto",
                                            50,
                                            "01/01/2009")
        genesis_signed_transaction = SignedTransaction("System", genesis_transaction)
        genesis_signed_transaction_chain = SignedTransactionChain([])
        genesis_signed_transaction_chain.add_transaction(genesis_signed_transaction)
        return BlockV2(0, "01/01/2009", "VDEODFTZ041jHIZuIyEY", "Satoshi Nakamoto", genesis_signed_transaction_chain)

    def get_latest_block(self):
        latest_blocks = self.chain[len(self.chain) - 1]
        nr_of_transactions = 0
        result_block = self.create_genesis_block()
        for latest_block in latest_blocks:
            if len(latest_block.transactions.chain) > nr_of_transactions:
                result_block = latest_block
            nr_of_transactions = len(latest_block.transactions.chain)

        blocks_with_the_most_trans = []
        for latest_block in latest_blocks:
            if len(latest_block.transactions.chain) == len(result_block.transactions.chain):
                blocks_with_the_most_trans.append(latest_block)

        if len(blocks_with_the_most_trans) == 1:
            return blocks_with_the_most_trans[0]

        for block_with_the_most_trans in blocks_with_the_most_trans:
            if datetime.fromisoformat(block_with_the_most_trans.timestamp) > \
                    datetime.fromisoformat(result_block.timestamp):
                result_block = block_with_the_most_trans

        return result_block

    def is_connected_to_previous(self, new_block):
        previous_index = new_block.nr - 1

        for previous_block in self.chain[previous_index]:
            if previous_block.hash == new_block.previous_hash:
                return True
        return False

    def is_not_duplicate_transaction(self, signed_transactions, added_transaction):

        if not signed_transactions:
            return True
        for current_transaction in signed_transactions:

            if added_transaction.signature == current_transaction.signature:
                return False
        return True

    def has_enough_funds(self, public_key, money):
        received_money = 0
        sent_money = 0
        received_transactions = []
        sent_transactions = []

        level = 0
        for level_blocks in range(len(self.chain)):
            print("Level:", level)
            level += 1
            for block in self.chain[level_blocks]:
                for signed_transaction in block.transactions.chain:
                    print("Pk: %s, trn_from: %s, trn_to: %s, sum: %d" % (
                        public_key, signed_transaction.transaction.trn_from, signed_transaction.transaction.trn_to,
                        signed_transaction.transaction.trn_sum))

                    if signed_transaction.transaction.trn_from == public_key and self.is_not_duplicate_transaction(
                            sent_transactions,
                            signed_transaction):
                        sent_transactions.append(signed_transaction)
                        sent_money += signed_transaction.transaction.trn_sum
                    if signed_transaction.transaction.trn_to == public_key and self.is_not_duplicate_transaction(
                            received_transactions,
                            signed_transaction):
                        received_money += signed_transaction.transaction.trn_sum
                        received_transactions.append(signed_transaction)

        total_money = received_money - sent_money
        print("received money:", received_money)
        print("sent money:", sent_money)

        if total_money >= money:
            return True
        else:
            return False

    def add_block(self, new_block):
        # new_block.previous_hash = self.get_latest_block().hash
        # new_block.hash = new_block.calculate_hash()
        #print("add_block - new_block.nr", new_block.nr)
        #print("add_block - len(self.chain)", len(self.chain))

        if new_block.nr == len(self.chain):
            if self.is_connected_to_previous(
                    new_block):  # kui lisatakse blokk, mis on madalamal levelil kui praegune chain
                self.chain.append([new_block])
                return True
        elif len(self.chain) > new_block.nr > 0:  # kui lisatakse blokk ja ei pea tegema uut levelit selle jaoks

            if self.is_connected_to_previous(new_block):
                self.chain[new_block.nr].append(new_block)

                return True
        return False

    def add_mined_block(self, new_block):
        pass

    def to_string(self):
        returned_string = '{"chain":['

        for block_levels in self.chain:
            returned_string += '['
            for block in block_levels:
                returned_string += block.to_string() + ","
            returned_string = returned_string[:-1] + '],'
        returned_string = returned_string[:-1] + ']}'
        return returned_string

    def to_json(self):
        return json.dumps(self.to_string(), separators=(',', ':'))






