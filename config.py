"""
Configuration settings for the banking chatbot application
"""

import os
from datetime import timedelta

# Flask Configuration
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'  # Only enable if explicitly set
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
HOST = os.environ.get('HOST', '0.0.0.0')
PORT = int(os.environ.get('PORT', 5000))

# Database Configuration
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database', 'banking.db')
DATABASE_URL = f'sqlite:///{DATABASE_PATH}'

# Session Configuration
PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Security
PASSWORD_MIN_LENGTH = 8
MAX_LOGIN_ATTEMPTS = 5
LOGIN_ATTEMPT_TIMEOUT = 15 * 60  # 15 minutes

# Chatbot Configuration
MAX_CONVERSATION_HISTORY = 100
RESPONSE_TIMEOUT = 30  # seconds

# Offer Configuration
MIN_BALANCE_FOR_PREMIUM_OFFERS = 100000
OFFER_REFRESH_INTERVAL = 7  # days
MAX_PERSONALIZED_OFFERS = 5

# Transaction Configuration
TRANSACTION_ALERT_THRESHOLD = 50000  # Alert for transactions above this amount
DAILY_TRANSACTION_LIMIT = 500000
SUSPICIOUS_TRANSACTION_THRESHOLD = 100000

# Fraud Detection
FRAUD_ALERT_ENABLED = True
MULTIPLE_LOGIN_ALERT = 3  # Alert after 3 logins in 1 hour
GEOGRAPHIC_ANOMALY_DETECTION = True

# Supported Languages
SUPPORTED_LANGUAGES = ['en', 'es', 'fr', 'de']
DEFAULT_LANGUAGE = 'en'

# Logging Configuration
LOG_LEVEL = 'INFO'
LOG_FILE = os.path.join(os.path.dirname(__file__), 'logs', 'chatbot.log')

# NLU Configuration
NLU_MODEL = 'en_core_web_sm'
CONFIDENCE_THRESHOLD = 0.7
