import os
import json
from eth_account import Account
from eth_keys import keys
from eth_utils import to_checksum_address
from typing import Dict, Optional

class AIWallet:
    def __init__(self, keystore_path: str = "wallets"):
        """Initialize wallet with path to keystore"""
        self.keystore_path = keystore_path
        os.makedirs(keystore_path, exist_ok=True)
        self.current_wallet: Optional[Dict] = None

    def create_wallet(self, password: str) -> Dict:
        """Create a new wallet with the given password"""
        # Generate a new private key
        acct = Account.create()
        
        # Create wallet info
        wallet_data = {
            'address': acct.address,
            'private_key': acct.key.hex(),  # Encrypted in actual implementation
            'public_key': keys.private_key_to_public_key(acct.key).to_hex()
        }
        
        # Save wallet to keystore
        wallet_file = os.path.join(self.keystore_path, f"wallet_{acct.address}.json")
        with open(wallet_file, 'w') as f:
            json.dump(wallet_data, f)
        
        self.current_wallet = wallet_data
        return wallet_data

    def load_wallet(self, address: str, password: str) -> Dict:
        """Load an existing wallet by address"""
        wallet_file = os.path.join(self.keystore_path, f"wallet_{address}.json")
        
        try:
            with open(wallet_file, 'r') as f:
                wallet_data = json.load(f)
            
            # In real implementation, decrypt private key with password
            self.current_wallet = wallet_data
            return wallet_data
            
        except FileNotFoundError:
            raise ValueError(f"No wallet found for address {address}")

    def get_balance(self, address: str = None) -> float:
        """Get wallet balance from blockchain"""
        if address is None and self.current_wallet:
            address = self.current_wallet['address']
        elif address is None:
            raise ValueError("No wallet loaded and no address provided")

        # Here you would actually query the blockchain
        # For now, return dummy balance
        return 0.0

    def sign_transaction(self, transaction_data: Dict) -> str:
        """Sign a transaction with the current wallet's private key"""
        if not self.current_wallet:
            raise ValueError("No wallet loaded")

        # Here you would actually sign the transaction
        # For demonstration, just return the transaction data
        return f"Signed_{transaction_data}"

    def submit_ai_code(self, code: str, dataset: Optional[str] = None) -> Dict:
        """Submit AI code to the blockchain using the current wallet"""
        if not self.current_wallet:
            raise ValueError("No wallet loaded")

        from ai_tasks import submit_to_blockchain
        
        result = submit_to_blockchain(
            wallet_address=self.current_wallet['address'],
            code=code,
            dataset=dataset
        )
        
        return result

    def get_submission_status(self, submission_hash: str) -> Dict:
        """Get status of an AI submission"""
        if not self.current_wallet:
            raise ValueError("No wallet loaded")

        from ai_tasks import get_submission_status
        return get_submission_status(submission_hash)

    @staticmethod
    def validate_address(address: str) -> bool:
        """Validate an Ethereum address"""
        try:
            to_checksum_address(address)
            return True
        except:
            return False 