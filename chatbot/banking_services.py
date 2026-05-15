"""
Banking services for handling core banking operations
"""

from models.user_model import Account, Transaction, Alert, Offer, ConversationHistory
from config import TRANSACTION_ALERT_THRESHOLD, SUSPICIOUS_TRANSACTION_THRESHOLD
from datetime import datetime, timedelta
from typing import List, Dict


class BalanceService:
    """Service for checking and managing account balances"""
    
    def __init__(self):
        self.account_model = Account()
    
    def get_balance(self, account_id: int) -> float:
        """Get current account balance"""
        return self.account_model.get_balance(account_id)
    
    def get_all_accounts_summary(self, user_id: int) -> List[Dict]:
        """Get summary of all accounts for a user"""
        accounts = self.account_model.get_user_accounts(user_id)
        summary = []
        
        for account in accounts:
            summary.append({
                'account_id': account['account_id'],
                'account_type': account['account_type'],
                'account_number': account['account_number'],
                'balance': account['balance'],
                'currency': account['currency']
            })
        
        return summary
    
    def get_total_balance(self, user_id: int) -> float:
        """Calculate total balance across all accounts"""
        accounts = self.account_model.get_user_accounts(user_id)
        total = sum(account['balance'] for account in accounts)
        return total


class TransactionService:
    """Service for managing transactions and transaction history"""
    
    def __init__(self):
        self.transaction_model = Transaction()
        self.account_model = Account()
        self.alert_service = AlertService()
    
    def record_transaction(self, account_id: int, transaction_type: str, 
                          amount: float, description: str, recipient=None, sender=None) -> int:
        """Record a new transaction"""
        transaction_id = self.transaction_model.record_transaction(
            account_id, transaction_type, amount, description, recipient, sender
        )
        
        # Update balance
        if transaction_type == 'debit':
            self.account_model.update_balance(account_id, -amount)
        else:
            self.account_model.update_balance(account_id, amount)
        
        # Check if alert should be triggered
        self._check_transaction_alerts(account_id, transaction_id, amount)
        
        return transaction_id
    
    def get_recent_transactions(self, account_id: int, limit: int = 10) -> List[Dict]:
        """Get recent transactions for an account"""
        transactions = self.transaction_model.get_recent_transactions(account_id, limit)
        
        formatted_transactions = []
        for trans in transactions:
            formatted_transactions.append({
                'transaction_id': trans['transaction_id'],
                'type': trans['transaction_type'],
                'amount': trans['amount'],
                'description': trans['description'],
                'recipient': trans['recipient'],
                'timestamp': trans['timestamp'],
                'status': trans['status'],
                'is_flagged': bool(trans['is_flagged'])
            })
        
        return formatted_transactions
    
    def _check_transaction_alerts(self, account_id: int, transaction_id: int, amount: float):
        """Check if transaction should trigger alerts"""
        account = self.account_model.get_account(account_id)
        
        # High-value transaction alert
        if amount > TRANSACTION_ALERT_THRESHOLD:
            self.alert_service.create_transaction_alert(
                account['user_id'],
                f"High-value transaction of {amount}",
                f"A transaction of {amount} was made on account {account['account_number']}"
            )
        
        # Suspicious transaction detection
        fraud_score = self._calculate_fraud_score(amount, account['balance'])
        if fraud_score > 0.7:
            self.transaction_model.flag_suspicious_transaction(transaction_id, fraud_score)
            self.alert_service.create_fraud_alert(
                account['user_id'],
                "Suspicious Transaction Detected",
                f"A suspicious transaction of {amount} was detected. Please verify.",
                action_required=True
            )
    
    def _calculate_fraud_score(self, amount: float, current_balance: float) -> float:
        """Calculate fraud score for a transaction"""
        score = 0.0
        
        # If amount is very large compared to balance
        if current_balance > 0 and amount > SUSPICIOUS_TRANSACTION_THRESHOLD:
            score += 0.4
        
        # If amount exceeds typical transaction patterns
        if amount > 500000:
            score += 0.3
        
        return min(score, 1.0)


class OfferService:
    """Service for managing personalized offers"""
    
    def __init__(self):
        self.offer_model = Offer()
        self.balance_service = BalanceService()
        self.transaction_model = Transaction()
    
    def get_personalized_offers(self, user_id: int, limit: int = 5) -> List[Dict]:
        """Get personalized offers for a user"""
        offers = self.offer_model.get_personalized_offers(user_id, limit)
        
        formatted_offers = []
        for offer in offers:
            formatted_offers.append({
                'offer_id': offer['offer_id'],
                'title': offer['offer_title'],
                'description': offer['offer_description'],
                'code': offer['offer_code'],
                'discount_percentage': offer['discount_percentage'],
                'discount_amount': offer['discount_amount'],
                'category': offer['category'],
                'expiry_date': offer['expiry_date']
            })
        
        return formatted_offers
    
    def generate_personalized_offers(self, user_id: int):
        """Generate personalized offers based on user profile"""
        offers = []
        
        # Get user spending patterns
        total_balance = self.balance_service.get_total_balance(user_id)
        
        # Premium offers for high-balance customers
        if total_balance > 1000000:
            offers.append({
                'title': 'Premium Investment Account',
                'description': 'Get higher returns with our premium investment account',
                'code': 'PREMIUM_INV_' + str(user_id),
                'discount_percentage': 10,
                'category': 'investment'
            })
        
        # Loan offers for regular customers
        if total_balance > 100000:
            offers.append({
                'title': 'Personal Loan',
                'description': 'Get instant personal loan with low interest rates',
                'code': 'LOAN_' + str(user_id),
                'discount_amount': 5000,
                'category': 'loan'
            })
        
        # Cashback offers
        offers.append({
            'title': '5% Cashback on all purchases',
            'description': 'Get 5% cashback on every transaction above 1000',
            'code': 'CASHBACK_' + str(user_id),
            'discount_percentage': 5,
            'category': 'cashback'
        })
        
        # Credit card offers
        offers.append({
            'title': 'Premium Credit Card',
            'description': 'Unlimited rewards and exclusive benefits',
            'code': 'CREDIT_CARD_' + str(user_id),
            'category': 'credit_card'
        })
        
        return offers


class AlertService:
    """Service for managing alerts"""
    
    def __init__(self):
        self.alert_model = Alert()
    
    def create_transaction_alert(self, user_id: int, title: str, message: str):
        """Create a transaction alert"""
        return self.alert_model.create_alert(
            user_id, 'transaction', title, message
        )
    
    def create_fraud_alert(self, user_id: int, title: str, message: str, action_required: bool = False):
        """Create a fraud alert"""
        return self.alert_model.create_alert(
            user_id, 'fraud', title, message, action_required
        )
    
    def create_security_alert(self, user_id: int, title: str, message: str):
        """Create a security alert"""
        return self.alert_model.create_alert(
            user_id, 'security', title, message
        )
    
    def get_unread_alerts(self, user_id: int) -> List[Dict]:
        """Get unread alerts for a user"""
        alerts = self.alert_model.get_unread_alerts(user_id)
        
        formatted_alerts = []
        for alert in alerts:
            formatted_alerts.append({
                'alert_id': alert['alert_id'],
                'type': alert['alert_type'],
                'title': alert['title'],
                'message': alert['message'],
                'created_at': alert['created_at'],
                'action_required': bool(alert['action_required'])
            })
        
        return formatted_alerts
    
    def mark_alert_as_read(self, alert_id: int):
        """Mark an alert as read"""
        return self.alert_model.mark_alert_as_read(alert_id)


class FraudDetectionService:
    """Service for detecting fraudulent transactions"""
    
    def __init__(self):
        self.transaction_model = Transaction()
    
    def detect_anomalies(self, user_id: int) -> List[Dict]:
        """Detect anomalous transactions"""
        anomalies = []
        
        # This is a basic implementation
        # In production, you would use machine learning models
        
        return anomalies
    
    def check_geographic_anomaly(self, user_id: int, transaction_location: str) -> bool:
        """Check if transaction location is anomalous"""
        # This would check if user made transactions from
        # geographically distant locations in short time
        return False


class LoanService:
    """Service for loan-related operations"""
    
    def get_available_loans(self, user_id: int) -> List[Dict]:
        """Get available loan products for user"""
        loans = [
            {
                'product': 'Personal Loan',
                'amount_range': '50,000 - 5,000,000',
                'interest_rate': '7.5% - 12.5%',
                'tenure': '1 - 5 years',
                'eligibility': 'Basic eligibility criteria met'
            },
            {
                'product': 'Home Loan',
                'amount_range': '500,000 - 50,000,000',
                'interest_rate': '6.5% - 8.5%',
                'tenure': '5 - 20 years',
                'eligibility': 'Basic eligibility criteria met'
            },
            {
                'product': 'Auto Loan',
                'amount_range': '100,000 - 2,000,000',
                'interest_rate': '8% - 11%',
                'tenure': '1 - 5 years',
                'eligibility': 'Basic eligibility criteria met'
            }
        ]
        return loans


class StatementService:
    """Service for account statements"""
    
    def __init__(self):
        self.transaction_model = Transaction()
    
    def get_monthly_statement(self, account_id: int, month: int, year: int) -> Dict:
        """Get monthly statement for an account"""
        transactions = self.transaction_model.get_recent_transactions(account_id, limit=100)
        
        # Filter transactions for the month
        filtered_transactions = []
        total_debit = 0
        total_credit = 0
        
        for trans in transactions:
            trans_date = datetime.fromisoformat(trans['timestamp'])
            if trans_date.month == month and trans_date.year == year:
                filtered_transactions.append(trans)
                
                if trans['transaction_type'] == 'debit':
                    total_debit += trans['amount']
                else:
                    total_credit += trans['amount']
        
        return {
            'month': month,
            'year': year,
            'transactions': filtered_transactions,
            'total_debit': total_debit,
            'total_credit': total_credit,
            'transaction_count': len(filtered_transactions)
        }
