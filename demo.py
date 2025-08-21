#!/usr/bin/env python3

from blockchain import Blockchain, Wallet

def demo_double_spend_prevention():
    """Demonstrate Requirement 5: Double-Spend Prevention"""
    print("\n" + "="*60)
    print("           DEMONSTRATING DOUBLE-SPEND PREVENTION")
    print("="*60)
    
    # Create a fresh blockchain for the demo
    blockchain = Blockchain(difficulty=2)
    
    # Create wallets
    alice_wallet = Wallet("Alice")
    bob_wallet = Wallet("Bob")
    charlie_wallet = Wallet("Charlie")
    
    blockchain.wallets["Alice"] = alice_wallet
    blockchain.wallets["Bob"] = bob_wallet
    blockchain.wallets["Charlie"] = charlie_wallet
    
    print("✓ Wallets created: Alice, Bob, Charlie")
    
    # Give Alice some initial coins
    print("\n✓ Giving Alice 100 coins to start...")
    blockchain.add_transaction("Genesis", "Alice", 100.0, alice_wallet)
    
    # Mine a block to confirm the transaction
    print("✓ Mining block to confirm Alice's coins...")
    block = blockchain.mine_block("Alice")
    
    print(f"✓ Block #{block.index} mined successfully!")
    print(f"  - Alice's balance: {blockchain.get_balance('Alice'):.2f} coins")
    
    print("\n" + "="*60)
    print("           ATTEMPTING DOUBLE-SPEND ATTACK")
    print("="*60)
    
    print("✓ Current wallet balances:")
    for wallet_name in blockchain.wallets:
        balance = blockchain.get_balance(wallet_name)
        print(f"  - {wallet_name}: {balance:.2f} coins")
    
    print("\n✓ Attempting double-spend attack...")
    
    # First transaction (should succeed)
    print("  1. Creating transaction: Alice -> Bob: 50 coins")
    tx1 = blockchain.add_transaction("Alice", "Bob", 50.0, alice_wallet)
    print(f"     Result: {'✓ Success' if tx1 else '✗ Failed'}")
    
    # Second transaction (should fail - double-spend)
    print("  2. Creating transaction: Alice -> Charlie: 60 coins")
    tx2 = blockchain.add_transaction("Alice", "Charlie", 60.0, alice_wallet)
    print(f"     Result: {'✓ Success' if tx2 else '✗ Failed'}")
    
    if tx1 and not tx2:
        print("\n✓ Double-spend prevention working correctly!")
        print("  - First transaction accepted")
        print("  - Second transaction rejected (insufficient balance)")
    else:
        print("\n✗ Double-spend prevention failed!")
    
    print("\n✓ Demonstrating UTXO model...")
    print("  - Each transaction output can only be spent once")
    print("  - Balance is calculated from unspent outputs only")
    print("  - Attempting to spend the same coins twice is automatically rejected")
    
    print("\n✓ Security features:")
    print("  - Transaction validation checks sender balance")
    print("  - UTXO set prevents double-spending")
    print("  - Digital signatures ensure transaction authenticity")
    
    print("\n" + "="*60)
    print("           DOUBLE-SPEND PREVENTION DEMO COMPLETE")
    print("="*60)
    
    return blockchain

if __name__ == "__main__":
    demo_double_spend_prevention()
