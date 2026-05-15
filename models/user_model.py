"""
Database models for the banking chatbot
"""

import sqlite3
import json
import os
from datetime import datetime
from config import DATABASE_PATH, DATABASE_URL
import hashlib


class Database:
    """Database connection and initialization"""
    
    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = db_path
        self._ensure_db_dir()
        self.init_database()
    
    def _ensure_db_dir(self):
        """Ensure database directory exists"""
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                full_name TEXT,
                phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                preferences TEXT
            )
        ''')
        
        # Accounts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                account_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                account_type TEXT NOT NULL,
                account_number TEXT UNIQUE NOT NULL,
                balance REAL DEFAULT 0.0,
                currency TEXT DEFAULT 'USD',
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                transaction_type TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                recipient TEXT,
                sender TEXT,
                status TEXT DEFAULT 'completed',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_flagged BOOLEAN DEFAULT 0,
                fraud_score REAL DEFAULT 0.0,
                FOREIGN KEY(account_id) REFERENCES accounts(account_id)
            )
        ''')
        
        # Alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                alert_type TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                is_read BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                action_required BOOLEAN DEFAULT 0,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Offers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS offers (
                offer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                offer_title TEXT NOT NULL,
                offer_description TEXT NOT NULL,
                offer_code TEXT UNIQUE NOT NULL,
                discount_percentage REAL,
                discount_amount REAL,
                min_transaction_amount REAL DEFAULT 0,
                expiry_date TIMESTAMP,
                category TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                personalization_score REAL DEFAULT 0.0,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Conversation History table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_history (
                history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                user_message TEXT NOT NULL,
                bot_response TEXT NOT NULL,
                intent TEXT,
                confidence REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Session Management table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                session_id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                device_info TEXT,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        ''')
        
        conn.commit()
        conn.close()


class User:
    """User model for authentication and profile management"""
    
    def __init__(self):
        self.db = Database()
    
    def create_user(self, username, password, email, full_name, phone=None):
        """Create a new user"""
        try:
            password_hash = self._hash_password(password)
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO users (username, password_hash, email, full_name, phone)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, password_hash, email, full_name, phone))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return user_id
        except sqlite3.IntegrityError:
            return None
    
    def authenticate(self, username, password):
        """Authenticate user"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT user_id, password_hash FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        conn.close()
        
        if row and self._verify_password(password, row['password_hash']):
            return row['user_id']
        return None
    
    def get_user(self, user_id):
        """Get user details"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE user_id = ? AND is_active = 1', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def update_last_login(self, user_id):
        """Update user's last login timestamp"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users SET last_login = CURRENT_TIMESTAMP 
            WHERE user_id = ?
        ''', (user_id,))
        
        conn.commit()
        conn.close()
    
    def update_preferences(self, user_id, preferences):
        """Update user preferences"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users SET preferences = ? 
            WHERE user_id = ?
        ''', (json.dumps(preferences), user_id))
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def _hash_password(password):
        """Hash password with salt"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def _verify_password(password, password_hash):
        """Verify password"""
        return User._hash_password(password) == password_hash


class Account:
    """Account model for managing user accounts"""
    
    def __init__(self):
        self.db = Database()
    
    def create_account(self, user_id, account_type, account_number, initial_balance=0.0):
        """Create a new account"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO accounts (user_id, account_type, account_number, balance)
                VALUES (?, ?, ?, ?)
            ''', (user_id, account_type, account_number, initial_balance))
            
            account_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return account_id
        except sqlite3.IntegrityError:
            conn.close()
            return None
    
    def get_account(self, account_id):
        """Get account details"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM accounts WHERE account_id = ?', (account_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def get_user_accounts(self, user_id):
        """Get all accounts for a user"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM accounts WHERE user_id = ? AND is_active = 1', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_balance(self, account_id):
        """Get account balance"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT balance FROM accounts WHERE account_id = ?', (account_id,))
        row = cursor.fetchone()
        conn.close()
        
        return row['balance'] if row else None
    
    def update_balance(self, account_id, amount):
        """Update account balance"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE accounts SET balance = balance + ? 
            WHERE account_id = ?
        ''', (amount, account_id))
        
        conn.commit()
        conn.close()


class Transaction:
    """Transaction model for managing transactions"""
    
    def __init__(self):
        self.db = Database()
    
    def record_transaction(self, account_id, transaction_type, amount, description, 
                          recipient=None, sender=None):
        """Record a new transaction"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO transactions 
            (account_id, transaction_type, amount, description, recipient, sender)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (account_id, transaction_type, amount, description, recipient, sender))
        
        transaction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return transaction_id
    
    def get_recent_transactions(self, account_id, limit=10):
        """Get recent transactions for an account"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM transactions 
            WHERE account_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (account_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def flag_suspicious_transaction(self, transaction_id, fraud_score):
        """Flag a transaction as suspicious"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE transactions 
            SET is_flagged = 1, fraud_score = ? 
            WHERE transaction_id = ?
        ''', (fraud_score, transaction_id))
        
        conn.commit()
        conn.close()


class Alert:
    """Alert model for transaction alerts and notifications"""
    
    def __init__(self):
        self.db = Database()
    
    def create_alert(self, user_id, alert_type, title, message, action_required=False):
        """Create a new alert"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO alerts (user_id, alert_type, title, message, action_required)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, alert_type, title, message, action_required))
        
        alert_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return alert_id
    
    def get_unread_alerts(self, user_id):
        """Get unread alerts for a user"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM alerts 
            WHERE user_id = ? AND is_read = 0 
            ORDER BY created_at DESC
        ''', (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def mark_alert_as_read(self, alert_id):
        """Mark alert as read"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('UPDATE alerts SET is_read = 1 WHERE alert_id = ?', (alert_id,))
        conn.commit()
        conn.close()
    
    def get_alerts_by_type(self, user_id, alert_type, limit=20):
        """Get alerts filtered by type"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM alerts 
            WHERE user_id = ? AND alert_type = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (user_id, alert_type, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]


class Offer:
    """Offer model for personalized offers"""
    
    def __init__(self):
        self.db = Database()
    
    def create_offer(self, offer_title, offer_description, offer_code, discount_percentage=None,
                    discount_amount=None, min_transaction_amount=0, expiry_date=None, category=None):
        """Create a new offer"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO offers 
            (offer_title, offer_description, offer_code, discount_percentage, 
             discount_amount, min_transaction_amount, expiry_date, category)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (offer_title, offer_description, offer_code, discount_percentage,
              discount_amount, min_transaction_amount, expiry_date, category))
        
        offer_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return offer_id
    
    def get_personalized_offers(self, user_id, limit=5):
        """Get personalized offers for a user"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM offers 
            WHERE (user_id = ? OR user_id IS NULL) AND is_active = 1
            AND (expiry_date IS NULL OR expiry_date > CURRENT_TIMESTAMP)
            ORDER BY personalization_score DESC 
            LIMIT ?
        ''', (user_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def assign_offer_to_user(self, offer_id, user_id, personalization_score):
        """Assign an offer to a user"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO offers 
            (offer_title, offer_description, offer_code, user_id, personalization_score)
            SELECT offer_title, offer_description, offer_code, ?, ?
            FROM offers WHERE offer_id = ?
        ''', (user_id, personalization_score, offer_id))
        
        conn.commit()
        conn.close()


class ConversationHistory:
    """Conversation History model for tracking dialogues"""
    
    def __init__(self):
        self.db = Database()
    
    def save_conversation(self, user_id, user_message, bot_response, intent=None, confidence=None):
        """Save conversation turn"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversation_history 
            (user_id, user_message, bot_response, intent, confidence)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, user_message, bot_response, intent, confidence))
        
        conn.commit()
        conn.close()
    
    def get_conversation_history(self, user_id, limit=50):
        """Get conversation history for a user"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM conversation_history 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (user_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in reversed(rows)]
