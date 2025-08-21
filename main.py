#!/usr/bin/env python3
"""
=============================================================================
BLOCKCHAIN CLI INTERFACE - INTE264 Assignment 2
=============================================================================
This file provides a comprehensive command-line interface for interacting with
the blockchain system. It demonstrates all the required functionality including:

CORE REQUIREMENTS (1-8):
1. Block Structure - View and understand block contents
2. Cryptographic Hashing - See hash calculations and chain integrity
3. Transaction Handling - Create, view, and manage transactions
4. Consensus Mechanism - Mine blocks with Proof-of-Work
5. Double-Spend Prevention - Test security features
6. Global Ordering - View chronological block ordering
7. Data Persistence - Save/load blockchain state
8. User Interface - Interactive menu system

OPTIONAL EXTENSIONS (9-10):
9. P2P Networking - Connect to other nodes
10. Wallet Functionality - Manage cryptographic keys

USAGE:
    python main.py          # Start interactive CLI
    python demo.py          # Run automated demonstration
    python test_blockchain.py  # Run automated tests

FEATURES:
- Interactive menu system with 10 options
- Real-time blockchain visualization
- Transaction creation and management
- Block mining with Proof-of-Work
- Chain validation and integrity checking
- Wallet creation and management
- P2P network operations
- Data persistence operations
- Double-spend prevention demonstration
=============================================================================
"""

import sys
import time
import os
from blockchain import Blockchain, Wallet
from p2p_network import P2PNode

class BlockchainCLI:
    """Command-line interface for the blockchain system"""
    
    def __init__(self):
        self.blockchain = None
        self.p2p_node = None
        self.current_wallet = None
        self.running = True
    
    def start(self):
        """Start the CLI interface"""
        print("=" * 60)
        print("           BLOCKCHAIN CLI INTERFACE")
        print("=" * 60)
        print("Loading blockchain...")
        
        # Try to load existing blockchain or create new one
        self.blockchain = Blockchain(difficulty=4)
        if not self.blockchain.load_from_file("blockchain.pkl"):
            print("No existing blockchain found. Creating new blockchain...")
            self.blockchain.save_to_file("blockchain.pkl")
        
        # Initialize wallets if they don't exist
        if not self.blockchain.wallets:
            self.initialize_wallets()
        
        # Start P2P networking
        self.start_p2p_network()
        
        # Main CLI loop
        self.main_loop()
    
    def initialize_wallets(self):
        """Initialize default wallets with some initial balance"""
        print("Initializing wallets...")
        
        # Create Alice's wallet
        alice_wallet = Wallet("Alice")
        self.blockchain.wallets["Alice"] = alice_wallet
        
        # Create Bob's wallet
        bob_wallet = Wallet("Bob")
        self.blockchain.wallets["Bob"] = bob_wallet
        
        # Create Charlie's wallet
        charlie_wallet = Wallet("Charlie")
        self.blockchain.wallets["Charlie"] = charlie_wallet
        
        # Add initial transactions to give wallets some balance
        genesis_tx = self.blockchain.add_transaction("Genesis", "Alice", 100.0, alice_wallet)
        genesis_tx2 = self.blockchain.add_transaction("Genesis", "Bob", 50.0, bob_wallet)
        genesis_tx3 = self.blockchain.add_transaction("Genesis", "Charlie", 75.0, charlie_wallet)
        
        # Mine the first block with initial transactions
        if genesis_tx and genesis_tx2 and genesis_tx3:
            print("Mining genesis block with initial transactions...")
            self.blockchain.mine_block("Alice")
            self.blockchain.save_to_file("blockchain.pkl")
            print("✓ Genesis block saved to blockchain.pkl")
        
        print("Wallets initialized successfully!")
    
    def start_p2p_network(self):
        """Start the P2P networking component"""
        try:
            self.p2p_node = P2PNode("localhost", 5000, self.blockchain)
            self.p2p_node.start()
            print("P2P networking started on localhost:5000")
        except Exception as e:
            print(f"Failed to start P2P networking: {e}")
            self.p2p_node = None
    
    def main_loop(self):
        """Main CLI loop"""
        while self.running:
            try:
                self.show_menu()
                if not self.process_choice():
                    break
            except KeyboardInterrupt:
                print("\n\nExiting...")
                self.cleanup()
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def show_menu(self):
        """Display the main menu"""
        print("\n" + "="*50)
        print("           BLOCKCHAIN INTERFACE")
        print("="*50)
        print("1.  View Blockchain")
        print("2.  View Balances")
        print("3.  Create Transaction")
        print("4.  Mine Block")
        print("5.  Validate Chain")
        print("6.  Create Wallet")
        print("7.  P2P Operations")
        print("8.  Save/Load Blockchain")
        print("9.  Demo Double-Spend Prevention")

        print("10. Exit")
        print("="*50)

    def process_choice(self):
        """Process user menu choice"""
        choice = input("\nEnter your choice (1-10): ").strip()
        
        if choice == "1":
            self.view_blockchain()
        elif choice == "2":
            self.view_balances()
        elif choice == "3":
            self.create_transaction()
        elif choice == "4":
            self.mine_block()
        elif choice == "5":
            self.validate_chain()
        elif choice == "6":
            self.create_wallet()
        elif choice == "7":
            self.p2p_operations()
        elif choice == "8":
            self.save_load_operations()
        elif choice == "9":
            self.demo_double_spend_prevention()

        elif choice == "10":
            print("\nExiting...")
            return False
        else:
            print("Invalid choice. Please enter a number between 1-10.")
        
        return True
    
    def view_blockchain(self):
        """Display the entire blockchain"""
        self.blockchain.print_chain()
    
    def view_balances(self):
        """Display all wallet balances"""
        self.blockchain.print_balances()
    
    def create_transaction(self):
        """Create a new transaction"""
        print("\n--- CREATE TRANSACTION ---")
        
        # Show available wallets
        print("Available wallets:")
        for i, wallet_name in enumerate(self.blockchain.wallets.keys(), 1):
            balance = self.blockchain.get_balance(wallet_name)
            print(f"{i}. {wallet_name} (Balance: {balance})")
        
        try:
            sender_idx = int(input("Select sender wallet (number): ")) - 1
            sender_name = list(self.blockchain.wallets.keys())[sender_idx]
            
            recipient_idx = int(input("Select recipient wallet (number): ")) - 1
            recipient_name = list(self.blockchain.wallets.keys())[recipient_idx]
            
            amount = float(input("Enter amount: "))
            
            if amount <= 0:
                print("Amount must be positive!")
                return
            
            # Get the sender's wallet
            sender_wallet = self.blockchain.wallets[sender_name]
            
            # Create and add transaction
            if self.blockchain.add_transaction(sender_name, recipient_name, amount, sender_wallet):
                print("Transaction created successfully!")
                if self.p2p_node:
                    # Find the transaction we just created
                    for tx in self.blockchain.pending_transactions:
                        if (tx.sender == sender_name and 
                            tx.recipient == recipient_name and 
                            tx.amount == amount):
                            self.p2p_node.broadcast_transaction(tx)
                            break
            else:
                print("Failed to create transaction!")
                
        except (ValueError, IndexError):
            print("Invalid input!")
    
    def mine_block(self):
        """Mine a new block"""
        if not self.blockchain.pending_transactions:
            print("No pending transactions to mine. Create some transactions first.")
            return
        
        print("\n--- MINING BLOCK ---")
        print(f"Current difficulty: {self.blockchain.difficulty}")
        print(f"Target block time: {self.blockchain.target_block_time} seconds")
        print(f"Pending transactions: {len(self.blockchain.pending_transactions)}")
        
        # Show what transactions are pending
        for i, tx in enumerate(self.blockchain.pending_transactions):
            if tx.sender == "System":
                print(f"  {i+1}. Mining Reward: {tx.amount} coins → {tx.recipient}")
            else:
                print(f"  {i+1}. {tx.sender} → {tx.recipient}: {tx.amount} coins")
        
        # Let user select the miner
        print("\nSelect miner for this block:")
        wallet_names = list(self.blockchain.wallets.keys())
        for i, wallet_name in enumerate(wallet_names, 1):
            balance = self.blockchain.get_balance(wallet_name)
            print(f"{i}. {wallet_name} (Balance: {balance})")
        
        try:
            miner_idx = int(input("Select miner wallet (number): ")) - 1
            if miner_idx < 0 or miner_idx >= len(wallet_names):
                print("Invalid miner selection!")
                return
            miner_address = wallet_names[miner_idx]
        except (ValueError, IndexError):
            print("Invalid input! Please enter a valid number.")
            return
        
        print(f"Miner: {miner_address}")
        print("Mining... (this may take a moment)")
        
        start_time = time.time()
        new_block = self.blockchain.mine_block(miner_address)
        mining_time = time.time() - start_time
        
        if new_block:
            print(f"\n✓ Block mined successfully!")
            print(f"  Block Index: {new_block.index}")
            print(f"  Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(new_block.timestamp))}")
            print(f"  Hash: {new_block.hash[:20]}...")
            print(f"  Nonce: {new_block.nonce}")
            print(f"  Difficulty: {new_block.difficulty}")
            print(f"  Mining Time: {mining_time:.2f} seconds")
            print(f"  Mining Reward: {self.blockchain.mining_reward} coins")
            
            # Show difficulty change if this isn't the first block
            if len(self.blockchain.chain) > 1:
                prev_block = self.blockchain.chain[-2]
                if new_block.difficulty > prev_block.difficulty:
                    print(f"  ✓ Difficulty increased from {prev_block.difficulty} to {new_block.difficulty}")
                elif new_block.difficulty < prev_block.difficulty:
                    print(f"  ✓ Difficulty decreased from {prev_block.difficulty} to {new_block.difficulty}")
                else:
                    print(f"  ✓ Difficulty remained at {new_block.difficulty}")
            
            print(f"  Transactions: {len(new_block.transactions)}")
            print(f"  Previous Hash: {new_block.previous_hash[:20]}...")
            
            # Show reward transaction details
            reward_tx = None
            for tx in new_block.transactions:
                if tx.sender == "System":
                    reward_tx = tx
                    break
            
            if reward_tx:
                print(f"  Mining Reward: {reward_tx.amount} coins → {reward_tx.recipient}")
            
            print(f"\nChain length: {len(self.blockchain.chain)}")
            print(f"Current difficulty: {self.blockchain.difficulty}")
            
            # Save blockchain after successful mining
            self.blockchain.save_to_file("blockchain.pkl")
            print("✓ Blockchain saved to blockchain.pkl")
        else:
            print("Failed to mine block.")
    
    def validate_chain(self):
        """Validate the blockchain integrity"""
        print("\n--- VALIDATE BLOCKCHAIN ---")
        
        if self.blockchain.is_chain_valid():
            print("✅ Blockchain is valid!")
            print(f"Chain length: {len(self.blockchain.chain)}")
            print(f"Total transactions: {sum(len(block.transactions) for block in self.blockchain.chain)}")
            
            # Show difficulty information
            if len(self.blockchain.chain) > 1:
                print(f"Current difficulty: {self.blockchain.difficulty}")
                print(f"Target block time: {self.blockchain.target_block_time} seconds")
                print(f"Mining reward: {self.blockchain.mining_reward} coins")
        else:
            print("❌ Blockchain is invalid!")
    
    def create_wallet(self):
        """Create a new wallet"""
        print("\n--- CREATE NEW WALLET ---")
        
        wallet_name = input("Enter wallet name: ").strip()
        
        if wallet_name in self.blockchain.wallets:
            print("Wallet name already exists!")
            return
        
        if not wallet_name:
            print("Wallet name cannot be empty!")
            return
        
        # Create new wallet
        new_wallet = Wallet(wallet_name)
        self.blockchain.wallets[wallet_name] = new_wallet
        
        print(f"Wallet '{wallet_name}' created successfully!")
        print(f"Public key: {new_wallet.public_key_pem[:50]}...")
    
    def p2p_operations(self):
        """P2P network operations"""
        if not self.p2p_node:
            print("P2P networking is not available!")
            return
        
        print("\n--- P2P NETWORK OPERATIONS ---")
        print("1. Add peer")
        print("2. Remove peer")
        print("3. View peers")
        print("4. Sync with network")
        print("5. View network info")
        print("6. Back to main menu")
        
        choice = input("Enter choice: ").strip()
        
        if choice == "1":
            peer_address = input("Enter peer address (host:port): ").strip()
            self.p2p_node.add_peer(peer_address)
        elif choice == "2":
            peer_address = input("Enter peer address to remove: ").strip()
            self.p2p_node.remove_peer(peer_address)
        elif choice == "3":
            peers = list(self.p2p_node.peers)
            if peers:
                print("Connected peers:")
                for peer in peers:
                    print(f"  - {peer}")
            else:
                print("No peers connected")
        elif choice == "4":
            print("Syncing with network...")
            self.p2p_node.sync_with_network()
        elif choice == "5":
            info = self.p2p_node.get_network_info()
            print("Network Information:")
            for key, value in info.items():
                print(f"  {key}: {value}")
    
    def save_load_operations(self):
        """Save/load blockchain operations"""
        print("\n--- SAVE/LOAD OPERATIONS ---")
        print("1. Save blockchain")
        print("2. Load blockchain")
        print("3. Back to main menu")
        
        choice = input("Enter choice: ").strip()
        
        if choice == "1":
            filename = input("Enter filename (default: blockchain.pkl): ").strip()
            if not filename:
                filename = "blockchain.pkl"
            self.blockchain.save_to_file(filename)
            print(f"✓ Blockchain saved to {filename}")
        elif choice == "2":
            filename = input("Enter filename to load (default: blockchain.pkl): ").strip()
            if not filename:
                filename = "blockchain.pkl"
            if self.blockchain.load_from_file(filename):
                print(f"✓ Blockchain loaded successfully from {filename}!")
            else:
                print(f"✗ Failed to load blockchain from {filename}!")
        elif choice == "3":
            return
        else:
            print("Invalid choice!")
    
    def demo_double_spend_prevention(self):
        """Demonstrate double-spend prevention"""
        print("\n--- DOUBLE-SPEND PREVENTION DEMO ---")
        
        if "Alice" not in self.blockchain.wallets:
            print("Alice wallet not found!")
            return
        
        alice_wallet = self.blockchain.wallets["Alice"]
        alice_balance = self.blockchain.get_balance("Alice")
        
        print(f"Alice's current balance: {alice_balance}")
        
        if alice_balance < 60:
            print("Alice needs at least 60 coins for this demo!")
            return
        
        print("\nAttempting double-spend...")
        print("1. Creating first transaction: Alice -> Bob: 30 coins")
        tx1 = self.blockchain.add_transaction("Alice", "Bob", 30.0, alice_wallet)
        
        print("2. Creating second transaction: Alice -> Charlie: 40 coins")
        tx2 = self.blockchain.add_transaction("Alice", "Charlie", 40.0, alice_wallet)
        
        if tx1 and not tx2:
            print("✅ Double-spend prevention working!")
            print("First transaction was accepted, second was rejected.")
            print("Alice's balance after first transaction: {self.blockchain.get_balance('Alice')}")
        else:
            print("❌ Double-spend prevention failed!")


        
        input("\nPress Enter to return to main menu...")
    
    def cleanup(self):
        """Clean up resources before exit"""
        print("Cleaning up...")
        
        if self.p2p_node:
            self.p2p_node.stop()
        
        if self.blockchain:
            self.blockchain.save_to_file("blockchain.pkl")
            print("✓ Blockchain saved to blockchain.pkl")
        
        print("Cleanup complete. Goodbye!")

def main():
    """Main entry point"""
    try:
        cli = BlockchainCLI()
        cli.start()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
