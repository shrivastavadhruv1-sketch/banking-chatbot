#!/usr/bin/env python
"""
Initialization and verification script for banking chatbot
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def check_imports():
    """Check if all modules can be imported"""
    print("Checking module imports...")
    
    try:
        import config
        print("✓ Config loaded")
    except Exception as e:
        print(f"✗ Config import failed: {e}")
        return False
    
    try:
        from models.user_model import Database, User, Account, Transaction, Alert, Offer
        print("✓ Models loaded")
    except Exception as e:
        print(f"✗ Models import failed: {e}")
        return False
    
    try:
        from nlu.intent_classifier import NLUEngine
        print("✓ NLU Engine loaded")
    except Exception as e:
        print(f"✗ NLU import failed: {e}")
        return False
    
    try:
        from chatbot.banking_services import (
            BalanceService, TransactionService, OfferService, AlertService
        )
        print("✓ Banking Services loaded")
    except Exception as e:
        print(f"✗ Banking Services import failed: {e}")
        return False
    
    try:
        from chatbot.conversation import ConversationManager
        print("✓ Conversation Manager loaded")
    except Exception as e:
        print(f"✗ Conversation Manager import failed: {e}")
        return False
    
    return True

def initialize_database():
    """Initialize the database"""
    print("\nInitializing database...")
    
    try:
        from models.user_model import Database
        db = Database()
        print("✓ Database initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return False

def test_nlu():
    """Test NLU engine"""
    print("\nTesting NLU engine...")
    
    try:
        from nlu.intent_classifier import NLUEngine
        nlu = NLUEngine()
        
        test_queries = [
            "Check my balance",
            "Show recent transactions",
            "Get personalized offers",
            "Hello!"
        ]
        
        for query in test_queries:
            result = nlu.process(query)
            print(f"  Query: '{query}'")
            print(f"    Intent: {result['intent']} (Confidence: {result['confidence']:.2f})")
        
        return True
    except Exception as e:
        print(f"✗ NLU test failed: {e}")
        return False

def create_demo_user():
    """Create a demo user for testing"""
    print("\nCreating demo user...")
    
    try:
        from models.user_model import User, Account
        
        user_model = User()
        account_model = Account()
        
        # Try to create demo user
        user_id = user_model.create_user(
            username="demo_user",
            password="Demo@1234",
            email="demo@banking.com",
            full_name="Demo User",
            phone="9999999999"
        )
        
        if user_id:
            # Create accounts for demo user
            account_model.create_account(user_id, "Savings", f"SAV{user_id:06d}", 50000.0)
            account_model.create_account(user_id, "Checking", f"CHK{user_id:06d}", 20000.0)
            
            print(f"✓ Demo user created successfully (ID: {user_id})")
            print("  Username: demo_user")
            print("  Password: Demo@1234")
            return True
        else:
            print("✓ Demo user already exists")
            return True
            
    except Exception as e:
        print(f"✗ Demo user creation failed: {e}")
        return False

def main():
    """Run all checks"""
    print("=" * 60)
    print("Banking Chatbot - Initialization & Verification")
    print("=" * 60)
    
    checks = [
        ("Module Imports", check_imports),
        ("Database Initialization", initialize_database),
        ("NLU Engine", test_nlu),
        ("Demo User Creation", create_demo_user)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n[{name}]")
        result = check_func()
        results.append((name, result))
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{name}: {status}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✓ All checks passed! The chatbot is ready to run.")
        print("\nTo start the application, run:")
        print("  python app.py")
        return 0
    else:
        print("\n✗ Some checks failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
