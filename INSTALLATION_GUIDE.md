# WorkHub AI - Installation & Setup Guide

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Pre-Installation](#pre-installation)
3. [Installation Steps](#installation-steps)
4. [First Time Setup](#first-time-setup)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)
7. [Post-Installation](#post-installation)

---

## System Requirements

### Minimum Hardware
- **CPU**: Dual-core 2.0 GHz or better
- **RAM**: 4 GB (8 GB recommended for face recognition)
- **Storage**: 500 MB (+ space for face images)
- **Webcam**: USB webcam (for face recognition feature)
- **Network**: Internet connection required for API keys

### Operating Systems
- ✅ Windows 10/11 (64-bit)
- ✅ macOS 10.14+
- ✅ Ubuntu 18.04+ / Debian 10+
- ✅ CentOS 7+
- ✅ Raspberry Pi OS (with sufficient RAM)

### Software Prerequisites
- **Python**: 3.8, 3.9, 3.10, or 3.11
- **pip**: Latest version (comes with Python)
- **Git**: For cloning repository (optional)
- **SQLite3**: Usually pre-installed

### API Keys Required
- **Google Gemini API Key** - for AI chatbot
- **Fast2SMS API Key** - for SMS notifications
- *(Optional)* Email credentials for email notifications

---

## Pre-Installation

### 1. Check Python Version
```bash
python --version
# Output should be 3.8 or higher

python -m pip --version
# Verify pip is installed
```

### 2. Create Project Directory
```bash
# Create directory
mkdir WorkHub_AI
cd WorkHub_AI

# If cloning from git
git clone <repository-url> .
cd WorkHub_AI
```

### 3. Get API Keys

#### Google Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Choose "Gemini API"
4. Copy the API key (you'll need this later)

#### Fast2SMS API Key
1. Visit [Fast2SMS](https://www.fast2sms.com/dev/apikey)
2. Sign up or log in
3. Copy your API key from dashboard

---

## Installation Steps

### Step 1: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**Verify activation**: Prompt should show `(venv)` prefix

### Step 2: Upgrade pip
```bash
python -m pip install --upgrade pip setuptools wheel
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

**Expected time**: 5-15 minutes (first install)

**If errors occur**:
```bash
# Clear pip cache
pip cache purge

# Try installing with upgrade flag
pip install --upgrade -r requirements.txt

# Install specific problematic packages individually
pip install tensorflow==2.10.1
pip install deepface==0.0.79
```

### Step 4: Create .env File
```bash
# Copy template
cp .env.example .env  # If template exists

# Or create manually
echo "" > .env
```

**Edit .env and add your API keys**:
```bash
GOOGLE_API_KEY=your_google_api_key_here
FAST2SMS_API_KEY=your_fast2sms_api_key_here
SECRET_KEY=your_super_secret_key_here
```

**Generate secure SECRET_KEY**:
```python
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Copy output and paste into .env
```

### Step 5: Initialize Database
```bash
python init_db.py
```

**Expected output**:
```
[OK] Database initialized successfully
[OK] Tables created
[OK] Default leave types added
```

### Step 6: Verify Installation
```bash
python -c "import flask; import cv2; import deepface; print('All modules loaded successfully')"
```

---

## First Time Setup

### Step 1: Start the Application
```bash
python app.py
```

**Expected output**:
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

### Step 2: Access Setup Page
1. Open browser and go to `http://localhost:5000`
2. Click "Setup" or go to `/setup`
3. Create admin account
   - **Admin ID**: Your admin username (e.g., admin)
   - **Password**: Strong password (min 6 chars)
   - **Confirm Password**: Must match

### Step 3: First Admin Login
1. Go to `http://localhost:5000/admin_login`
2. Enter Admin ID and password
3. You're now logged in

### Step 4: Configure Settings
1. Go to Admin Dashboard
2. Click "Email Settings" (optional)
3. Add SMTP configuration if needed
4. Save settings

### Step 5: Register First Employee
1. Go to Admin Dashboard
2. Click "Register Employee"
3. Fill in details:
   - **Employee ID**: Unique ID (e.g., EMP001)
   - **Name**: Full name
   - **Email**: Email address
   - **Contact Number**: 10-digit phone number
   - **Joining Date**: YYYY-MM-DD format
   - **Password**: Auto-generated or set manually
   - **Photo**: Upload clear face photo
4. Click Register
5. Employee will receive SMS with credentials

---

## Verification

### Step 1: Check Database
```bash
# View database structure
sqlite3 database.db ".tables"

# Expected tables:
# admin employees attendance work_updates payroll projects
# project_assignments project_updates performance_reviews kpi_tracking
# leave_types leave_requests leave_balances notifications
# notification_preferences email_config user_preferences groups
# group_members messages announcements
```

### Step 2: Test API Keys
```bash
# Test Google API
python -c "from chatbot_ai import AIAssistant; a = AIAssistant(); print('Google API: OK')"

# Test SMS API
python -c "from sms_service import SMSService; print('SMS Service: OK')"
```

### Step 3: Test Face Recognition
1. Go to Employee Dashboard
2. Click "Mark Attendance"
3. Allow camera access
4. Verify face is detected (should see bounding box)

### Step 4: Test Login Sessions
1. Login as admin
2. Open another tab (should stay logged in)
3. Logout (should redirect to home)
4. Try accessing `/admin_dashboard` without login (should redirect to login)

---

## Troubleshooting

### Issue: "ModuleNotFoundError" on pip install
**Solution**:
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Clear cache
pip cache purge

# Try again
pip install -r requirements.txt
```

### Issue: "No module named 'cv2'" (OpenCV)
**Solution**:
```bash
# Reinstall OpenCV
pip uninstall opencv-python -y
pip install opencv-python==4.8.1.78
```

### Issue: "TensorFlow not found"
**Solution**:
```bash
# Reinstall TensorFlow
pip uninstall tensorflow -y
pip install tensorflow==2.10.1

# May take several minutes to compile
```

### Issue: "GOOGLE_API_KEY not found"
**Solution**:
1. Verify .env file exists in project root
2. Check that GOOGLE_API_KEY line has no spaces
3. Verify API key is correct
```bash
# Test loading
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('GOOGLE_API_KEY'))"
```

### Issue: "Database is locked"
**Solution**:
```bash
# Close any open connections
# Restart application
python app.py

# If persists, check no other processes using database
# Linux/Mac:
lsof | grep database.db

# Windows:
Get-Process | Where-Object {$_.Name -like "*python*"}
```

### Issue: "Face recognition not working"
**Solution**:
1. Check lighting (front-facing, bright)
2. Ensure face is at least 100x100 pixels
3. Remove obstructions (glasses, mask, hat)
4. Try different angle
5. Update face encoding:
   - Admin: Delete and re-register employee with new photo

### Issue: "Camera/Webcam not accessible"
**Solution**:
1. Check browser camera permissions
   - Chrome: Settings → Privacy → Camera
   - Firefox: Preferences → Privacy → Camera
2. Check system camera permissions
   - Windows: Settings → Privacy → Camera
   - Mac: System Preferences → Security → Camera
3. Try a different browser
4. Restart application

### Issue: "SMS not sending"
**Solution**:
1. Verify FAST2SMS_API_KEY is correct
2. Check phone number format (10 digits, no spaces)
3. Check account balance/quota in Fast2SMS
4. View logs: Check console output for error message
5. Test API directly:
```python
from sms_service import SMSService
result = SMSService.send_sms("9876543210", "Test message")
print(result)
```

### Issue: "Port 5000 already in use"
**Solution**:
```bash
# Use different port
python -c "from app import app; app.run(port=5001)"

# Or kill process using port
# Windows (PowerShell as Admin):
Stop-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess -Force

# Linux/Mac:
lsof -ti:5000 | xargs kill -9
```

### Issue: "Unicode/Emoji encoding errors"
**Solution**:
1. Verify Python file has UTF-8 encoding declaration
   - `# -*- coding: utf-8 -*-` at the top
2. Set environment variable:
```bash
# Windows (PowerShell)
$env:PYTHONIOENCODING = 'utf-8'

# Linux/Mac
export PYTHONIOENCODING=utf-8
```

---

## Post-Installation

### 1. Create Admin Backup
```bash
# Create additional admin account
# Via Setup page: /setup
# Keep credentials in secure location
```

### 2. Test All Features
- [ ] Login as admin
- [ ] Register an employee
- [ ] Test face recognition
- [ ] Request leave
- [ ] Check notifications
- [ ] Test chatbot
- [ ] Send message in group

### 3. Backup Database
```bash
# Create backup
sqlite3 database.db ".backup backups/database_backup.db"

# Schedule regular backups (see SECURITY_GUIDE.md)
```

### 4. Configure Email (Optional)
```bash
# For email notifications:
1. Get SMTP credentials (Gmail, Outlook, etc.)
2. Go to Admin Dashboard → Email Settings
3. Enter SMTP details
4. Test by requesting leave
5. Employee should receive email
```

### 5. Production Deployment
For production use, see [SECURITY_GUIDE.md](SECURITY_GUIDE.md):
- [ ] Change SECRET_KEY
- [ ] Disable debug mode
- [ ] Enable HTTPS
- [ ] Configure proper logging
- [ ] Setup monitoring
- [ ] Create incident response plan

### 6. Team Training
Prepare team for using the system:
- [ ] Train admins on dashboard
- [ ] Train employees on login/attendance
- [ ] Document policies for leave, payroll
- [ ] Create user manual
- [ ] Setup support contact

---

## Quick Reference Commands

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Run application
python app.py

# Run with different port
python app.py --port 5001

# Initialize database
python init_db.py

# Check Python version
python --version

# List installed packages
pip list

# Install specific version
pip install package_name==version

# Uninstall package
pip uninstall package_name

# Generate requirements file
pip freeze > requirements.txt

# Deactivate virtual environment
deactivate
```

---

## Support

### Getting Help
1. Check the documentation files:
   - `FEATURES_DOCUMENTATION.md` - Feature details
   - `SECURITY_GUIDE.md` - Security configuration
   - `UI_THEME_GUIDE.md` - UI/CSS customization

2. Check logs:
   - Console output while running
   - Check browser console (F12)
   - Check browser network tab (F12)

3. Contact support:
   - Document error message
   - Include Python version
   - Include OS type
   - Include steps to reproduce

---

## Next Steps

1. ✅ **Explore Features**: [FEATURES_DOCUMENTATION.md](FEATURES_DOCUMENTATION.md)
2. ✅ **Secure Deployment**: [SECURITY_GUIDE.md](SECURITY_GUIDE.md)
3. ✅ **Customize UI**: [UI_THEME_GUIDE.md](UI_THEME_GUIDE.md)
4. ✅ **Create Employees**: Register 2-3 test employees
5. ✅ **Test All Features**: Test each module
6. ✅ **Deploy**: Move to production when ready

---

**Installation Guide Version**: 1.0.0  
**Last Updated**: June 2026  
**Compatible With**: WorkHub AI v1.0.0
