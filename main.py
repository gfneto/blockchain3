import argparse
import threading
import time
from blockchain import Blockchain
from node import Node
from flask import Flask
from ai_tasks import perform_ai_work  # Import perform_ai_work from ai_tasks.py

# Flask App Setup
app = Flask(__name__)

def sync_loop(node, interval):
    """
    Periodically synchronizes the blockchain with connected peers.
    """
    while True:
        time.sleep(interval)
        node.sync_blockchain()

def create_and_submit_block_loop(node, blockchain):
    """
    Creates and submits a block periodically with AI work
    """
    while True:
        ai_task = blockchain.generate_ai_task()
        ai_solution = perform_ai_work(ai_task)  # Use perform_ai_work from ai_tasks.py
        new_block = blockchain.add_block_with_ai_work(ai_task, ai_solution)
        if new_block:
            print(f"Block #{new_block['index']} added with AI solution")
        else:
            print("Failed to validate AI solution.")
        time.sleep(10)  # Create a block every 10 seconds

# Flask Route for getting the current blockchain
@app.route('/get_chain', methods=['GET'])
def get_chain():
    return {"chain": node2.blockchain.chain, "transactions": node2.blockchain.transactions}

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

