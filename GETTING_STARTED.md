# Banking Chatbot - Getting Started Guide

Welcome to the Banking Chatbot! This guide will help you get up and running quickly.

## 5-Minute Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Initialize the Application

```bash
python init.py
```

This command will:
- ✓ Verify all modules import correctly
- ✓ Initialize the SQLite database
- ✓ Test the NLU engine
- ✓ Create a demo user account

### 3. Run the Application

```bash
python app.py
```

### 4. Access the Chatbot

Open your browser and go to:
```
http://localhost:5000
```

### 5. Login with Demo Account

- **Username:** `demo_user`
- **Password:** `Demo@1234`

---

## What You Can Do

Once logged in, try these commands:

### Banking Operations
```
"Check my balance"
"Show recent transactions"
"Transfer 5000 to John"
"Pay my electricity bill"
```

### Offers & Promotions
```
"Show personalized offers"
"What deals are available?"
"Show me discounts"
```

### Account Management
```
"Show fraud alerts"
"Tell me about loans"
"Credit card information"
"Account statement"
```

### General Help
```
"Help"
"Hello"
"What can you do?"
```

---

## Directory Structure

```
banking-chatbot/
├── app.py                      # Main Flask application
├── config.py                   # Configuration settings
├── init.py                     # Initialization script
├── requirements.txt            # Python dependencies
│
├── models/
│   └── user_model.py          # Database models
│
├── nlu/
│   └── intent_classifier.py   # Natural language understanding
│
├── chatbot/
│   ├── conversation.py        # Chat management
│   └── banking_services.py    # Banking operations
│
├── templates/
│   ├── login.html             # Login page
│   ├── register.html          # Registration page
│   └── chat.html              # Chat interface
│
└── static/
    ├── css/style.css          # Styling
    └── js/script.js           # Frontend logic
```

---

## Development Setup

### Setting Up Your Development Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize
python init.py

# Run
python app.py
```

### Code Structure

**Frontend Flow:**
1. User enters message in chat box (chat.html)
2. JavaScript sends message to `/api/chat` (script.js)
3. Backend processes message through NLU (intent_classifier.py)
4. Services handle the intent (banking_services.py)
5. Response is returned and displayed

**Backend Flow:**
1. Flask receives chat request (app.py)
2. Message sent to ConversationManager (conversation.py)
3. NLU Engine classifies intent (intent_classifier.py)
4. Appropriate service handles operation (banking_services.py)
5. Response generated and returned

---

## Testing

### Run Unit Tests

```bash
python -m unittest discover tests/
```

### Manual Testing

```bash
# Test a specific intent
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Check my balance", "account_id": 1}'
```

### Verify Deployment

```bash
python deployment_verify.py
```

---

## Common Tasks

### How to Add a New Intent

1. Add pattern to `nlu/intent_classifier.py`:

```python
'your_intent': {
    'keywords': ['keyword1', 'keyword2'],
    'patterns': [r'\b(your|pattern)\b']
}
```

2. Add handler to `chatbot/conversation.py`:

```python
def _handle_your_intent(self, user_id, account_id, entities, message):
    # Your implementation
    return {'response': '...', 'action': 'your_action'}
```

### How to Add a New Service

1. Create service class in `chatbot/banking_services.py`:

```python
class YourService:
    def __init__(self):
        self.model = YourModel()
    
    def your_method(self):
        pass
```

2. Use in `ConversationManager`:

```python
from chatbot.banking_services import YourService
self.your_service = YourService()
```

### How to Create a New API Endpoint

1. Add to `app.py`:

```python
@app.route('/api/your-endpoint', methods=['GET', 'POST'])
@login_required
def your_endpoint():
    # Your implementation
    return jsonify({'success': True, 'data': ...})
```

---

## Database

### View Database

```bash
sqlite3 database/banking.db
```

### Common SQL Queries

```sql
-- View all users
SELECT * FROM users;

-- View all accounts
SELECT * FROM accounts;

-- View transactions for account
SELECT * FROM transactions WHERE account_id = 1;

-- View alerts for user
SELECT * FROM alerts WHERE user_id = 1;
```

### Reset Database

```bash
# Backup first
cp database/banking.db database/banking.db.backup

# Delete and reinitialize
rm database/banking.db
python init.py
```

---

## Configuration

Edit `config.py` to customize:

```python
DEBUG = False                          # Enable debug mode
PORT = 5000                           # Server port
TRANSACTION_ALERT_THRESHOLD = 50000  # Alert for high transactions
MIN_BALANCE_FOR_PREMIUM_OFFERS = 100000  # Tier for premium offers
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'flask'"

**Solution:**
```bash
pip install -r requirements.txt
```

### "Database locked" error

**Solution:**
```bash
# Close other database connections
# Restart the application
python app.py
```

### "Port 5000 already in use"

**Solution:**
```bash
# Use different port
export PORT=5001
python app.py
```

Or on Windows:
```bash
set PORT=5001
python app.py
```

### Chat not responding

**Solution:**
```bash
# Check server logs
tail -f logs/app.log

# Verify database
sqlite3 database/banking.db ".tables"
```

---

## Next Steps

### For Users
- Explore the chat interface
- Create your own account
- Try different banking queries
- Check personalized offers

### For Developers
- Review code structure
- Add new intents
- Create custom services
- Deploy to production

### For Deployment
- Follow DEPLOYMENT.md guide
- Use Docker setup for easy deployment
- Configure monitoring and logging
- Set up automated backups

---

## Key Features

✅ **Multi-Account Support** - Manage multiple accounts  
✅ **Real-Time Balance Check** - Instant account balance  
✅ **Transaction Tracking** - Complete transaction history  
✅ **Fraud Detection** - Automatic suspicious activity detection  
✅ **Personalized Offers** - AI-driven recommendations  
✅ **Secure Authentication** - bcrypt password hashing  
✅ **API-First Design** - Easy integration  
✅ **Production-Ready** - Tested and hardened  

---

## Resources

- **API Docs:** See `API_DOCUMENTATION.md`
- **Deployment:** See `DEPLOYMENT.md`
- **Main README:** See `README.md`
- **GitHub:** https://github.com/shrivastavadhruv1-sketch/banking-chatbot

---

## Support

For questions or issues:
1. Check README.md and API_DOCUMENTATION.md
2. Review code comments and docstrings
3. Check existing GitHub issues
4. Create a new GitHub issue with details

---

**Happy Banking! 🏦💳**

Start with the 5-minute quick start above, and you'll be up and running in no time!
