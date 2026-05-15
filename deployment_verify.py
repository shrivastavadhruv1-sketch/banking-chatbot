#!/usr/bin/env python
"""
Deployment Verification Script for Banking Chatbot
Verifies all components are working correctly for production deployment
"""

import sys
import os
import sqlite3
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

class DeploymentVerifier:
    def __init__(self):
        self.results = []
        self.errors = []
    
    def check(self, name, func):
        """Run a check and record result"""
        try:
            result = func()
            status = "✓ PASS" if result else "✗ FAIL"
            self.results.append((name, status))
            return result
        except Exception as e:
            self.errors.append((name, str(e)))
            self.results.append((name, "✗ ERROR"))
            return False
    
    def verify_imports(self):
        """Verify all modules can be imported"""
        try:
            import config
            import models.user_model
            import nlu.intent_classifier
            import chatbot.banking_services
            import chatbot.conversation
            return True
        except Exception as e:
            raise Exception(f"Import failed: {e}")
    
    def verify_database(self):
        """Verify database is initialized"""
        try:
            from models.user_model import Database
            db = Database()
            conn = db.get_connection()
            
            # Check if tables exist
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            table_names = [t[0] for t in tables]
            
            required_tables = ['users', 'accounts', 'transactions', 'alerts', 'offers', 
                             'conversation_history', 'user_sessions']
            
            for table in required_tables:
                if table not in table_names:
                    raise Exception(f"Missing table: {table}")
            
            conn.close()
            return True
        except Exception as e:
            raise Exception(f"Database verification failed: {e}")
    
    def verify_demo_user(self):
        """Verify demo user exists"""
        try:
            from models.user_model import User
            user_model = User()
            user = user_model.authenticate('demo_user', 'Demo@1234')
            return user is not None
        except Exception as e:
            raise Exception(f"Demo user check failed: {e}")
    
    def verify_nlu(self):
        """Verify NLU engine works"""
        try:
            from nlu.intent_classifier import NLUEngine
            nlu = NLUEngine()
            
            test_cases = [
                ('Check my balance', 'check_balance'),
                ('Show recent transactions', 'recent_transactions'),
                ('Hello', 'greeting'),
            ]
            
            for query, expected_intent in test_cases:
                result = nlu.process(query)
                if result['intent'] != expected_intent:
                    raise Exception(f"NLU failed for '{query}': got {result['intent']}, expected {expected_intent}")
            
            return True
        except Exception as e:
            raise Exception(f"NLU verification failed: {e}")
    
    def verify_config(self):
        """Verify configuration is set"""
        try:
            import config
            
            # Check critical configs
            if not config.SECRET_KEY or config.SECRET_KEY == 'your-secret-key-change-in-production':
                raise Exception("SECRET_KEY not configured or still uses default")
            
            if config.DEBUG:
                raise Exception("DEBUG mode is enabled in production")
            
            return True
        except Exception as e:
            raise Exception(f"Configuration check failed: {e}")
    
    def verify_security(self):
        """Verify security settings"""
        try:
            from models.user_model import User
            
            # Test bcrypt hashing
            password = "test_password_12345"
            hash1 = User._hash_password(password)
            
            # Should be different from plain password
            if hash1 == password:
                raise Exception("Password hashing not working")
            
            # Should be repeatable
            verified = User._verify_password(password, hash1)
            if not verified:
                raise Exception("Password verification failed")
            
            return True
        except Exception as e:
            raise Exception(f"Security verification failed: {e}")
    
    def verify_api_endpoints(self):
        """Verify Flask app can be created"""
        try:
            from app import app
            
            # Check routes exist
            routes = [rule.rule for rule in app.url_map.iter_rules()]
            
            required_routes = ['/login', '/register', '/logout', '/chat', '/api/chat']
            
            for route in required_routes:
                if route not in routes:
                    raise Exception(f"Missing route: {route}")
            
            return True
        except Exception as e:
            raise Exception(f"API endpoint verification failed: {e}")
    
    def verify_templates(self):
        """Verify HTML templates exist"""
        try:
            templates = ['templates/login.html', 'templates/register.html', 'templates/chat.html']
            
            for template in templates:
                if not os.path.exists(template):
                    raise Exception(f"Missing template: {template}")
            
            return True
        except Exception as e:
            raise Exception(f"Template verification failed: {e}")
    
    def verify_static_files(self):
        """Verify static files exist"""
        try:
            static_files = [
                'static/css/style.css',
                'static/js/script.js'
            ]
            
            for file in static_files:
                if not os.path.exists(file):
                    raise Exception(f"Missing static file: {file}")
            
            return True
        except Exception as e:
            raise Exception(f"Static files verification failed: {e}")
    
    def verify_requirements(self):
        """Verify requirements.txt has patched versions"""
        try:
            with open('requirements.txt', 'r') as f:
                content = f.read()
            
            # Check for vulnerable versions
            if 'cryptography==41' in content:
                raise Exception("cryptography version is vulnerable")
            if 'Flask==2.3.0' in content or 'Flask==2.2.0' in content:
                raise Exception("Flask version is vulnerable")
            if 'nltk==3.8' in content:
                raise Exception("nltk version is vulnerable")
            
            return True
        except Exception as e:
            raise Exception(f"Requirements verification failed: {e}")
    
    def verify_permissions(self):
        """Verify file permissions for security"""
        try:
            # Database should be readable/writable by app only
            if os.path.exists('database/banking.db'):
                stat = os.stat('database/banking.db')
                # Check if world-readable (should not be)
                if stat.st_mode & 0o004:
                    raise Exception("Database is world-readable - security risk")
            
            # .env should not be world-readable
            if os.path.exists('.env'):
                stat = os.stat('.env')
                if stat.st_mode & 0o004:
                    raise Exception(".env file is world-readable - security risk")
            
            return True
        except Exception as e:
            raise Exception(f"Permission verification failed: {e}")
    
    def run_all_checks(self):
        """Run all verification checks"""
        print("=" * 70)
        print("BANKING CHATBOT - PRODUCTION DEPLOYMENT VERIFICATION")
        print("=" * 70)
        print(f"\nVerification started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        checks = [
            ("Module Imports", self.verify_imports),
            ("Database Initialization", self.verify_database),
            ("Demo User", self.verify_demo_user),
            ("NLU Engine", self.verify_nlu),
            ("Configuration", self.verify_config),
            ("Security Settings", self.verify_security),
            ("API Endpoints", self.verify_api_endpoints),
            ("HTML Templates", self.verify_templates),
            ("Static Files", self.verify_static_files),
            ("Requirements Versions", self.verify_requirements),
            ("File Permissions", self.verify_permissions),
        ]
        
        for name, check_func in checks:
            print(f"Checking {name:.<50}", end=" ", flush=True)
            self.check(name, check_func)
            print(self.results[-1][1])
        
        print("\n" + "=" * 70)
        print("VERIFICATION SUMMARY")
        print("=" * 70)
        
        passed = sum(1 for _, status in self.results if "PASS" in status)
        failed = sum(1 for _, status in self.results if "FAIL" in status)
        errors = sum(1 for _, status in self.results if "ERROR" in status)
        
        print(f"\nResults: {passed} passed, {failed} failed, {errors} errors\n")
        
        if errors > 0:
            print("ERRORS DETECTED:")
            for name, error in self.errors:
                print(f"  ✗ {name}: {error}")
            print()
        
        all_passed = (failed == 0 and errors == 0)
        
        if all_passed:
            print("✓ ALL CHECKS PASSED - System is ready for production deployment!")
            print("\nDeployment Recommendations:")
            print("  1. Set unique SECRET_KEY in environment/config")
            print("  2. Enable SSL/TLS for HTTPS")
            print("  3. Configure automated backups")
            print("  4. Set up monitoring and logging")
            print("  5. Configure firewall rules")
            print("  6. Set up rate limiting")
            print("  7. Enable database indexes for performance")
            print("\nSee DEPLOYMENT.md for detailed deployment instructions.")
        else:
            print("✗ CHECKS FAILED - Fix issues before deploying to production!")
        
        print("\n" + "=" * 70)
        
        return 0 if all_passed else 1

if __name__ == "__main__":
    verifier = DeploymentVerifier()
    sys.exit(verifier.run_all_checks())
