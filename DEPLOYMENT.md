# Banking Chatbot - Production Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the Banking Chatbot to production environments. The chatbot is a Flask-based conversational AI application with SQLite database, custom NLU engine, and comprehensive banking features.

## Pre-Deployment Checklist

- [ ] All tests passing (`python -m unittest discover tests/`)
- [ ] Security vulnerabilities scanned and resolved
- [ ] Dependencies updated to latest patched versions
- [ ] Environment variables configured
- [ ] Database backups created
- [ ] SSL/TLS certificates ready (for HTTPS)
- [ ] Monitoring and logging configured
- [ ] Rate limiting configured
- [ ] CORS policies reviewed

## Local Development Setup

### Prerequisites

- Python 3.7+
- pip or Poetry for dependency management
- Git for version control

### Quick Start

```bash
# Clone repository
git clone https://github.com/shrivastavadhruv1-sketch/banking-chatbot.git
cd banking-chatbot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python init.py

# Run application
python app.py
```

The chatbot will be available at `http://localhost:5000`

### Demo User Credentials

- **Username**: demo_user
- **Password**: Demo@1234

## Production Deployment

### Option 1: Traditional Server (Linux/Ubuntu)

#### 1. Server Setup

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Python and dependencies
sudo apt-get install python3.9 python3-pip python3-venv nginx supervisor -y

# Create application user
sudo useradd -m -s /bin/bash chatbot
sudo su - chatbot

# Clone repository
git clone https://github.com/shrivastavadhruv1-sketch/banking-chatbot.git
cd banking-chatbot
```

#### 2. Environment Setup

```bash
# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn  # Production WSGI server

# Initialize database
python init.py
```

#### 3. Configure Supervisor

Create `/etc/supervisor/conf.d/banking-chatbot.conf`:

```ini
[program:banking-chatbot]
command=/home/chatbot/banking-chatbot/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:8000 app:app
directory=/home/chatbot/banking-chatbot
user=chatbot
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/banking-chatbot/app.log
environment=DEBUG=False,FLASK_ENV=production
```

#### 4. Configure Nginx

Create `/etc/nginx/sites-available/banking-chatbot`:

```nginx
upstream banking_chatbot {
    server 0.0.0.0:8000;
}

server {
    listen 80;
    server_name your-domain.com;
    client_max_body_size 20M;

    location / {
        proxy_pass http://banking_chatbot;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /home/chatbot/banking-chatbot/static;
        expires 30d;
    }
}
```

Enable site and reload:

```bash
sudo ln -s /etc/nginx/sites-available/banking-chatbot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
sudo systemctl start supervisor
```

### Option 2: Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install gunicorn

# Copy application
COPY . .

# Initialize database
RUN python init.py

# Expose port
EXPOSE 5000

# Run application
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5000", "app:app"]
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  chatbot:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DEBUG=False
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./database:/app/database
      - ./logs:/app/logs
    restart: unless-stopped
```

Deploy:

```bash
docker-compose build
docker-compose up -d
```

### Option 3: Heroku Deployment

Create `Procfile`:

```
web: gunicorn --workers 4 --bind 0.0.0.0:$PORT app:app
```

Deploy:

```bash
# Login to Heroku
heroku login

# Create app
heroku create your-banking-chatbot

# Set environment variables
heroku config:set DEBUG=False
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')

# Deploy
git push heroku main
```

### Option 4: AWS EC2 Deployment

See `DEPLOYMENT_AWS.md` for detailed AWS EC2 setup with RDS and S3.

## Environment Variables

Create `.env` file in production (use `.env.example` as template):

```bash
# Server
DEBUG=False
FLASK_ENV=production
HOST=0.0.0.0
PORT=5000

# Security
SECRET_KEY=your-secure-random-key-here
PASSWORD_MIN_LENGTH=8
MAX_LOGIN_ATTEMPTS=5

# Database
DATABASE_PATH=/var/lib/chatbot/banking.db

# Features
TRANSACTION_ALERT_THRESHOLD=50000
SUSPICIOUS_TRANSACTION_THRESHOLD=100000
MIN_BALANCE_FOR_PREMIUM_OFFERS=100000

# Logging
LOG_LEVEL=WARNING
LOG_FILE=/var/log/chatbot/app.log
```

## Security Hardening

### 1. SSL/TLS Setup

```bash
# Using Let's Encrypt with Certbot
sudo apt-get install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d your-domain.com
```

### 2. Update Nginx for HTTPS

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Rest of configuration...
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

### 3. Database Security

```bash
# Backup database before going live
sqlite3 /var/lib/chatbot/banking.db ".backup '/backups/banking.db.backup'"

# Set proper file permissions
chmod 600 /var/lib/chatbot/banking.db
```

### 4. Firewall Configuration

```bash
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw enable
```

## Monitoring and Logging

### Application Logs

```bash
# Monitor logs in real-time
tail -f /var/log/banking-chatbot/app.log

# Check for errors
grep ERROR /var/log/banking-chatbot/app.log
```

### Performance Monitoring

```bash
# Install monitoring tools
sudo apt-get install htop iotop nethogs -y

# Monitor system resources
htop

# Monitor application processes
ps aux | grep gunicorn
```

### Database Monitoring

```bash
# Check database size
ls -lh /var/lib/chatbot/banking.db

# Database integrity check
sqlite3 /var/lib/chatbot/banking.db "PRAGMA integrity_check;"

# Backup script (add to cron)
0 2 * * * sqlite3 /var/lib/chatbot/banking.db ".backup '/backups/banking_$(date +\%Y\%m\%d).db'"
```

## Performance Optimization

### 1. Database Optimization

```bash
# Add database indexes
sqlite3 /var/lib/chatbot/banking.db << EOF
CREATE INDEX IF NOT EXISTS idx_transactions_account ON transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_alerts_user ON alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_offers_user ON offers(user_id);
VACUUM;
EOF
```

### 2. Application Caching

- Implement Redis caching for frequently accessed data
- Cache user sessions and balance information
- Add CDN for static assets

### 3. Load Balancing

For high-traffic scenarios:

```bash
# Install HAProxy
sudo apt-get install haproxy -y

# Configure in /etc/haproxy/haproxy.cfg
frontend banking_chatbot
    bind *:80
    default_backend backend_servers

backend backend_servers
    balance roundrobin
    server app1 127.0.0.1:8001
    server app2 127.0.0.1:8002
    server app3 127.0.0.1:8003
```

## Backup and Recovery

### Automated Backups

Create `/usr/local/bin/backup-chatbot.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/backups/chatbot"
DB_PATH="/var/lib/chatbot/banking.db"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
sqlite3 $DB_PATH ".backup '$BACKUP_DIR/banking_$DATE.db'"

# Compress
gzip "$BACKUP_DIR/banking_$DATE.db"

# Keep only last 30 days
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

# Upload to S3 (optional)
# aws s3 cp "$BACKUP_DIR/banking_$DATE.db.gz" s3://your-bucket/backups/
```

Add to crontab:

```bash
0 2 * * * /usr/local/bin/backup-chatbot.sh
```

### Recovery Procedure

```bash
# List available backups
ls -lh /backups/chatbot/

# Restore from backup
gunzip /backups/chatbot/banking_20240515_020000.db.gz
cp /backups/chatbot/banking_20240515_020000.db /var/lib/chatbot/banking.db
chown chatbot:chatbot /var/lib/chatbot/banking.db
chmod 600 /var/lib/chatbot/banking.db
```

## Testing in Production

```bash
# Verify application is running
curl http://localhost:5000/

# Test login endpoint
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "demo_user", "password": "Demo@1234"}'

# Check application logs
tail -50 /var/log/banking-chatbot/app.log

# Run health check script
python deployment_verify.py
```

## Troubleshooting

### Application Won't Start

```bash
# Check logs
journalctl -u banking-chatbot -n 50 --no-pager

# Verify Python installation
python3 --version

# Test imports
python3 -c "from app import app; print('OK')"
```

### Database Errors

```bash
# Check database integrity
sqlite3 /var/lib/chatbot/banking.db "PRAGMA integrity_check;"

# Rebuild database
sqlite3 /var/lib/chatbot/banking.db ".dump" | sqlite3 /var/lib/chatbot/banking_new.db
```

### Performance Issues

```bash
# Check resource usage
free -h
df -h
top -b -n 1

# Analyze database queries
sqlite3 /var/lib/chatbot/banking.db ".eqp on"
```

## Rollback Procedure

If issues occur in production:

```bash
# Stop application
sudo systemctl stop banking-chatbot

# Restore from backup
cp /backups/chatbot/banking_last_good.db /var/lib/chatbot/banking.db

# Restart application
sudo systemctl start banking-chatbot

# Verify
curl http://localhost:5000/
```

## Support and Maintenance

- **Documentation**: See README.md for feature documentation
- **Issues**: Report bugs on GitHub
- **Updates**: Check GitHub for security patches and updates
- **Community**: Contribute improvements via pull requests

## Scaling Considerations

For enterprise deployment with thousands of users:

1. **Database**: Migrate to PostgreSQL for better concurrency
2. **Caching**: Implement Redis for session and data caching
3. **Message Queue**: Add Celery for background tasks
4. **CDN**: Use CloudFront/CloudFlare for static assets
5. **Monitoring**: Implement DataDog/New Relic for APM
6. **Load Balancing**: Use AWS ALB/NLB or Nginx

## Version History

- **v1.0.0** (May 2024): Initial production release
  - 12 NLU intents
  - Multi-account support
  - Fraud detection
  - Personalized offers
  - Secure authentication

---

**For production support and enterprise features, contact the development team.**
