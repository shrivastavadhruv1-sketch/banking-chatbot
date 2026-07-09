"""
Unit tests for the banking chatbot
"""

import unittest
import json
from datetime import datetime
from models.user_model import User, Account, Transaction, Alert, Offer, Database
from nlu.intent_classifier import IntentClassifier, EntityExtractor
from chatbot.banking_services import (
    BalanceService, TransactionService, OfferService, AlertService
)


class TestIntentClassification(unittest.TestCase):
    """Test intent classification"""
    
    def setUp(self):
        self.classifier = IntentClassifier()
    
    def test_balance_check_intent(self):
        intent, conf = self.classifier.classify("What is my account balance?")
        self.assertEqual(intent, 'check_balance')
        self.assertGreater(conf, 0.7)
    
    def test_transaction_intent(self):
        intent, conf = self.classifier.classify("Show me my recent transactions")
        self.assertEqual(intent, 'recent_transactions')
        self.assertGreater(conf, 0.7)
    
    def test_transfer_intent(self):
        intent, conf = self.classifier.classify("I want to transfer 5000 to John")
        self.assertEqual(intent, 'transfer_money')
        self.assertGreater(conf, 0.7)
    
    def test_offer_intent(self):
        intent, conf = self.classifier.classify("Show me available offers")
        self.assertEqual(intent, 'get_offers')
        self.assertGreater(conf, 0.7)
    
    def test_greeting_intent(self):
        intent, conf = self.classifier.classify("Hello")
        self.assertEqual(intent, 'greeting')
        self.assertGreater(conf, 0.7)


class TestEntityExtraction(unittest.TestCase):
    """Test entity extraction"""
    
    def setUp(self):
        self.extractor = EntityExtractor()
    
    def test_amount_extraction(self):
        text = "Transfer 5000 rupees to my friend"
        entities = self.extractor.extract(text)
        self.assertEqual(entities['amount'], 5000.0)
    
    def test_amount_with_currency(self):
        text = "Send $1500 to John"
        entities = self.extractor.extract(text)
        self.assertEqual(entities['amount'], 1500.0)
    
    def test_recipient_extraction(self):
        text = "Transfer money to Sarah"
        entities = self.extractor.extract(text)
        self.assertEqual(entities['recipient'], 'Sarah')
    
    def test_account_type_extraction(self):
        text = "Check my savings account balance"
        entities = self.extractor.extract(text)
        self.assertEqual(entities['account_type'], 'savings')
    
    def test_time_period_extraction(self):
        text = "Show transactions from last 7 days"
        entities = self.extractor.extract(text)
        self.assertEqual(entities['time_period'], '7_days')


class TestUserModel(unittest.TestCase):
    """Test user model operations"""
    
    def setUp(self):
        self.user_model = User()
        # This would typically use a test database
    
    def test_password_hashing(self):
        password = "test_password123"
        hash1 = User._hash_password(password)
        hash2 = User._hash_password(password)
        self.assertEqual(hash1, hash2)
    
    def test_password_verification(self):
        password = "test_password123"
        hash_val = User._hash_password(password)
        self.assertTrue(User._verify_password(password, hash_val))
        self.assertFalse(User._verify_password("wrong_password", hash_val))


class TestBalanceService(unittest.TestCase):
    """Test balance service"""
    
    def setUp(self):
        self.balance_service = BalanceService()
        # Setup test data
    
    def test_get_balance(self):
        # This would test getting balance
        # Requires database setup
        pass


class TestTransactionService(unittest.TestCase):
    """Test transaction service"""
    
    def setUp(self):
        self.transaction_service = TransactionService()
        # Setup test data
    
    def test_record_transaction(self):
        # This would test recording transactions
        pass


class TestOfferService(unittest.TestCase):
    """Test offer service"""
    
    def setUp(self):
        self.offer_service = OfferService()
    
    def test_generate_offers(self):
        # This would test offer generation
        pass


if __name__ == '__main__':
    unittest.main()
