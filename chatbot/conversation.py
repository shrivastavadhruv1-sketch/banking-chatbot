"""
Conversation management for the banking chatbot
"""

from nlu.intent_classifier import NLUEngine
from chatbot.banking_services import (
    BalanceService, TransactionService, OfferService, 
    AlertService, LoanService, StatementService
)
from models.user_model import ConversationHistory, User
from config import MAX_CONVERSATION_HISTORY
from typing import Dict, Tuple, List
import json


class ConversationManager:
    """Manages conversation state and flow"""
    
    def __init__(self):
        self.nlu_engine = NLUEngine()
        self.balance_service = BalanceService()
        self.transaction_service = TransactionService()
        self.offer_service = OfferService()
        self.alert_service = AlertService()
        self.loan_service = LoanService()
        self.statement_service = StatementService()
        self.user_model = User()
        self.conversation_history = ConversationHistory()
        self.responses = ResponseGenerator()
    
    def process_message(self, user_id: int, user_message: str, 
                       account_id: int = None) -> Dict:
        """
        Process user message and generate response
        """
        # Process with NLU
        nlu_result = self.nlu_engine.process(user_message)
        intent = nlu_result['intent']
        confidence = nlu_result['confidence']
        entities = nlu_result['entities']
        
        # Get default account if not specified
        if account_id is None:
            user = self.user_model.get_user(user_id)
            if user:
                accounts = self.balance_service.get_all_accounts_summary(user_id)
                if accounts:
                    account_id = accounts[0]['account_id']
        
        # Generate response based on intent
        response_data = self._handle_intent(
            intent, user_id, account_id, entities, user_message
        )
        
        # Save to conversation history
        self.conversation_history.save_conversation(
            user_id, user_message, response_data['response'],
            intent, confidence
        )
        
        return {
            'response': response_data['response'],
            'intent': intent,
            'confidence': confidence,
            'data': response_data.get('data', None),
            'action': response_data.get('action', None),
            'success': response_data.get('success', True)
        }
    
    def _handle_intent(self, intent: str, user_id: int, account_id: int,
                       entities: Dict, original_message: str) -> Dict:
        """Handle different intents and return appropriate response"""
        
        handlers = {
            'check_balance': self._handle_check_balance,
            'recent_transactions': self._handle_recent_transactions,
            'transfer_money': self._handle_transfer_money,
            'bill_payment': self._handle_bill_payment,
            'get_offers': self._handle_get_offers,
            'loan_info': self._handle_loan_info,
            'credit_card_info': self._handle_credit_card_info,
            'fraud_alert': self._handle_fraud_alert,
            'account_statement': self._handle_account_statement,
            'help': self._handle_help,
            'greeting': self._handle_greeting,
            'goodbye': self._handle_goodbye
        }
        
        handler = handlers.get(intent, self._handle_general_inquiry)
        return handler(user_id, account_id, entities, original_message)
    
    def _handle_check_balance(self, user_id: int, account_id: int,
                             entities: Dict, message: str) -> Dict:
        """Handle balance check request"""
        try:
            if not account_id:
                accounts = self.balance_service.get_all_accounts_summary(user_id)
                if not accounts:
                    return {
                        'response': self.responses.no_accounts(),
                        'success': False
                    }
                
                data = []
                for account in accounts:
                    data.append({
                        'account_type': account['account_type'],
                        'account_number': account['account_number'],
                        'balance': account['balance'],
                        'currency': account['currency']
                    })
                
                return {
                    'response': self.responses.multiple_accounts_balance(data),
                    'data': data,
                    'action': 'display_balances'
                }
            else:
                balance = self.balance_service.get_balance(account_id)
                return {
                    'response': self.responses.balance_response(balance),
                    'data': {'balance': balance, 'account_id': account_id},
                    'action': 'display_balance'
                }
        except Exception as e:
            return {
                'response': self.responses.error_response(str(e)),
                'success': False
            }
    
    def _handle_recent_transactions(self, user_id: int, account_id: int,
                                   entities: Dict, message: str) -> Dict:
        """Handle recent transactions request"""
        try:
            if not account_id:
                return {
                    'response': self.responses.account_required(),
                    'success': False
                }
            
            transactions = self.transaction_service.get_recent_transactions(account_id)
            return {
                'response': self.responses.transactions_response(transactions),
                'data': {'transactions': transactions},
                'action': 'display_transactions'
            }
        except Exception as e:
            return {
                'response': self.responses.error_response(str(e)),
                'success': False
            }
    
    def _handle_transfer_money(self, user_id: int, account_id: int,
                              entities: Dict, message: str) -> Dict:
        """Handle money transfer request"""
        amount = entities.get('amount')
        recipient = entities.get('recipient')
        
        if not amount or not recipient:
            return {
                'response': self.responses.missing_transfer_details(amount, recipient),
                'success': False
            }
        
        return {
            'response': self.responses.transfer_initiated(amount, recipient),
            'data': {
                'amount': amount,
                'recipient': recipient,
                'account_id': account_id
            },
            'action': 'initiate_transfer',
            'requires_confirmation': True
        }
    
    def _handle_bill_payment(self, user_id: int, account_id: int,
                            entities: Dict, message: str) -> Dict:
        """Handle bill payment request"""
        return {
            'response': self.responses.bill_payment_menu(),
            'action': 'show_bill_payment_options',
            'data': {
                'account_id': account_id,
                'payment_types': ['electricity', 'water', 'gas', 'internet', 'mobile']
            }
        }
    
    def _handle_get_offers(self, user_id: int, account_id: int,
                          entities: Dict, message: str) -> Dict:
        """Handle personalized offers request"""
        try:
            offers = self.offer_service.get_personalized_offers(user_id)
            return {
                'response': self.responses.offers_response(offers),
                'data': {'offers': offers},
                'action': 'display_offers'
            }
        except Exception as e:
            return {
                'response': self.responses.error_response(str(e)),
                'success': False
            }
    
    def _handle_loan_info(self, user_id: int, account_id: int,
                         entities: Dict, message: str) -> Dict:
        """Handle loan information request"""
        loans = self.loan_service.get_available_loans(user_id)
        return {
            'response': self.responses.loan_info_response(loans),
            'data': {'loans': loans},
            'action': 'display_loan_products'
        }
    
    def _handle_credit_card_info(self, user_id: int, account_id: int,
                                entities: Dict, message: str) -> Dict:
        """Handle credit card information request"""
        return {
            'response': self.responses.credit_card_menu(),
            'action': 'show_credit_card_options'
        }
    
    def _handle_fraud_alert(self, user_id: int, account_id: int,
                           entities: Dict, message: str) -> Dict:
        """Handle fraud alert inquiry"""
        alerts = self.alert_service.get_unread_alerts(user_id)
        return {
            'response': self.responses.fraud_alerts_response(alerts),
            'data': {'alerts': alerts},
            'action': 'display_alerts'
        }
    
    def _handle_account_statement(self, user_id: int, account_id: int,
                                 entities: Dict, message: str) -> Dict:
        """Handle account statement request"""
        return {
            'response': self.responses.statement_period_prompt(),
            'action': 'get_statement_period'
        }
    
    def _handle_help(self, user_id: int, account_id: int,
                    entities: Dict, message: str) -> Dict:
        """Handle help request"""
        return {
            'response': self.responses.help_menu(),
            'action': 'show_help'
        }
    
    def _handle_greeting(self, user_id: int, account_id: int,
                        entities: Dict, message: str) -> Dict:
        """Handle greeting"""
        user = self.user_model.get_user(user_id)
        username = user['full_name'] if user else 'User'
        return {
            'response': self.responses.greeting_response(username),
            'action': 'greeting'
        }
    
    def _handle_goodbye(self, user_id: int, account_id: int,
                       entities: Dict, message: str) -> Dict:
        """Handle goodbye"""
        return {
            'response': self.responses.goodbye_response(),
            'action': 'goodbye'
        }
    
    def _handle_general_inquiry(self, user_id: int, account_id: int,
                               entities: Dict, message: str) -> Dict:
        """Handle general inquiry"""
        return {
            'response': self.responses.general_inquiry_response(),
            'action': 'show_help'
        }


class ResponseGenerator:
    """Generate natural language responses"""
    
    def greeting_response(self, name: str) -> str:
        """Generate greeting response"""
        return f"Hello {name}! Welcome to our banking assistant. How can I help you today? You can ask me to check your balance, view recent transactions, explore offers, or get information about loans and credit cards."
    
    def balance_response(self, balance: float) -> str:
        """Generate balance response"""
        return f"Your current account balance is ₹{balance:,.2f}. Is there anything else you'd like to know?"
    
    def multiple_accounts_balance(self, accounts: List[Dict]) -> str:
        """Generate response for multiple accounts"""
        response = "Here are your account balances:\n"
        for account in accounts:
            response += f"- {account['account_type'].title()}: ₹{account['balance']:,.2f}\n"
        return response
    
    def transactions_response(self, transactions: List[Dict]) -> str:
        """Generate recent transactions response"""
        if not transactions:
            return "You have no recent transactions."
        
        response = "Here are your 10 most recent transactions:\n"
        for trans in transactions[:5]:
            response += f"- {trans['description']}: ₹{trans['amount']} ({trans['timestamp']})\n"
        response += f"\nShowing 5 out of {len(transactions)} transactions. Would you like to see more?"
        return response
    
    def transfer_initiated(self, amount: float, recipient: str) -> str:
        """Generate transfer initiation response"""
        return f"I'm ready to transfer ₹{amount:,.2f} to {recipient}. Please confirm this transaction."
    
    def missing_transfer_details(self, amount, recipient) -> str:
        """Generate response for missing transfer details"""
        missing = []
        if not amount:
            missing.append("amount")
        if not recipient:
            missing.append("recipient")
        return f"Please provide the {' and '.join(missing)} for the transfer."
    
    def offers_response(self, offers: List[Dict]) -> str:
        """Generate personalized offers response"""
        if not offers:
            return "No personalized offers available at this time. Check back soon!"
        
        response = "Here are your personalized offers:\n"
        for i, offer in enumerate(offers, 1):
            discount = offer.get('discount_percentage') or offer.get('discount_amount')
            response += f"{i}. {offer['title']} - {offer['description']} (Code: {offer['code']})\n"
        return response
    
    def loan_info_response(self, loans: List[Dict]) -> str:
        """Generate loan information response"""
        response = "Here are our available loan products:\n"
        for i, loan in enumerate(loans, 1):
            response += f"\n{i}. {loan['product']}\n"
            response += f"   Amount: {loan['amount_range']}\n"
            response += f"   Interest Rate: {loan['interest_rate']}\n"
            response += f"   Tenure: {loan['tenure']}\n"
        return response
    
    def bill_payment_menu(self) -> str:
        """Generate bill payment menu"""
        return "Which bill would you like to pay?\n1. Electricity\n2. Water\n3. Gas\n4. Internet\n5. Mobile"
    
    def credit_card_menu(self) -> str:
        """Generate credit card menu"""
        return "Credit Card Services:\n1. Check Card Details\n2. View Card Statement\n3. Report Lost Card\n4. Apply for New Card"
    
    def help_menu(self) -> str:
        """Generate help menu"""
        return """I can help you with:
1. Check Account Balance
2. View Recent Transactions
3. Transfer Money
4. Pay Bills
5. View Personalized Offers
6. Loan Information
7. Credit Card Services
8. Fraud Alerts

What would you like to do?"""
    
    def fraud_alerts_response(self, alerts: List[Dict]) -> str:
        """Generate fraud alerts response"""
        if not alerts:
            return "No fraud alerts. Your account is secure!"
        
        response = f"You have {len(alerts)} alerts:\n"
        for alert in alerts:
            response += f"- {alert['title']}: {alert['message']}\n"
        return response
    
    def statement_period_prompt(self) -> str:
        """Generate statement period prompt"""
        return "Which period would you like to view? (Last 7 days, Last 30 days, Last 90 days, Last Year, or specific month/year)"
    
    def goodbye_response(self) -> str:
        """Generate goodbye response"""
        return "Thank you for using our banking assistant. Have a great day!"
    
    def general_inquiry_response(self) -> str:
        """Generate general inquiry response"""
        return "I'm not sure I understood that. You can ask me to check your balance, view transactions, explore offers, or get banking information. How can I help?"
    
    def no_accounts(self) -> str:
        """Generate no accounts response"""
        return "No accounts found for your profile. Please contact customer support."
    
    def account_required(self) -> str:
        """Generate account required response"""
        return "Please select an account first."
    
    def error_response(self, error: str) -> str:
        """Generate error response"""
        return f"An error occurred: {error}. Please try again later or contact support."
