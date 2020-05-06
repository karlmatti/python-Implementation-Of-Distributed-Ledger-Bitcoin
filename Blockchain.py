import json

from Block import Block


class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, "01/01/2020",
                     1)

    def get_latest_block(self):
        return self.chain[len(self.chain) - 1]

    def add_block(self, new_block):
        # new_block.previous_hash = self.get_latest_block().hash
        # new_block.hash = new_block.calculate_hash()
        if new_block.previous_hash == self.get_latest_block().hash:
            self.chain.append(new_block)
            return True
        return False
    def to_string(self):
        returned_string = '{"chain":['

        for block in self.chain:
            returned_string += block.to_string() + ","
        returned_string = returned_string[:-1] + ']}'
        return returned_string

    def to_json(self):
        return json.dumps(self.to_string(), separators=(',', ':'))