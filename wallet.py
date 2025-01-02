import hashlib
import json
import os
from ecdsa import SigningKey, VerifyingKey, SECP256k1
from blockchain import Blockchain
from typing import Dict, Optional
import time

class Wallet:
    def __init__(self):
        """Initialize the wallet with a new private/public key pair."""
        self.private_key = SigningKey.generate(curve=SECP256k1)
        self.public_key = self.private_key.get_verifying_key()
        self.address = self.generate_address()
        self.keystore_path = "wallets"
        os.makedirs(self.keystore_path, exist_ok=True)

    def generate_address(self):
        """Generate a unique wallet address from the public key."""
        public_key_bytes = self.public_key.to_string()
        return hashlib.sha256(public_key_bytes).hexdigest()

    def sign_transaction(self, transaction):
        """Sign a transaction with the private key."""
        transaction_data = json.dumps(transaction, sort_keys=True).encode()
        signature = self.private_key.sign(transaction_data)
        return signature

    def verify_signature(self, transaction, signature):
        """Verify a transaction signature using the public key."""
        transaction_data = json.dumps(transaction, sort_keys=True).encode()
        try:
            self.public_key.verify(signature, transaction_data)
            return True
        except:
            return False

    def save_wallet(self, password: str) -> Dict:
        """Save wallet to keystore"""
        wallet_data = {
            'address': self.address,
            'public_key': self.public_key.to_string().hex(),
            'created_at': int(time.time())
        }
        
        wallet_file = os.path.join(self.keystore_path, f"wallet_{self.address}.json")
        with open(wallet_file, 'w') as f:
            json.dump(wallet_data, f, indent=4)
        
        return wallet_data

    def submit_ai_code(self, code: str, dataset: Optional[str] = None) -> Dict:
        """Submit AI code to the blockchain using this wallet"""
        from ai_tasks import submit_to_blockchain
        
        result = submit_to_blockchain(
            wallet_address=self.address,
            code=code,
            dataset=dataset
        )
        
        return result

    def get_submission_status(self, submission_hash: str) -> Dict:
        """Get status of an AI submission"""
        from ai_tasks import get_submission_status
        return get_submission_status(submission_hash)

    def submit_ml_task(self, dataset_path, code_path):
        """Submit a dataset and a Python code file for machine learning processing."""
        if not os.path.exists(dataset_path):
            print(f"Dataset file not found: {dataset_path}")
            return

        if not os.path.exists(code_path):
            print(f"Code file not found: {code_path}")
            return

        # Read the files
        with open(dataset_path, 'r') as f:
            dataset = f.read()
        with open(code_path, 'r') as f:
            code = f.read()

        # Submit to blockchain
        result = self.submit_ai_code(code, dataset)
        print(f"ML Task submitted to blockchain: {result}")
        return result

def cli():
    wallet = None

    while True:
        print("\nWallet CLI")
        print("1. Create Wallet")
        print("2. Send Transaction")
        print("3. Receive")
        print("4. Submit ML Task")
        print("5. Check ML Task Status")
        print("6. Quit")
        choice = input("Choose an option: ")

        if choice == "1":
            wallet = Wallet()
            wallet.save_wallet("password")  # In production, get password from user
            print(f"Wallet created! Address: {wallet.address}")

        elif choice == "2":
            if not wallet:
                print("No wallet found. Please create a wallet first.")
                continue

            receiver = input("Enter receiver address: ")
            amount = input("Enter amount to send: ")
            transaction = {
                "sender": wallet.address,
                "receiver": receiver,
                "amount": float(amount)
            }
            signature = wallet.sign_transaction(transaction)
            print("Transaction signed!")
            print(f"Transaction: {transaction}")
            print(f"Signature: {signature.hex()}")

        elif choice == "3":
            if not wallet:
                print("No wallet found. Please create a wallet first.")
                continue
            print(f"Your wallet address: {wallet.address}")

        elif choice == "4":
            if not wallet:
                print("No wallet found. Please create a wallet first.")
                continue
            dataset_path = input("Enter the path to the dataset: ")
            code_path = input("Enter the path to the Python code: ")
            wallet.submit_ml_task(dataset_path, code_path)

        elif choice == "5":
            if not wallet:
                print("No wallet found. Please create a wallet first.")
                continue
            submission_hash = input("Enter submission hash: ")
            status = wallet.get_submission_status(submission_hash)
            print(f"Submission status: {status}")

        elif choice == "6":
            print("Exiting Wallet CLI. Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    cli()
