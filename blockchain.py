import hashlib
import json
import time
from typing import Dict, List, Optional
import numpy as np
from sklearn.linear_model import LinearRegression

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()
        self.create_genesis_block()
        self.mining_reward = 10  # Reward for successful AI work

    def create_genesis_block(self):
        """Create the genesis block"""
        self.mine_block(miner_address="0", is_genesis=True)

    def proof_of_ai_work(self, ai_task: Dict, ai_solution: Dict) -> bool:
        """
        Verify AI work as proof instead of traditional PoW
        Returns True if the AI solution meets accuracy requirements
        """
        try:
            # Verify that solution matches expected coefficients
            expected_coeffs = np.array(ai_task['coefficients'])
            solution_coeffs = np.array(ai_solution['coefficients'])
            
            # Check if the solution is within acceptable error margin
            is_valid = np.allclose(expected_coeffs, solution_coeffs, rtol=0.1, atol=0.1)
            
            return is_valid
        except Exception as e:
            print(f"Error in proof_of_ai_work: {e}")
            return False

    def mine_block(self, miner_address: str, ai_task: Optional[Dict] = None, 
                  ai_solution: Optional[Dict] = None, is_genesis: bool = False) -> Dict:
        """
        Create a new block using AI work as proof
        """
        block = {
            'index': len(self.chain),
            'timestamp': time.time(),
            'transactions': self.current_transactions,
            'previous_hash': self.get_last_block()['hash'] if self.chain else None,
            'miner': miner_address,
            'ai_task': ai_task,
            'ai_solution': ai_solution,
            'is_genesis': is_genesis
        }

        # For genesis block or when no AI task is provided
        if is_genesis or not ai_task:
            block['hash'] = self.calculate_hash(block)
            self.chain.append(block)
            self.current_transactions = []
            return block

        # Verify AI work
        if self.proof_of_ai_work(ai_task, ai_solution):
            # Calculate block hash
            block['hash'] = self.calculate_hash(block)
            
            # Add block to chain
            self.chain.append(block)
            
            # Clear current transactions
            self.current_transactions = []
            
            # Reward the miner
            self.new_transaction(
                sender="0",
                recipient=miner_address,
                amount=self.mining_reward
            )
            
            return block
        else:
            raise ValueError("AI solution verification failed")

    def calculate_hash(self, block: Dict) -> str:
        """Calculate hash of the block"""
        # Remove hash from block if it exists to calculate new hash
        block_copy = block.copy()
        block_copy.pop('hash', None)
        block_string = json.dumps(block_copy, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def new_transaction(self, sender: str, recipient: str, amount: float) -> int:
        """Add a new transaction to the list of transactions"""
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
            'timestamp': time.time()
        })
        return self.get_last_block()['index'] + 1 if self.chain else 0

    def get_last_block(self) -> Dict:
        """Return the last block in the chain"""
        return self.chain[-1]

    def register_node(self, address: str):
        """Add a new node to the set of nodes"""
        self.nodes.add(address)

    def validate_chain(self, chain: List[Dict]) -> bool:
        """Check if a blockchain is valid"""
        for i in range(1, len(chain)):
            current = chain[i]
            previous = chain[i-1]

            # Check hash integrity
            if current['previous_hash'] != previous['hash']:
                return False

            # Skip AI verification for genesis block
            if current['is_genesis']:
                continue

            # Verify AI work for non-genesis blocks with AI tasks
            if current['ai_task'] and current['ai_solution']:
                if not self.proof_of_ai_work(current['ai_task'], current['ai_solution']):
                    return False

        return True

    def submit_ai_task(self, wallet_address: str, code: str, dataset: str) -> Dict:
        """Submit a new AI task to the blockchain"""
        task = {
            'code': code,
            'dataset': dataset,
            'timestamp': time.time(),
            'submitter': wallet_address
        }
        
        self.new_transaction(
            sender=wallet_address,
            recipient="0",  # System address
            amount=0  # Task submission might have a cost in the future
        )
        
        return task

