# WorkHub AI - Complete Documentation

## Overview
WorkHub AI is an Integrated HR Management & AI Assistant System built with Flask, featuring face recognition-based attendance tracking, employee management, leave management, payroll system, project management, and an AI chatbot.

## Table of Contents
1. [Getting Started](#getting-started)
2. [System Architecture](#system-architecture)
3. [Features & Modules](#features--modules)
4. [Database Schema](#database-schema)
5. [API Endpoints](#api-endpoints)
6. [Configuration](#configuration)
7. [Security](#security)
8. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Prerequisites
- Python 3.8+
- SQLite 3
- Webcam (for face recognition)
- All dependencies in `requirements.txt`

### Installation
```bash
# 1. Clone/Download the project
# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create .env file with API keys
cp .env.example .env  # Then update with your API keys

# 6. Initialize database
python init_db.py

# 7. Run the application
python app.py
```

### First Time Setup
1. Visit `http://localhost:5000` to access the home page
2. Go to `/setup` to create the first admin account
3. Login as admin to start managing the system
4. Add employees through the admin dashboard

---

## System Architecture

### Technology Stack
- **Backend**: Flask 2.3.3
- **Database**: SQLite 3
- **Frontend**: HTML5, CSS3, JavaScript
- **Face Recognition**: DeepFace, RetinaFace, TensorFlow
- **AI Integration**: Google Generative AI (Gemini)
- **SMS Service**: Fast2SMS API
- **Image Processing**: OpenCV, Pillow
- **Authentication**: Werkzeug (password hashing)

### Project Structure
```
WorkHub AI/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── database.py            # Database connection handler
├── init_db.py             # Database initialization & schema
├── models.py              # Data models
├── sms_service.py         # SMS notification service
├── chatbot_ai.py          # AI assistant (Gemini)
├── face_utils.py          # Face recognition utilities
├── camera_api.py          # Camera/video streaming
├── .env                   # Environment variables (API keys)
├── requirements.txt       # Python dependencies
├── templates/             # HTML templates (24 pages)
├── static/
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript files
│   └── uploads/          # User uploads
└── captured_faces/       # Face capture storage
```

---

## Features & Modules

### 1. Authentication System
**Files**: `app.py` (routes: /admin_login, /employee_login, /setup)

**Features**:
- Admin and Employee login with password hashing
- Session management with 24-hour expiration
- Setup page for initial admin creation
- Secure password validation

**Login Decorators**:
- `@login_required_admin()` - Protects admin routes
- `@login_required_employee()` - Protects employee routes

**Key Routes**:
- `POST /setup` - Create admin account
- `POST /admin_login` - Admin authentication
- `POST /employee_login` - Employee authentication
- `GET /logout` - Session termination

---

### 2. Face Recognition & Attendance
**Files**: `camera_api.py`, `face_utils.py`, `app.py`

**Features**:
- Real-time face detection and recognition
- Automatic attendance marking based on face
- Manual attendance marking by admin
- Attendance history with timestamps
- Face encoding storage in database
- Quality-based adaptive thresholds

**Key Endpoints**:
- `GET /camera` - Live camera feed
- `GET /video_feed` - Video streaming endpoint
- `POST /mark_attendance_manual` - Manual attendance entry
- `GET /attendance_report` - View attendance history
- `GET /live_attendance_admin` - Admin live attendance monitoring

**Face Recognition Config** (in config.py):
```python
FACE_RECOGNITION_THRESHOLD = 60      # Base threshold (%)
HIGH_QUALITY_THRESHOLD = 58          # >70% quality
MEDIUM_QUALITY_THRESHOLD = 60        # 50-70% quality
LOW_QUALITY_THRESHOLD = 65           # <50% quality
DETECTION_STABILITY_FRAMES = 5       # Frames to confirm detection
```

---

### 3. Employee Management
**Files**: `app.py`, `templates/admin_dashboard.html`

**Features**:
- Employee registration with face photo
- Employee profile management
- Contact number and email storage
- Employee deletion with data cleanup
- Employee list with search functionality

**Key Routes**:
- `POST /register_employee` - Register new employee
- `GET /employee_dashboard` - Employee profile
- `POST /delete_employee` - Remove employee
- `GET /admin_dashboard` - Admin view all employees

**Employee Data Stored**:
- Employee ID (unique)
- Name
- Email
- Contact Number
- Joining Date
- Password Hash
- Photo Path
- Face Encoding (BLOB)

---

### 4. Leave Management
**Files**: `app.py`, `init_db.py`, `sms_service.py`

**Features**:
- Multiple leave types (Sick, Casual, Earned, etc.)
- Leave request submission by employees
- Approval/Rejection workflow by admin
- Leave balance tracking
- SMS notifications
- Leave history reports

**Leave Types**:
- Sick Leave (12 days/year)
- Casual Leave (10 days/year)
- Earned Leave (20 days/year)
- Unpaid Leave
- Maternity Leave (90 days)
- Paternity Leave (10 days)
- Marriage Leave (5 days)
- Bereavement Leave (3 days)

**Key Routes**:
- `POST /request_leave` - Submit leave request
- `POST /approve_leave` - Approve leave
- `POST /reject_leave` - Reject leave
- `GET /leave_management` - View all leave requests
- `GET /employee_leave_history` - View personal leave history

**Database Tables**:
- `leave_types` - Define leave types
- `leave_requests` - Leave requests with status
- `leave_balances` - Track remaining days per employee

---

### 5. Payroll System
**Files**: `app.py`, `templates/payroll.html`

**Features**:
- Payroll record creation and management
- Salary calculation (base + bonus - deductions)
- Payment status tracking
- Monthly payroll reports
- SMS notifications for payroll

**Payroll Fields**:
- Employee ID
- Month and Year
- Base Salary
- Attendance Bonus
- Deductions
- Net Salary
- Payment Status (Pending/Completed)
- Payment Date
- Notes

**Key Routes**:
- `POST /add_payroll` - Add payroll record
- `POST /update_payroll` - Update payroll
- `POST /delete_payroll` - Delete payroll record
- `GET /payroll` - View all payroll records

**Status Values**:
- `Pending` - Not yet paid
- `Completed` - Payment processed

---

### 6. Project Management
**Files**: `app.py`, `templates/project_details.html`

**Features**:
- Create and manage projects
- Assign employees to projects
- Track project status and progress
- Project updates and hours tracking
- Project reports
- Team member management

**Project Fields**:
- Project ID (unique)
- Project Name
- Description
- Status (Active/Completed/On Hold)
- Start Date, End Date
- Budget
- Priority (Low/Medium/High)
- Created By (admin ID)

**Key Routes**:
- `POST /create_project` - Create new project
- `POST /update_project` - Update project details
- `POST /assign_project` - Assign employee to project
- `POST /remove_from_project` - Remove employee from project
- `POST /submit_project_update` - Submit project update
- `GET /project_details` - View project details
- `GET /project_reports` - View project reports

**Project Status**:
- `Active` - Currently ongoing
- `Completed` - Project finished
- `On Hold` - Temporarily paused

---

### 7. Performance Reviews & KPIs
**Files**: `app.py`, `templates/performance_reviews.html`

**Features**:
- Monthly/Quarterly performance reviews
- 5-star rating system
- Feedback and goals documentation
- KPI tracking
- Performance history

**Review Fields**:
- Employee ID
- Review Date
- Reviewer (Admin ID)
- Rating (1-5 stars)
- Feedback
- Goals
- Review Type
- Status

**KPI Fields**:
- Employee ID
- KPI Name
- Target Value
- Actual Value
- Month and Year
- Status

**Key Routes**:
- `POST /add_performance_review` - Create performance review
- `GET /performance_reviews` - View all reviews

---

### 8. Notifications & Alerts
**Files**: `app.py`, `init_db.py`

**Features**:
- In-app notifications
- SMS notifications for major events
- Real-time alerts
- Notification preferences
- Read/Unread status tracking

**Notification Types**:
- `attendance` - Attendance marked
- `leave_request` - Leave request status
- `payroll` - Payroll generated
- `project` - Project assignment
- `review` - Performance review
- `info` - General information

**Key Routes**:
- `GET /notifications` - View notifications
- `POST /mark_announcement_read` - Mark as read
- `GET /get_unread_count` - Get unread count

**SMS Notifications for**:
- Employee registration
- Attendance marking
- Leave approval/rejection
- Project assignment
- Payroll generation

---

### 9. Group Messaging & Chat
**Files**: `app.py`, `templates/employee_messages.html`

**Features**:
- Group-based messaging
- Real-time message delivery
- Message history
- Multiple groups support
- User mentions and tagging
- General discussion group (auto-created)

**Key Routes**:
- `POST /send_message` - Send message to group
- `GET /messages` - Retrieve group messages
- `POST /create_group` - Create new group
- `GET /get_groups` - List all groups

**Message Fields**:
- Group ID
- Sender (employee ID)
- Message text
- Timestamp
- Read status

---

### 10. AI Chatbot Assistant
**Files**: `chatbot_ai.py`, `app.py`

**Features**:
- Google Generative AI (Gemini) powered
- Technical issue resolution
- HR policy guidance
- Project management advice
- 24/7 availability
- Multi-user support

**Chatbot Capabilities**:
- Technical troubleshooting
- HR & Leave policy explanation
- Project management guidance
- General workplace questions
- Context-aware responses

**Key Routes**:
- `POST /chat` - Send message to chatbot
- `GET /chatbot` - Chatbot interface

**Available Models** (in order of preference):
1. gemini-2.0-flash
2. gemini-1.5-flash
3. gemini-1.5-pro
4. gemini-pro

---

### 11. Announcements
**Files**: `app.py`, `templates/announcements.html`

**Features**:
- Create and manage announcements
- Broadcast to all users
- Mark as read
- View announcement history
- Admin-only creation

**Key Routes**:
- `POST /create_announcement` - Create announcement
- `GET /announcements` - View all announcements
- `POST /mark_announcement_read` - Mark read
- `POST /delete_announcement` - Delete announcement

---

### 12. User Preferences & Settings
**Files**: `app.py`, `templates/user_preferences.html`

**Features**:
- Dark mode toggle
- Language selection
- Timezone configuration
- Notification frequency
- Email digest preferences

**Preferences Saved**:
- Dark Mode (enabled/disabled)
- Language (en, es, fr, etc.)
- Timezone (Asia/Kolkata, etc.)
- Email Digest (enabled/disabled)
- Notification Frequency (instant/daily/weekly)

---

## Database Schema

### Core Tables

#### admin
```sql
- id (PK)
- admin_id (unique)
- name
- password_hash
- created_at
```

#### employees
```sql
- id (PK)
- employee_id (unique)
- name
- email
- contact_number
- joining_date
- password_hash
- photo_path
- face_encoding (BLOB)
- created_at
```

#### attendance
```sql
- id (PK)
- employee_id (FK)
- date
- time
- status (Present/Absent/Leave)
- captured_image_path
- latitude, longitude
- is_manual (0/1)
- marked_by_admin
- created_at
- UNIQUE(employee_id, date)
```

#### leave_requests
```sql
- id (PK)
- employee_id (FK)
- leave_type
- start_date
- end_date
- reason
- status (Pending/Approved/Rejected)
- approved_by (FK to admin)
- approval_date
- created_at, updated_at
```

#### payroll
```sql
- id (PK)
- employee_id (FK)
- month, year
- base_salary
- attendance_bonus
- deductions
- net_salary
- payment_status (Pending/Completed)
- payment_date
- notes
- created_at, updated_at
- UNIQUE(employee_id, month, year)
```

#### projects
```sql
- id (PK)
- project_id (unique)
- project_name
- description
- status (Active/Completed/On Hold)
- start_date, end_date
- budget
- priority (Low/Medium/High)
- created_by (FK to admin)
- created_at, updated_at
```

#### performance_reviews
```sql
- id (PK)
- employee_id (FK)
- review_date
- reviewer_id (FK to admin)
- rating (1-5)
- feedback
- goals
- review_type (Monthly/Quarterly)
- status (Completed/Pending)
- created_at, updated_at
```

#### messages
```sql
- id (PK)
- group_id (FK)
- sender_id (employee_id)
- message_text
- sender_type (employee/admin)
- is_read (0/1)
- created_at
```

#### notifications
```sql
- id (PK)
- user_id (FK)
- user_type
- message
- notification_type
- read_status (0/1)
- related_table
- related_id
- created_at
```

---

## API Endpoints

### Authentication
```
POST /setup                    - Create admin account
POST /admin_login             - Admin login
POST /employee_login          - Employee login
GET /logout                   - Logout
```

### Attendance
```
GET /camera                   - Live camera feed
GET /video_feed              - Video streaming
POST /mark_attendance_manual  - Manual attendance marking
GET /attendance_report        - View attendance history
GET /live_attendance_admin    - Admin monitoring
```

### Employees
```
POST /register_employee       - Register employee
GET /employee_dashboard       - Employee profile
POST /delete_employee         - Delete employee
GET /admin_dashboard          - Admin view employees
```

### Leave Management
```
POST /request_leave          - Submit leave request
POST /approve_leave          - Approve leave
POST /reject_leave           - Reject leave
GET /leave_management        - Admin view requests
GET /employee_leave_history  - Employee leave history
```

### Payroll
```
POST /add_payroll           - Add payroll record
POST /update_payroll        - Update payroll
POST /delete_payroll        - Delete payroll record
GET /payroll                - View payroll records
```

### Projects
```
POST /create_project        - Create project
POST /update_project        - Update project
POST /assign_project        - Assign employee
POST /remove_from_project   - Remove employee
POST /submit_project_update - Submit update
GET /project_details        - View project
GET /project_reports        - View reports
```

### Performance
```
POST /add_performance_review - Add review
GET /performance_reviews     - View reviews
```

### Messaging
```
POST /send_message          - Send group message
GET /messages               - Get messages
POST /create_group          - Create group
GET /get_groups             - List groups
```

### Notifications
```
GET /notifications          - View notifications
POST /mark_announcement_read - Mark read
GET /get_unread_count       - Unread count
```

### Announcements
```
POST /create_announcement   - Create announcement
GET /announcements          - View announcements
POST /delete_announcement   - Delete announcement
```

### AI Chatbot
```
POST /chat                  - Send message to AI
GET /chatbot                - Chatbot interface
```

---

## Configuration

### Environment Variables (.env)
```bash
# API Keys
GOOGLE_API_KEY=your_google_gemini_api_key
FAST2SMS_API_KEY=your_fast2sms_api_key
SECRET_KEY=your_secret_key_for_sessions

# Database
DATABASE_PATH=database.db

# Optional
FLASK_ENV=development
FLASK_DEBUG=True
```

### Config File (config.py)
```python
# Face Recognition Thresholds
FACE_RECOGNITION_THRESHOLD = 60
HIGH_QUALITY_THRESHOLD = 58
MEDIUM_QUALITY_THRESHOLD = 60
LOW_QUALITY_THRESHOLD = 65

# Session Configuration
PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
SESSION_COOKIE_SECURE = False  # True for production with HTTPS
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
```

---

## Security

### Implemented Security Measures
✅ Password hashing with Werkzeug (SHA256)
✅ Session-based authentication
✅ Login required decorators for protected routes
✅ CSRF protection through Flask sessions
✅ HTTPOnly cookies (no JavaScript access)
✅ SameSite cookie policy
✅ API keys in environment variables (not hardcoded)
✅ UTF-8 encoding throughout application
✅ SQL injection prevention (parameterized queries)
✅ Input validation on forms

### Security Recommendations for Production
⚠️ Set `SESSION_COOKIE_SECURE = True` (requires HTTPS)
⚠️ Set `SECRET_KEY` to a strong random value
⚠️ Use environment-specific configuration
⚠️ Enable HTTPS/SSL
⚠️ Add rate limiting on login attempts
⚠️ Implement 2FA for admin accounts
⚠️ Regular database backups
⚠️ Log all admin actions
⚠️ Regular security audits

---

## Troubleshooting

### Common Issues

#### 1. "Chatbot feature not available"
**Solution**: Install Google Generative AI
```bash
pip install google-generativeai
```

#### 2. "FAST2SMS_API_KEY not found"
**Solution**: Add to .env file
```bash
FAST2SMS_API_KEY=your_actual_api_key
```

#### 3. Face Recognition Not Working
**Solution**: Ensure good lighting and clear face
- Good lighting from front
- Face at least 100x100 pixels
- No obstructions (sunglasses, mask)
- Direct eye contact with camera

#### 4. Database Lock Error
**Solution**: Close other database connections
```bash
# Restart the application
python app.py
```

#### 5. "Employee not found" on Attendance
**Solution**: Register employee first
- Admin Dashboard → Register Employee
- Take clear face photo
- Ensure proper lighting

---

## Best Practices

### For Administrators
1. ✅ Regularly backup database
2. ✅ Monitor attendance discrepancies
3. ✅ Process leave requests promptly
4. ✅ Generate monthly payroll on time
5. ✅ Review performance regularly
6. ✅ Create announcements for important updates
7. ✅ Archive old data quarterly

### For Employees
1. ✅ Mark attendance using face recognition
2. ✅ Request leave in advance
3. ✅ Update project progress regularly
4. ✅ Review performance feedback
5. ✅ Check announcements regularly
6. ✅ Set notification preferences
7. ✅ Keep contact info updated

---

## Support & Maintenance

For issues or feature requests, please:
1. Check documentation
2. Review error logs
3. Check database integrity
4. Restart application
5. Contact system administrator

**Last Updated**: June 2026
**Version**: 1.0.0
