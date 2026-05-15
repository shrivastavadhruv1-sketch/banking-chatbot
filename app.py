"""
Flask application for the banking chatbot
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from functools import wraps
import logging
import os
from datetime import datetime

from config import *
from models.user_model import User, Account, Database
from chatbot.conversation import ConversationManager

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True

CORS(app)

# Initialize database
db = Database()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize services
user_model = User()
account_model = Account()
conversation_manager = ConversationManager()


def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    """Home page"""
    if 'user_id' in session:
        return redirect(url_for('chat'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        data = request.get_json()
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        full_name = data.get('full_name', '').strip()
        phone = data.get('phone', '').strip()
        
        # Validation
        if not all([username, email, password, full_name]):
            return jsonify({'success': False, 'error': 'All fields are required'}), 400
        
        if len(password) < PASSWORD_MIN_LENGTH:
            return jsonify({
                'success': False,
                'error': f'Password must be at least {PASSWORD_MIN_LENGTH} characters'
            }), 400
        
        # Create user
        user_id = user_model.create_user(username, password, email, full_name, phone)
        
        if not user_id:
            return jsonify({'success': False, 'error': 'Username or email already exists'}), 400
        
        # Create default accounts for new user
        account_model.create_account(user_id, 'Savings', f'SAV{user_id:06d}', 10000.0)
        account_model.create_account(user_id, 'Checking', f'CHK{user_id:06d}', 5000.0)
        
        logger.info(f"New user registered: {username}")
        
        return jsonify({'success': True, 'message': 'Registration successful. Please login.'}), 201
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        data = request.get_json()
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'success': False, 'error': 'Username and password required'}), 400
        
        user_id = user_model.authenticate(username, password)
        
        if not user_id:
            logger.warning(f"Failed login attempt: {username}")
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
        # Update last login
        user_model.update_last_login(user_id)
        
        # Set session
        session['user_id'] = user_id
        session['username'] = username
        
        logger.info(f"User logged in: {username}")
        
        return jsonify({'success': True, 'message': 'Login successful'}), 200
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """User logout"""
    username = session.get('username', 'Unknown')
    session.clear()
    logger.info(f"User logged out: {username}")
    return redirect(url_for('login'))


@app.route('/chat')
@login_required
def chat():
    """Chat interface"""
    user_id = session['user_id']
    user = user_model.get_user(user_id)
    accounts = account_model.get_user_accounts(user_id)
    
    return render_template('chat.html', user=user, accounts=accounts)


@app.route('/api/chat', methods=['POST'])
@login_required
def api_chat():
    """Chat API endpoint"""
    try:
        data = request.get_json()
        user_id = session['user_id']
        
        message = data.get('message', '').strip()
        account_id = data.get('account_id')
        
        if not message:
            return jsonify({'success': False, 'error': 'Message cannot be empty'}), 400
        
        # Process message through conversation manager
        response = conversation_manager.process_message(
            user_id, message, account_id
        )
        
        return jsonify({
            'success': response.get('success', True),
            'response': response['response'],
            'intent': response.get('intent'),
            'data': response.get('data'),
            'action': response.get('action')
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An error occurred processing your message'
        }), 500


@app.route('/api/accounts', methods=['GET'])
@login_required
def get_accounts():
    """Get user accounts"""
    try:
        user_id = session['user_id']
        accounts = account_model.get_user_accounts(user_id)
        
        return jsonify({
            'success': True,
            'accounts': [
                {
                    'account_id': acc['account_id'],
                    'account_type': acc['account_type'],
                    'account_number': acc['account_number'],
                    'balance': acc['balance']
                }
                for acc in accounts
            ]
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching accounts: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/balance/<int:account_id>', methods=['GET'])
@login_required
def get_balance(account_id):
    """Get account balance"""
    try:
        user_id = session['user_id']
        account = account_model.get_account(account_id)
        
        if not account or account['user_id'] != user_id:
            return jsonify({'success': False, 'error': 'Account not found'}), 404
        
        return jsonify({
            'success': True,
            'balance': account['balance'],
            'account_id': account_id
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching balance: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/profile', methods=['GET'])
@login_required
def get_profile():
    """Get user profile"""
    try:
        user_id = session['user_id']
        user = user_model.get_user(user_id)
        
        return jsonify({
            'success': True,
            'user': {
                'user_id': user['user_id'],
                'username': user['username'],
                'email': user['email'],
                'full_name': user['full_name'],
                'phone': user['phone'],
                'created_at': user['created_at']
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching profile: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/alerts', methods=['GET'])
@login_required
def get_alerts():
    """Get user alerts"""
    try:
        user_id = session['user_id']
        from chatbot.banking_services import AlertService
        alert_service = AlertService()
        
        alerts = alert_service.get_unread_alerts(user_id)
        
        return jsonify({
            'success': True,
            'alerts': alerts,
            'unread_count': len(alerts)
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching alerts: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/offers', methods=['GET'])
@login_required
def get_offers():
    """Get personalized offers"""
    try:
        user_id = session['user_id']
        from chatbot.banking_services import OfferService
        offer_service = OfferService()
        
        offers = offer_service.get_personalized_offers(user_id)
        
        return jsonify({
            'success': True,
            'offers': offers
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching offers: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'success': False, 'error': 'Resource not found'}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    logger.error(f"Server error: {str(error)}")
    return jsonify({'success': False, 'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=DEBUG)
