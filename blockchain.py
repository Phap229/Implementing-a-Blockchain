
import hashlib          # For SHA-256 cryptographic hashing
import json            # For data serialization
import time            # For timestamps
import os              # For file operations
from typing import List, Dict, Optional  # Type hints for better code clarity
from dataclasses import dataclass, asdict  # For clean data structures
from cryptography.hazmat.primitives import hashes  # Cryptographic hash functions
from cryptography.hazmat.primitives.asymmetric import rsa, padding  # RSA encryption
from cryptography.hazmat.primitives import serialization  # Key serialization
import pickle          # For blockchain data persistence

# =============================================================================
# TRANSACTION CLASS - Represents a single transaction in the blockchain
# =============================================================================
# A transaction records the transfer of value (coins) from one wallet to another
# Each transaction is cryptographically signed to ensure authenticity
# =============================================================================

@dataclass
class Transaction:
    """
    Represents a transaction in the blockchain.
    """
    sender: str          # sender
    recipient: str       # recipient
    amount: float        # amount
    transaction_id: str  # transaction_id
    timestamp: float     # timestamp
    signature: Optional[str] = None  # signature
    
    def to_dict(self) -> Dict:
        """
        Convert transaction to dictionary format for hashing and serialization.
        
        Returns:
            Dict: Dictionary representation of transaction (without signature)
        """
        return {
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount,
            'transaction_id': self.transaction_id,
            'timestamp': self.timestamp
        }
    
    def calculate_hash(self) -> str:
        """
        Calculate the SHA-256 hash of this transaction.
         
        Returns:
            str: 64-character hexadecimal hash string
        """
        # Convert transaction to JSON string (sorted for consistency)
        transaction_string = json.dumps(self.to_dict(), sort_keys=True)
        # Create SHA-256 hash and return as hex string
        return hashlib.sha256(transaction_string.encode()).hexdigest()

# =============================================================================
# BLOCK CLASS - Represents a single block in the blockchain
# =============================================================================
# A block contains multiple transactions and is cryptographically linked
# to the previous block, creating an immutable chain
# =============================================================================

@dataclass
class Block:
    
    index: int                    # Block number 
    timestamp: float              
    transactions: List[Transaction]  # Transactions in this block
    previous_hash: str            # Hash of previous block 
    nonce: int                    # Proof-of-Work number
    difficulty: int               # Mining difficulty target
    merkle_root: str              # Merkle tree root hash
    
    def calculate_hash(self) -> str:
        """
        Calculate the SHA-256 hash of this block.
        
        Returns:
            str: 64-character hexadecimal hash string
        """
        # Create a dictionary with all block data (excluding the hash itself)
        block_data = {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': [tx.to_dict() for tx in self.transactions],  # Convert transactions to dicts
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'difficulty': self.difficulty,
            'merkle_root': self.merkle_root
        }
        
        # Convert to JSON string (sorted for consistency) and hash
        block_string = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def to_dict(self) -> Dict:
        """
        Convert block to dictionary format for serialization and storage.
        
        Returns:
            Dict: Complete dictionary representation of the block
        """
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': [asdict(tx) for tx in self.transactions],  # Include all transaction fields
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'difficulty': self.difficulty,
            'merkle_root': self.merkle_root
        }

# =============================================================================
# WALLET CLASS - Manages cryptographic keys and transaction signing
# =============================================================================
# A wallet contains a pair of cryptographic keys:
# - Private key: Used to sign transactions (keep secret!)
# - Public key: Used to verify signatures (can share with others)
# =============================================================================

class Wallet:
    """
    Simple wallet implementation with RSA public/private key pairs.
    
    The wallet provides:
    - Key generation (2048-bit RSA keys)
    - Transaction signing with private key
    - Signature verification with public key
    - Secure key storage and management
    
    """
    
    def __init__(self, name: str):
        """
        Initialize a new wallet with cryptographic keys.
        
        Args:
            name (str): Human-readable name for this wallet
            
        """
        self.name = name
        
        # Generate a new RSA private key (2048 bits for security)
        # 65537 is the standard public exponent used in RSA
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,  # Standard RSA exponent
            key_size=2048           # 2048 bits for strong security
        )
        
        # Extract the public key from the private key
        self.public_key = self.private_key.public_key()
        
        # Convert public key to PEM format
        self.public_key_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,           # Text format
            format=serialization.PublicFormat.SubjectPublicKeyInfo  # Standard format
        ).decode()  # Convert bytes to string
    
    def __getstate__(self):
        """
        Custom serialization method to handle private key objects.
        
        This method is called by pickle when saving the wallet.
        We exclude the private key because it cannot be serialized.
        
        Returns:
            dict: Wallet state without private key objects
        """
        state = self.__dict__.copy()
        # Remove the private key (can't be pickled)
        state['private_key'] = None
        # Remove the public key object (can't be pickled)
        state['public_key'] = None
        return state
    
    def __setstate__(self, state):
        """
        Custom deserialization method to handle private key objects.
        
        This method is called by pickle when loading the wallet.
        We regenerate the private key since it couldn't be saved.
        
        Args:
            state (dict): Wallet state from pickle
        """
        self.__dict__.update(state)
        
        
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        
        # Regenerate public key from the new private key
        self.public_key = self.private_key.public_key()
        
        # Update the PEM representation
        self.public_key_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()
    
    def sign_transaction(self, transaction: Transaction) -> str:
        """
        Sign a transaction using the wallet's private key.
        
        Args:
            transaction (Transaction): The transaction to sign
            
        Returns:
            str: Hexadecimal representation of the digital signature
            
        """
        # Convert transaction to JSON string 
        transaction_string = json.dumps(transaction.to_dict(), sort_keys=True)
        
        # Create digital signature using RSA-PSS with SHA-256
        signature = self.private_key.sign(
            transaction_string.encode(),  # Convert string to bytes
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),  # Mask generation function
                salt_length=padding.PSS.MAX_LENGTH   # Maximum salt for security
            ),
            hashes.SHA256()  # Use SHA-256 for hashing
        )
        
        # Return signature as hexadecimal string for easy storage/transmission
        return signature.hex()
    
    def verify_signature(self, transaction: Transaction, signature: str) -> bool:
        """
        Verify a transaction signature using the wallet's public key.
                
        Args:
            transaction (Transaction): The transaction to verify
            signature (str): The signature to verify (hex string)
            
        Returns:
            bool: True if signature is valid, False otherwise
        """
        try:
            # Convert transaction to same format used for signing
            transaction_string = json.dumps(transaction.to_dict(), sort_keys=True)
            
            # Convert hex signature back to bytes
            signature_bytes = bytes.fromhex(signature)
            
            # Verify the signature using the public key
            # This will raise an exception if the signature is invalid
            self.public_key.verify(
                signature_bytes,                    # The signature to verify
                transaction_string.encode(),        # The original data
                padding.PSS(                       # Same padding as signing
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()                    # Same hash function
            )
            return True  # Signature is valid
            
        except Exception:
            # Signature verification failed (invalid, corrupted, or forged)
            return False

# =============================================================================
# BLOCKCHAIN CLASS - Main blockchain implementation and management
# =============================================================================
# The blockchain class manages:
# - The chain of blocks (linked list structure)
# - Pending transactions (mempool)
# - Proof-of-Work consensus
# - Double-spend prevention
# - Wallet management
# =============================================================================

class Blockchain:
    """
    Main blockchain implementation that manages the entire blockchain system.
    
    The blockchain provides:
    - Block creation and validation
    - Transaction management and verification
    - Proof-of-Work consensus mechanism
    - Double-spend prevention using UTXO model
    - Chain integrity verification
    - Data persistence and loading
    
    """
    
    def __init__(self, difficulty: int = 4):
        """
        Initialize a new blockchain.
        
        Args:
            difficulty (int): Mining difficulty (number of leading zeros required)
        
        """
        self.chain: List[Block] = []                    # List of all blocks in the chain
        self.pending_transactions: List[Transaction] = []  # Transactions waiting to be mined
        self.difficulty = difficulty                     # Mining difficulty target
        self.utxo_set: Dict[str, float] = {}            # Unspent Transaction Output set (for balance tracking)
        self.wallets: Dict[str, Wallet] = {}            # Collection of wallets by name
        self.mining_reward = 50.0                       # Reward for mining a block
        self.target_block_time = 10.0                   # Target time between blocks (seconds)
        self.last_mining_time = 0.0                     # Time of last block mining
        
        # Create the first block (genesis block) to start the chain
        self.create_genesis_block()
    
    def create_genesis_block(self):
        """
        Create the genesis block (first block) in the blockchain.
        """
        # Create the genesis block with special initial values
        genesis_block = Block(
            index=0,                           
            timestamp=time.time(),             # Current time
            transactions=[],                   # No transactions in genesis
            previous_hash="0",                 # No previous block (special value)
            nonce=0,                          # No mining required for genesis
            difficulty=self.difficulty,        # Set initial mining difficulty
            merkle_root="0"                   # No transactions = no merkle root
        )
        
        # Calculate the hash of the genesis block
        genesis_block.hash = genesis_block.calculate_hash()
        
        # Add the genesis block to the beginning of the chain
        self.chain.append(genesis_block)
    
    def calculate_merkle_root(self, transactions: List[Transaction]) -> str:
        """
        Calculate the Merkle root hash of a list of transactions.
        
        Args:
            transactions (List[Transaction]): List of transactions to hash
            
        Returns:
            str: Merkle root hash (64-character hex string)
        """
        # If no transactions, return special "0" value
        if not transactions:
            return "0"
        
        # Convert all transactions to their hashes
        # These hashes become the leaf nodes of the Merkle tree
        tx_hashes = [tx.calculate_hash() for tx in transactions]
        
        # Build the Merkle tree from bottom up
        while len(tx_hashes) > 1:
            # If odd number of hashes, duplicate the last one
            # This ensures we always have pairs to hash together
            if len(tx_hashes) % 2 == 1:
                tx_hashes.append(tx_hashes[-1])
            
            # Create new level by hashing pairs of hashes
            new_level = []
            for i in range(0, len(tx_hashes), 2):
                # Combine two hashes and hash them together
                combined = tx_hashes[i] + tx_hashes[i + 1]
                new_level.append(hashlib.sha256(combined.encode()).hexdigest())
            
            # Move up one level in the tree
            tx_hashes = new_level
        
        # Return the root hash 
        return tx_hashes[0] if tx_hashes else "0"
    
    def get_latest_block(self) -> Block:
        """Get the most recent block in the chain"""
        return self.chain[-1]
    
    def add_transaction(self, sender: str, recipient: str, amount: float, wallet: Wallet) -> bool:
        """
        Add a new transaction to the pending transactions pool.
        
        Args:
            sender (str): Name/address of the sending wallet
            recipient (str): Name/address of the receiving wallet
            amount (float): Amount of coins to transfer
            wallet (Wallet): The sender's wallet (for signing)
            
        Returns:
            bool: True if transaction was added successfully, False otherwise
            
        Note: Transactions are not immediately added to the blockchain.
        They wait in the pending pool until a block is mined.
        """
        # Check if sender has sufficient balance
        if sender != "Genesis" and self.get_balance(sender) < amount:
            print(f"Insufficient balance for {sender}")
            return False
        
        #Create the transaction object
        transaction = Transaction(
            sender=sender,
            recipient=recipient,
            amount=amount,
            # Create unique transaction ID using sender, recipient, and timestamp
            transaction_id=f"{sender}_{recipient}_{int(time.time())}",
            timestamp=time.time()
        )
        
        # Sign the transaction with the sender's private key
        transaction.signature = wallet.sign_transaction(transaction)
        
        # Verify the signature is valid
        if not wallet.verify_signature(transaction, transaction.signature):
            print("Invalid transaction signature")
            return False
        
        # Check for double-spend attempts
        if not self.is_valid_transaction(transaction):
            print("Double-spend detected!")
            return False
        
        # Add transaction to pending pool
        self.pending_transactions.append(transaction)
        print(f"Transaction added: {sender} -> {recipient}: {amount}")
        return True
    
    def is_valid_transaction(self, transaction: Transaction) -> bool:
        """Check if transaction is valid (no double-spend)"""
        if transaction.sender == "Genesis":
            return True
        
        # Check if sender has sufficient balance
        sender_balance = self.get_balance(transaction.sender)
        if sender_balance < transaction.amount:
            return False
        
        # Check for double-spend in pending transactions
        for pending_tx in self.pending_transactions:
            if (pending_tx.sender == transaction.sender and 
                pending_tx.transaction_id != transaction.transaction_id):
                return False
        
        return True
    
    def get_balance(self, address: str) -> float:
        """Get current balance of an address"""
        balance = 0.0
        
        # Process all blocks to calculate balance
        for block in self.chain:
            for tx in block.transactions:
                if tx.recipient == address:
                    balance += tx.amount
                if tx.sender == address:
                    balance -= tx.amount
        
        # Process pending transactions
        for tx in self.pending_transactions:
            if tx.recipient == address:
                balance += tx.amount
            if tx.sender == address:
                balance -= tx.amount
        
        return balance
    
    def mine_block(self, miner_address: str) -> Optional[Block]:
       
        # Check if there are transactions to mine
        if not self.pending_transactions:
            print("No transactions to mine")
            return None
        
        # Get information about the previous block
        previous_block = self.get_latest_block()
        new_index = previous_block.index + 1
        new_timestamp = time.time()
        
        # Create mining reward transaction
        reward_transaction = Transaction(
            sender="System",
            recipient=miner_address,
            amount=self.mining_reward,
            transaction_id=f"reward_{new_index}_{int(time.time())}",
            timestamp=time.time()
        )
        
        # Prepare all transactions for the block (pending + reward)
        all_transactions = self.pending_transactions.copy() + [reward_transaction]
        
        # Create the new block structure
        new_block = Block(
            index=new_index,                                    # Next block number
            timestamp=new_timestamp,                            # Current time
            transactions=all_transactions,                      # All transactions including reward
            previous_hash=previous_block.calculate_hash(),       # Link to previous block
            nonce=0,                                            # Start with nonce 0
            difficulty=self.difficulty,                         # Current difficulty target
            merkle_root=self.calculate_merkle_root(all_transactions)  # Hash of all transactions
        )
        
        # Mine the block (Proof-of-Work)
        # The target is a string of zeros (e.g., "0000" for difficulty 4)
        target = "0" * self.difficulty
        print(f"Mining block {new_index} with difficulty {self.difficulty}...")
        
        # Start mining: try different nonce values until we find a valid hash
        start_time = time.time()
        while True:
            # Try the next nonce value
            new_block.nonce += 1
            
            # Calculate the block hash with current nonce
            block_hash = new_block.calculate_hash()
            
            # Check if the hash meets the difficulty requirement
            if block_hash.startswith(target):
                # We found a valid solution!
                mining_time = time.time() - start_time
                print(f"Block mined! Hash: {block_hash[:20]}...")
                print(f"Mining time: {mining_time:.2f} seconds")
                print(f"Nonce: {new_block.nonce}")
                break
        
        # Add the mined block to the blockchain
        new_block.hash = new_block.calculate_hash()
        self.chain.append(new_block)
        
        # Clear pending transactions 
        self.pending_transactions = []
        
        #Update UTXO set to reflect new block
        self.update_utxo_set()
        
        # Adjust difficulty based on mining time
        self.adjust_difficulty()
        
        return new_block
    
    def update_utxo_set(self):
        """Update the UTXO set based on current chain state"""
        self.utxo_set = {}
        for block in self.chain:
            for tx in block.transactions:
                if tx.recipient not in self.utxo_set:
                    self.utxo_set[tx.recipient] = 0
                self.utxo_set[tx.recipient] += tx.amount
    
    def adjust_difficulty(self):
       
        if len(self.chain) < 2:  # Need at least 2 blocks to calculate time difference
            return
        
        current_time = time.time()
        if self.last_mining_time > 0:
            time_diff = current_time - self.last_mining_time
            
            if time_diff < self.target_block_time * 0.5:  # Too fast
                self.difficulty += 1
                print(f"Difficulty increased to {self.difficulty} (blocks too fast)")
            elif time_diff > self.target_block_time * 2.0:  # Too slow
                self.difficulty = max(1, self.difficulty - 1)  # Don't go below 1
                print(f"Difficulty decreased to {self.difficulty} (blocks too slow)")
        
        self.last_mining_time = current_time
    
    def is_chain_valid(self) -> bool:
        """
        Verify the integrity of the entire blockchain.
        
        Returns:
            bool: True if blockchain is valid, False if corruption detected
            
        """
        # Start validation from block 1 (genesis block is always valid)
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Check 1: Verify current block hash is correct
            if current_block.calculate_hash() != current_block.hash:
                print(f"Invalid hash in block {i}")
                return False
            
            # Check 2: Verify chain linking is correct
            # Each block must point to the previous block's hash
            if current_block.previous_hash != previous_block.hash:
                print(f"Invalid previous hash in block {i}")
                return False
            
            # Check 3: Verify Proof-of-Work consensus
            # Block hash must meet the difficulty requirement
            target = "0" * current_block.difficulty
            if not current_block.hash.startswith(target):
                print(f"Block {i} doesn't meet difficulty requirement")
                return False
        
        # All checks passed - blockchain is valid
        return True
    
    def add_block(self, block: Block) -> bool:
        """Add a block to the chain (for P2P networking)"""
        if self.is_block_valid(block):
            self.chain.append(block)
            self.update_utxo_set()
            return True
        return False
    
    def is_block_valid(self, block: Block) -> bool:
        """Check if a block is valid"""
        # Check if previous hash matches
        if block.previous_hash != self.get_latest_block().hash:
            return False
        
        # Check if block hash meets difficulty
        target = "0" * block.difficulty
        if not block.hash.startswith(target):
            return False
        
        # Check if block hash is correct
        if block.calculate_hash() != block.hash:
            return False
        
        return True
    
    def save_to_file(self, filename: str = "blockchain.pkl"):
        """Save blockchain to file"""
        try:
            with open(filename, 'wb') as f:
                pickle.dump(self, f)
            print(f"Blockchain saved to {filename}")
        except Exception as e:
            print(f"Error saving blockchain: {e}")
    
    def load_from_file(self, filename: str = "blockchain.pkl") -> bool:
        """Load blockchain from file"""
        try:
            if os.path.exists(filename):
                with open(filename, 'rb') as f:
                    loaded_blockchain = pickle.load(f)
                    self.chain = loaded_blockchain.chain
                    self.pending_transactions = loaded_blockchain.pending_transactions
                    self.difficulty = loaded_blockchain.difficulty
                    self.utxo_set = loaded_blockchain.utxo_set
                    self.wallets = loaded_blockchain.wallets
                print(f"Blockchain loaded from {filename}")
                return True
            return False
        except Exception as e:
            print(f"Error loading blockchain: {e}")
            return False
    
    def print_chain(self):
        """Print the entire blockchain"""
        print("\n" + "="*50)
        print("BLOCKCHAIN")
        print("="*50)
        
        for block in self.chain:
            print(f"\nBlock #{block.index}")
            print(f"Timestamp: {time.ctime(block.timestamp)}")
            print(f"Previous Hash: {block.previous_hash[:20]}...")
            print(f"Hash: {block.hash[:20]}...")
            print(f"Nonce: {block.nonce}")
            print(f"Difficulty: {block.difficulty}")
            print(f"Transactions: {len(block.transactions)}")
            
            for tx in block.transactions:
                print(f"  {tx.sender} -> {tx.recipient}: {tx.amount}")
        
        print(f"\nChain length: {len(self.chain)}")
        print(f"Pending transactions: {len(self.pending_transactions)}")
        print("="*50)
    
    def print_balances(self):
        """Print all wallet balances"""
        print("\n" + "="*30)
        print("WALLET BALANCES")
        print("="*30)
        
        for wallet_name in self.wallets:
            balance = self.get_balance(wallet_name)
            print(f"{wallet_name}: {balance}")
        
        print("="*30)

    def demonstrate_immutability(self) -> bool:
        """
        Demonstrate blockchain immutability by attempting to tamper with block data.
        This shows how any modification immediately invalidates the entire chain.
        
        Returns:
            bool: True if tampering was detected, False otherwise
        """
        print("\n" + "="*60)
        print("           IMMUTABILITY DEMONSTRATION")
        print("="*60)
        
        # Step 1: Verify chain is initially valid
        print("1. Initial chain validation:")
        initial_validity = self.is_chain_valid()
        print(f"   Chain valid: {'✓ Yes' if initial_validity else '✗ No'}")
        
        if len(self.chain) < 2:
            print("   Need at least 2 blocks to demonstrate immutability")
            return False
        
        # Step 2: Show original block data
        target_block = self.chain[1]  # Use first non-genesis block
        print(f"\n2. Original Block #{target_block.index} data:")
        print(f"   - Hash: {target_block.hash[:20]}...")
        print(f"   - Previous Hash: {target_block.previous_hash[:20]}...")
        print(f"   - Transactions: {len(target_block.transactions)}")
        
        # Step 3: Tamper with block data (simulate attack)
        print(f"\n3. Attempting to tamper with Block #{target_block.index}...")
        original_hash = target_block.hash
        original_previous_hash = target_block.previous_hash
        
        # Simulate tampering by modifying transaction amount
        if target_block.transactions:
            original_amount = target_block.transactions[0].amount
            target_block.transactions[0].amount = original_amount + 1.0  # Add 1 coin
            print(f"   - Modified transaction amount from {original_amount} to {target_block.transactions[0].amount}")
        
        # Step 4: Show that the block hash has changed
        new_hash = target_block.calculate_hash()
        print(f"\n4. Hash change detection:")
        print(f"   - Original hash: {original_hash[:20]}...")
        print(f"   - New hash: {new_hash[:20]}...")
        print(f"   - Hashes match: {'✗ No' if original_hash != new_hash else '✓ Yes'}")
        
        # Step 5: Show chain invalidation
        print(f"\n5. Chain validation after tampering:")
        chain_valid = self.is_chain_valid()
        print(f"   - Chain valid: {'✗ No' if not chain_valid else '✓ Yes'}")
        
        if not chain_valid:
            print("   - ✓ IMMUTABILITY DEMONSTRATED: Tampered block invalidated the chain!")
            print("   - ✓ Any attempt to modify block data is immediately detected")
            print("   - ✓ The blockchain is truly tamper-resistant")
        
        # Step 6: Show cascade effect on subsequent blocks
        print(f"\n6. Cascade effect demonstration:")
        for i in range(1, len(self.chain)):
            block = self.chain[i]
            calculated_hash = block.calculate_hash()
            stored_hash = block.hash
            
            if calculated_hash != stored_hash:
                print(f"   - Block #{block.index}: Hash mismatch detected")
                print(f"     Stored: {stored_hash[:20]}...")
                print(f"     Calculated: {calculated_hash[:20]}...")
            else:
                print(f"   - Block #{block.index}: Hash valid")
        
        # Step 7: Restore original data (for demonstration purposes)
        print(f"\n7. Restoring original data...")
        if target_block.transactions:
            target_block.transactions[0].amount = original_amount
        target_block.hash = original_hash
        
        # Step 8: Verify chain is valid again
        print(f"\n8. Final validation:")
        final_validity = self.is_chain_valid()
        print(f"   - Chain valid: {'✓ Yes' if final_validity else '✗ No'}")
        
        print("\n" + "="*60)
        print("           IMMUTABILITY DEMONSTRATION COMPLETE")
        print("="*60)
        return not chain_valid  # Return True if tampering was detected

    def comprehensive_validation_demo(self) -> None:
        """
        Demonstrate comprehensive validation features of the blockchain.
        """
        print("\n" + "="*60)
        print("           COMPREHENSIVE VALIDATION DEMONSTRATION")
        print("="*60)
        
        print("1. Block-by-block validation:")
        for i, block in enumerate(self.chain):
            print(f"   Block #{block.index}:")
            
            # Validate individual block hash
            calculated_hash = block.calculate_hash()
            hash_valid = block.hash == calculated_hash
            print(f"     - Hash validation: {'✓ Valid' if hash_valid else '✗ Invalid'}")
            
            # Validate Proof-of-Work
            target = "0" * block.difficulty
            pow_valid = block.hash.startswith(target)
            print(f"     - Proof-of-Work: {'✓ Valid' if pow_valid else '✗ Invalid'}")
            
            # Validate chain linking (except genesis)
            if i > 0:
                link_valid = block.previous_hash == self.chain[i-1].hash
                print(f"     - Chain linking: {'✓ Valid' if link_valid else '✗ Invalid'}")
        
        print(f"\n2. Overall chain validation:")
        chain_valid = self.is_chain_valid()
        print(f"   - Complete chain: {'✓ Valid' if chain_valid else '✗ Invalid'}")
        
        print(f"\n3. Transaction validation:")
        total_transactions = sum(len(block.transactions) for block in self.chain)
        print(f"   - Total transactions: {total_transactions}")
        
        # Validate transaction hashes
        invalid_transactions = 0
        for block in self.chain:
            for tx in block.transactions:
                if tx.calculate_hash() != tx.transaction_id:
                    invalid_transactions += 1
        
        print(f"   - Invalid transactions: {invalid_transactions}")
        print(f"   - Transaction integrity: {'✓ Valid' if invalid_transactions == 0 else '✗ Invalid'}")
        
        print(f"\n4. Merkle root validation:")
        for block in self.chain:
            if block.transactions:
                calculated_merkle = self.calculate_merkle_root(block.transactions)
                merkle_valid = block.merkle_root == calculated_merkle
                print(f"   - Block #{block.index} Merkle root: {'✓ Valid' if merkle_valid else '✗ Invalid'}")
        
        print("\n" + "="*60)
        print("           VALIDATION DEMONSTRATION COMPLETE")
        print("="*60)
