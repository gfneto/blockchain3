import argparse
import threading
import time
from blockchain import Blockchain
from node import Node
from flask import Flask, request, jsonify
from wallet import Wallet
from ai_tasks import perform_ai_work, verify_ai_work
import requests
import json
import sys
import os

# Add the current directory to Python path if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import wallet after ensuring path is correct
from wallet import Wallet

# Flask App Setup
app = Flask(__name__)
blockchain = Blockchain()
wallet = Wallet()

# Save wallet data
wallet_data = wallet.save_wallet("your_password")
print(f"Using wallet address: {wallet.address}")

def create_and_submit_block_loop(blockchain, wallet):
    """Background task to create and submit blocks"""
    while True:
        try:
            # Get AI task and perform work
            ai_task = {
                'code': """
                def predict(X):
                    return X.mean()
                """,
                'dataset': 'sample_data.csv',
                'coefficients': [0.31479989701085853, 0.19944146798778906]
            }
            
            # Perform AI work
            ai_solution = perform_ai_work(ai_task['code'])
            
            if ai_solution['status'] == 'success':
                # Mine block with AI solution
                new_block = blockchain.mine_block(
                    miner_address=wallet.address,
                    ai_task=ai_task,
                    ai_solution=ai_solution
                )
                
                # Broadcast new block
                if new_block:
                    broadcast_new_block(new_block)
                    print(f"New block mined and broadcasted! Reward: {blockchain.mining_reward}")
            
        except Exception as e:
            print(f"Error in mining loop: {e}")
        
        time.sleep(10)  # Wait before next attempt

def sync_loop(node_address: str, interval: int):
    """Synchronization loop to keep the blockchain up to date"""
    while True:
        try:
            # Get the blockchain from the node
            response = requests.get(f'http://{node_address}/chain')
            if response.status_code == 200:
                chain_data = response.json()
                
                # If the node's chain is longer, replace ours
                if len(chain_data['chain']) > len(blockchain.chain):
                    if blockchain.validate_chain(chain_data['chain']):
                        blockchain.chain = chain_data['chain']
                        print(f"Chain synchronized with {node_address}")
                    
        except requests.exceptions.RequestException as e:
            print(f"Error syncing with {node_address}: {e}")
            
        time.sleep(interval)

@app.route('/chain', methods=['GET'])
def get_chain():
    """Get the full blockchain"""
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    """Register a new node in the network"""
    nodes = request.get_json().get('nodes')
    if nodes is None:
        return jsonify({'message': 'Error: Please supply a valid list of nodes'}), 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes)
    }
    return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    """Resolve conflicts between nodes"""
    replaced = resolve_conflicts()
    
    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }
    return jsonify(response), 200

@app.route('/submit/ai_task', methods=['POST'])
def submit_ai_task():
    """Submit a new AI task to the blockchain"""
    values = request.get_json()
    
    required = ['code', 'dataset']
    if not all(k in values for k in required):
        return jsonify({'message': 'Missing values'}), 400
    
    # Submit task using current wallet
    task = blockchain.submit_ai_task(
        wallet_address=wallet.address,
        code=values['code'],
        dataset=values['dataset']
    )
    
    response = {
        'message': 'AI task submitted successfully',
        'task': task
    }
    return jsonify(response), 201

@app.route('/block/new', methods=['POST'])
def new_block():
    """Receive a new block from another node"""
    values = request.get_json()
    
    required = ['block']
    if not all(k in values for k in required):
        return jsonify({'message': 'Missing values'}), 400
    
    block = values['block']
    
    # Verify the block
    if blockchain.validate_chain([block]):
        blockchain.chain.append(block)
        return jsonify({'message': 'Block added to chain'}), 201
    
    return jsonify({'message': 'Invalid block'}), 400

def broadcast_new_block(block):
    """Broadcast a new block to all nodes in the network"""
    for node in blockchain.nodes:
        try:
            requests.post(f'http://{node}/block/new', json={'block': block})
        except requests.exceptions.RequestException as e:
            print(f"Error broadcasting to node {node}: {e}")

def resolve_conflicts():
    """Consensus algorithm to resolve conflicts between nodes"""
    neighbours = blockchain.nodes
    new_chain = None
    max_length = len(blockchain.chain)
    
    for node in neighbours:
        try:
            response = requests.get(f'http://{node}/chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                
                if length > max_length and blockchain.validate_chain(chain):
                    max_length = length
                    new_chain = chain
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to node {node}: {e}")
    
    if new_chain:
        blockchain.chain = new_chain
        return True
    
    return False

def parse_args():
    """
    Parse the command line arguments to configure the server and peer node connection.
    """
    parser = argparse.ArgumentParser(description="Blockchain Node and Server Setup")
    parser.add_argument('--server', required=True, help="IP address of this server (e.g., 192.168.1.203)")
    parser.add_argument('--connect-to-node', required=True, help="IP address of the peer node to connect to (e.g., 192.168.1.202)")

    return parser.parse_args()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', type=str, required=True, help='Server IP address')
    parser.add_argument('--connect-to-node', type=str, help='IP address of node to connect to')
    args = parser.parse_args()
    
    # Start mining thread with correct arguments
    mining_thread = threading.Thread(
        target=create_and_submit_block_loop,
        args=(blockchain, wallet)
    )
    mining_thread.daemon = True
    mining_thread.start()
    
    # Connect to existing node if specified
    if args.connect_to_node:
        node_address = f"{args.connect_to_node}:5000"
        print(f"Connected to {node_address}")
        blockchain.register_node(node_address)
        
        # Start sync thread with string address
        sync_thread = threading.Thread(
            target=sync_loop,
            args=(node_address, 5)
        )
        sync_thread.daemon = True
        sync_thread.start()
        
        # Initial blockchain sync
        resolve_conflicts()
    
    # Start server
    print(f"Node running on {args.server}:5000")
    app.run(host=args.server, port=5000)

@app.route('/mine', methods=['POST'])
def start_mining():
    """Manually trigger mining process"""
    try:
        # Create AI task with proper code formatting
        ai_task = {
            'code': "def predict(X):\n    return X.mean()",  # Fixed indentation
            'dataset': 'sample_data.csv',
            'coefficients': [0.31479989701085853, 0.19944146798778906]
        }
        
        print("Starting mining process...")
        print(f"AI Task: {ai_task}")
        
        # Perform AI work
        ai_solution = perform_ai_work(ai_task['code'])
        print(f"AI Solution: {ai_solution}")
        
        if ai_solution['status'] == 'success':
            # Mine block with AI solution
            new_block = blockchain.mine_block(
                miner_address=wallet.address,
                ai_task=ai_task,
                ai_solution=ai_solution
            )
            
            # Broadcast new block
            if new_block:
                broadcast_new_block(new_block)
                return jsonify({
                    'message': 'New block mined!',
                    'block': new_block,
                    'reward': blockchain.mining_reward,
                    'miner_address': wallet.address
                }), 200
        
        return jsonify({
            'message': 'Mining failed', 
            'error': ai_solution.get('message'),
            'status': ai_solution.get('status')
        }), 400
        
    except Exception as e:
        print(f"Mining error: {str(e)}")  # Added logging
        return jsonify({'message': 'Error mining block', 'error': str(e)}), 500

if __name__ == "__main__":
    main()

