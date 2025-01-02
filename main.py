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

# Create or load wallet
wallet_data = wallet.create_wallet("your_password")
print(f"Using wallet address: {wallet_data['address']}")

def create_and_submit_block_loop():
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
                    miner_address=wallet_data['address'],
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
        wallet_address=wallet_data['address'],
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
    # Parse command line arguments
    args = parse_args()

    # Initialize Blockchain
    blockchain = Blockchain()

    # Create a node based on the server IP provided in command-line args
    node = Node(args.server, 5000, blockchain)

    # Connect to the peer node specified
    node.connect_to_peer(args.connect_to_node, 5000)

    # Start syncing loop for node2
    threading.Thread(target=sync_loop, args=(node, 5), daemon=True).start()

    # Start periodic block creation loop
    threading.Thread(target=create_and_submit_block_loop, args=(node, blockchain), daemon=True).start()

    # Start Flask server to accept API requests
    app.run(host='0.0.0.0', port=5002)

if __name__ == '__main__':
    main()

