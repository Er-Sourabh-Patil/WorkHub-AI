# WorkHub-AI
AI-powered ERP and Workforce Management System with face recognition attendance, employee management, payroll, leave workflow, project management, messaging, notifications, reporting, and Gemini AI chatbot integration using Flask, SQLite, DeepFace, and TensorFlow.


# WorkHub AI - Intelligent Workforce Management System

## Project Description

WorkHub AI is a comprehensive workforce and organizational management platform developed using Flask and SQLite. The system integrates employee management, AI-powered attendance tracking, payroll administration, project monitoring, communication services, leave management, and performance evaluation into a single centralized platform.

The application is designed to help organizations streamline daily operations, improve workforce productivity, automate administrative processes, and provide a modern digital workplace experience.

WorkHub AI combines traditional Human Resource Management System (HRMS) functionality with Artificial Intelligence features such as face-recognition-based attendance tracking and an integrated AI chatbot assistant.

The project consists of the following major modules:

1. Workforce & Employee Management
2. AI-Based Attendance Management
3. Payroll Management
4. Project Management System
5. Internal Communication Platform
6. Performance Review & Evaluation System
7. AI Chatbot Assistant
8. Notification & Announcement System

---

## Features

### AI Attendance Management

* Face recognition-based attendance tracking
* Live attendance monitoring
* Automated attendance recording
* Employee attendance history management
* Real-time camera integration

### Employee Management

* Employee profile management
* Employee dashboard
* Intern management
* User preference management
* Employee activity tracking

### Payroll Management

* Salary management
* Payroll generation
* Employee payment records
* Payroll administration dashboard

### Project Management

* Project creation and assignment
* Project progress tracking
* Project reporting system
* Project details management
* Employee project allocation

### Leave Management

* Leave request submission
* Leave approval workflow
* Leave history tracking
* Employee leave dashboard

### Communication System

* Employee-admin messaging
* Internal communication portal
* Notifications management
* Organization-wide announcements

### Performance Evaluation

* Employee performance reviews
* Feedback management
* Performance tracking
* Review administration system

### AI Chatbot Assistant

* Integrated AI-powered chatbot
* Employee assistance and support
* Quick information retrieval
* User interaction system

### Security & Access Control

* Role-based authentication
* Admin login portal
* Employee login portal
* Intern login portal
* Secure session management

---

## Technologies Used

### Programming Language

* Python 3.10+

### Backend Framework

* Flask

### Database

* SQLite

### Frontend Technologies

* HTML5
* CSS3
* JavaScript

### AI & Computer Vision

* OpenCV
* Face Recognition
* AI Chatbot Integration

### Database Management

* SQLite Database Engine

### Development Tools

* VS Code
* Git
* GitHub

### Additional Libraries

* Flask
* OpenCV
* NumPy
* SQLite3
* Requests
* Python Dotenv

---

## Project Structure

WorkHub-AI/

├── app.py
├── config.py
├── database.py
├── models.py
├── init_db.py

├── camera_api.py
├── face_utils.py

├── chatbot_ai.py

├── sms_service.py

├── static/
│   ├── css/
│   └── js/

├── templates/
│   ├── admin_dashboard.html
│   ├── employee_dashboard.html
│   ├── live_attendance.html
│   ├── payroll.html
│   ├── project_reports.html
│   ├── leave_management.html
│   └── ...

├── Structure/
│   ├── DFD Diagrams
│   ├── ER Diagrams
│   ├── System Architecture
│   ├── Activity Diagram
│   └── Use Case Diagram

├── requirements.txt

├── README.md

└── Documentation Files

---

## System Modules

### 1. User Authentication Module

* Admin Login
* Employee Login
* Intern Login
* Session Management

### 2. Attendance Management Module

* Face Recognition Attendance
* Attendance Monitoring
* Attendance Records

### 3. Employee Management Module

* Employee Registration
* Employee Information Management
* Employee Dashboard

### 4. Project Management Module

* Project Assignment
* Project Tracking
* Project Reports

### 5. Payroll Management Module

* Salary Processing
* Payroll Reports
* Payment Records

### 6. Communication Module

* Messaging System
* Notifications
* Announcements

### 7. Performance Management Module

* Employee Reviews
* Performance Tracking
* Feedback System

### 8. AI Assistant Module

* Chatbot Interaction
* Employee Support Services

---

## Database Information

The system utilizes SQLite as its primary database for storing:

* Employee Records
* Attendance Data
* Payroll Information
* Leave Requests
* Project Details
* Messages
* Notifications
* Performance Reviews
* User Authentication Data

---

## AI Attendance Workflow

### Face Recognition Process

1. Camera captures employee image
2. Face detection is performed
3. Facial features are extracted
4. Employee identity is verified
5. Attendance record is generated
6. Database is updated automatically

---

## Installation Instructions

### Prerequisites

* Python 3.10+
* Git
* pip

### Steps

### 1. Clone Repository

```bash
git clone https://github.com/Er-Sourabh-Patil/WorkHub-AI.git

cd WorkHub-AI
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

Windows:

```bash
venv\Scripts\activate
```

Linux/Mac:

```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file and add required API keys and configuration settings.

### 6. Initialize Database

```bash
python init_db.py
```

### 7. Run Application

```bash
python app.py
```

### 8. Open Browser

```text
http://127.0.0.1:5000
```

---

## Future Enhancements

* Advanced AI Analytics Dashboard
* Employee Productivity Prediction
* Face Recognition Optimization
* Mobile Application Integration
* Cloud Database Support
* Multi-Organization Support
* Email Automation System
* AI-Based Employee Performance Prediction

---

## Author

**Sourabh Patil**

Artificial Intelligence & Data Science Engineer

GitHub:
https://github.com/Er-Sourabh-Patil

---

## License

This project is developed for educational and research purposes.
