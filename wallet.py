from wallet import AIWallet

def setup_wallet():
    # Initialize wallet
    wallet = AIWallet()
    
    try:
        # Create new wallet
        wallet_data = wallet.create_wallet("your_secure_password")
        print("\nWallet created successfully!")
        print(f"Address: {wallet_data['address']}")
        print(f"Public Key: {wallet_data['public_key']}")
        print("\nIMPORTANT: Save these credentials securely!")
        
        # Save wallet address to a config file for easy access
        with open('wallet_config.json', 'w') as f:
            json.dump({
                'wallet_address': wallet_data['address']
            }, f, indent=4)
            
        return wallet_data
        
    except Exception as e:
        print(f"Error creating wallet: {e}")
        return None

if __name__ == "__main__":
    import json
    wallet_data = setup_wallet()
    if wallet_data:
        print("\nWallet setup complete. You can now use this wallet for AI submissions.")