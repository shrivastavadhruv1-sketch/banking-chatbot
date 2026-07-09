# Banking Chatbot - Testing Guide

Complete testing guide for the Banking Chatbot application covering unit tests, integration tests, and manual testing scenarios.

## Table of Contents

1. [Running Tests](#running-tests)
2. [Unit Tests](#unit-tests)
3. [Integration Tests](#integration-tests)
4. [Manual Testing](#manual-testing)
5. [API Testing](#api-testing)
6. [Performance Testing](#performance-testing)
7. [Security Testing](#security-testing)
8. [Test Coverage](#test-coverage)

---

## Running Tests

### Quick Test Run

```bash
# Run all tests
python -m unittest discover tests/

# Run specific test module
python -m unittest tests.test_chatbot.TestIntentClassification

# Run with verbose output
python -m unittest discover tests/ -v

# Run with coverage
pip install coverage
coverage run -m unittest discover tests/
coverage report
```

### Test Output Example

```
test_balance_check_intent (tests.test_chatbot.TestIntentClassification) ... ok
test_transfer_intent (tests.test_chatbot.TestIntentClassification) ... ok
test_amount_extraction (tests.test_chatbot.TestEntityExtraction) ... ok
...
----------------------------------------------------------------------
Ran 12 tests in 0.123s

OK
```

---

## Unit Tests

### 1. Intent Classification Tests

**File:** `tests/test_chatbot.py`

**What's Tested:**
- Intent recognition accuracy
- Confidence scoring
- Fallback to general inquiry

**Test Cases:**

```python
# Test balance check intent
intent, conf = classifier.classify("What is my account balance?")
assert intent == 'check_balance'
assert conf > 0.7

# Test transaction intent
intent, conf = classifier.classify("Show me my recent transactions")
assert intent == 'recent_transactions'

# Test transfer intent
intent, conf = classifier.classify("I want to transfer 5000 to John")
assert intent == 'transfer_money'

# Test greeting
intent, conf = classifier.classify("Hello")
assert intent == 'greeting'
```

**Running:**
```bash
python -m unittest tests.test_chatbot.TestIntentClassification -v
```

### 2. Entity Extraction Tests

**What's Tested:**
- Monetary amount extraction
- Account type identification
- Recipient/recipient detection
- Date and time period extraction

**Test Cases:**

```python
# Amount extraction
entities = extractor.extract("Transfer 5000 rupees")
assert entities['amount'] == 5000.0

# Account type
entities = extractor.extract("Check my savings account")
assert entities['account_type'] == 'savings'

# Recipient
entities = extractor.extract("Send money to Sarah")
assert entities['recipient'] == 'Sarah'
```

**Running:**
```bash
python -m unittest tests.test_chatbot.TestEntityExtraction -v
```

### 3. User Model Tests

**What's Tested:**
- User creation
- Authentication
- Password hashing and verification
- Session management

**Test Cases:**

```python
# Password hashing
hash1 = User._hash_password("password123")
assert hash1 != "password123"  # Should be hashed

# Password verification
verified = User._verify_password("password123", hash1)
assert verified == True

# Wrong password
verified = User._verify_password("wrong_password", hash1)
assert verified == False
```

**Running:**
```bash
python -m unittest tests.test_chatbot.TestUserModel -v
```

### 4. Service Tests

**What's Tested:**
- Balance retrieval
- Transaction recording
- Offer generation
- Alert creation

```python
# Balance service
service = BalanceService()
balance = service.get_balance(account_id=1)
assert balance > 0

# Transaction service
trans_id = service.record_transaction(1, 'debit', 1000, 'Test transaction')
assert trans_id is not None
```

---

## Integration Tests

### Test Scenarios

#### Scenario 1: Complete Chat Flow

```bash
# Start app
python app.py

# In another terminal, run:
python -m unittest tests.test_chatbot.TestChatFlow -v
```

**Steps:**
1. User registers
2. User logs in
3. User sends balance check message
4. System returns balance
5. User sends offer request
6. System returns offers
7. User logs out

#### Scenario 2: Multi-Account Operations

```bash
# Test operations across multiple accounts
python -m unittest tests.test_chatbot.TestMultiAccount -v
```

**Steps:**
1. User has multiple accounts
2. Switch between accounts
3. Check balance for each
4. Transfer between accounts
5. View transactions per account

#### Scenario 3: Fraud Detection Flow

```bash
python -m unittest tests.test_chatbot.TestFraudDetection -v
```

**Steps:**
1. Make normal transactions
2. Make suspicious transaction (high amount)
3. System flags transaction
4. Alert created for user
5. User receives notification

---

## Manual Testing

### 1. Authentication Testing

#### Test: User Registration

```bash
1. Go to http://localhost:5000
2. Click "Register here"
3. Fill form:
   - Full Name: Test User
   - Username: testuser123
   - Email: test@example.com
   - Phone: 9876543210
   - Password: TestPass123!
4. Click Register
5. Verify success message
6. Login with new credentials
```

**Expected:** User created successfully, redirected to login

#### Test: Login

```bash
1. Go to http://localhost:5000
2. Username: demo_user
3. Password: Demo@1234
4. Click Login
```

**Expected:** Redirected to chat page, user info displayed

### 2. Chat Interface Testing

#### Test: Balance Check

```bash
1. Login as demo_user
2. Type: "Check my balance"
3. Press Send
```

**Expected:** 
- Bot responds with balance
- Account balance displayed
- Transaction is quick (<2 seconds)

#### Test: View Transactions

```bash
1. Type: "Show recent transactions"
2. Press Send
```

**Expected:**
- List of transactions displayed
- Shows amount, description, date
- Formatted nicely in response

#### Test: Get Offers

```bash
1. Type: "Show personalized offers"
2. Press Send
```

**Expected:**
- Multiple offers displayed
- Shows discount/offer code
- Category information

#### Test: Fraud Alerts

```bash
1. Type: "Show fraud alerts"
2. Press Send
```

**Expected:**
- Alerts displayed (or "No alerts")
- Alert type, title, message shown

### 3. UI/UX Testing

#### Test: Responsive Design

```bash
1. Resize browser window to mobile size (375px)
2. Chat interface should adapt
3. Text should be readable
4. Buttons clickable
5. Scroll works smoothly
```

#### Test: Form Validation

```bash
1. Try to send empty message
2. Try to register with short password
3. Try invalid email format
4. All should show appropriate errors
```

---

## API Testing

### Using curl

#### Test 1: Register User

```bash
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPass123!",
    "full_name": "Test User",
    "phone": "9876543210"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Registration successful. Please login."
}
```

#### Test 2: Login

```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo_user",
    "password": "Demo@1234"
  }' \
  -c cookies.txt
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Login successful"
}
```

#### Test 3: Send Chat Message

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "message": "Check my balance",
    "account_id": 1
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "response": "Your current account balance is ₹50,000.00...",
  "intent": "check_balance",
  "data": {"balance": 50000.00},
  "action": "display_balance"
}
```

#### Test 4: Get Accounts

```bash
curl -X GET http://localhost:5000/api/accounts \
  -b cookies.txt
```

**Expected Response:**
```json
{
  "success": true,
  "accounts": [
    {"account_id": 1, "account_type": "Savings", "balance": 50000},
    {"account_id": 2, "account_type": "Checking", "balance": 20000}
  ]
}
```

### Using Postman

1. Import API endpoints
2. Set authentication type to "Cookies"
3. Login first to get session cookie
4. Test each endpoint

---

## Performance Testing

### Load Testing

```bash
pip install locust

# Create locustfile.py with test scenarios
# Run: locust -f locustfile.py --host=http://localhost:5000
```

### Response Time Testing

```bash
import time
import requests

start = time.time()
response = requests.post('http://localhost:5000/api/chat', json={
    'message': 'Check my balance',
    'account_id': 1
})
end = time.time()

print(f"Response time: {(end - start) * 1000}ms")
assert (end - start) < 2, "Response too slow"
```

### Database Query Performance

```bash
sqlite3 database/banking.db

-- Analyze query performance
.timer on

SELECT * FROM transactions WHERE account_id = 1;
SELECT * FROM alerts WHERE user_id = 1 AND is_read = 0;
```

---

## Security Testing

### 1. SQL Injection Testing

**Test:** Try SQL injection in login

```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin\" OR \"1\"=\"1",
    "password": "anything"
  }'
```

**Expected:** Login fails, no SQL injection occurs

### 2. XSS Testing

**Test:** Input malicious script

```bash
Message: <script>alert('XSS')</script>
```

**Expected:** Script is escaped, alert doesn't execute

### 3. CSRF Testing

**Test:** Try POST without session

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Test"}'
```

**Expected:** 302 redirect to login (unauthorized)

### 4. Authentication Testing

**Test:** Access protected route without login

```bash
curl http://localhost:5000/chat
```

**Expected:** Redirect to login page

### 5. Password Security

**Test:** Check password hashing

```python
from models.user_model import User

password = "SecurePassword123!"
hash1 = User._hash_password(password)

# Verify hash is not plain password
assert hash1 != password

# Verify bcrypt is used
assert len(hash1) > 50  # bcrypt hashes are long
assert '$2b$' in hash1  # bcrypt prefix
```

---

## Test Coverage

### Run Coverage Report

```bash
pip install coverage

coverage run -m unittest discover tests/
coverage report
coverage html  # Creates htmlcov/index.html
```

### Expected Coverage

- Lines: >80%
- Branches: >70%
- Functions: >80%

### View HTML Report

```bash
# Generate and open report
coverage html
open htmlcov/index.html  # Mac
start htmlcov/index.html  # Windows
```

---

## Continuous Integration

### GitHub Actions (Optional)

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - run: pip install -r requirements.txt
      - run: python -m unittest discover tests/ -v
      - run: python deployment_verify.py
```

---

## Troubleshooting Tests

### Test Hangs

```bash
# Run with timeout
timeout 30 python -m unittest tests.test_chatbot
```

### Database Issues in Tests

```bash
# Use in-memory database for tests
# Modify test to use ':memory:' database
```

### Import Errors

```bash
# Ensure path is correct
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python -m unittest discover tests/
```

---

## Best Practices

1. **Always run tests before committing**
2. **Write tests for new features**
3. **Keep tests independent (no side effects)**
4. **Use meaningful test names**
5. **Clean up test data**
6. **Document complex test scenarios**
7. **Use setUp/tearDown for initialization**

---

## Test Checklist

Before deploying to production:

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Manual testing completed
- [ ] No SQL injection vulnerabilities
- [ ] No XSS vulnerabilities
- [ ] Password hashing verified
- [ ] API responses correct
- [ ] UI responsive on mobile
- [ ] Performance acceptable
- [ ] Deployment verification passes

---

## Support

For test-related questions:
1. Check this guide
2. Review existing tests in `tests/` directory
3. Open GitHub issue with details

---

**Happy Testing! 🧪**
