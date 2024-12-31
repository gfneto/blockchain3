import time
import json
from hashlib import sha256
import numpy as np
from sklearn.linear_model import LinearRegression

class Blockchain:
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = {
            'index': 0,
            'timestamp': time.time(),
            'transactions': [],
            'ai_solution': None,
            'previous_hash': '0',
            'hash': '',
        }
        genesis_block['hash'] = self.calculate_hash(genesis_block)
        self.chain.append(genesis_block)

    def create_block(self, ai_solution):
        if not self.transactions:
            return None
        last_block = self.chain[-1]
        block = {
            'index': len(self.chain),
            'timestamp': time.time(),
            'transactions': self.transactions,
            'ai_solution': ai_solution,
            'previous_hash': last_block['hash'],
            'hash': ''
        }
        block['hash'] = self.calculate_hash(block)
        self.chain.append(block)
        self.transactions = []  # Clear transactions after block creation
        return block

    @staticmethod
    def calculate_hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return sha256(block_string).hexdigest()

    def add_transaction(self, transaction):
        self.transactions.append(transaction)

    def is_valid_chain(self, chain):
        for i in range(1, len(chain)):
            current = chain[i]
            previous = chain[i - 1]
            if current['previous_hash'] != previous['hash']:
                return False
            if current['hash'] != self.calculate_hash(current):
                return False
        return True

    def replace_chain(self, chain):
        if len(chain) > len(self.chain) and self.is_valid_chain(chain):
            self.chain = chain

    def generate_ai_task(self):
        """
        Generates a random AI task involving linear regression.
        Returns a dictionary with the task data and target values.
        """
        X = np.random.rand(10, 2)  # 10 samples, 2 features
        coefficients = np.random.rand(2)
        y = X @ coefficients + np.random.normal(scale=0.1, size=10)  # Add noise
        return {'data': X.tolist(), 'target': y.tolist(), 'coefficients': coefficients.tolist()}

    def verify_ai_work(self, ai_task, ai_solution):
        """
        Verifies the AI solution by comparing the solution coefficients with the expected coefficients.
        """
        model = LinearRegression()
        X, y = np.array(ai_task['data']), np.array(ai_task['target'])
        model.fit(X, y)
        
        # Print AI solution vs model coefficients for debugging
        print(f"Expected coefficients: {ai_task['coefficients']}")
        print(f"AI solution coefficients: {ai_solution['coefficients']}")
        
        # Check if the coefficients are close enough
        return np.allclose(model.coef_, ai_solution['coefficients'], atol=0.05)  # Increased tolerance for debugging

    def add_block_with_ai_work(self, ai_task, ai_solution):
        """
        Attempts to add a block with the AI work solution if it is verified.
        """
        if self.verify_ai_work(ai_task, ai_solution):
            print("AI work verified successfully.")
            return self.create_block(ai_solution)
        else:
            print("AI work verification failed.")
            return None

