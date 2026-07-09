# Banking Chatbot

A comprehensive conversational AI chatbot for banking services, featuring personalized offers, balance inquiries, transaction alerts, and fraud detection.

> **⚡ Quick Start**: New to the chatbot? Start with [GETTING_STARTED.md](GETTING_STARTED.md) for a 5-minute setup guide!

> **📚 Documentation**:
> - [Getting Started Guide](GETTING_STARTED.md) - 5-minute quick start
> - [API Documentation](API_DOCUMENTATION.md) - Complete API reference
> - [Deployment Guide](DEPLOYMENT.md) - Production deployment instructions
> - [This README](README.md) - Feature overview and architecture

## Features

### Core Banking Features
- **Account Balance Check** - Real-time balance inquiry for all account types
- **Transaction History** - View recent transactions with detailed information
- **Money Transfer** - Initiate fund transfers between accounts
- **Bill Payment** - Pay utilities, credit cards, and other bills
- **Account Statement** - Download and view monthly/yearly statements

### Intelligent Services
- **Personalized Offers** - AI-driven offers based on user profile and spending patterns
- **Fraud Detection** - Real-time detection of suspicious transactions
- **Transaction Alerts** - Instant notifications for high-value transactions
- **Loan Information** - Details on available loan products
- **Credit Card Services** - Card management and information

### Security & User Management
- **User Authentication** - Secure login with password hashing
- **Session Management** - Secure session handling
- **Profile Management** - User profile and preferences
- **Activity Tracking** - Conversation history and audit logs

## Technology Stack

- **Backend**: Python Flask (REST API)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **NLU**: Custom intent classification and entity extraction
- **Database**: SQLite
- **Authentication**: Session-based with password hashing

## Project Structure

```
banking-chatbot/
├── app.py                      # Main Flask application
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
│
├── models/
│   └── user_model.py          # Database models (User, Account, Transaction, Alert, Offer)
│
├── nlu/
│   └── intent_classifier.py   # Intent classification and entity extraction
│
├── chatbot/
│   ├── conversation.py        # Conversation management
│   └── banking_services.py    # Banking operations
│
├── templates/
│   ├── login.html             # Login page
│   ├── register.html          # Registration page
│   └── chat.html              # Chat interface
│
├── static/
│   ├── css/
│   │   └── style.css          # Application styling
│   └── js/
│       └── script.js          # Chat functionality
│
├── database/
│   └── banking.db             # SQLite database (auto-created)
│
└── tests/
    └── test_chatbot.py        # Unit tests
```

## Installation

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd banking-chatbot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the chatbot**
   - Open your browser and navigate to `http://localhost:5000`
   - Default port is 5000 (configurable in config.py)

## Usage

### Creating an Account
1. Click "Register here" on the login page
2. Fill in your details (Name, Email, Username, Phone)
3. Create a secure password (minimum 8 characters)
4. Click Register
5. You'll be provided with two accounts: Savings and Checking

### Using the Chatbot

#### Checking Balance
- Say: "Check my balance"
- Say: "What is my account balance?"
- Say: "How much do I have?"

#### Viewing Transactions
- Say: "Show recent transactions"
- Say: "Last 10 transactions"
- Say: "Transaction history"

#### Transferring Money
- Say: "Transfer 5000 to John"
- Say: "Send 1000 rupees to savings account"

#### Getting Offers
- Say: "Show personalized offers"
- Say: "Available deals"
- Say: "What discounts do I get?"

#### Checking Alerts
- Say: "Show fraud alerts"
- Say: "Any suspicious transactions?"
- Say: "What's my recent activity?"

#### Getting Loan Information
- Say: "Tell me about loans"
- Say: "What are loan options?"
- Say: "Personal loan information"

## Key Components

### Intent Classification
The chatbot recognizes the following intents:
- check_balance
- recent_transactions
- transfer_money
- bill_payment
- get_offers
- loan_info
- credit_card_info
- fraud_alert
- account_statement
- help
- greeting
- goodbye

### Entity Extraction
Automatically extracts:
- Monetary amounts
- Account types
- Recipient information
- Time periods
- Transaction types

### Services

#### BalanceService
- Get account balance
- Get all accounts summary
- Calculate total balance

#### TransactionService
- Record transactions
- Get transaction history
- Detect fraudulent transactions
- Trigger alerts

#### OfferService
- Generate personalized offers
- Get active offers
- Assign offers to users

#### AlertService
- Create transaction alerts
- Create fraud alerts
- Get unread alerts
- Mark alerts as read

## Configuration

Edit `config.py` to customize:

```python
# Server
HOST = '0.0.0.0'
PORT = 5000
DEBUG = True

# Database
DATABASE_PATH = 'database/banking.db'

# Security
PASSWORD_MIN_LENGTH = 8
MAX_LOGIN_ATTEMPTS = 5

# Offers
MIN_BALANCE_FOR_PREMIUM_OFFERS = 100000
MAX_PERSONALIZED_OFFERS = 5

# Transactions
TRANSACTION_ALERT_THRESHOLD = 50000
SUSPICIOUS_TRANSACTION_THRESHOLD = 100000
```

## API Endpoints

### Authentication
- `POST /register` - Register new user
- `POST /login` - User login
- `GET /logout` - User logout

### Chat
- `POST /api/chat` - Send message to chatbot
- `GET /api/profile` - Get user profile
- `GET /api/accounts` - Get user accounts
- `GET /api/balance/<account_id>` - Get account balance
- `GET /api/alerts` - Get user alerts
- `GET /api/offers` - Get personalized offers

## Testing

Run the test suite:
```bash
python -m unittest discover tests/
```

Run specific tests:
```bash
python -m unittest tests.test_chatbot.TestIntentClassification
```

## Security Considerations

1. **Password Security**: Passwords are hashed using SHA-256
2. **Session Management**: Secure session handling with HTTP-only cookies
3. **SQL Injection Prevention**: Using parameterized queries
4. **Input Validation**: All user inputs are validated
5. **HTTPS**: Recommended for production deployment

## Fraud Detection

The chatbot includes fraud detection mechanisms:
- Detects high-value transactions (> ₹100,000)
- Flags suspicious transactions
- Geographic anomaly detection
- Unusual transaction pattern detection

## Future Enhancements

1. **Machine Learning Integration**
   - Advanced fraud detection models
   - Transaction pattern analysis
   - Personalized offer optimization

2. **Multi-Channel Support**
   - WhatsApp integration
   - SMS support
   - Voice assistance

3. **Advanced NLU**
   - Deep learning models (BERT, GPT)
   - Multi-language support
   - Context-aware responses

4. **Additional Features**
   - Investment portfolio management
   - Mutual fund recommendations
   - Insurance products
   - Savings goal tracking

5. **Analytics & Reporting**
   - User engagement analytics
   - Chatbot performance metrics
   - Customer satisfaction tracking

## Troubleshooting

### Port Already in Use
```bash
# Change port in config.py or run on different port
python app.py  # Modify PORT in config.py
```

### Database Issues
```bash
# Delete existing database to start fresh
rm database/banking.db
python app.py  # New database will be created
```

### Dependencies Not Installing
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is open source and available under the MIT License.

## Support

For issues or questions:
1. Check the documentation above
2. Review test cases for usage examples
3. Open an issue on the repository

## Author

Created as a comprehensive banking chatbot solution for 24/7 customer support and engagement.

---

**Happy Banking! 🏦💳**