```markdown
# Blockchain Node Setup

## File structure

/project_directory
│
├── blockchain.py    # Contains the Blockchain class and related methods
├── node.py          # Contains the Node class and networking logic
├── ai_tasks.py      # Handles AI task generation and solution verification
├── api.py           # Contains Flask routes and APIs for interactions
└── main.py          # Initializes the blockchain, nodes, and starts the Flask server



## Requirements

from Ubuntu Server cloud image:
apt-get update
apt-get install python3-pip python3.12-venv
python3 -m venv ~/myenv
source ~/myenv/bin/activate
pip install ecdsa (for wallet) flask (for node) numpy scikit-learn (for ai tasks)
run inside of virtual env.

```
## To Run

python3 main.py --server 192.168.1.202 --connect-to-node 192.168.1.203

### From a Third Machine
To add a transaction to the blockchain, use the following command:
```bash
curl -X POST http://192.168.1.203:5001/add_transaction -H "Content-Type: application/json" -d '{"amount": 100}'
```

To retrieve the current blockchain:
```bash
curl http://192.168.1.202:5001/get_chain
```

# Blockchain Block Structure

The structure of a block in the blockchain consists of the following key elements:

1. **Index**:
   - A unique identifier for the block in the blockchain (its position in the chain).

2. **Timestamp**:
   - The time when the block was created (usually in Unix epoch format).

3. **Transactions**:
   - A list of transactions included in the block. Each transaction represents a change or a task that was added to the blockchain.

4. **AI Solution**:
   - The AI solution associated with this block. This is typically the output of an AI task, such as the coefficients learned from a machine learning model.

5. **Previous Hash**:
   - A hash of the previous block in the chain. This ensures the integrity of the blockchain, linking blocks together in a chain.

6. **Hash**:
   - A cryptographic hash of the current block's content (including index, timestamp, transactions, AI solution, and previous hash). This ensures the immutability of the block.

## Example Block:

```json
{
    "index": 1,
    "timestamp": 1617770000,
    "transactions": [
        {"sender": "A", "recipient": "B", "amount": 10},
        {"sender": "C", "recipient": "D", "amount": 5}
    ],
    "ai_solution": {
        "coefficients": [0.36, 0.42]
    },
    "previous_hash": "abc123...",
    "hash": "xyz456..."
}



This version consolidates everything into one text block for easier reading and copying into a single markdown file.

references:

https://github.com/nambrot/blockchain-in-js

