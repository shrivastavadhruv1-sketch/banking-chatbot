"""
Natural Language Understanding module for intent classification and entity extraction
"""

import re
from typing import Tuple, List, Dict


class IntentClassifier:
    """Classify user intents from natural language inputs"""
    
    def __init__(self):
        # Define intent patterns
        self.intent_patterns = {
            'check_balance': {
                'keywords': ['balance', 'account balance', 'how much', 'available funds', 'total balance'],
                'patterns': [r'\b(what|how much|check|show|view).*\b(balance|account balance)\b']
            },
            'recent_transactions': {
                'keywords': ['recent transactions', 'last transactions', 'transaction history', 'last activity'],
                'patterns': [r'\b(recent|last|show|check).*\b(transactions|activity|history)\b']
            },
            'transfer_money': {
                'keywords': ['transfer', 'send', 'move money', 'payment'],
                'patterns': [r'\b(transfer|send|pay|move).*\b(money|funds|amount)\b']
            },
            'bill_payment': {
                'keywords': ['bill payment', 'pay bill', 'utility payment', 'credit card payment'],
                'patterns': [r'\b(pay|bill).*\b(bill|utility|credit card|loan)\b']
            },
            'get_offers': {
                'keywords': ['offers', 'deals', 'promotions', 'discounts', 'personalized offer'],
                'patterns': [r'\b(show|get|available).*\b(offers|deals|promotions|discounts)\b']
            },
            'loan_info': {
                'keywords': ['loan', 'loan information', 'loan details', 'interest rate', 'emi'],
                'patterns': [r'\b(loan|emi|interest).*\b(information|details|rate)\b']
            },
            'credit_card_info': {
                'keywords': ['credit card', 'card details', 'card statement', 'card limit'],
                'patterns': [r'\b(credit card|card|card limit|card statement)\b']
            },
            'fraud_alert': {
                'keywords': ['fraud', 'suspicious', 'unauthorized', 'alert'],
                'patterns': [r'\b(fraud|suspicious|unauthorized|alert)\b']
            },
            'account_statement': {
                'keywords': ['statement', 'account statement', 'monthly statement'],
                'patterns': [r'\b(account statement|statement|monthly statement)\b']
            },
            'help': {
                'keywords': ['help', 'support', 'assistance', 'how', 'what can you do'],
                'patterns': [r'\b(help|support|assist|what can you do|how can you help)\b']
            },
            'greeting': {
                'keywords': ['hello', 'hi', 'hey', 'greetings'],
                'patterns': [r'^\b(hello|hi|hey|greetings|good morning|good afternoon)\b']
            },
            'goodbye': {
                'keywords': ['bye', 'goodbye', 'farewell', 'see you later'],
                'patterns': [r'\b(bye|goodbye|farewell|see you later|take care)\b']
            }
        }
    
    def classify(self, text: str) -> Tuple[str, float]:
        """
        Classify the intent of the input text
        Returns: (intent, confidence)
        """
        text_lower = text.lower().strip()
        
        max_confidence = 0.0
        predicted_intent = 'general_inquiry'
        
        for intent, config in self.intent_patterns.items():
            # Check patterns
            for pattern in config['patterns']:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    confidence = 0.95
                    if confidence > max_confidence:
                        max_confidence = confidence
                        predicted_intent = intent
                    break
            
            # Check keywords
            if max_confidence < 0.95:
                keyword_matches = sum(1 for keyword in config['keywords'] 
                                     if keyword.lower() in text_lower)
                if keyword_matches > 0:
                    confidence = min(0.9, 0.5 + (keyword_matches * 0.2))
                    if confidence > max_confidence:
                        max_confidence = confidence
                        predicted_intent = intent
        
        return predicted_intent, max_confidence


class EntityExtractor:
    """Extract entities (amounts, dates, account numbers, etc.) from text"""
    
    def __init__(self):
        pass
    
    def extract(self, text: str) -> Dict:
        """
        Extract entities from text
        Returns: dict with extracted entities
        """
        entities = {
            'amount': self._extract_amount(text),
            'account_type': self._extract_account_type(text),
            'recipient': self._extract_recipient(text),
            'date': self._extract_date(text),
            'time_period': self._extract_time_period(text),
            'transaction_type': self._extract_transaction_type(text)
        }
        return entities
    
    @staticmethod
    def _extract_amount(text: str):
        """Extract monetary amounts from text"""
        patterns = [
            r'(?:amount of |amount )?(?:(?:Rs|₹|\$|£|€)\s*)?(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)(?:\s*(?:Rs|₹|\$|£|€))?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    return float(amount_str)
                except ValueError:
                    continue
        return None
    
    @staticmethod
    def _extract_account_type(text: str):
        """Extract account type from text"""
        account_types = ['savings', 'checking', 'credit card', 'investment', 'demat']
        text_lower = text.lower()
        
        for acc_type in account_types:
            if acc_type in text_lower:
                return acc_type
        return None
    
    @staticmethod
    def _extract_recipient(text: str):
        """Extract recipient information from text"""
        patterns = [
            r'to\s+(\w+(?:\s+\w+)*)',
            r'recipient\s*:?\s*(\w+(?:\s+\w+)*)',
            r'pay\s+(\w+(?:\s+\w+)*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    @staticmethod
    def _extract_date(text: str):
        """Extract date references from text"""
        date_patterns = {
            'today': r'\btoday\b',
            'yesterday': r'\byesterday\b',
            'last_week': r'\blast\s+week\b',
            'last_month': r'\blast\s+month\b',
            'last_year': r'\blast\s+year\b'
        }
        
        for date_ref, pattern in date_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                return date_ref
        return None
    
    @staticmethod
    def _extract_time_period(text: str):
        """Extract time period from text"""
        text_lower = text.lower()
        
        if 'last 7 days' in text_lower or 'week' in text_lower:
            return '7_days'
        elif 'last 30 days' in text_lower or 'month' in text_lower:
            return '30_days'
        elif 'last 3 months' in text_lower or 'quarter' in text_lower:
            return '90_days'
        elif 'last 6 months' in text_lower:
            return '180_days'
        elif 'last year' in text_lower or 'year' in text_lower:
            return '365_days'
        
        return None
    
    @staticmethod
    def _extract_transaction_type(text: str):
        """Extract transaction type from text"""
        transaction_types = {
            'debit': [r'\bdebit\b', r'\bspent\b', r'\bwithdraw\b'],
            'credit': [r'\bcredit\b', r'\bdeposit\b', r'\breceived\b'],
            'transfer': [r'\btransfer\b', r'\bsend\b'],
            'payment': [r'\bpayment\b', r'\bpay\b']
        }
        
        for trans_type, patterns in transaction_types.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return trans_type
        
        return None


class NLUEngine:
    """Combined NLU engine for intent classification and entity extraction"""
    
    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.entity_extractor = EntityExtractor()
    
    def process(self, text: str) -> Dict:
        """
        Process user input and return intent, confidence, and extracted entities
        """
        intent, confidence = self.intent_classifier.classify(text)
        entities = self.entity_extractor.extract(text)
        
        return {
            'intent': intent,
            'confidence': confidence,
            'entities': entities,
            'original_text': text
        }
