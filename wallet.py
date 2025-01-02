import hashlib
import json
import os
from ecdsa import SigningKey, VerifyingKey, SECP256k1
from blockchain import Blockchain

class Wallet:
    def __init__(self):
        """Initialize the wallet with a new private/public key pair."""
        self.private_key = SigningKey.generate(curve=SECP256k1)
        self.public_key = self.private_key.get_verifying_key()
        self.address = self.generate_address()

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

def submit_ml_task(dataset_path, code_path):
    """Submit a dataset and a Python code file for machine learning processing."""
    if not os.path.exists(dataset_path):
        print(f"Dataset file not found: {dataset_path}")
        return

    if not os.path.exists(code_path):
        print(f"Code file not found: {code_path}")
        return

    print(f"Submitting ML Task:\nDataset: {dataset_path}\nCode: {code_path}")
    # Here you could implement additional logic to execute the code or interact with other systems.
    # For example, you could run the Python script with the dataset using subprocess.

def cli():
    wallet = None

    while True:
        print("\nWallet CLI")
        print("1. Create Wallet")
        print("2. Send Transaction")
        print("3. Receive")
        print("4. Submit ML Task")
        print("5. Quit")
        choice = input("Choose an option: ")

        if choice == "1":
            wallet = Wallet()
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
            dataset_path = input("Enter the path to the dataset: ")
            code_path = input("Enter the path to the Python code: ")
            submit_ml_task(dataset_path, code_path)

        elif choice == "5":
            print("Exiting Wallet CLI. Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    cli()
