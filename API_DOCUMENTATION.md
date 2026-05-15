# Banking Chatbot - API Documentation

## Overview

The Banking Chatbot API provides a comprehensive set of RESTful endpoints for authentication, chat interactions, and banking operations. All responses are in JSON format.

## Base URL

```
http://localhost:5000
```

## Authentication

The API uses session-based authentication. Users must first register/login to obtain a session.

## Response Format

All API responses follow this format:

```json
{
  "success": true,
  "message": "Optional success message",
  "data": {}
}
```

Error responses:

```json
{
  "success": false,
  "error": "Error description"
}
```

---

## Endpoints

### Authentication Endpoints

#### 1. Register New User

**Endpoint:** `POST /register`

**Description:** Create a new user account

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe",
  "phone": "9876543210"
}
```

**Response (Success - 201):**
```json
{
  "success": true,
  "message": "Registration successful. Please login."
}
```

**Response (Error - 400):**
```json
{
  "success": false,
  "error": "Username or email already exists"
}
```

**Requirements:**
- Username: Unique, alphanumeric
- Email: Valid email, unique
- Password: Minimum 8 characters
- Full name: Required
- Phone: Optional

---

#### 2. User Login

**Endpoint:** `POST /login`

**Description:** Authenticate user and establish session

**Request Body:**
```json
{
  "username": "john_doe",
  "password": "SecurePassword123!"
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Login successful"
}
```

**Response (Error - 401):**
```json
{
  "success": false,
  "error": "Invalid credentials"
}
```

**Note:** Sets secure HTTP-only session cookie

---

#### 3. User Logout

**Endpoint:** `GET /logout`

**Description:** End user session

**Response:**
Redirects to login page

---

### Chat Endpoints

#### 4. Send Chat Message

**Endpoint:** `POST /api/chat`

**Authentication:** Required (session)

**Description:** Send a message to the chatbot and receive response

**Request Body:**
```json
{
  "message": "Check my balance",
  "account_id": 1
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "response": "Your current account balance is ₹50,000.00",
  "intent": "check_balance",
  "data": {
    "balance": 50000.00,
    "account_id": 1
  },
  "action": "display_balance"
}
```

**Supported Intents:**
- `check_balance` - Check account balance
- `recent_transactions` - View transaction history
- `transfer_money` - Initiate fund transfer
- `bill_payment` - Pay bills
- `get_offers` - View personalized offers
- `loan_info` - Get loan information
- `credit_card_info` - Credit card services
- `fraud_alert` - Check fraud alerts
- `account_statement` - Request account statement
- `help` - Show help menu
- `greeting` - Greeting response
- `goodbye` - End conversation

**Query Examples:**
- "Check my balance"
- "Show recent transactions"
- "Transfer 5000 to John"
- "Show personalized offers"
- "Tell me about loans"

---

### Account Endpoints

#### 5. Get User Accounts

**Endpoint:** `GET /api/accounts`

**Authentication:** Required (session)

**Description:** Retrieve all user accounts

**Response (Success - 200):**
```json
{
  "success": true,
  "accounts": [
    {
      "account_id": 1,
      "account_type": "Savings",
      "account_number": "SAV000001",
      "balance": 50000.00
    },
    {
      "account_id": 2,
      "account_type": "Checking",
      "account_number": "CHK000001",
      "balance": 20000.00
    }
  ]
}
```

---

#### 6. Get Account Balance

**Endpoint:** `GET /api/balance/<account_id>`

**Authentication:** Required (session)

**Description:** Get balance for specific account

**URL Parameters:**
- `account_id` (integer): Account ID

**Response (Success - 200):**
```json
{
  "success": true,
  "balance": 50000.00,
  "account_id": 1
}
```

**Response (Error - 404):**
```json
{
  "success": false,
  "error": "Account not found"
}
```

---

### User Profile Endpoints

#### 7. Get User Profile

**Endpoint:** `GET /api/profile`

**Authentication:** Required (session)

**Description:** Retrieve user profile information

**Response (Success - 200):**
```json
{
  "success": true,
  "user": {
    "user_id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "phone": "9876543210",
    "created_at": "2024-05-15T10:30:00"
  }
}
```

---

### Alert Endpoints

#### 8. Get User Alerts

**Endpoint:** `GET /api/alerts`

**Authentication:** Required (session)

**Description:** Retrieve unread alerts (fraud, transactions, etc.)

**Response (Success - 200):**
```json
{
  "success": true,
  "alerts": [
    {
      "alert_id": 1,
      "type": "transaction",
      "title": "High-value transaction",
      "message": "A transaction of ₹75,000 was made",
      "created_at": "2024-05-15T14:20:00",
      "action_required": false
    },
    {
      "alert_id": 2,
      "type": "fraud",
      "title": "Suspicious Transaction",
      "message": "A suspicious transaction was detected",
      "created_at": "2024-05-15T15:10:00",
      "action_required": true
    }
  ],
  "unread_count": 2
}
```

---

### Offer Endpoints

#### 9. Get Personalized Offers

**Endpoint:** `GET /api/offers`

**Authentication:** Required (session)

**Description:** Retrieve personalized offers for user

**Response (Success - 200):**
```json
{
  "success": true,
  "offers": [
    {
      "offer_id": 1,
      "title": "5% Cashback on purchases",
      "description": "Get 5% cashback on transactions above 1000",
      "code": "CASHBACK_1",
      "discount_percentage": 5,
      "category": "cashback",
      "expiry_date": "2024-12-31"
    },
    {
      "offer_id": 2,
      "title": "Personal Loan",
      "description": "Get instant personal loan with low interest rates",
      "code": "LOAN_1",
      "discount_amount": 5000,
      "category": "loan",
      "expiry_date": "2024-11-30"
    }
  ]
}
```

---

## Chat Interaction Examples

### Example 1: Check Balance

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is my account balance?", "account_id": 1}'
```

**Response:**
```json
{
  "success": true,
  "response": "Your current account balance is ₹50,000.00. Is there anything else?",
  "intent": "check_balance",
  "data": {"balance": 50000.00},
  "action": "display_balance"
}
```

### Example 2: View Recent Transactions

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Show my recent transactions", "account_id": 1}'
```

**Response:**
```json
{
  "success": true,
  "response": "Here are your 10 most recent transactions:\n- Groceries: ₹2500 (2024-05-15 14:30)\n- Fuel: ₹1200 (2024-05-15 10:15)\n...",
  "intent": "recent_transactions",
  "action": "display_transactions",
  "data": {"transactions": [...]}
}
```

### Example 3: Transfer Money

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Transfer 5000 to John", "account_id": 1}'
```

**Response:**
```json
{
  "success": true,
  "response": "I'\''m ready to transfer ₹5,000.00 to John. Please confirm this transaction.",
  "intent": "transfer_money",
  "action": "initiate_transfer",
  "data": {"amount": 5000, "recipient": "John"},
  "requires_confirmation": true
}
```

---

## Error Handling

### Common Error Codes

| Status | Error | Description |
|--------|-------|-------------|
| 400 | Bad Request | Invalid request format or missing required fields |
| 401 | Unauthorized | Not authenticated or session expired |
| 404 | Not Found | Resource not found |
| 500 | Server Error | Internal server error |

### Error Response Example

```json
{
  "success": false,
  "error": "Message cannot be empty"
}
```

---

## Rate Limiting

- No strict rate limiting in base version
- Recommended for production: 100 requests per minute per user

---

## Security

- All endpoints use HTTPS in production
- Session-based authentication with HTTP-only cookies
- Passwords hashed with bcrypt
- Parameterized SQL queries prevent SQL injection
- CSRF protection on form submissions
- Input validation on all endpoints

---

## Pagination

Currently not implemented. Future enhancement for large datasets.

---

## Webhooks

Not available in current version. Planned for future releases.

---

## SDKs and Libraries

Currently no official SDKs available. You can use any HTTP client library:

**JavaScript (Fetch):**
```javascript
const response = await fetch('/api/chat', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({message: 'Check my balance', account_id: 1})
});
const data = await response.json();
```

**Python (Requests):**
```python
import requests
response = requests.post('/api/chat', json={
  'message': 'Check my balance',
  'account_id': 1
})
data = response.json()
```

---

## Changelog

### v1.0.0 (May 2024)
- Initial API release
- 12 NLU intents
- Multi-account support
- Transaction tracking
- Fraud detection
- Personalized offers

---

## Support

For API support and issues, please refer to the GitHub repository or contact the development team.
