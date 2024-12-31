import hashlib
import time
import random

class Block:
    def __init__(self, index, previous_hash, timestamp, data, validator):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.validator = validator
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = f"{self.index}{self.previous_hash}{self.timestamp}{self.data}{self.validator}"
        return hashlib.sha256(block_string.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.stakeholders = {}

    def create_genesis_block(self):
        return Block(0, "0", time.time(), "Genesis Block", "System")

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, new_block):
        new_block.previous_hash = self.get_latest_block().hash
        new_block.hash = new_block.calculate_hash()
        self.chain.append(new_block)

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            if current_block.hash != current_block.calculate_hash():
                return False

            if current_block.previous_hash != previous_block.hash:
                return False

        return True

    def add_stakeholder(self, address, amount):
        if address in self.stakeholders:
            self.stakeholders[address] += amount
        else:
            self.stakeholders[address] = amount

    def choose_validator(self):
        total_stake = sum(self.stakeholders.values())
        rand = random.uniform(0, total_stake)
        cumulative_stake = 0
        for stakeholder, stake in self.stakeholders.items():
            cumulative_stake += stake
            if rand < cumulative_stake:
                return stakeholder

    def create_block(self, data):
        validator = self.choose_validator()
        new_block = Block(len(self.chain), self.get_latest_block().hash, time.time(), data, validator)
        self.add_block(new_block)
        return new_block

# Example usage
blockchain = Blockchain()
blockchain.add_stakeholder("Validator1", 100)
blockchain.add_stakeholder("Validator2", 50)

# Create a new block
blockchain.create_block("Some transaction data")
