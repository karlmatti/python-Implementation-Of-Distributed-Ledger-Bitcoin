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

    def add_block(self, new_block):
        # new_block.previous_hash = self.get_latest_block().hash
        # new_block.hash = new_block.calculate_hash()
        if new_block.nr == len(self.chain):
            if self.is_connected_to_previous(new_block):
                self.chain.append([new_block])
                return True
        elif new_block.nr < len(self.chain):
            if self.is_connected_to_previous(new_block):
                self.chain[new_block.nr].append(new_block)
                return True
        return False

    def add_mined_block(self, new_block):
        pass

    def to_string(self):
        returned_string = '{"chain":['

        for block in self.chain:
            returned_string += block.to_string() + ","
        returned_string = returned_string[:-1] + ']}'
        return returned_string

    def to_json(self):
        return json.dumps(self.to_string(), separators=(',', ':'))
