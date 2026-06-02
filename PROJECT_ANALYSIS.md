# WorkHub AI - Comprehensive Project Analysis

## 1. MAIN PYTHON FILES & PURPOSES

### Core Files

| File | Purpose | Key Functions |
|------|---------|---------------|
| **app.py** | Main Flask application with all routes | 72 routes for authentication, dashboards, API endpoints, messaging, payroll, projects, leave management, chatbot |
| **config.py** | Configuration and settings | Database path, SECRET_KEY, face recognition thresholds, session config, upload folders |
| **database.py** | Database connection management | SQLite connection, row factory setup, cleanup functions |
| **init_db.py** | Database schema initialization | 22+ database tables creation, column migration, default data insertion |
| **models.py** | (Placeholder) | Currently empty - reserved for future model definitions |

### Feature-Specific Files

| File | Purpose | Key Features |
|------|---------|--------------|
| **sms_service.py** | SMS notifications via Fast2SMS | Registration, attendance, leave approval, project assignment, payroll notifications |
| **chatbot_ai.py** | AI Assistant using Google Gemini API | Message categorization, HR/technical/project guidance, conversation tracking |
| **camera_api.py** | Face recognition & attendance | Blueprint for camera routes, face encoding, recognition, attendance marking |
| **face_utils.py** | Face detection and encoding | RetinaFace detection, DeepFace encoding, face comparison, quality scoring |
| **check_db.py** | Database verification utility | Schema validation, data integrity checks |
| **fix_encoding.py** | Encoding issue resolution | Character encoding fixes for various file types |
| **verify_db.py** | Database consistency checker | Verifies database integrity |
| **verify_schema.py** | Database schema validator | Validates all tables and columns exist |
| **build_executable.py** | PyInstaller build script | Bundles Flask app as Windows executable |

---

## 2. API CALLS & HARDCODED API KEYS

### ⚠️ CRITICAL SECURITY ISSUES

#### **Fast2SMS API (SMS Service)**
- **Location**: [sms_service.py](sms_service.py#L18)
- **Hardcoded API Key**: `DkAe7bOVgVITd6KtfUx4zQQnf06yIDnLl5VZFrCqTLhkSPPgaUFQ8CAOujku`
- **API Endpoint**: `https://www.fast2sms.com/dev/bulkV2`
- **Purpose**: Sends SMS for registration, attendance, leave approvals, project assignments, payroll
- **Risk**: **EXPOSED - SHOULD BE ROTATED IMMEDIATELY**

#### **Google Generative AI (Chatbot)**
- **Location**: [chatbot_ai.py](chatbot_ai.py#L20-L30)
- **API Key Source**: Environment variable `GOOGLE_API_KEY` (from .env)
- **API Models Supported**: 
  - `gemini-2.0-flash` (preferred)
  - `gemini-1.5-flash` (fallback)
  - `gemini-1.5-pro` (fallback)
  - `gemini-pro` (legacy)
- **Purpose**: AI-powered employee assistance (technical, HR, project management)
- **Risk**: **BETTER** - Uses env variable, but needs .env file protection

### API Integration Details

**SMS Functions**:
```python
- send_registration_sms(employee_id, name, contact_number, password)
- send_attendance_sms(employee_id, attendance_status)
- send_leave_approval_sms(employee_id, leave_type, status)
- send_leave_rejection_sms(employee_id, leave_type, reason)
- send_project_assignment_sms(employee_id, project_name, role)
- send_payroll_sms(employee_id, month, year, net_salary)
```

**Chatbot Functions**:
```python
- AIAssistant(api_key) - Initialize with Gemini API
- categorize_message(message) - Technical, HR, or Project category
- get_system_prompt(user_type) - Different prompts for admin vs employee
- get_ai_response(message, user_type) - Streaming response support
```

---

## 3. FLASK ROUTES & TEMPLATES MAPPING

### Authentication Routes (4)
| Route | Method | Template | Purpose |
|-------|--------|----------|---------|
| `/setup` | GET, POST | setup.html | Initial admin setup (one-time) |
| `/admin_login` | GET, POST | admin_login.html | Admin authentication |
| `/employee_login` | GET, POST | employee_login.html | Employee authentication |
| `/logout` | GET | - | Session termination |

### Admin Dashboard Routes (12)
| Route | Method | Template | Purpose |
|-------|--------|----------|---------|
| `/admin_dashboard` | GET | admin_dashboard.html | Main admin panel |
| `/admin_messages` | GET | admin_messages.html | Admin messaging interface |
| `/live_attendance_admin` | GET | live_attendance.html | Real-time attendance monitoring |
| `/add_employee` | POST | - | Add new employee (API) |
| `/delete_employee/<id>` | POST | - | Delete employee (API) |
| `/mark_attendance_manual` | POST | - | Manual attendance marking |
| `/admin_projects` | GET | admin_projects.html | Project management |
| `/add_project` | POST | - | Create new project |
| `/edit_project/<id>` | POST | - | Update project |
| `/assign_employee_to_project` | POST | - | Assign staff to project |
| `/unassign_employee_from_project` | POST | - | Remove staff from project |
| `/delete_project/<id>` | POST | - | Delete project |

### Employee Dashboard Routes (10)
| Route | Method | Template | Purpose |
|-------|--------|----------|---------|
| `/employee_dashboard` | GET | employee_dashboard.html | Main employee panel |
| `/employee_messages` | GET | employee_messages.html | Employee messaging |
| `/update_work` | POST | - | Update daily work description |
| `/employee_performance/<id>` | GET | employee_performance.html | View performance metrics |
| `/employee_projects` | GET | employee_projects.html | View assigned projects |
| `/submit_project_update` | POST | - | Submit project progress |
| `/employee_reviews/<id>` | GET | employee_reviews.html | View performance reviews |
| `/employee_request_leave` | GET | employee_request_leave.html | Leave request form |
| `/employee_leave_history/<id>` | GET | employee_leave_history.html | Leave history |
| `/download_my_performance` | GET | - | Export performance data |

### Payroll Routes (4)
| Route | Method | Template | Purpose |
|-------|--------|----------|---------|
| `/payroll` | GET | payroll.html | Payroll management |
| `/add_payroll` | POST | - | Add payroll record |
| `/edit_payroll/<id>` | POST | - | Edit payroll |
| `/delete_payroll/<id>` | POST | - | Delete payroll |
| `/download_payroll` | GET | - | Export payroll data |

### Performance & Reviews Routes (5)
| Route | Method | Template | Purpose |
|-------|--------|----------|---------|
| `/performance_reviews` | GET | performance_reviews.html | Admin review management |
| `/add_performance_review` | POST | - | Create review |
| `/download_employee_performance/<id>` | GET | - | Export employee performance |

### Leave Management Routes (5)
| Route | Method | Template | Purpose |
|-------|--------|----------|---------|
| `/leave_management` | GET | leave_management.html | Leave request processing |
| `/request_leave` | POST | - | Employee leave request |
| `/approve_leave/<id>` | POST | - | Approve leave request |
| `/reject_leave/<id>` | POST | - | Reject leave request |

### Settings & Preferences Routes (5)
| Route | Method | Template | Purpose |
|-------|--------|----------|---------|
| `/email_settings` | GET | email_settings.html | Email configuration |
| `/save_email_config` | POST | - | Save email settings |
| `/user_preferences` | GET | user_preferences.html | User preferences |
| `/save_preferences` | POST | - | Save preferences |
| `/notifications` | GET | notifications.html | Notification center |

### Messaging & Groups Routes (5)
| Route | Method | Template | Purpose |
|-------|--------|----------|---------|
| `/api/get_groups` | GET | - | Fetch user groups |
| `/api/send_message` | POST | - | Send message to group |
| `/api/get_messages/<id>` | GET | - | Fetch group messages |
| `/api/create_group` | POST | - | Create new group |
| `/api/message_count` | GET | - | Get unread count |

### AI Chatbot Routes (3)
| Route | Method | Purpose |
|-------|--------|---------|
| `/chatbot` | GET | Chatbot interface |
| `/api/chatbot/send_message` | POST | Process user message |
| `/api/chatbot/history` | GET | Get conversation history |
| `/api/chatbot/conversation/<id>` | GET | Get specific conversation |

### Announcements Routes (4)
| Route | Method | Purpose |
|-------|--------|---------|
| `/announcements` | GET | View announcements |
| `/admin_announcements` | GET | Create announcements |
| `/api/create_announcement` | POST | Create new announcement |
| `/api/mark_announcement_read` | POST | Mark announcement read |
| `/api/delete_announcement/<id>` | DELETE | Delete announcement |
| `/api/get_announcements` | GET | Fetch announcements |

### API & Utility Routes (5)
| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Home page (home.html) |
| `/api/stats` | GET | Dashboard statistics |
| `/api/today_work` | GET | Today's work updates |
| `/api/user_dark_mode` | GET | Dark mode preference |
| `/api/notifications` | GET | User notifications |
| `/camera_status` | GET | Camera availability check |
| `/download_employees` | GET | Export employee list |
| `/project_reports` | GET | Project analytics |
| `/test_admin_dashboard` | GET | Test dashboard (dev only) |
| `/test_employee_dashboard` | GET | Test dashboard (dev only) |

### Templates Summary (26 total)
**Admin Pages**: admin_dashboard.html, admin_login.html, admin_messages.html, admin_announcements.html, admin_projects.html
**Employee Pages**: employee_dashboard.html, employee_login.html, employee_messages.html, employee_performance.html, employee_projects.html, employee_reviews.html, employee_request_leave.html, employee_leave_history.html
**Settings**: email_settings.html, user_preferences.html, notifications.html
**Other**: home.html, setup.html, announcements.html, leave_management.html, live_attendance.html, payroll.html, performance_reviews.html, project_details.html, project_reports.html, intern_login.html

---

## 4. DATABASE SCHEMA

### Database: SQLite (database.db)

#### 22+ Tables

**User Management**
```
admin
├─ id (INT, PK)
├─ admin_id (TEXT, UNIQUE)
├─ name (TEXT)
├─ password_hash (TEXT)
└─ created_at (TIMESTAMP)

employees
├─ id (INT, PK)
├─ employee_id (TEXT, UNIQUE)
├─ name (TEXT)
├─ email (TEXT)
├─ contact_number (TEXT)
├─ joining_date (TEXT)
├─ password_hash (TEXT)
├─ photo_path (TEXT)
├─ face_encoding (BLOB) [Face recognition data]
└─ created_at (TIMESTAMP)
```

**Attendance**
```
attendance
├─ id (INT, PK)
├─ employee_id (FK)
├─ date (TEXT)
├─ time (TEXT)
├─ status (TEXT: Present/Absent)
├─ captured_image_path (TEXT)
├─ latitude (REAL)
├─ longitude (REAL)
├─ is_manual (BOOL)
├─ marked_by_admin (TEXT)
└─ created_at (TIMESTAMP)
UNIQUE(employee_id, date)

work_updates
├─ id (INT, PK)
├─ employee_id (FK)
├─ date (TEXT)
├─ work_description (TEXT)
└─ created_at (TIMESTAMP)
```

**Payroll**
```
payroll
├─ id (INT, PK)
├─ employee_id (FK)
├─ month (TEXT)
├─ year (INT)
├─ base_salary (REAL)
├─ attendance_bonus (REAL)
├─ deductions (REAL)
├─ net_salary (REAL)
├─ payment_status (TEXT)
├─ payment_date (TEXT)
├─ notes (TEXT)
├─ created_at (TIMESTAMP)
└─ updated_at (TIMESTAMP)
UNIQUE(employee_id, month, year)
```

**Projects**
```
projects
├─ id (INT, PK)
├─ project_id (TEXT, UNIQUE)
├─ project_name (TEXT)
├─ description (TEXT)
├─ status (TEXT: Active/Completed)
├─ start_date (TEXT)
├─ end_date (TEXT)
├─ budget (REAL)
├─ priority (TEXT: Low/Medium/High)
├─ created_by (FK admin)
└─ created_at, updated_at (TIMESTAMP)

project_assignments
├─ id (INT, PK)
├─ project_id (FK)
├─ employee_id (FK)
├─ role (TEXT)
├─ assignment_date (TEXT)
├─ status (TEXT)
├─ created_at, updated_at (TIMESTAMP)
UNIQUE(project_id, employee_id)

project_updates
├─ id (INT, PK)
├─ project_id (FK)
├─ employee_id (FK)
├─ update_date (TEXT)
├─ progress_percentage (INT)
├─ description (TEXT)
├─ hours_worked (REAL)
├─ status (TEXT)
└─ created_at (TIMESTAMP)
```

**Performance & Reviews**
```
performance_reviews
├─ id (INT, PK)
├─ employee_id (FK)
├─ review_date (TEXT)
├─ reviewer_id (FK admin)
├─ rating (INT: 1-5)
├─ feedback (TEXT)
├─ goals (TEXT)
├─ review_type (TEXT: Monthly/Quarterly/Annual)
├─ status (TEXT)
└─ created_at, updated_at (TIMESTAMP)

kpi_tracking
├─ id (INT, PK)
├─ employee_id (FK)
├─ kpi_name (TEXT)
├─ target_value (REAL)
├─ actual_value (REAL)
├─ month (TEXT)
├─ year (INT)
├─ status (TEXT)
└─ created_at (TIMESTAMP)
```

**Leave Management**
```
leave_types
├─ id (INT, PK)
├─ type_name (TEXT, UNIQUE)
├─ days_per_year (INT)
├─ accrual_rate (REAL)
└─ created_at (TIMESTAMP)

leave_requests
├─ id (INT, PK)
├─ employee_id (FK)
├─ leave_type (TEXT)
├─ start_date (TEXT)
├─ end_date (TEXT)
├─ reason (TEXT)
├─ status (TEXT: Pending/Approved/Rejected)
├─ approved_by (FK admin)
├─ approval_date (TEXT)
└─ created_at, updated_at (TIMESTAMP)

leave_balances
├─ id (INT, PK)
├─ employee_id (FK)
├─ leave_type (TEXT)
├─ total_days (INT)
├─ used_days (INT)
├─ remaining_days (INT)
├─ year (INT)
└─ created_at, updated_at (TIMESTAMP)
UNIQUE(employee_id, leave_type, year)
```

**Messaging & Notifications**
```
groups
├─ id (INT, PK)
├─ group_id (TEXT, UNIQUE)
├─ group_name (TEXT)
├─ description (TEXT)
├─ created_by (TEXT)
└─ created_at, updated_at (TIMESTAMP)

group_members
├─ id (INT, PK)
├─ group_id (FK)
├─ user_id (TEXT)
├─ user_type (TEXT: admin/employee)
├─ joined_at (TIMESTAMP)
UNIQUE(group_id, user_id, user_type)

messages
├─ id (INT, PK)
├─ group_id (FK)
├─ sender_id (TEXT)
├─ sender_type (TEXT)
├─ sender_name (TEXT)
├─ message_text (TEXT)
├─ is_read (BOOL)
└─ created_at (TIMESTAMP)

notifications
├─ id (INT, PK)
├─ user_id (FK)
├─ user_type (TEXT)
├─ message (TEXT)
├─ notification_type (TEXT)
├─ read_status (BOOL)
├─ related_table (TEXT)
├─ related_id (INT)
└─ created_at (TIMESTAMP)

notification_preferences
├─ id (INT, PK)
├─ user_id (FK)
├─ notification_type (TEXT)
├─ enabled (BOOL)
├─ method (TEXT: in_app/email/sms)
└─ created_at (TIMESTAMP)
```

**Chatbot**
```
chatbot_conversations
├─ id (INT, PK)
├─ user_id (FK)
├─ user_type (TEXT)
├─ conversation_id (TEXT, UNIQUE)
├─ topic (TEXT)
└─ created_at, updated_at (TIMESTAMP)

chatbot_messages
├─ id (INT, PK)
├─ conversation_id (FK)
├─ user_id (TEXT)
├─ user_message (TEXT)
├─ bot_response (TEXT)
├─ message_category (TEXT)
└─ created_at (TIMESTAMP)
```

**Announcements**
```
announcements
├─ id (INT, PK)
├─ announcement_id (TEXT, UNIQUE)
├─ title (TEXT)
├─ description (TEXT)
├─ content (TEXT)
├─ announcement_type (TEXT)
├─ priority (TEXT)
├─ created_by (FK admin)
├─ published_date (TIMESTAMP)
├─ expiry_date (TEXT)
├─ status (TEXT: active/archived)
└─ created_at (TIMESTAMP)

announcement_reads
├─ id (INT, PK)
├─ announcement_id (FK)
├─ employee_id (FK)
├─ read_at (TIMESTAMP)
UNIQUE(announcement_id, employee_id)
```

**Configuration**
```
email_config
├─ id (INT, PK)
├─ smtp_server (TEXT)
├─ smtp_port (INT)
├─ sender_email (TEXT)
├─ sender_password (TEXT)
├─ enable_notifications (BOOL)
├─ enable_reports (BOOL)
├─ enable_leave_emails (BOOL)
├─ enable_payroll_emails (BOOL)
└─ created_at, updated_at (TIMESTAMP)

user_preferences
├─ id (INT, PK)
├─ user_id (FK, UNIQUE)
├─ user_type (TEXT)
├─ dark_mode (BOOL)
├─ language (TEXT)
├─ timezone (TEXT)
├─ email_digest (BOOL)
├─ notification_frequency (TEXT)
└─ created_at, updated_at (TIMESTAMP)
```

#### Default Leave Types (8)
- Sick Leave (12 days)
- Casual Leave (10 days)
- Earned Leave (20 days)
- Unpaid Leave (0 days)
- Maternity Leave (90 days)
- Paternity Leave (10 days)
- Marriage Leave (5 days)
- Bereavement Leave (3 days)

---

## 5. CSS FILES & STYLING ANALYSIS

### CSS Files (3)

#### [style.css](static/css/style.css) - Main Stylesheet
- **Lines**: ~600+ (includes responsive design)
- **Design Theme**: Modern glassmorphism + gradient backgrounds
- **Color Palette**:
  - Primary: Dark Blue (#0f172a, #1e293b)
  - Light Mode: Soft blues & grays (#f0f4f8, #d9e2ec)
  - Accent: Green (#22c55e, #16a34a)
  - Admin: Blue gradient
  - Employee: Orange/Amber gradient
  - Error: Red tones

**Key Components**:
```css
- .container {} - Centered layout (90% width, max 1200px)
- .card {} - Glassmorphic cards with backdrop blur
- .login-container {} - Specialized login forms
- .input-group {} - Form input styling
- button {} - Green gradient buttons (primary action)
```

**Variants**:
- `.light-mode` - Light theme styling
- `.employee-login` - Orange-tinted employee login
- `.admin-login` - Blue-tinted admin login

**Responsive Breakpoints**: 768px (tablet), 480px (mobile)

#### [chatbot.css](static/css/chatbot.css) - AI Chatbot Widget
- **Purpose**: Floating chatbot widget styling
- **Key Classes**:
  - `.chatbot-widget` - Fixed position (bottom-right), 380x600px
  - `.chatbot-header` - Purple gradient header (#667eea to #764ba2)
  - `.chatbot-messages` - Message container with custom scrollbar
  - `.chat-message.user` - User messages (blue)
  - `.chat-message.bot` - Bot messages (white)
  - `.typing-indicator` - Animated typing dots

**Animations**:
- `slideUp` - Widget entrance
- `messageSlide` - Message appearance
- `typing` - Typing indicator animation

#### [footer.css](static/css/footer.css) - Unified Footer
- **Purpose**: Consistent footer across all pages
- **Styling**:
  - `.footer` - Dark background with gradient, 30px padding
  - Responsive: 768px (20px padding), 480px (15px padding)
  - Link color: #60a5fa (blue), hover: #93c5fd

---

## 6. STYLING INCONSISTENCIES & ISSUES

### ⚠️ **Identified Issues**

#### 1. **Color Palette Inconsistency**
- **Issue**: Multiple color schemes (green, blue, orange/amber, purple)
- **Location**: style.css, chatbot.css
- **Impact**: Disjointed visual experience
- **Recommendation**: 
  - Establish single primary palette: Blue (#3b82f6) + Green (#22c55e)
  - Use Purple (#667eea) only for chatbot
  - Consistent accent colors across all pages

#### 2. **Font Family Mismatch**
- **Declared**: 'Poppins', sans-serif (throughout)
- **Issue**: No webfont import (CSS assumes local/fallback)
- **Recommendation**: Add Google Fonts import:
  ```html
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
  ```

#### 3. **Dark Mode Implementation**
- **Status**: Partial (body.light-mode exists, but not fully implemented)
- **Issue**: Many components don't have .light-mode variants
- **Elements Missing**:
  - Chatbot widget light mode
  - Footer light mode
  - Button light mode styling
- **Recommendation**: Implement complete light/dark mode CSS variable system

#### 4. **Responsive Design Gaps**
- **Issue**: Only 2 breakpoints (768px, 480px), missing XL+ screens (>1200px)
- **Missing**: Tablet-landscape (992px), Large desktop (1440px+)
- **Recommendation**: Add breakpoints at 992px, 1440px

#### 5. **Z-Index Conflicts**
- **Chatbot widget**: z-index: 10000 (extreme)
- **Other modals/dropdowns**: Unknown z-index values
- **Issue**: Potential stacking context problems
- **Recommendation**: Define z-index layer system (e.g., 100, 200, 300, etc.)

#### 6. **Accessibility Issues**
- **Issue**: No ARIA labels, insufficient color contrast in some states
- **Buttons**: Hover states only (no focus/active distinction for keyboard)
- **Recommendation**: 
  - Add focus states: `button:focus { outline: 2px solid #3b82f6; }`
  - Ensure WCAG AA contrast ratios (4.5:1 for text)

#### 7. **CSS Specificity Conflicts**
- **Issue**: Multiple selectors for same elements (e.g., button styling in multiple files)
- **Problem**: Cascade order dependency
- **Recommendation**: Implement BEM naming convention (e.g., `.chatbot__header`, `.form__input`)

#### 8. **Missing CSS Reset/Normalize**
- **Issue**: Only basic reset at start of style.css (*, body)
- **Recommendation**: Use modern CSS reset or normalize.css for consistency

#### 9. **Performance Issues**
- **Issue**: Multiple large gradients on background elements
- **Recommendation**: Use CSS filters sparingly, cache computed styles

---

## 7. TECHNOLOGY STACK

### Backend
- **Framework**: Flask 2.3.3
- **Server**: Development server (needs production WSGI)
- **Security**: Werkzeug 2.3.7 (password hashing)

### Database
- **Type**: SQLite3
- **ORM**: None (raw SQL queries)

### Face Recognition & CV
- **DeepFace** 0.0.79 (face encoding)
- **RetinaFace** 0.0.12+ (face detection)
- **OpenCV** 4.8.1.78 (image processing)
- **TensorFlow** 2.10.1 (DL backend)
- **NumPy** 1.23.5 (array operations)

### AI/ML
- **Google Generative AI** (Gemini models)
- **SciPy** (cosine similarity for face matching)

### Utilities
- **Requests** 2.31.0 (HTTP API calls)
- **Pandas** 2.0.3 (data export)
- **Pillow** 10.0.0 (image handling)
- **python-dotenv** 1.0.0 (.env file support)

### Frontend
- **HTML5 Templates** (Jinja2)
- **CSS3** (modern features: gradients, backdrop-filter, animations)
- **JavaScript** (vanilla - no framework detected)

---

## 8. KEY SECURITY CONCERNS

### Critical 🔴
1. **Fast2SMS API key exposed in source code** (sms_service.py:18)
2. **No HTTPS enforcement** (SESSION_COOKIE_SECURE = False)
3. **Test routes active** (/test_admin_dashboard, /test_employee_dashboard)
4. **Raw SQL queries** (SQL injection potential if inputs not properly sanitized)

### High 🟠
1. **No CSRF protection** (Flask-WTF recommended)
2. **Session secrets** (dev-secret-key-change-in-production)
3. **Password hashing** is good (Werkzeug), but no rate limiting on login
4. **Face encoding stored as BLOB** (no encryption)

### Medium 🟡
1. **FACE_RECOGNITION_THRESHOLD** configurable but hardcoded values
2. **No input validation** on many endpoints
3. **File upload** without strict MIME type checking
4. **Database backups** - no automated backup strategy

---

## 9. FEATURE SUMMARY

### Complete Features ✅
- **Authentication**: Admin, Employee login/logout
- **Attendance**: Face recognition, manual marking, geo-location
- **Payroll**: Add/edit/delete, export to CSV
- **Projects**: Create, assign, track progress
- **Performance Reviews**: Monthly/annual reviews with ratings
- **Leave Management**: 8 leave types, request/approval workflow
- **Messaging**: Group-based messaging with read status
- **Announcements**: Create/publish/read tracking
- **Notifications**: In-app notification system
- **Dark Mode**: User preference storage
- **AI Chatbot**: Google Gemini-powered assistant
- **SMS Alerts**: Event-triggered SMS notifications
- **Email Config**: SMTP configuration storage

### Partial/Incomplete Features ⚠️
- **Email Notifications**: Configured but not fully implemented
- **KPI Tracking**: Schema exists, no UI
- **Intern Login**: Template exists, route not implemented
- **Face Encoding Optimization**: High quality thresholds not adaptive

---

## SUMMARY TABLE

| Category | Status | Count | Notes |
|----------|--------|-------|-------|
| Python Modules | Active | 10 | Core + 7 utilities |
| Flask Routes | Complete | 72 | Fully mapped |
| Database Tables | Complete | 22 | Normalized schema |
| HTML Templates | Complete | 26 | All mapped |
| CSS Files | Complete | 3 | Some inconsistencies |
| API Endpoints | External | 2 | Fast2SMS, Google Gemini |
| Hardcoded Secrets | Found | 1 | Fast2SMS key (CRITICAL) |
| Security Issues | Identified | 8 | Critical: 1, High: 4, Medium: 3 |

