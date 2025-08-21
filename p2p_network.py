# =============================================================================
# P2P NETWORKING MODULE - INTE264 Assignment 2 (Optional Extension 9)
# =============================================================================
# This module implements peer-to-peer networking functionality for the blockchain.
# It enables nodes to communicate, share transactions and blocks, and maintain
# network consensus.
#
# FEATURES IMPLEMENTED:
# - Node communication and message handling
# - Transaction broadcasting across the network
# - Block synchronization between nodes
# - Peer discovery and management
# - Network state monitoring
#
# NETWORK PROTOCOL:
# - TCP-based communication for reliability
# - JSON message format for easy parsing
# - Threaded message handling for concurrency
# - Automatic peer management and cleanup
# =============================================================================

import socket          # For network communication
import threading       # For concurrent message handling
import json            # For message serialization
import time            # For timing and delays
from typing import List, Dict, Set  # Type hints for better code clarity
from blockchain import Blockchain, Block, Transaction  # Core blockchain classes

class P2PNode:
    """Represents a node in the P2P network"""
    
    def __init__(self, host: str, port: int, blockchain: Blockchain):
        self.host = host
        self.port = port
        self.blockchain = blockchain
        self.peers: Set[str] = set()  # Set of peer addresses (host:port)
        self.server_socket = None
        self.running = False
        
    def start(self):
        """Start the P2P node"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.running = True
        
        print(f"P2P Node started on {self.host}:{self.port}")
        
        # Start listening for connections
        listen_thread = threading.Thread(target=self.listen_for_connections)
        listen_thread.daemon = True
        listen_thread.start()
    
    def stop(self):
        """Stop the P2P node"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        print(f"P2P Node stopped on {self.host}:{self.port}")
    
    def add_peer(self, peer_address: str):
        """Add a peer to the network"""
        if peer_address != f"{self.host}:{self.port}":
            self.peers.add(peer_address)
            print(f"Added peer: {peer_address}")
    
    def remove_peer(self, peer_address: str):
        """Remove a peer from the network"""
        self.peers.discard(peer_address)
        print(f"Removed peer: {peer_address}")
    
    def listen_for_connections(self):
        """Listen for incoming connections from other nodes"""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                client_thread = threading.Thread(
                    target=self.handle_client_connection,
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
            except Exception as e:
                if self.running:
                    print(f"Error accepting connection: {e}")
    
    def handle_client_connection(self, client_socket: socket.socket, address):
        """Handle incoming connection from a client"""
        try:
            data = client_socket.recv(4096).decode('utf-8')
            if data:
                message = json.loads(data)
                self.process_message(message, address)
        except Exception as e:
            print(f"Error handling client connection: {e}")
        finally:
            client_socket.close()
    
    def process_message(self, message: Dict, address):
        """Process incoming messages from peers"""
        message_type = message.get('type')
        
        if message_type == 'new_transaction':
            self.handle_new_transaction(message['transaction'])
        elif message_type == 'new_block':
            self.handle_new_block(message['block'])
        elif message_type == 'chain_request':
            self.send_chain(address)
        elif message_type == 'chain_response':
            self.handle_chain_response(message['chain'])
        elif message_type == 'peer_discovery':
            self.handle_peer_discovery(message['peers'])
    
    def broadcast_transaction(self, transaction: Transaction):
        """Broadcast a new transaction to all peers"""
        message = {
            'type': 'new_transaction',
            'transaction': {
                'sender': transaction.sender,
                'recipient': transaction.recipient,
                'amount': transaction.amount,
                'transaction_id': transaction.transaction_id,
                'timestamp': transaction.timestamp,
                'signature': transaction.signature
            }
        }
        self.broadcast_message(message)
    
    def broadcast_block(self, block: Block):
        """Broadcast a new block to all peers"""
        message = {
            'type': 'new_block',
            'block': {
                'index': block.index,
                'timestamp': block.timestamp,
                'transactions': [tx.to_dict() for tx in block.transactions],
                'previous_hash': block.previous_hash,
                'nonce': block.nonce,
                'difficulty': block.difficulty,
                'merkle_root': block.merkle_root,
                'hash': block.hash
            }
        }
        self.broadcast_message(message)
    
    def broadcast_message(self, message: Dict):
        """Broadcast a message to all peers"""
        message_str = json.dumps(message)
        
        for peer in self.peers:
            try:
                host, port = peer.split(':')
                port = int(port)
                
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((host, port))
                client_socket.send(message_str.encode('utf-8'))
                client_socket.close()
            except Exception as e:
                print(f"Failed to send message to {peer}: {e}")
                self.remove_peer(peer)
    
    def handle_new_transaction(self, transaction_data: Dict):
        """Handle a new transaction from a peer"""
        # Create transaction object
        transaction = Transaction(
            sender=transaction_data['sender'],
            recipient=transaction_data['recipient'],
            amount=transaction_data['amount'],
            transaction_id=transaction_data['transaction_id'],
            timestamp=transaction_data['timestamp'],
            signature=transaction_data['signature']
        )
        
        # Add to pending transactions if not already present
        if not any(tx.transaction_id == transaction.transaction_id 
                  for tx in self.blockchain.pending_transactions):
            self.blockchain.pending_transactions.append(transaction)
            print(f"Received new transaction from peer: {transaction.sender} -> {transaction.recipient}")
    
    def handle_new_block(self, block_data: Dict):
        """Handle a new block from a peer"""
        # Create block object
        transactions = []
        for tx_data in block_data['transactions']:
            tx = Transaction(
                sender=tx_data['sender'],
                recipient=tx_data['recipient'],
                amount=tx_data['amount'],
                transaction_id=tx_data['transaction_id'],
                timestamp=tx_data['timestamp'],
                signature=tx_data.get('signature')
            )
            transactions.append(tx)
        
        block = Block(
            index=block_data['index'],
            timestamp=block_data['timestamp'],
            transactions=transactions,
            previous_hash=block_data['previous_hash'],
            nonce=block_data['nonce'],
            difficulty=block_data['difficulty'],
            merkle_root=block_data['merkle_root']
        )
        block.hash = block_data['hash']
        
        # Add block if it's valid and extends our chain
        if (self.blockchain.is_block_valid(block) and 
            block.previous_hash == self.blockchain.get_latest_block().hash):
            self.blockchain.add_block(block)
            print(f"Received new block from peer: Block #{block.index}")
            
            # Remove transactions that are now in the block
            block_tx_ids = {tx.transaction_id for tx in block.transactions}
            self.blockchain.pending_transactions = [
                tx for tx in self.blockchain.pending_transactions
                if tx.transaction_id not in block_tx_ids
            ]
    
    def request_chain(self, peer_address: str):
        """Request the blockchain from a specific peer"""
        try:
            host, port = peer_address.split(':')
            port = int(port)
            
            message = {'type': 'chain_request'}
            message_str = json.dumps(message)
            
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((host, port))
            client_socket.send(message_str.encode('utf-8'))
            client_socket.close()
        except Exception as e:
            print(f"Failed to request chain from {peer_address}: {e}")
    
    def send_chain(self, address):
        """Send the blockchain to a requesting peer"""
        try:
            host, port = address
            peer_address = f"{host}:{port}"
            
            # Convert blockchain to serializable format
            chain_data = []
            for block in self.blockchain.chain:
                block_dict = block.to_dict()
                block_dict['hash'] = block.hash
                chain_data.append(block_dict)
            
            message = {
                'type': 'chain_response',
                'chain': chain_data
            }
            message_str = json.dumps(message)
            
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((host, port))
            client_socket.send(message_str.encode('utf-8'))
            client_socket.close()
        except Exception as e:
            print(f"Failed to send chain to {address}: {e}")
    
    def handle_chain_response(self, chain_data: List[Dict]):
        """Handle blockchain response from a peer"""
        # Implement longest chain rule
        if len(chain_data) > len(self.blockchain.chain):
            # Validate the received chain
            if self.validate_received_chain(chain_data):
                self.blockchain.chain = []
                for block_data in chain_data:
                    transactions = []
                    for tx_data in block_data['transactions']:
                        tx = Transaction(
                            sender=tx_data['sender'],
                            recipient=tx_data['recipient'],
                            amount=tx_data['amount'],
                            transaction_id=tx_data['transaction_id'],
                            timestamp=tx_data['timestamp'],
                            signature=tx_data.get('signature')
                        )
                        transactions.append(tx)
                    
                    block = Block(
                        index=block_data['index'],
                        timestamp=block_data['timestamp'],
                        transactions=transactions,
                        previous_hash=block_data['previous_hash'],
                        nonce=block_data['nonce'],
                        difficulty=block_data['difficulty'],
                        merkle_root=block_data['merkle_root']
                    )
                    block.hash = block_data['hash']
                    self.blockchain.chain.append(block)
                
                self.blockchain.update_utxo_set()
                print(f"Updated blockchain from peer: {len(chain_data)} blocks")
    
    def validate_received_chain(self, chain_data: List[Dict]) -> bool:
        """Validate a received blockchain"""
        if not chain_data:
            return False
        
        # Check genesis block
        if chain_data[0]['index'] != 0 or chain_data[0]['previous_hash'] != "0":
            return False
        
        # Check chain integrity
        for i in range(1, len(chain_data)):
            current_block = chain_data[i]
            previous_block = chain_data[i - 1]
            
            if current_block['previous_hash'] != previous_block['hash']:
                return False
            
            if current_block['index'] != previous_block['index'] + 1:
                return False
        
        return True
    
    def handle_peer_discovery(self, peers: List[str]):
        """Handle peer discovery message"""
        for peer in peers:
            if peer != f"{self.host}:{self.port}":
                self.add_peer(peer)
    
    def discover_peers(self):
        """Discover peers by broadcasting our address"""
        message = {
            'type': 'peer_discovery',
            'peers': [f"{self.host}:{self.port}"]
        }
        self.broadcast_message(message)
    
    def sync_with_network(self):
        """Sync blockchain with the network"""
        for peer in list(self.peers):
            self.request_chain(peer)
    
    def get_network_info(self) -> Dict:
        """Get information about the P2P network"""
        return {
            'node_address': f"{self.host}:{self.port}",
            'peers': list(self.peers),
            'blockchain_length': len(self.blockchain.chain),
            'pending_transactions': len(self.blockchain.pending_transactions)
        }
