from flask import Flask, request, jsonify
from node import Node

app = Flask(__name__)

@app.route('/get_chain', methods=['GET'])
def get_chain():
    return jsonify({"chain": node2.blockchain.chain, "transactions": node2.blockchain.transactions})

# Additional routes can be added here as needed

