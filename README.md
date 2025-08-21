# Blockchain Implementation - INTE264 Assignment 2


## 📋 Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Phap229/Implementing-a-Blockchain.git
   cd Implementing-a-blockchain
   ```

2. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Quick Start

### Interactive Interface 
Run the main interactive interface:
```bash
python main.py
```

**Available Menu Options:**
1. **View Blockchain** - Display current blockchain structure
2. **View Balances** - Show all wallet balances
3. **Create Transaction** - Send coins between wallets
4. **Mine Block** - Mine a new block with Proof-of-Work
5. **Validate Chain** - Verify blockchain integrity
6. **Create Wallet** - Generate new cryptographic wallet
7. **P2P Operations** - Start P2P networking node
8. **Save/Load Blockchain** - Persist blockchain data
9. **Demo Double-Spend Prevention** - See security features in action
10. **Exit** - Close the application


## 💡 How to Use the System

### 1. **Getting Started**
- Run `python main.py`
- Choose option 6 to create your first wallet
- The system automatically creates a genesis block

### 2. **Creating Transactions**
- Choose option 3 (Create Transaction)
- Enter sender wallet name
- Enter recipient wallet name
- Enter amount to send
- The system validates the transaction and adds it to the pending pool

### 3. **Mining Blocks**
- Choose option 4 (Mine Block)
- Enter miner wallet name
- Watch the Proof-of-Work process
- See difficulty adjustment in action
- Mining rewards are automatically distributed

### 4. **Viewing Blockchain**
- Choose option 1 (View Blockchain)
- See all blocks with their details
- View transaction history
- Check block hashes and linking

### 5. **P2P Networking**
- Choose option 7 (P2P Operations)
- Start a network node
- Connect to other peers
- Broadcast transactions and blocks

## 🔒 Security Features

### **Double-Spend Prevention**
- **UTXO Model**: Each transaction output can only be spent once
- **Real-time Validation**: Immediate balance checking
- **Digital Signatures**: RSA-based transaction authentication
- **Chain Integrity**: Cryptographic hash linking prevents tampering

### **Immutable Ledger**
- SHA-256 cryptographic hashing
- Previous hash linking creates unbreakable chain
- Any modification immediately invalidates the chain
- Comprehensive validation on all operations

## 🏗️ Architecture

The system uses a modular design with separate classes:

- **`Block`** - Individual block structure with all required fields
- **`Transaction`** - Transaction data, validation, and signing
- **`Wallet`** - RSA key management and digital signatures
- **`Blockchain`** - Core blockchain logic, consensus, and validation
- **`P2PNode`** - Network communication and peer management

## 📊 Key Implementation Details

### **Difficulty Adjustment**
- **Automatic**: No manual control needed
- **Target**: 10 seconds per block
- **Adjustment**: ±1 difficulty based on mining time
- **Display**: Shows during mining process

### **Mining Rewards**
- **Amount**: 50 coins per block
- **Source**: Protocol-generated (simplified simulation)
- **Recipient**: Successful miner

### **Transaction Pool**
- Pending transactions wait for inclusion in blocks
- Automatic cleanup after mining
- Merkle root calculation for efficient verification

## 🧪 Testing

### **Run the Demo**
```bash
python demo.py
```

### **Test Individual Features**
Use the main interface (`python main.py`) to test:
- Transaction creation and validation
- Block mining and difficulty adjustment
- Chain validation and integrity
- Wallet creation and management
- P2P networking operations

## 📁 File Structure

```
├── blockchain.py          # Core blockchain implementation
├── main.py               # Interactive CLI interface
├── demo.py               # Double-spend prevention demo
├── p2p_network.py        # P2P networking functionality
├── requirements.txt       # Python dependencies
├── README.md             # This documentation
└── .gitignore            # Git ignore file 
```


## 📚 Technical Details

### **Cryptographic Implementation**
- **Hashing**: SHA-256 for block and transaction hashes
- **Keys**: RSA-2048 for wallet key pairs
- **Signatures**: RSA-PSS with SHA-256 for transactions
- **Merkle Trees**: Efficient transaction verification

### **Consensus Mechanism**
- **Algorithm**: Proof-of-Work
- **Target**: Configurable difficulty (leading zeros)
- **Adjustment**: Automatic based on mining time
- **Rewards**: Incentivizes network security

### **Data Persistence**
- **Format**: Python pickle for complex object serialization
- **Automatic**: Saves after significant operations
- **Validation**: Integrity checks on load
- **Backup**: Support for multiple save files



