import time
import json
import socket
import threading
from hashlib import sha256
from flask import Flask, request, jsonify
import os
from blockchain import Blockchain

app = Flask(__name__)

BLOCKCHAIN_FILE = "blockchain.data"

# Initialize blockchain
blockchain = Blockchain()

# Add stakeholders (example)
blockchain.add_stakeholder("Validator1", 100)
blockchain.add_stakeholder("Validator2", 50)

class Node:
    def __init__(self, host, port, blockchain):
        self.host = host
        self.port = port
        self.blockchain = blockchain
        self.peers = []
        self.start_server()

    def start_server(self):
        server_thread = threading.Thread(target=self.run_server)
        server_thread.start()

    def run_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen(5)
        print(f"Node running on {self.host}:{self.port}")
        while True:
            conn, addr = server.accept()
            threading.Thread(target=self.handle_client, args=(conn,)).start()

    def handle_client(self, conn):
        data = conn.recv(1024).decode()
        if data:
            try:
                request = json.loads(data)
                if request.get('transaction'):
                    self.blockchain.add_transaction(request['transaction'])
                    conn.send(json.dumps({"status": "Transaction added"}).encode())
                elif request.get('get_chain'):
                    conn.send(json.dumps({"chain": self.blockchain.chain}).encode())
            except json.JSONDecodeError:
                conn.send(json.dumps({"error": "Invalid JSON format"}).encode())
        conn.close()

    def connect_to_peer(self, peer_host, peer_port):
        self.peers.append((peer_host, peer_port))
        print(f"Connected to {peer_host}:{peer_port}")

    def sync_blockchain(self):
        for peer_host, peer_port in self.peers:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as peer:
                    peer.connect((peer_host, peer_port))
                    peer.send(json.dumps({"get_chain": True}).encode())
                    data = peer.recv(4096).decode()
                    chain = json.loads(data)
                    if chain['chain'] and len(chain['chain']) > len(self.blockchain.chain):
                        self.blockchain.replace_chain(chain['chain'])
            except:
                print(f"Failed to synchronize with {peer_host}:{peer_port}")

# Flask Route for adding transactions via POST method
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    try:
        data = request.get_json()
        if 'amount' in data:
            transaction = {'amount': data['amount']}
            # Add the transaction to the blockchain
            node1.blockchain.add_transaction(transaction)
            return jsonify({"status": "Transaction added"}), 200
        else:
            return jsonify({"error": "Invalid transaction data"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Flask Route for getting the current blockchain
@app.route('/get_chain', methods=['GET'])
def get_chain():
    return jsonify({"chain": node1.blockchain.chain, "transactions": node1.blockchain.transactions})

# Create blockchain and node1
blockchain = Blockchain()
node1 = Node("192.168.1.202", 5000, blockchain)

# Connect node1 to node2
node1.connect_to_peer("192.168.1.203", 5000)

# Periodic blockchain sync
def sync_loop(node, interval):
    while True:
        time.sleep(interval)
        node.sync_blockchain()

# Start syncing loop for node1
threading.Thread(target=sync_loop, args=(node1, 5)).start()

if __name__ == '__main__':
    # Start Flask server to accept POST requests
    app.run(host='0.0.0.0', port=5001)
