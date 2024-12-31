import json
import socket
import threading
from blockchain import Blockchain

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
                    chain_data = json.loads(data)
                    if 'chain' in chain_data:
                        chain = chain_data['chain']
                        if len(chain) > len(self.blockchain.chain) and self.blockchain.is_valid_chain(chain):
                            self.blockchain.replace_chain(chain)
            except Exception as e:
                print(f"Failed to synchronize with {peer_host}:{peer_port}: {e}")

