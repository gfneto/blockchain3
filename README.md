```markdown
# Blockchain Node Setup

## Requirements
To get started, you need to install the following packages:


sudo apt-get install python3-pip python3.12-venv
python3 -m venv ~/myenv
source ~/myenv/bin/activate
pip install ecdsa flask
```

## To Run

### Worker02 (Node1)
1. Clone the blockchain code to the machine:
   ```bash
   cd ~
   git clone <repository-url> blockchain3
   cd blockchain3
   ```
2. Activate the virtual environment:
   ```bash
   source ~/myenv/bin/activate
   ```
3. Run Node 1:
   ```bash
   python3 node1.py
   ```

### Worker03 (Node2)
1. Clone the blockchain code to the machine:
   ```bash
   cd ~
   git clone <repository-url> blockchain3
   cd blockchain3
   ```
2. Activate the virtual environment:
   ```bash
   source ~/myenv/bin/activate
   ```
3. Run Node 2:
   ```bash
   python3 node2.py
   ```

### From a Third Machine
To add a transaction to the blockchain, use the following command:
```bash
curl -X POST http://192.168.1.203:5001/add_transaction -H "Content-Type: application/json" -d '{"amount": 100}'
```

To retrieve the current blockchain:
```bash
curl http://192.168.1.202:5001/get_chain
```

## Block Structure
Each block in the blockchain contains the following fields:
- **Index**: The position of the block in the chain.
- **Timestamp**: The time when the block is created.
- **Transactions**: A list of transactions included in the block. This can be empty if no transactions are added.
- **Previous Hash**: The hash of the previous block in the chain.
- **Hash**: The hash of the current block, calculated based on its contents (transactions, timestamp, previous hash, etc.).

### Example Block:
```json
{
  "index": 1,
  "timestamp": 1609437279.4263,
  "transactions": [{"amount": 500}],
  "previous_hash": "previous_block_hash",
  "hash": "current_block_hash"
}
```

This block structure ensures that each block is securely linked to the previous one through the `previous_hash`.

## Create a Second Node (Node2) on a Different IP or Port
To create a second node (node2) on a different IP or port, use the following code:
```python
node2 = Node("192.168.1.203", 5001, blockchain)
node2.connect_to_peer("192.168.1.202", 5000)
```

Start the block creation loop for node2:
```python
threading.Thread(target=block_creation_loop, args=(node2, 5)).start()
```
```

This version consolidates everything into one text block for easier reading and copying into a single markdown file.
