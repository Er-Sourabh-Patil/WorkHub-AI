# WorkHub AI - Security & Configuration Guide

## Overview
This guide covers security best practices, API key configuration, session management, and deployment recommendations for WorkHub AI.

---

## API Keys Management

### 1. Google Generative AI (Gemini)

**Purpose**: Powers the AI chatbot for HR assistance and technical support.

**Getting API Key**:
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key and add to `.env` file

**Configuration**:
```bash
# .env
GOOGLE_API_KEY=your_actual_key_here
```

**In Code**:
```python
# Automatically loaded from .env
api_key = os.getenv('GOOGLE_API_KEY')
```

**Supported Models** (in priority order):
- `gemini-2.0-flash` - Latest, fastest
- `gemini-1.5-flash` - Fast, good quality
- `gemini-1.5-pro` - Slower, highest quality
- `gemini-pro` - Fallback option

---

### 2. Fast2SMS API

**Purpose**: Sends SMS notifications for attendance, leaves, payroll, and project updates.

**Getting API Key**:
1. Visit [Fast2SMS](https://www.fast2sms.com/dev/apikey)
2. Register and generate API key
3. Add to `.env` file

**Configuration**:
```bash
# .env
FAST2SMS_API_KEY=your_actual_key_here
```

**In Code**:
```python
# sms_service.py
FAST2SMS_API_KEY = os.getenv('FAST2SMS_API_KEY')
```

**SMS Events**:
- Employee registration
- Attendance marked
- Leave approved/rejected
- Project assignment
- Payroll generated

**Message Format**:
- Max 160 characters per SMS
- Automatically truncated if longer
- Includes employee name, event, date

---

### 3. Flask Session Secret Key

**Purpose**: Encrypts session cookies and maintains user authentication.

**Configuration**:
```bash
# .env
SECRET_KEY=your_super_secret_random_string_here
```

**Generating Secure Key**:
```python
import secrets
secret_key = secrets.token_urlsafe(32)
print(secret_key)
```

**Best Practices**:
✅ Use at least 32 characters
✅ Use random characters (letters, numbers, symbols)
✅ Never commit to version control
✅ Change periodically
✅ Different key per environment

**Session Configuration** (in config.py):
```python
PERMANENT_SESSION_LIFETIME = timedelta(hours=24)  # 24-hour sessions
SESSION_COOKIE_SECURE = False  # True for HTTPS in production
SESSION_COOKIE_HTTPONLY = True  # Prevent JS access
SESSION_COOKIE_SAMESITE = "Lax"  # CSRF protection
```

---

## .env File Setup

### Complete .env Template
```bash
# ========================
# API KEYS CONFIGURATION
# ========================

# Google Generative AI (Gemini) API Key
# Get it from: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=your_google_api_key_here

# Fast2SMS API Key
# Get it from: https://www.fast2sms.com/dev/apikey
FAST2SMS_API_KEY=your_fast2sms_api_key_here

# ========================
# SESSION CONFIGURATION
# ========================

# Flask session secret key (change in production)
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=your_secret_key_here_minimum_32_chars

# ========================
# DATABASE CONFIGURATION
# ========================

# Database path (relative to project root)
DATABASE_PATH=database.db

# ========================
# ENVIRONMENT
# ========================

# Application environment
FLASK_ENV=development
FLASK_DEBUG=False

# ========================
# EMAIL CONFIGURATION (Optional)
# ========================

# SMTP Server for email notifications
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password  # Use app-specific password for Gmail
```

### File Permissions
```bash
# Make .env readable only by owner (Linux/Mac)
chmod 600 .env

# Ensure .env is in .gitignore
echo ".env" >> .gitignore
```

---

## Session Management

### Session Storage
```python
# Stored in secure HTTP-only cookies
session['employee'] = employee_id
session['admin'] = admin_id
```

### Session Decorators

**For Admin Routes**:
```python
@app.route("/admin_dashboard")
@login_required_admin
def admin_dashboard():
    return render_template("admin_dashboard.html")
```

**For Employee Routes**:
```python
@app.route("/employee_dashboard")
@login_required_employee
def employee_dashboard():
    return render_template("employee_dashboard.html")
```

### Session Lifetime
```python
# Default: 24 hours
PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

# Automatic session update on each request
@app.before_request
def make_session_permanent():
    session.permanent = True
```

### Logout Implementation
```python
@app.route("/logout")
def logout():
    session.clear()  # Clear all session data
    return redirect("/")  # Redirect to home
```

---

## Password Security

### Password Hashing
```python
from werkzeug.security import generate_password_hash, check_password_hash

# Hashing password on registration
password_hash = generate_password_hash(password)

# Verifying password on login
check_password_hash(stored_hash, provided_password)
```

### Password Requirements
- Minimum 6 characters
- Case-sensitive
- Stored as hashed (SHA256)
- Never stored in plain text
- SMS notifications include temporary password only

### Best Practices
✅ Enforce strong passwords (8+ chars, mixed case, numbers, symbols)
✅ Implement password change policy (every 90 days)
✅ Prevent password reuse (last 5 passwords)
✅ Implement account lockout (5 failed attempts)
✅ Add forgot password mechanism
✅ Log password changes
✅ Never email passwords

---

## Encoding & Character Handling

### UTF-8 Encoding Declaration
```python
# -*- coding: utf-8 -*-
# Add at the top of all Python files with special characters/emojis
```

### Supported Special Characters
- ✅ Status emojis: ✅ ❌ ✨
- ✅ Unicode characters: 你好, مرحبا, नमस्ते
- ✅ Indian phone numbers with spaces
- ✅ Email addresses with special characters
- ✅ Names in multiple languages

### Database Character Encoding
```sql
-- SQLite uses UTF-8 by default
-- Ensure Python connection:
conn = sqlite3.connect(DATABASE)
conn.execute("PRAGMA encoding='UTF-8'")
```

---

## HTTPS & SSL/TLS

### Development (HTTP)
```bash
# No special configuration needed
python app.py
# Access at http://localhost:5000
```

### Production (HTTPS)

**Using Let's Encrypt**:
```bash
# Install Certbot
pip install certbot certbot-nginx

# Generate certificate
sudo certbot certonly --standalone -d yourdomain.com

# Update Flask configuration
SSL_CONTEXT = ('path/to/cert.pem', 'path/to/key.pem')
```

**Update .env**:
```bash
SESSION_COOKIE_SECURE=True
```

**Update config.py**:
```python
SESSION_COOKIE_SECURE = True  # Require HTTPS
```

---

## Database Security

### Backup Strategy
```bash
# Daily backup script
sqlite3 database.db ".backup 'backups/database_$(date +%Y%m%d).db'"

# Schedule with cron (Linux/Mac)
0 2 * * * sqlite3 /path/to/database.db ".backup '/path/to/backups/database_$(date +\%Y\%m\%d).db'"

# Schedule with Task Scheduler (Windows)
# Create backup.bat and schedule daily at 2 AM
```

### Database Cleanup
```python
# Regular cleanup script (run monthly)
import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Archive old attendance records (>1 year)
old_date = (datetime.now() - timedelta(days=365)).isoformat()
cursor.execute(
    "DELETE FROM attendance WHERE date < ?",
    (old_date,)
)

conn.commit()
conn.close()
```

### SQL Injection Prevention
```python
# ✅ CORRECT - Parameterized queries
cursor.execute(
    "SELECT * FROM employees WHERE employee_id = ?",
    (employee_id,)
)

# ❌ WRONG - String concatenation
cursor.execute(f"SELECT * FROM employees WHERE employee_id = '{employee_id}'")
```

---

## Input Validation

### Form Validation
```python
# Email validation
import re
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Phone number validation (India)
def is_valid_phone(phone):
    phone = str(phone).strip()
    return phone.isdigit() and len(phone) == 10

# Date validation
from datetime import datetime
def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False
```

### File Upload Validation
```python
import os

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def is_allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_photo(file):
    # Check file size
    if len(file.read()) > MAX_FILE_SIZE:
        return False, "File size exceeds 5MB"
    
    file.seek(0)  # Reset file pointer
    
    # Check extension
    if not is_allowed_file(file.filename):
        return False, "Only JPG, PNG, GIF allowed"
    
    return True, "OK"
```

---

## CORS & Cross-Origin Requests

### Current Setup
```python
# CORS is not explicitly configured
# Same-origin requests only (recommended for internal apps)
```

### Enable CORS (if needed)
```python
from flask_cors import CORS

CORS(app, resources={
    r"/api/*": {
        "origins": ["https://yourdomain.com"],
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type"]
    }
})
```

---

## Logging & Monitoring

### Application Logging
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    filename='logs/app.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Log important events
logger.info(f"Employee {emp_id} logged in")
logger.warning(f"Unusual activity detected for {emp_id}")
logger.error(f"Database error: {error_message}")
```

### Security Event Logging
```python
# Create security_events.log
- Successful logins
- Failed login attempts
- Password changes
- Admin actions
- Access to sensitive data
- Data exports
```

---

## Vulnerability Scanning

### Check for Security Issues
```bash
# Install safety
pip install safety

# Scan dependencies
safety check

# Fix vulnerable packages
pip install --upgrade vulnerable_package
```

### Regular Security Audits
```bash
# Install bandit (Python security scanner)
pip install bandit

# Scan project
bandit -r .

# Generate report
bandit -r . -f json -o security_report.json
```

---

## Compliance & Data Protection

### GDPR Compliance (EU Users)
- ✅ Data minimization (collect only needed data)
- ✅ Storage limitation (delete old data)
- ✅ User data export (implement data export feature)
- ✅ Right to be forgotten (implement data deletion)
- ✅ Privacy policy document
- ✅ Data processing agreement

### India Data Protection
- ✅ Store data within India (recommended)
- ✅ Implement data protection measures
- ✅ Regular security audits
- ✅ Incident response plan
- ✅ Data retention policy

### Data Retention Policy
```
- Attendance records: Keep for 3 years
- Leave records: Keep for 5 years
- Payroll records: Keep for 7 years
- Performance reviews: Keep for 3 years
- Archived data: Secure deletion after period
```

---

## Deployment Checklist

- [ ] Change SECRET_KEY to strong random value
- [ ] Set FLASK_ENV=production
- [ ] Disable FLASK_DEBUG
- [ ] Enable HTTPS/SSL
- [ ] Set SESSION_COOKIE_SECURE=True
- [ ] Configure proper logging
- [ ] Setup database backups
- [ ] Create admin backup account
- [ ] Implement rate limiting
- [ ] Add monitoring & alerts
- [ ] Create incident response plan
- [ ] Document security procedures
- [ ] Train team on security
- [ ] Perform security audit
- [ ] Get liability insurance

---

**Last Updated**: June 2026
**Version**: 1.0.0
