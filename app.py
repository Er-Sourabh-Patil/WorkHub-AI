# -*- coding: utf-8 -*-
"""
WorkHub AI - Integrated HR Management & AI Assistant System
Main Flask application with face recognition, attendance, leave management, payroll, and AI chatbot
"""
from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
from functools import wraps
import os
import sys
import numpy as np
import cv2
import secrets
import uuid
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from config import SECRET_KEY
from database import get_db, close_db
from init_db import init_db
from face_utils import encode_face
from camera_api import camera_bp
from sms_service import (
    send_registration_sms,
    send_attendance_sms,
    send_leave_approval_sms,
    send_leave_rejection_sms,
    send_project_assignment_sms,
    send_payroll_sms
)

# Try to import chatbot (optional feature)
try:
    from chatbot_ai import get_ai_assistant
    CHATBOT_AVAILABLE = True
except Exception as e:
    print(f"[WARN] Chatbot feature not available: {e}")
    CHATBOT_AVAILABLE = False
    def get_ai_assistant(*args, **kwargs):
        return None

# ============================================================================
# HANDLE PYINSTALLER PATHS
# ============================================================================

def get_base_path():
    """Get the correct base path for bundled files (works with PyInstaller)"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable (PyInstaller)
        return sys._MEIPASS
    else:
        # Running as normal Python script
        return os.path.dirname(os.path.abspath(__file__))

BASE_PATH = get_base_path()
TEMPLATE_FOLDER = os.path.join(BASE_PATH, 'templates')
STATIC_FOLDER = os.path.join(BASE_PATH, 'static')

# Create Flask app with correct paths
app = Flask(__name__, 
            template_folder=TEMPLATE_FOLDER,
            static_folder=STATIC_FOLDER)
app.secret_key = SECRET_KEY

# Configure session
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# ============================================================================
# SESSION MANAGEMENT DECORATORS
# ============================================================================

def login_required_admin(f):
    """Decorator to protect admin-only routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin" not in session:
            return redirect("/admin_login")
        return f(*args, **kwargs)
    return decorated_function

def login_required_employee(f):
    """Decorator to protect employee-only routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "employee" not in session:
            return redirect("/employee_login")
        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def make_session_permanent():
    """Make session permanent with configured lifetime"""
    session.permanent = True
    app.permanent_session_lifetime = app.config['PERMANENT_SESSION_LIFETIME']

UPLOAD_FOLDER = os.path.join(STATIC_FOLDER, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

init_db()


def initialize_groups():
    """Initialize default group and add all users to it"""
    conn = get_db()
    try:
        # Check if general group exists
        general_group = conn.execute(
            "SELECT id FROM groups WHERE group_id='general'"
        ).fetchone()
        
        if not general_group:
            # Create general group
            conn.execute("""
                INSERT INTO groups (group_id, group_name, description, created_by)
                VALUES (?, ?, ?, ?)
            """, ('general', 'General Discussion', 'Group for all users to communicate', 'system'))
            
            # Add all admins to general group
            admins = conn.execute("SELECT admin_id FROM admin").fetchall()
            for admin in admins:
                try:
                    conn.execute("""
                        INSERT INTO group_members (group_id, user_id, user_type)
                        VALUES (?, ?, ?)
                    """, ('general', admin['admin_id'], 'admin'))
                except:
                    pass  # Already exists
            
            # Add all employees to general group
            employees = conn.execute("SELECT employee_id FROM employees").fetchall()
            for emp in employees:
                try:
                    conn.execute("""
                        INSERT INTO group_members (group_id, user_id, user_type)
                        VALUES (?, ?, ?)
                    """, ('general', emp['employee_id'], 'employee'))
                except:
                    pass  # Already exists
            
            conn.commit()
            print("[OK] Default general group initialized")
        else:
            # Ensure all admins and employees are members of general group
            admins = conn.execute("SELECT admin_id FROM admin").fetchall()
            for admin in admins:
                try:
                    conn.execute("""
                        INSERT INTO group_members (group_id, user_id, user_type)
                        VALUES (?, ?, ?)
                    """, ('general', admin['admin_id'], 'admin'))
                except:
                    pass  # Already exists
            
            employees = conn.execute("SELECT employee_id FROM employees").fetchall()
            for emp in employees:
                try:
                    conn.execute("""
                        INSERT INTO group_members (group_id, user_id, user_type)
                        VALUES (?, ?, ?)
                    """, ('general', emp['employee_id'], 'employee'))
                except:
                    pass  # Already exists
            
            conn.commit()
    except Exception as e:
        print(f"[WARN] Error initializing groups: {e}")
    finally:
        close_db(conn)


# Initialize groups on app startup
initialize_groups()
app.register_blueprint(camera_bp)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/setup", methods=["GET", "POST"])
def setup():
    """Initial admin setup - only works if no admin exists yet"""
    conn = get_db()
    try:
        admin_count = conn.execute("SELECT COUNT(*) as cnt FROM admin").fetchone()["cnt"]
        if admin_count > 0:
            return "Admin already exists. Setup is disabled.", 403

        if request.method == "POST":
            admin_id = request.form.get("admin_id", "").strip()
            password = request.form.get("password", "").strip()
            confirm_password = request.form.get("confirm_password", "").strip()

            if not all([admin_id, password, confirm_password]):
                return "All fields are required", 400

            if len(admin_id) < 3:
                return "Admin ID must be at least 3 characters", 400

            if len(password) < 6:
                return "Password must be at least 6 characters", 400

            if password != confirm_password:
                return "Passwords do not match", 400

            conn.execute(
                "INSERT INTO admin (admin_id, password_hash) VALUES (?, ?)",
                (admin_id, generate_password_hash(password))
            )
            conn.commit()
            return redirect("/admin_login")

        return render_template("setup.html")
    finally:
        close_db(conn)


@app.route("/test_admin_dashboard")
def test_admin_dashboard():
    """Test dashboard without authentication"""
    session["admin"] = "test_admin"
    conn = get_db()
    try:
        employees = conn.execute("SELECT * FROM employees").fetchall()
        return render_template("admin_dashboard.html", employees=employees)
    finally:
        close_db(conn)


@app.route("/test_employee_dashboard")
def test_employee_dashboard():
    """Test dashboard without authentication"""
    session["employee"] = "test_employee"
    return render_template("employee_dashboard.html")


@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        admin_id = request.form.get("admin_id", "").strip()
        password = request.form.get("password", "").strip()

        if not admin_id or not password:
            return "❌ Admin ID and password are required", 400

        conn = get_db()
        try:
            admin = conn.execute(
                "SELECT * FROM admin WHERE admin_id=?",
                (admin_id,)
            ).fetchone()

            if admin and check_password_hash(admin["password_hash"], password):
                session["admin"] = admin_id
                session.permanent = True
                return redirect("/admin_dashboard")

            return "❌ Invalid credentials", 401
        finally:
            close_db(conn)

    return render_template("admin_login.html")


@app.route("/admin_dashboard")
def admin_dashboard():
    if "admin" not in session:
        return redirect("/admin_login")

    conn = get_db()
    try:
        employees = conn.execute("SELECT * FROM employees").fetchall()
        return render_template("admin_dashboard.html", employees=employees)
    finally:
        close_db(conn)


@app.route("/admin_messages")
def admin_messages():
    """Admin dedicated messages page"""
    if "admin" not in session:
        return redirect("/admin_login")
    return render_template("admin_messages.html")


@app.route("/live_attendance_admin")
def live_attendance_admin():
    """Admin page to monitor live attendance"""
    if "admin" not in session:
        return redirect("/admin_login")
    return render_template("live_attendance.html")


@app.route("/add_employee", methods=["POST"])
def add_employee():
    if "admin" not in session:
        return redirect("/admin_login")

    try:
        employee_id = request.form.get("employee_id", "").strip()
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        contact_number = request.form.get("contact_number", "").strip()
        joining_date = request.form.get("joining_date", "").strip()
        password = request.form.get("password", "").strip()

        # Validate inputs
        if not all([employee_id, name, email, contact_number, joining_date, password]):
            return "❌ All fields are required", 400

        if "photo" not in request.files:
            return "❌ Photo file is required", 400

        photo = request.files["photo"]
        if photo.filename == "":
            return "❌ No photo selected", 400

        # Secure filename
        photo.filename = f"{employee_id}_{secrets.token_hex(4)}.jpg"
        path = os.path.join(UPLOAD_FOLDER, photo.filename)

        # Check if employee already exists
        conn = get_db()
        try:
            existing = conn.execute(
                "SELECT * FROM employees WHERE employee_id=?",
                (employee_id,)
            ).fetchone()

            if existing:
                return f"❌ Employee ID '{employee_id}' already exists", 409

            # Save photo and encode face
            photo.save(path)
            encoding = encode_face(path)

            if encoding is None:
                if os.path.exists(path):
                    os.remove(path)
                return "❌ Face encoding failed. Please ensure the photo contains a clear face", 400

            # Insert into database
            conn.execute("""
            INSERT INTO employees (employee_id, name, email, contact_number, joining_date, password_hash, photo_path, face_encoding)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                employee_id,
                name,
                email,
                contact_number,
                joining_date,
                generate_password_hash(password),
                path,
                encoding.tobytes()
            ))
            conn.commit()

            # Send registration SMS notification
            try:
                sms_result = send_registration_sms(employee_id, name, contact_number, password)
                print(f"[SMS] Registration SMS result: {sms_result}")
            except Exception as sms_error:
                print(f"[WARN] Failed to send registration SMS: {sms_error}")

            return redirect("/admin_dashboard")
        except Exception as e:
            # Cleanup on error
            if os.path.exists(path):
                try:
                    os.remove(path)
                except:
                    pass
            return f"❌ Error adding employee: {str(e)}", 500
        finally:
            close_db(conn)

    except Exception as e:
        return f"❌ Unexpected error: {str(e)}", 500


@app.route("/employee_login", methods=["GET", "POST"])
def employee_login():
    if request.method == "POST":
        employee_id = request.form.get("employee_id", "").strip()
        password = request.form.get("password", "").strip()

        if not employee_id or not password:
            return "❌ Employee ID and password are required", 400

        conn = get_db()
        try:
            employee = conn.execute(
                "SELECT * FROM employees WHERE employee_id=?",
                (employee_id,)
            ).fetchone()

            if employee and check_password_hash(employee["password_hash"], password):
                session["employee"] = employee_id
                session.permanent = True
                return redirect("/employee_dashboard")

            return "❌ Invalid credentials", 401
        finally:
            close_db(conn)

    return render_template("employee_login.html")


@app.route("/employee_dashboard")
def employee_dashboard():
    if "employee" not in session:
        return redirect("/employee_login")

    employee_id = session["employee"]

    conn = get_db()
    try:
        # Get employee name
        employee = conn.execute(
            "SELECT name FROM employees WHERE employee_id=?",
            (employee_id,)
        ).fetchone()
        employee_name = employee['name'] if employee else employee_id

        # Get today's attendance status
        from datetime import datetime, date
        today = date.today().isoformat()

        attendance = conn.execute(
            "SELECT * FROM attendance WHERE employee_id=? AND date=?",
            (employee_id, today)
        ).fetchone()

        # Get attendance history with work updates
        history_raw = conn.execute(
            "SELECT * FROM attendance WHERE employee_id=? ORDER BY date DESC LIMIT 30",
            (employee_id,)
        ).fetchall()

        # Enrich history with work updates
        history = []
        for record in history_raw:
            work_entry = conn.execute(
                "SELECT work_description FROM work_updates WHERE employee_id=? AND date=?",
                (employee_id, record['date'])
            ).fetchone()
            
            record_dict = dict(record)
            record_dict['work_description'] = work_entry['work_description'] if work_entry else "-"
            history.append(record_dict)

        # Get latest payroll information
        payroll = conn.execute(
            "SELECT * FROM payroll WHERE employee_id=? ORDER BY year DESC, month DESC LIMIT 1",
            (employee_id,)
        ).fetchone()

        return render_template(
            "employee_dashboard.html",
            employee_id=employee_id,
            employee_name=employee_name,
            today_status="Present" if attendance else "Absent",
            history=history,
            payroll=payroll
        )
    finally:
        close_db(conn)


@app.route("/employee_messages")
def employee_messages():
    """Employee dedicated messages page"""
    if "employee" not in session:
        return redirect("/employee_login")
    return render_template("employee_messages.html")


@app.route("/update_work", methods=["POST"])
def update_work():
    if "employee" not in session:
        return redirect("/employee_login")

    employee_id = session["employee"]
    work_description = request.form.get("work_description", "").strip()

    if not work_description:
        return "❌ Work description is required", 400

    from datetime import date
    today = date.today().isoformat()

    conn = get_db()
    try:
        # Upsert: update if already exists for today, otherwise insert
        existing = conn.execute(
            "SELECT id FROM work_updates WHERE employee_id=? AND date=?",
            (employee_id, today)
        ).fetchone()

        if existing:
            conn.execute("""
                UPDATE work_updates SET work_description=? WHERE employee_id=? AND date=?
            """, (work_description, employee_id, today))
        else:
            conn.execute("""
                INSERT INTO work_updates (employee_id, date, work_description)
                VALUES (?, ?, ?)
            """, (employee_id, today, work_description))
        conn.commit()
        return redirect("/employee_dashboard")
    except Exception as e:
        return f"❌ Error updating work: {str(e)}", 500
    finally:
        close_db(conn)


@app.route("/employee_performance/<employee_id>")
def employee_performance(employee_id):
    if "admin" not in session:
        return redirect("/admin_login")

    conn = get_db()
    try:
        employee = conn.execute(
            "SELECT * FROM employees WHERE employee_id=?",
            (employee_id,)
        ).fetchone()

        if not employee:
            return "❌ Employee not found", 404

        # Get attendance records with work updates
        attendance_raw = conn.execute(
            "SELECT * FROM attendance WHERE employee_id=? ORDER BY date DESC",
            (employee_id,)
        ).fetchall()

        # Enrich attendance with work updates
        attendance = []
        for record in attendance_raw:
            work_entry = conn.execute(
                "SELECT work_description FROM work_updates WHERE employee_id=? AND date=?",
                (employee_id, record['date'])
            ).fetchone()
            
            record_dict = dict(record)
            record_dict['work_description'] = work_entry['work_description'] if work_entry else "-"
            attendance.append(record_dict)

        # Get work updates
        work_updates = conn.execute(
            "SELECT * FROM work_updates WHERE employee_id=? ORDER BY date DESC LIMIT 30",
            (employee_id,)
        ).fetchall()

        # Calculate metrics
        from datetime import datetime, date, timedelta
        today = date.today()
        
        joining_date = datetime.strptime(employee['joining_date'], '%Y-%m-%d').date()
        days_since_joining = (today - joining_date).days
        
        total_attendance = len(attendance)
        present_days = sum(1 for a in attendance if a['status'] == 'Present')
        absent_days = total_attendance - present_days
        attendance_percentage = int((present_days / total_attendance * 100)) if total_attendance > 0 else 0
        work_submissions = len(work_updates)
        last_attendance = attendance[0]['date'] if attendance else "N/A"

        metrics = {
            'days_since_joining': days_since_joining,
            'total_days': total_attendance,
            'present_days': present_days,
            'absent_days': absent_days,
            'attendance_percentage': attendance_percentage,
            'work_submissions': work_submissions,
            'last_attendance': last_attendance
        }

        return render_template(
            "employee_performance.html",
            employee=employee,
            metrics=metrics,
            attendance=attendance,
            work_updates=work_updates
        )
    finally:
        close_db(conn)


@app.route("/delete_employee/<employee_id>", methods=["POST"])
def delete_employee(employee_id):
    if "admin" not in session:
        return {"status": "Error", "message": "Unauthorized"}, 401

    conn = get_db()
    try:
        # Delete related records
        conn.execute("DELETE FROM attendance WHERE employee_id=?", (employee_id,))
        conn.execute("DELETE FROM work_updates WHERE employee_id=?", (employee_id,))
        
        # Delete employee's photo
        employee = conn.execute(
            "SELECT photo_path FROM employees WHERE employee_id=?",
            (employee_id,)
        ).fetchone()
        
        if employee and os.path.exists(employee['photo_path']):
            os.remove(employee['photo_path'])
        
        # Delete employee record
        conn.execute("DELETE FROM employees WHERE employee_id=?", (employee_id,))
        conn.commit()

        return {"status": "Success", "message": f"✅ Employee {employee_id} deleted successfully"}
    except Exception as e:
        return {"status": "Error", "message": f"❌ Error deleting employee: {str(e)}"}, 500
    finally:
        close_db(conn)


@app.route("/api/stats")
def api_stats():
    if "admin" not in session:
        return {"error": "Unauthorized"}, 401

    from datetime import datetime, date, timedelta
    
    conn = get_db()
    try:
        # Get last 7 days stats
        stats = {}
        labels = []
        values = []

        for i in range(6, -1, -1):
            day = date.today() - timedelta(days=i)
            day_str = day.isoformat()
            labels.append(day.strftime("%a %d"))

            count = conn.execute(
                "SELECT COUNT(*) as cnt FROM attendance WHERE date=? AND status='Present'",
                (day_str,)
            ).fetchone()
            values.append(count['cnt'] if count else 0)

        return {"labels": labels, "values": values}
    finally:
        close_db(conn)


@app.route("/api/today_work")
def api_today_work():
    if "admin" not in session:
        return {"error": "Unauthorized", "data": []}, 401

    from datetime import date
    
    conn = get_db()
    try:
        today = date.today().isoformat()
        
        # Get all attendance records for today with work descriptions
        records = conn.execute("""
            SELECT 
                a.employee_id,
                e.name as employee_name,
                a.time,
                w.work_description
            FROM attendance a
            LEFT JOIN employees e ON a.employee_id = e.employee_id
            LEFT JOIN work_updates w ON a.employee_id = w.employee_id AND a.date = w.date
            WHERE a.date = ? AND w.work_description IS NOT NULL AND w.work_description != ''
            ORDER BY a.time DESC
        """, (today,)).fetchall()
        
        # Convert to list of dicts
        work_list = [dict(record) for record in records]
        return {"success": True, "data": work_list, "count": len(work_list)}, 200
    except Exception as e:
        print(f"Error fetching today's work: {str(e)}")
        return {"success": False, "error": str(e), "data": []}, 500
    finally:
        close_db(conn)


@app.route("/download_employees")
def download_employees():
    if "admin" not in session:
        return redirect("/admin_login")

    conn = get_db()
    try:
        employees = conn.execute("SELECT * FROM employees").fetchall()
        
        # Create CSV content
        csv_content = "Employee ID,Name,Joining Date,Created At\n"
        for employee in employees:
            csv_content += f"{employee['employee_id']},{employee['name']},{employee['joining_date']},{employee['created_at']}\n"

        from flask import Response
        return Response(
            csv_content,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=employees_list.csv"}
        )
    finally:
        close_db(conn)


@app.route("/camera_status")
def camera_status():
    import cv2
    cap = cv2.VideoCapture(0)
    is_available = cap.isOpened()
    if cap.isOpened():
        cap.release()
    return {"camera_available": is_available, "camera_index": 0}


@app.route("/mark_attendance_manual", methods=["POST"])
def mark_attendance_manual():
    if "admin" not in session:
        return {"status": "Error", "message": "Admin authentication required"}, 401

    try:
        admin_id = session.get("admin")
        admin_password = request.json.get("admin_password", "").strip()
        employee_id = request.json.get("employee_id", "").strip()

        if not all([admin_password, employee_id]):
            return {"status": "Error", "message": "Missing required fields"}, 400

        conn = get_db()
        try:
            # Verify admin password
            admin = conn.execute(
                "SELECT * FROM admin WHERE admin_id=?",
                (admin_id,)
            ).fetchone()

            if not admin or not check_password_hash(admin["password_hash"], admin_password):
                return {"status": "Error", "message": "❌ Invalid admin password"}, 401

            # Check if employee exists
            employee = conn.execute(
                "SELECT * FROM employees WHERE employee_id=?",
                (employee_id,)
            ).fetchone()

            if not employee:
                return {"status": "Error", "message": "❌ Employee not found"}, 404

            from datetime import datetime, date
            today = date.today().isoformat()

            # Check if already marked today
            existing = conn.execute(
                "SELECT * FROM attendance WHERE employee_id=? AND date=?",
                (employee_id, today)
            ).fetchone()

            if existing:
                return {"status": "Error", "message": "❌ Attendance already marked for today"}, 400

            # Get location from request
            latitude = request.json.get("latitude")
            longitude = request.json.get("longitude")

            now = datetime.now()
            time = now.strftime("%H:%M:%S")

            # Mark attendance manually
            conn.execute("""
                INSERT INTO attendance (employee_id, date, time, status, is_manual, marked_by_admin, latitude, longitude)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (employee_id, today, time, "Present", 1, admin_id, latitude, longitude))
            conn.commit()

            # Send attendance notification SMS
            try:
                sms_result = send_attendance_sms(
                    employee_id,
                    employee['name'],
                    employee['contact_number'],
                    today,
                    time,
                    "Present"
                )
                print(f"[SMS] Attendance SMS result: {sms_result}")
            except Exception as sms_error:
                print(f"[WARN] Failed to send attendance SMS: {sms_error}")

            return {"status": "Success", "message": f"✅ Attendance marked for {employee['name']}"}
        finally:
            close_db(conn)

    except Exception as e:
        return {"status": "Error", "message": f"❌ Error: {str(e)}"}, 500


@app.route("/download_employee_performance/<employee_id>")
def download_employee_performance(employee_id):
    """Download employee performance data as CSV (admin only)"""
    if "admin" not in session:
        return redirect("/admin_login")

    conn = get_db()
    try:
        employee = conn.execute(
            "SELECT * FROM employees WHERE employee_id=?",
            (employee_id,)
        ).fetchone()

        if not employee:
            return "❌ Employee not found", 404

        # Get attendance records
        attendance = conn.execute(
            "SELECT * FROM attendance WHERE employee_id=? ORDER BY date DESC",
            (employee_id,)
        ).fetchall()

        # Get work updates
        work_updates = conn.execute(
            "SELECT * FROM work_updates WHERE employee_id=? ORDER BY date DESC",
            (employee_id,)
        ).fetchall()

        # Create CSV content
        from datetime import datetime, date
        csv_content = f"Employee Performance Report\n"
        csv_content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        csv_content += f"Employee ID: {employee['employee_id']}\n"
        csv_content += f"Name: {employee['name']}\n"
        csv_content += f"Joining Date: {employee['joining_date']}\n\n"
        
        # Calculate metrics
        total_attendance = len(attendance)
        present_days = sum(1 for a in attendance if a['status'] == 'Present')
        absent_days = total_attendance - present_days
        attendance_percentage = int((present_days / total_attendance * 100)) if total_attendance > 0 else 0
        
        csv_content += f"Performance Metrics\n"
        csv_content += f"Total Attendance Records,{total_attendance}\n"
        csv_content += f"Present Days,{present_days}\n"
        csv_content += f"Absent Days,{absent_days}\n"
        csv_content += f"Attendance Percentage,{attendance_percentage}%\n"
        csv_content += f"Work Submissions,{len(work_updates)}\n\n"
        
        csv_content += f"Attendance History\n"
        csv_content += f"Date,Time,Status,Location (Lat/Lon),Is Manual,Marked By\n"
        for record in attendance:
            location = f"{record['latitude']},{record['longitude']}" if record['latitude'] and record['longitude'] else "N/A"
            marked_by = record['marked_by_admin'] if record['is_manual'] else "Auto"
            csv_content += f"{record['date']},{record['time']},{record['status']},\"{location}\",{record['is_manual']},{marked_by}\n"
        
        csv_content += f"\nWork Updates\n"
        csv_content += f"Date,Work Description\n"
        for update in work_updates:
            # Escape quotes in work description
            work_desc = update['work_description'].replace('"', '""') if update['work_description'] else ""
            csv_content += f"{update['date']},\"{work_desc}\"\n"

        from flask import Response
        return Response(
            csv_content,
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment; filename=performance_{employee_id}_{datetime.now().strftime('%Y%m%d')}.csv"}
        )
    finally:
        close_db(conn)


@app.route("/download_my_performance")
def download_my_performance():
    """Download employee's own performance data as CSV (employee only)"""
    if "employee" not in session:
        return redirect("/employee_login")

    employee_id = session["employee"]
    conn = get_db()
    try:
        employee = conn.execute(
            "SELECT * FROM employees WHERE employee_id=?",
            (employee_id,)
        ).fetchone()

        if not employee:
            return "❌ Employee not found", 404

        # Get attendance history
        attendance = conn.execute(
            "SELECT * FROM attendance WHERE employee_id=? ORDER BY date DESC LIMIT 30",
            (employee_id,)
        ).fetchall()

        # Get work updates
        work_updates = conn.execute(
            "SELECT * FROM work_updates WHERE employee_id=? ORDER BY date DESC LIMIT 30",
            (employee_id,)
        ).fetchall()

        # Create CSV content
        from datetime import datetime
        csv_content = f"My Attendance & Work Report\n"
        csv_content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        csv_content += f"Employee ID: {employee['employee_id']}\n"
        csv_content += f"Name: {employee['name']}\n"
        csv_content += f"Joining Date: {employee['joining_date']}\n\n"
        
        # Calculate metrics
        total_attendance = len(attendance)
        present_days = sum(1 for a in attendance if a['status'] == 'Present')
        absent_days = total_attendance - present_days
        attendance_percentage = int((present_days / total_attendance * 100)) if total_attendance > 0 else 0
        
        csv_content += f"Summary\n"
        csv_content += f"Total Records (Last 30 Days),{total_attendance}\n"
        csv_content += f"Present Days,{present_days}\n"
        csv_content += f"Absent Days,{absent_days}\n"
        csv_content += f"Attendance Percentage,{attendance_percentage}%\n"
        csv_content += f"Work Submissions,{len(work_updates)}\n\n"
        
        csv_content += f"Attendance History (Last 30 Days)\n"
        csv_content += f"Date,Time,Status,Works Done By\n"
        for record in attendance:
            # Find matching work update
            work_entry = conn.execute(
                "SELECT work_description FROM work_updates WHERE employee_id=? AND date=?",
                (employee_id, record['date'])
            ).fetchone()
            work_desc = work_entry['work_description'].replace('"', '""') if work_entry and work_entry['work_description'] else "-"
            csv_content += f"{record['date']},{record['time']},{record['status']},\"{work_desc}\"\n"

        from flask import Response
        return Response(
            csv_content,
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment; filename=my_performance_{employee_id}_{datetime.now().strftime('%Y%m%d')}.csv"}
        )
    finally:
        close_db(conn)


@app.route("/payroll")
def payroll():
    """Admin payroll management page"""
    if "admin" not in session:
        return redirect("/admin_login")

    conn = get_db()
    try:
        employees = conn.execute("SELECT * FROM employees ORDER BY name").fetchall()
        payrolls = conn.execute("""
            SELECT * FROM payroll ORDER BY year DESC, month DESC
        """).fetchall()
        
        # Calculate summary statistics
        total_salary = sum(p['net_salary'] for p in payrolls) if payrolls else 0
        paid_count = sum(1 for p in payrolls if p['payment_status'] == 'Paid')
        pending_count = sum(1 for p in payrolls if p['payment_status'] == 'Pending')
        
        return render_template(
            "payroll.html",
            employees=employees,
            payrolls=payrolls,
            total_salary=total_salary,
            paid_count=paid_count,
            pending_count=pending_count
        )
    finally:
        close_db(conn)


@app.route("/add_payroll", methods=["POST"])
def add_payroll():
    """Add new payroll record"""
    if "admin" not in session:
        return {"status": "Error", "message": "Unauthorized"}, 401

    try:
        employee_id = request.form.get("employee_id", "").strip()
        month = request.form.get("month", "").strip()
        base_salary = float(request.form.get("base_salary", 0))
        attendance_bonus = float(request.form.get("attendance_bonus", 0))
        deductions = float(request.form.get("deductions", 0))
        payment_status = request.form.get("payment_status", "Pending").strip()
        payment_date = request.form.get("payment_date", "").strip()
        notes = request.form.get("notes", "").strip()

        if not employee_id or not month:
            return {"status": "Error", "message": "Employee ID and month are required"}, 400

        # Parse month (YYYY-MM format)
        year = int(month.split('-')[0])
        month_str = month.split('-')[1]

        net_salary = base_salary + attendance_bonus - deductions

        conn = get_db()
        try:
            conn.execute("""
                INSERT INTO payroll (employee_id, month, year, base_salary, attendance_bonus, 
                                    deductions, net_salary, payment_status, payment_date, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (employee_id, month_str, year, base_salary, attendance_bonus, deductions,
                  net_salary, payment_status, payment_date if payment_date else None, notes))
            conn.commit()

            # Get employee details for SMS
            employee = conn.execute(
                "SELECT * FROM employees WHERE employee_id=?",
                (employee_id,)
            ).fetchone()

            # Send payroll generation SMS notification
            if employee:
                try:
                    sms_result = send_payroll_sms(
                        employee_id,
                        employee['name'],
                        employee['contact_number'],
                        month,
                        net_salary
                    )
                    print(f"[SMS] Payroll SMS result: {sms_result}")
                except Exception as sms_error:
                    print(f"[WARN] Failed to send payroll SMS: {sms_error}")

            return {"status": "Success", "message": f"✅ Payroll record added for {employee_id}"}
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                return {"status": "Error", "message": "❌ Payroll record already exists for this employee and month"}, 400
            raise
        finally:
            close_db(conn)

    except ValueError as e:
        return {"status": "Error", "message": f"❌ Invalid input: {str(e)}"}, 400
    except Exception as e:
        return {"status": "Error", "message": f"❌ Error: {str(e)}"}, 500


@app.route("/edit_payroll/<int:payroll_id>", methods=["POST"])
def edit_payroll(payroll_id):
    """Edit existing payroll record"""
    if "admin" not in session:
        return {"status": "Error", "message": "Unauthorized"}, 401

    try:
        employee_id = request.form.get("employee_id", "").strip()
        month = request.form.get("month", "").strip()
        base_salary = float(request.form.get("base_salary", 0))
        attendance_bonus = float(request.form.get("attendance_bonus", 0))
        deductions = float(request.form.get("deductions", 0))
        payment_status = request.form.get("payment_status", "Pending").strip()
        payment_date = request.form.get("payment_date", "").strip()
        notes = request.form.get("notes", "").strip()

        net_salary = base_salary + attendance_bonus - deductions

        # Parse month (YYYY-MM format)
        year = int(month.split('-')[0])
        month_str = month.split('-')[1]

        conn = get_db()
        try:
            conn.execute("""
                UPDATE payroll SET employee_id=?, month=?, year=?, base_salary=?, 
                attendance_bonus=?, deductions=?, net_salary=?, payment_status=?, 
                payment_date=?, notes=?, updated_at=CURRENT_TIMESTAMP
                WHERE id=?
            """, (employee_id, month_str, year, base_salary, attendance_bonus, deductions,
                  net_salary, payment_status, payment_date if payment_date else None, notes, payroll_id))
            conn.commit()

            return {"status": "Success", "message": f"✅ Payroll record updated"}
        finally:
            close_db(conn)

    except ValueError as e:
        return {"status": "Error", "message": f"❌ Invalid input: {str(e)}"}, 400
    except Exception as e:
        return {"status": "Error", "message": f"❌ Error: {str(e)}"}, 500


@app.route("/delete_payroll/<int:payroll_id>", methods=["POST"])
def delete_payroll(payroll_id):
    """Delete payroll record"""
    if "admin" not in session:
        return {"status": "Error", "message": "Unauthorized"}, 401

    try:
        conn = get_db()
        try:
            conn.execute("DELETE FROM payroll WHERE id=?", (payroll_id,))
            conn.commit()
            return {"status": "Success", "message": "✅ Payroll record deleted"}
        finally:
            close_db(conn)

    except Exception as e:
        return {"status": "Error", "message": f"❌ Error: {str(e)}"}, 500


@app.route("/download_payroll")
def download_payroll():
    """Download payroll records as CSV"""
    if "admin" not in session:
        return redirect("/admin_login")

    try:
        conn = get_db()
        try:
            payrolls = conn.execute("""
                SELECT * FROM payroll ORDER BY year DESC, month DESC
            """).fetchall()

            employees = conn.execute("SELECT * FROM employees").fetchall()
            employee_map = {e['employee_id']: e['name'] for e in employees}

            from datetime import datetime
            csv_content = "Payroll Records\n"
            csv_content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            csv_content += "Employee ID,Name,Month,Year,Base Salary,Bonus,Deductions,Net Salary,Status,Payment Date,Notes\n"

            for payroll in payrolls:
                employee_name = employee_map.get(payroll['employee_id'], 'N/A')
                notes = payroll['notes'].replace('"', '""') if payroll['notes'] else ""
                payment_date = payroll['payment_date'] or ''
                csv_content += f"{payroll['employee_id']},{employee_name},{payroll['month']},{payroll['year']},{payroll['base_salary']},{payroll['attendance_bonus']},{payroll['deductions']},{payroll['net_salary']},{payroll['payment_status']},{payment_date},\"{notes}\"\n"

            from flask import Response
            return Response(
                csv_content,
                mimetype="text/csv",
                headers={"Content-Disposition": f"attachment; filename=payroll_{datetime.now().strftime('%Y%m%d')}.csv"}
            )
        finally:
            close_db(conn)

    except Exception as e:
        return f"❌ Error: {str(e)}", 500


# ==================== PROJECT MANAGEMENT ROUTES ====================

@app.route("/admin_projects")
def admin_projects():
    """Admin project management page"""
    if "admin" not in session:
        return redirect("/admin_login")

    conn = get_db()
    try:
        projects = conn.execute("""
            SELECT p.*, COUNT(DISTINCT pa.employee_id) as team_size
            FROM projects p
            LEFT JOIN project_assignments pa ON p.project_id = pa.project_id
            GROUP BY p.project_id
            ORDER BY p.created_at DESC
        """).fetchall()
        
        employees = conn.execute("SELECT * FROM employees ORDER BY name").fetchall()
        
        # Get statistics
        total_projects = len(projects) if projects else 0
        active_projects = sum(1 for p in projects if p['status'] == 'Active') if projects else 0
        
        return render_template(
            "admin_projects.html",
            projects=projects,
            employees=employees,
            total_projects=total_projects,
            active_projects=active_projects
        )
    finally:
        close_db(conn)


@app.route("/add_project", methods=["POST"])
def add_project():
    """Create a new project"""
    if "admin" not in session:
        return {"status": "Error", "message": "Unauthorized"}, 401

    try:
        project_id = request.form.get("project_id", "").strip().upper()
        project_name = request.form.get("project_name", "").strip()
        description = request.form.get("description", "").strip()
        start_date = request.form.get("start_date", "").strip()
        end_date = request.form.get("end_date", "").strip() or None
        budget = float(request.form.get("budget", 0))
        priority = request.form.get("priority", "Medium").strip()

        if not all([project_id, project_name, start_date]):
            return {"status": "Error", "message": "Project ID, name, and start date are required"}, 400

        admin_id = session.get("admin")
        
        conn = get_db()
        try:
            # Check if project already exists
            existing = conn.execute(
                "SELECT * FROM projects WHERE project_id=?",
                (project_id,)
            ).fetchone()

            if existing:
                return {"status": "Error", "message": f"❌ Project '{project_id}' already exists"}, 409

            conn.execute("""
                INSERT INTO projects (project_id, project_name, description, start_date, 
                                     end_date, budget, priority, created_by, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (project_id, project_name, description, start_date, end_date, budget, priority, admin_id, "Active"))
            conn.commit()

            return {"status": "Success", "message": f"✅ Project '{project_name}' created successfully"}
        finally:
            close_db(conn)

    except ValueError as e:
        return {"status": "Error", "message": f"❌ Invalid input: {str(e)}"}, 400
    except Exception as e:
        return {"status": "Error", "message": f"❌ Error: {str(e)}"}, 500


@app.route("/edit_project/<project_id>", methods=["POST"])
def edit_project(project_id):
    """Edit project details"""
    if "admin" not in session:
        return {"status": "Error", "message": "Unauthorized"}, 401

    try:
        project_name = request.form.get("project_name", "").strip()
        description = request.form.get("description", "").strip()
        status = request.form.get("status", "Active").strip()
        end_date = request.form.get("end_date", "").strip() or None
        budget = float(request.form.get("budget", 0))
        priority = request.form.get("priority", "Medium").strip()

        if not project_name:
            return {"status": "Error", "message": "Project name is required"}, 400

        conn = get_db()
        try:
            conn.execute("""
                UPDATE projects SET project_name=?, description=?, status=?, 
                                   end_date=?, budget=?, priority=?, updated_at=CURRENT_TIMESTAMP
                WHERE project_id=?
            """, (project_name, description, status, end_date, budget, priority, project_id))
            conn.commit()

            return {"status": "Success", "message": "✅ Project updated successfully"}
        finally:
            close_db(conn)

    except ValueError as e:
        return {"status": "Error", "message": f"❌ Invalid input: {str(e)}"}, 400
    except Exception as e:
        return {"status": "Error", "message": f"❌ Error: {str(e)}"}, 500


@app.route("/assign_employee_to_project", methods=["POST"])
def assign_employee_to_project():
    """Assign an employee to a project"""
    if "admin" not in session:
        return {"status": "Error", "message": "Unauthorized"}, 401

    try:
        project_id = request.form.get("project_id", "").strip()
        employee_id = request.form.get("employee_id", "").strip()
        role = request.form.get("role", "Team Member").strip()
        assignment_date = request.form.get("assignment_date", "").strip()

        if not all([project_id, employee_id, assignment_date]):
            return {"status": "Error", "message": "Project ID, employee ID, and assignment date are required"}, 400

        conn = get_db()
        try:
            # Check if assignment already exists
            existing = conn.execute(
                "SELECT * FROM project_assignments WHERE project_id=? AND employee_id=?",
                (project_id, employee_id)
            ).fetchone()

            if existing:
                return {"status": "Error", "message": "❌ Employee already assigned to this project"}, 409

            # Verify project and employee exist
            project = conn.execute(
                "SELECT * FROM projects WHERE project_id=?",
                (project_id,)
            ).fetchone()

            employee = conn.execute(
                "SELECT * FROM employees WHERE employee_id=?",
                (employee_id,)
            ).fetchone()

            if not project or not employee:
                return {"status": "Error", "message": "❌ Project or employee not found"}, 404

            conn.execute("""
                INSERT INTO project_assignments (project_id, employee_id, role, assignment_date, status)
                VALUES (?, ?, ?, ?, ?)
            """, (project_id, employee_id, role, assignment_date, "Active"))
            conn.commit()

            # Send project assignment SMS notification
            try:
                sms_result = send_project_assignment_sms(
                    employee_id,
                    employee['name'],
                    employee['contact_number'],
                    project['project_name'],
                    role
                )
                print(f"[SMS] Project assignment SMS result: {sms_result}")
            except Exception as sms_error:
                print(f"[WARN] Failed to send project assignment SMS: {sms_error}")

            return {"status": "Success", "message": f"✅ Employee '{employee_id}' assigned to project '{project_id}'"}
        finally:
            close_db(conn)

    except Exception as e:
        return {"status": "Error", "message": f"❌ Error: {str(e)}"}, 500


@app.route("/unassign_employee_from_project", methods=["POST"])
def unassign_employee_from_project():
    """Remove employee from a project"""
    if "admin" not in session:
        return {"status": "Error", "message": "Unauthorized"}, 401

    try:
        project_id = request.form.get("project_id", "").strip()
        employee_id = request.form.get("employee_id", "").strip()

        if not all([project_id, employee_id]):
            return {"status": "Error", "message": "Project ID and employee ID are required"}, 400

        conn = get_db()
        try:
            conn.execute(
                "DELETE FROM project_assignments WHERE project_id=? AND employee_id=?",
                (project_id, employee_id)
            )
            conn.commit()

            return {"status": "Success", "message": "✅ Employee removed from project"}
        finally:
            close_db(conn)

    except Exception as e:
        return {"status": "Error", "message": f"❌ Error: {str(e)}"}, 500


@app.route("/project_details/<project_id>")
def project_details(project_id):
    """View detailed project information"""
    if "admin" not in session:
        return redirect("/admin_login")

    conn = get_db()
    try:
        project = conn.execute(
            "SELECT * FROM projects WHERE project_id=?",
            (project_id,)
        ).fetchone()

        if not project:
            return "❌ Project not found", 404

        # Get assigned employees with their details
        assignments = conn.execute("""
            SELECT pa.*, e.name, e.employee_id
            FROM project_assignments pa
            JOIN employees e ON pa.employee_id = e.employee_id
            WHERE pa.project_id=?
            ORDER BY pa.assignment_date
        """, (project_id,)).fetchall()

        # Get project updates/progress
        updates = conn.execute("""
            SELECT pu.*, e.name
            FROM project_updates pu
            JOIN employees e ON pu.employee_id = e.employee_id
            WHERE pu.project_id=?
            ORDER BY pu.update_date DESC
        """, (project_id,)).fetchall()

        # Calculate project statistics
        total_hours = sum(u['hours_worked'] for u in updates) if updates else 0
        team_size = len(assignments) if assignments else 0
        total_updates = len(updates) if updates else 0
        
        # Get average progress
        avg_progress = int(sum(u['progress_percentage'] for u in updates) / len(updates)) if updates else 0

        return render_template(
            "project_details.html",
            project=project,
            assignments=assignments,
            updates=updates,
            team_size=team_size,
            total_hours=total_hours,
            total_updates=total_updates,
            avg_progress=avg_progress
        )
    finally:
        close_db(conn)


@app.route("/employee_projects")
def employee_projects():
    """Employee view of assigned projects"""
    if "employee" not in session:
        return redirect("/employee_login")

    employee_id = session["employee"]
    conn = get_db()
    try:
        # Get assigned projects
        projects = conn.execute("""
            SELECT p.*, pa.role, pa.assignment_date, pa.status as assignment_status
            FROM project_assignments pa
            JOIN projects p ON pa.project_id = p.project_id
            WHERE pa.employee_id=?
            ORDER BY pa.assignment_date DESC
        """, (employee_id,)).fetchall()

        # Get employee's work on projects
        employee_work = conn.execute("""
            SELECT * FROM project_updates
            WHERE employee_id=?
            ORDER BY update_date DESC
            LIMIT 20
        """, (employee_id,)).fetchall()

        return render_template(
            "employee_projects.html",
            projects=projects,
            employee_work=employee_work,
            employee_id=employee_id
        )
    finally:
        close_db(conn)


@app.route("/submit_project_update", methods=["POST"])
def submit_project_update():
    """Employee submits project update"""
    if "employee" not in session:
        return redirect("/employee_login")

    try:
        employee_id = session["employee"]
        project_id = request.form.get("project_id", "").strip()
        update_date = request.form.get("update_date", "").strip()
        progress_percentage = int(request.form.get("progress_percentage", 0))
        description = request.form.get("description", "").strip()
        hours_worked = float(request.form.get("hours_worked", 0))
        status = request.form.get("status", "In Progress").strip()

        if not all([project_id, update_date, description]):
            return {"status": "Error", "message": "Project, date, and description are required"}, 400

        if not (0 <= progress_percentage <= 100):
            return {"status": "Error", "message": "Progress must be between 0 and 100"}, 400

        conn = get_db()
        try:
            # Verify employee is assigned to project
            assignment = conn.execute(
                "SELECT * FROM project_assignments WHERE project_id=? AND employee_id=?",
                (project_id, employee_id)
            ).fetchone()

            if not assignment:
                return {"status": "Error", "message": "❌ You are not assigned to this project"}, 403

            conn.execute("""
                INSERT INTO project_updates (project_id, employee_id, update_date, 
                                            progress_percentage, description, hours_worked, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (project_id, employee_id, update_date, progress_percentage, description, hours_worked, status))
            conn.commit()

            return {"status": "Success", "message": "✅ Project update submitted successfully"}
        finally:
            close_db(conn)

    except ValueError as e:
        return {"status": "Error", "message": f"❌ Invalid input: {str(e)}"}, 400
    except Exception as e:
        return {"status": "Error", "message": f"❌ Error: {str(e)}"}, 500


@app.route("/project_reports")
def project_reports():
    """View project analytics and reports"""
    if "admin" not in session:
        return redirect("/admin_login")

    conn = get_db()
    try:
        # Get all projects with statistics
        projects_raw = conn.execute("""
            SELECT p.*, COUNT(DISTINCT pa.employee_id) as team_size
            FROM projects p
            LEFT JOIN project_assignments pa ON p.project_id = pa.project_id
            GROUP BY p.project_id
            ORDER BY p.created_at DESC
        """).fetchall()

        projects = []
        for p in projects_raw:
            # Get updates for this project
            updates = conn.execute(
                "SELECT * FROM project_updates WHERE project_id=?",
                (p['project_id'],)
            ).fetchall()

            total_hours = sum(u['hours_worked'] for u in updates) if updates else 0
            avg_progress = int(sum(u['progress_percentage'] for u in updates) / len(updates)) if updates else 0
            
            project_dict = dict(p)
            project_dict['total_hours'] = total_hours
            project_dict['avg_progress'] = avg_progress
            project_dict['total_updates'] = len(updates)
            projects.append(project_dict)

        # Get overall statistics
        total_projects = len(projects)
        total_team_members = sum(p['team_size'] for p in projects)
        total_hours = sum(p['total_hours'] for p in projects)
        avg_progress = int(sum(p['avg_progress'] for p in projects) / len(projects)) if projects else 0

        return render_template(
            "project_reports.html",
            projects=projects,
            total_projects=total_projects,
            total_team_members=total_team_members,
            total_hours=total_hours,
            avg_progress=avg_progress
        )
    finally:
        close_db(conn)


@app.route("/delete_project/<project_id>", methods=["POST"])
def delete_project(project_id):
    """Delete a project (admin only)"""
    if "admin" not in session:
        return {"status": "Error", "message": "Unauthorized"}, 401

    conn = get_db()
    try:
        # Delete related data
        conn.execute("DELETE FROM project_updates WHERE project_id=?", (project_id,))
        conn.execute("DELETE FROM project_assignments WHERE project_id=?", (project_id,))
        conn.execute("DELETE FROM projects WHERE project_id=?", (project_id,))
        conn.commit()

        return {"status": "Success", "message": f"✅ Project '{project_id}' deleted successfully"}
    except Exception as e:
        return {"status": "Error", "message": f"❌ Error: {str(e)}"}, 500
    finally:
        close_db(conn)


# ============================================
# NEW FEATURE 1: PERFORMANCE REVIEWS & APPRAISALS
# ============================================

@app.route("/performance_reviews")
def performance_reviews():
    """Admin view for all performance reviews"""
    if "admin" not in session:
        return redirect("/admin_login")

    conn = get_db()
    try:
        employees = conn.execute("SELECT * FROM employees ORDER BY name").fetchall()
        reviews = conn.execute("""
            SELECT pr.*, e.name as employee_name 
            FROM performance_reviews pr
            JOIN employees e ON pr.employee_id = e.employee_id
            ORDER BY pr.review_date DESC
        """).fetchall()

        return render_template(
            "performance_reviews.html",
            employees=employees,
            reviews=reviews
        )
    finally:
        close_db(conn)


@app.route("/add_performance_review", methods=["POST"])
def add_performance_review():
    """Add a new performance review"""
    if "admin" not in session:
        return {"status": "Error", "message": "Unauthorized"}, 401

    try:
        from datetime import date
        employee_id = request.form.get("employee_id", "").strip()
        rating = int(request.form.get("rating", 0))
        feedback = request.form.get("feedback", "").strip()
        goals = request.form.get("goals", "").strip()
        review_type = request.form.get("review_type", "Monthly").strip()

        if not employee_id or rating < 1 or rating > 5:
            return {"status": "Error", "message": "Invalid inputs"}, 400

        conn = get_db()
        try:
            conn.execute("""
                INSERT INTO performance_reviews 
                (employee_id, review_date, reviewer_id, rating, feedback, goals, review_type)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (employee_id, date.today().isoformat(), session["admin"], rating, feedback, goals, review_type))
            conn.commit()

            # Create notification for employee
            conn.execute("""
                INSERT INTO notifications (user_id, user_type, message, notification_type)
                VALUES (?, 'employee', 'Performance review completed', 'review')
            """, (employee_id,))
            conn.commit()

            return {"status": "Success", "message": "✅ Performance review added"}
        finally:
            close_db(conn)
    except Exception as e:
        return {"status": "Error", "message": f"Error: {str(e)}"}, 500


@app.route("/employee_reviews/<employee_id>")
def employee_reviews(employee_id):
    """View employee's performance reviews"""
    if "admin" not in session and session.get("employee") != employee_id:
        return redirect("/employee_login")

    conn = get_db()
    try:
        reviews = conn.execute("""
            SELECT * FROM performance_reviews 
            WHERE employee_id=? 
            ORDER BY review_date DESC
        """, (employee_id,)).fetchall()

        avg_rating = conn.execute("""
            SELECT AVG(rating) as avg FROM performance_reviews WHERE employee_id=?
        """, (employee_id,)).fetchone()

        return render_template(
            "employee_reviews.html",
            employee_id=employee_id,
            reviews=reviews,
            avg_rating=round(avg_rating['avg'], 1) if avg_rating['avg'] else 0
        )
    finally:
        close_db(conn)


# ============================================
# NEW FEATURE 2: LEAVE MANAGEMENT SYSTEM
# ============================================

@app.route("/employee_request_leave")
def employee_request_leave():
    """Employee form to request leave"""
    if "employee" not in session:
        return redirect("/employee_login")

    from datetime import date
    employee_id = session["employee"]
    current_year = date.today().year

    conn = get_db()
    try:
        # Get employee info
        employee = conn.execute(
            "SELECT * FROM employees WHERE employee_id=?", 
            (employee_id,)
        ).fetchone()
        
        # Get leave types
        leave_types = conn.execute("SELECT * FROM leave_types").fetchall()
        
        # Get current year leave balance
        leave_balances = conn.execute("""
            SELECT * FROM leave_balances 
            WHERE employee_id=? AND year=?
        """, (employee_id, current_year)).fetchall()

        return render_template(
            "employee_request_leave.html",
            employee_id=employee_id,
            employee=employee,
            leave_types=leave_types,
            leave_balances=leave_balances,
            current_year=current_year
        )
    finally:
        close_db(conn)


@app.route("/leave_management")
def leave_management():
    """Admin view for leave management"""
    if "admin" not in session:
        return redirect("/admin_login")

    conn = get_db()
    try:
        employees = conn.execute("SELECT * FROM employees ORDER BY name").fetchall()
        leave_types = conn.execute("SELECT * FROM leave_types").fetchall()
        leave_requests = conn.execute("""
            SELECT lr.*, e.name as employee_name
            FROM leave_requests lr
            JOIN employees e ON lr.employee_id = e.employee_id
            ORDER BY lr.start_date DESC
        """).fetchall()

        return render_template(
            "leave_management.html",
            employees=employees,
            leave_types=leave_types,
            leave_requests=leave_requests
        )
    finally:
        close_db(conn)


@app.route("/request_leave", methods=["POST"])
def request_leave():
    """Employee requests leave"""
    if "employee" not in session:
        return {"status": "Error", "message": "Not authenticated"}, 401

    try:
        from datetime import datetime, date
        
        employee_id = session["employee"]
        leave_type = request.form.get("leave_type", "").strip()
        start_date = request.form.get("start_date", "").strip()
        end_date = request.form.get("end_date", "").strip()
        reason = request.form.get("reason", "").strip()

        if not all([leave_type, start_date, end_date]):
            return {"status": "Error", "message": "❌ All fields required"}, 400

        # Validate date format and logic
        try:
            start = datetime.fromisoformat(start_date).date()
            end = datetime.fromisoformat(end_date).date()
            
            if end < start:
                return {"status": "Error", "message": "❌ End date cannot be before start date"}, 400
            
            if start < date.today():
                return {"status": "Error", "message": "❌ Cannot request leave for past dates"}, 400
                
        except ValueError:
            return {"status": "Error", "message": "❌ Invalid date format"}, 400

        conn = get_db()
        try:
            # Check if employee has enough leave balance
            days_requested = (end - start).days + 1
            balance = conn.execute("""
                SELECT remaining_days FROM leave_balances 
                WHERE employee_id=? AND leave_type=? AND year=?
            """, (employee_id, leave_type, start.year)).fetchone()
            
            if balance and balance['remaining_days'] < days_requested:
                return {"status": "Error", "message": f"❌ Only {balance['remaining_days']} days available"}, 400
            
            conn.execute("""
                INSERT INTO leave_requests 
                (employee_id, leave_type, start_date, end_date, reason, status)
                VALUES (?, ?, ?, ?, ?, 'Pending')
            """, (employee_id, leave_type, start_date, end_date, reason))
            conn.commit()

            # Notify all admins
            admins = conn.execute("SELECT admin_id FROM admin").fetchall()
            for admin in admins:
                try:
                    conn.execute("""
                        INSERT INTO notifications (user_id, user_type, message, notification_type)
                        VALUES (?, ?, ?, ?)
                    """, (admin['admin_id'], 'admin', f"New leave request from {employee_id}: {days_requested} days of {leave_type}", 'leave_request'))
                except:
                    pass  # Skip if notification already exists
            conn.commit()

            return {"status": "Success", "message": "✅ Leave request submitted"}, 200
        finally:
            close_db(conn)
    except Exception as e:
        print(f"Leave request error: {str(e)}")
        return {"status": "Error", "message": f"❌ Error: {str(e)}"}, 500


@app.route("/approve_leave/<int:request_id>", methods=["POST"])
def approve_leave(request_id):
    """Admin approves leave request"""
    if "admin" not in session:
        return {"status": "Error", "message": "Unauthorized"}, 401

    from datetime import date
    conn = get_db()
    try:
        leave_request = conn.execute(
            "SELECT * FROM leave_requests WHERE id=?", (request_id,)
        ).fetchone()

        if not leave_request:
            return {"status": "Error", "message": "Leave request not found"}, 404

        conn.execute("""
            UPDATE leave_requests 
            SET status='Approved', approved_by=?, approval_date=?
            WHERE id=?
        """, (session["admin"], date.today().isoformat(), request_id))
        conn.commit()

        # Update leave balance
        year = int(leave_request['start_date'].split('-')[0])
        days = (date.fromisoformat(leave_request['end_date']) - 
                date.fromisoformat(leave_request['start_date'])).days + 1

        conn.execute("""
            UPDATE leave_balances 
            SET used_days = used_days + ?, remaining_days = remaining_days - ?
            WHERE employee_id=? AND leave_type=? AND year=?
        """, (days, days, leave_request['employee_id'], leave_request['leave_type'], year))
        conn.commit()

        # Get employee details for SMS
        employee = conn.execute(
            "SELECT * FROM employees WHERE employee_id=?",
            (leave_request['employee_id'],)
        ).fetchone()

        # Send leave approval SMS notification
        if employee:
            try:
                sms_result = send_leave_approval_sms(
                    leave_request['employee_id'],
                    employee['name'],
                    employee['contact_number'],
                    leave_request['start_date'],
                    leave_request['end_date']
                )
                print(f"[SMS] Leave approval SMS result: {sms_result}")
            except Exception as sms_error:
                print(f"[WARN] Failed to send leave approval SMS: {sms_error}")

        return {"status": "Success", "message": "✅ Leave approved"}
    finally:
        close_db(conn)


@app.route("/reject_leave/<int:request_id>", methods=["POST"])
def reject_leave(request_id):
    """Admin rejects leave request"""
    if "admin" not in session:
        return {"status": "Error", "message": "Unauthorized"}, 401

    from datetime import date
    conn = get_db()
    try:
        leave_request = conn.execute(
            "SELECT * FROM leave_requests WHERE id=?", (request_id,)
        ).fetchone()

        if not leave_request:
            return {"status": "Error", "message": "Leave request not found"}, 404

        rejection_reason = request.json.get("reason", "") if request.is_json else ""

        conn.execute("""
            UPDATE leave_requests 
            SET status='Rejected', approved_by=?, approval_date=?
            WHERE id=?
        """, (session["admin"], date.today().isoformat(), request_id))
        conn.commit()

        # Get employee details for SMS
        employee = conn.execute(
            "SELECT * FROM employees WHERE employee_id=?",
            (leave_request['employee_id'],)
        ).fetchone()

        # Send leave rejection SMS notification
        if employee:
            try:
                sms_result = send_leave_rejection_sms(
                    leave_request['employee_id'],
                    employee['name'],
                    employee['contact_number'],
                    leave_request['start_date'],
                    leave_request['end_date'],
                    rejection_reason
                )
                print(f"[SMS] Leave rejection SMS result: {sms_result}")
            except Exception as sms_error:
                print(f"[WARN] Failed to send leave rejection SMS: {sms_error}")

        return {"status": "Success", "message": "✅ Leave rejected"}
    finally:
        close_db(conn)


@app.route("/employee_leave_history/<employee_id>")
def employee_leave_history(employee_id):
    """Employee views their leave history and balance"""
    if "admin" not in session and session.get("employee") != employee_id:
        return redirect("/employee_login")

    from datetime import date
    current_year = date.today().year

    conn = get_db()
    try:
        leave_requests = conn.execute("""
            SELECT * FROM leave_requests 
            WHERE employee_id=?
            ORDER BY start_date DESC
        """, (employee_id,)).fetchall()

        leave_balances = conn.execute("""
            SELECT * FROM leave_balances 
            WHERE employee_id=? AND year=?
        """, (employee_id, current_year)).fetchall()

        return render_template(
            "employee_leave_history.html",
            employee_id=employee_id,
            leave_requests=leave_requests,
            leave_balances=leave_balances
        )
    finally:
        close_db(conn)


# ============================================
# NEW FEATURE 3: REAL-TIME NOTIFICATIONS & ALERTS
# ============================================

@app.route("/notifications")
def view_notifications():
    """View user notifications"""
    if "employee" not in session and "admin" not in session:
        return redirect("/employee_login")

    user_id = session.get("employee") or session.get("admin")
    user_type = "employee" if "employee" in session else "admin"

    conn = get_db()
    try:
        notifications = conn.execute("""
            SELECT * FROM notifications 
            WHERE user_id=? AND user_type=?
            ORDER BY created_at DESC
        """, (user_id, user_type)).fetchall()

        unread_count = sum(1 for n in notifications if not n['read_status'])

        return render_template(
            "notifications.html",
            notifications=notifications,
            unread_count=unread_count
        )
    finally:
        close_db(conn)


@app.route("/api/notifications")
def api_get_notifications():
    """API endpoint to get unread notifications"""
    if "employee" not in session and "admin" not in session:
        return {"error": "Unauthorized"}, 401

    user_id = session.get("employee") or session.get("admin")
    user_type = "employee" if "employee" in session else "admin"

    conn = get_db()
    try:
        notifications = conn.execute("""
            SELECT * FROM notifications 
            WHERE user_id=? AND user_type=? AND read_status=0
            ORDER BY created_at DESC
            LIMIT 10
        """, (user_id, user_type)).fetchall()

        return {"notifications": [dict(n) for n in notifications]}
    finally:
        close_db(conn)


@app.route("/mark_notification_read/<int:notif_id>", methods=["POST"])
def mark_notification_read(notif_id):
    """Mark notification as read"""
    if "employee" not in session and "admin" not in session:
        return {"error": "Unauthorized"}, 401

    conn = get_db()
    try:
        conn.execute(
            "UPDATE notifications SET read_status=1 WHERE id=?",
            (notif_id,)
        )
        conn.commit()
        return {"status": "Success"}
    finally:
        close_db(conn)


# ============================================
# NEW FEATURE 4: EMAIL INTEGRATION
# ============================================

@app.route("/email_settings")
def email_settings():
    """Admin page to configure email settings"""
    if "admin" not in session:
        return redirect("/admin_login")

    conn = get_db()
    try:
        config = conn.execute("SELECT * FROM email_config LIMIT 1").fetchone()
        return render_template("email_settings.html", config=config)
    finally:
        close_db(conn)


@app.route("/save_email_config", methods=["POST"])
def save_email_config():
    """Save email configuration"""
    if "admin" not in session:
        return {"status": "Error", "message": "Unauthorized"}, 401

    try:
        smtp_server = request.form.get("smtp_server", "").strip()
        smtp_port = int(request.form.get("smtp_port", 587))
        sender_email = request.form.get("sender_email", "").strip()
        sender_password = request.form.get("sender_password", "").strip()
        enable_notifications = int(request.form.get("enable_notifications", 1))
        enable_reports = int(request.form.get("enable_reports", 1))
        enable_leave_emails = int(request.form.get("enable_leave_emails", 1))
        enable_payroll_emails = int(request.form.get("enable_payroll_emails", 1))

        if not all([smtp_server, sender_email, sender_password]):
            return {"status": "Error", "message": "Missing required fields"}, 400

        conn = get_db()
        try:
            existing = conn.execute("SELECT id FROM email_config LIMIT 1").fetchone()
            
            if existing:
                conn.execute("""
                    UPDATE email_config 
                    SET smtp_server=?, smtp_port=?, sender_email=?, sender_password=?,
                        enable_notifications=?, enable_reports=?, enable_leave_emails=?,
                        enable_payroll_emails=?, updated_at=CURRENT_TIMESTAMP
                """, (smtp_server, smtp_port, sender_email, sender_password,
                      enable_notifications, enable_reports, enable_leave_emails, enable_payroll_emails))
            else:
                conn.execute("""
                    INSERT INTO email_config 
                    (smtp_server, smtp_port, sender_email, sender_password,
                     enable_notifications, enable_reports, enable_leave_emails, enable_payroll_emails)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (smtp_server, smtp_port, sender_email, sender_password,
                      enable_notifications, enable_reports, enable_leave_emails, enable_payroll_emails))
            
            conn.commit()
            return {"status": "Success", "message": "✅ Email settings saved"}
        finally:
            close_db(conn)
    except Exception as e:
        return {"status": "Error", "message": f"Error: {str(e)}"}, 500


# ============================================
# NEW FEATURE 5: DARK MODE THEME
# ============================================

@app.route("/user_preferences")
def user_preferences():
    """User preferences page"""
    if "employee" not in session and "admin" not in session:
        return redirect("/employee_login")

    user_id = session.get("employee") or session.get("admin")
    user_type = "employee" if "employee" in session else "admin"

    conn = get_db()
    try:
        prefs = conn.execute(
            "SELECT * FROM user_preferences WHERE user_id=?",
            (user_id,)
        ).fetchone()

        return render_template(
            "user_preferences.html",
            preferences=prefs,
            user_type=user_type
        )
    finally:
        close_db(conn)


@app.route("/save_preferences", methods=["POST"])
def save_preferences():
    """Save user preferences including dark mode"""
    if "employee" not in session and "admin" not in session:
        return {"status": "Error", "message": "Unauthorized"}, 401

    try:
        user_id = session.get("employee") or session.get("admin")
        user_type = "employee" if "employee" in session else "admin"
        dark_mode = int(request.form.get("dark_mode", 0))
        language = request.form.get("language", "en").strip()
        timezone = request.form.get("timezone", "Asia/Kolkata").strip()
        email_digest = int(request.form.get("email_digest", 1))
        notification_frequency = request.form.get("notification_frequency", "instant").strip()

        conn = get_db()
        try:
            existing = conn.execute(
                "SELECT id FROM user_preferences WHERE user_id=?",
                (user_id,)
            ).fetchone()

            if existing:
                conn.execute("""
                    UPDATE user_preferences 
                    SET dark_mode=?, language=?, timezone=?, email_digest=?,
                        notification_frequency=?, updated_at=CURRENT_TIMESTAMP
                    WHERE user_id=?
                """, (dark_mode, language, timezone, email_digest, notification_frequency, user_id))
            else:
                conn.execute("""
                    INSERT INTO user_preferences 
                    (user_id, user_type, dark_mode, language, timezone, email_digest, notification_frequency)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (user_id, user_type, dark_mode, language, timezone, email_digest, notification_frequency))

            conn.commit()
            return {"status": "Success", "message": "✅ Preferences saved"}
        finally:
            close_db(conn)
    except Exception as e:
        return {"status": "Error", "message": f"Error: {str(e)}"}, 500


@app.route("/api/user_dark_mode")
def api_user_dark_mode():
    """API endpoint to get user's dark mode preference"""
    if "employee" not in session and "admin" not in session:
        return {"dark_mode": 0}

    user_id = session.get("employee") or session.get("admin")

    conn = get_db()
    try:
        prefs = conn.execute(
            "SELECT dark_mode FROM user_preferences WHERE user_id=?",
            (user_id,)
        ).fetchone()

        dark_mode = prefs['dark_mode'] if prefs else 0
        return {"dark_mode": dark_mode}
    finally:
        close_db(conn)


# ============================================
# NEW FEATURE 4: MESSAGING SYSTEM
# ============================================

@app.route("/api/get_groups", methods=["GET"])
def api_get_groups():
    """Get list of groups user is a member of"""
    if "employee" not in session and "admin" not in session:
        return {"error": "Not authenticated", "groups": []}, 401

    user_id = session.get("employee") or session.get("admin")
    user_type = "employee" if "employee" in session else "admin"

    conn = get_db()
    try:
        groups = conn.execute("""
            SELECT g.*, 
                   COUNT(DISTINCT gm.user_id) as member_count,
                   (SELECT message_text FROM messages WHERE group_id=g.group_id ORDER BY timestamp DESC LIMIT 1) as last_message,
                   (SELECT sender_name FROM messages WHERE group_id=g.group_id ORDER BY timestamp DESC LIMIT 1) as last_sender,
                   (SELECT timestamp FROM messages WHERE group_id=g.group_id ORDER BY timestamp DESC LIMIT 1) as last_message_time,
                   (SELECT COUNT(*) FROM messages WHERE group_id=g.group_id AND is_read=0) as unread_count
            FROM groups g
            LEFT JOIN group_members gm ON g.group_id = gm.group_id
            WHERE g.group_id IN (
                SELECT group_id FROM group_members WHERE user_id=? AND user_type=?
            )
            GROUP BY g.group_id
            ORDER BY last_message_time DESC
        """, (user_id, user_type)).fetchall()

        groups_list = [dict(g) for g in groups]
        return {"success": True, "groups": groups_list}, 200
    except Exception as e:
        print(f"Error fetching groups: {str(e)}")
        return {"error": str(e), "groups": []}, 500
    finally:
        close_db(conn)


@app.route("/api/send_message", methods=["POST"])
def api_send_message():
    """Send a message to a group"""
    if "employee" not in session and "admin" not in session:
        return {"status": "Error", "message": "Not authenticated"}, 401

    try:
        sender_id = session.get("employee") or session.get("admin")
        sender_type = "employee" if "employee" in session else "admin"
        group_id = request.json.get("group_id", "").strip()
        message_text = request.json.get("message_text", "").strip()

        if not group_id or not message_text:
            return {"status": "Error", "message": "❌ Group and message required"}, 400

        if len(message_text) > 5000:
            return {"status": "Error", "message": "❌ Message too long (max 5000 characters)"}, 400

        conn = get_db()
        try:
            # Check if user is member of this group
            member = conn.execute(
                "SELECT id FROM group_members WHERE group_id=? AND user_id=? AND user_type=?",
                (group_id, sender_id, sender_type)
            ).fetchone()

            if not member:
                return {"status": "Error", "message": "❌ You are not a member of this group"}, 403

            # Get sender name
            sender_name = sender_id
            if sender_type == "employee":
                emp = conn.execute("SELECT name FROM employees WHERE employee_id=?", (sender_id,)).fetchone()
                if emp:
                    sender_name = emp['name']
            else:
                adm = conn.execute("SELECT name FROM admin WHERE admin_id=?", (sender_id,)).fetchone()
                if adm and adm['name']:
                    sender_name = adm['name']

            conn.execute("""
                INSERT INTO messages 
                (group_id, sender_id, sender_type, sender_name, message_text)
                VALUES (?, ?, ?, ?, ?)
            """, (group_id, sender_id, sender_type, sender_name, message_text))
            conn.commit()

            return {"status": "Success", "message": "✅ Message sent"}, 200
        finally:
            close_db(conn)
    except Exception as e:
        print(f"Error sending message: {str(e)}")
        return {"status": "Error", "message": f"❌ Error: {str(e)}"}, 500


@app.route("/api/get_messages/<group_id>", methods=["GET"])
def api_get_messages(group_id):
    """Get messages from a group"""
    if "employee" not in session and "admin" not in session:
        return {"error": "Not authenticated", "messages": []}, 401

    user_id = session.get("employee") or session.get("admin")
    user_type = "employee" if "employee" in session else "admin"

    conn = get_db()
    try:
        # Check if user is member of this group
        member = conn.execute(
            "SELECT id FROM group_members WHERE group_id=? AND user_id=? AND user_type=?",
            (group_id, user_id, user_type)
        ).fetchone()

        if not member:
            return {"error": "You are not a member of this group", "messages": []}, 403

        # Get all messages from the group
        messages = conn.execute("""
            SELECT id, group_id, sender_id, sender_type, sender_name, message_text, timestamp, created_at
            FROM messages 
            WHERE group_id=?
            ORDER BY timestamp ASC
            LIMIT 500
        """, (group_id,)).fetchall()

        messages_list = [dict(msg) for msg in messages]
        
        # Mark all messages as read for current user
        conn.execute(
            "UPDATE messages SET is_read=1 WHERE group_id=? AND is_read=0",
            (group_id,)
        )
        conn.commit()

        # Get group info
        group = conn.execute("SELECT * FROM groups WHERE group_id=?", (group_id,)).fetchone()
        group_info = dict(group) if group else {}

        # Get group members
        members = conn.execute("""
            SELECT user_id, user_type FROM group_members WHERE group_id=? ORDER BY joined_at ASC
        """, (group_id,)).fetchall()

        members_list = []
        for member in members:
            member_dict = dict(member)
            if member_dict['user_type'] == 'employee':
                emp = conn.execute("SELECT name FROM employees WHERE employee_id=?", (member_dict['user_id'],)).fetchone()
                member_dict['name'] = emp['name'] if emp else member_dict['user_id']
            else:
                adm = conn.execute("SELECT name FROM admin WHERE admin_id=?", (member_dict['user_id'],)).fetchone()
                member_dict['name'] = adm['name'] if adm and adm['name'] else f"Admin ({member_dict['user_id']})"
            members_list.append(member_dict)

        return {
            "success": True, 
            "messages": messages_list,
            "group": group_info,
            "members": members_list,
            "current_user_id": user_id,
            "current_user_type": user_type
        }, 200
    except Exception as e:
        print(f"Error fetching messages: {str(e)}")
        return {"error": str(e), "messages": []}, 500
    finally:
        close_db(conn)


@app.route("/api/create_group", methods=["POST"])
def api_create_group():
    """Create a new group"""
    if "admin" not in session:
        return {"status": "Error", "message": "Only admins can create groups"}, 403

    try:
        admin_id = session.get("admin")
        group_name = request.json.get("group_name", "").strip()
        description = request.json.get("description", "").strip()

        if not group_name:
            return {"status": "Error", "message": "❌ Group name required"}, 400

        conn = get_db()
        try:
            # Generate unique group_id
            import uuid
            group_id = str(uuid.uuid4())

            # Create group
            conn.execute("""
                INSERT INTO groups (group_id, group_name, description, created_by)
                VALUES (?, ?, ?, ?)
            """, (group_id, group_name, description, admin_id))

            # Add creator as member
            conn.execute("""
                INSERT INTO group_members (group_id, user_id, user_type)
                VALUES (?, ?, ?)
            """, (group_id, admin_id, "admin"))

            # Add all employees to the group
            employees = conn.execute("SELECT employee_id FROM employees").fetchall()
            for emp in employees:
                try:
                    conn.execute("""
                        INSERT INTO group_members (group_id, user_id, user_type)
                        VALUES (?, ?, ?)
                    """, (group_id, emp['employee_id'], "employee"))
                except:
                    pass  # Skip if already exists

            # Add all other admins to the group
            admins = conn.execute("SELECT admin_id FROM admin WHERE admin_id!=?", (admin_id,)).fetchall()
            for adm in admins:
                try:
                    conn.execute("""
                        INSERT INTO group_members (group_id, user_id, user_type)
                        VALUES (?, ?, ?)
                    """, (group_id, adm['admin_id'], "admin"))
                except:
                    pass  # Skip if already exists

            conn.commit()
            return {"status": "Success", "message": f"✅ Group '{group_name}' created", "group_id": group_id}, 200
        finally:
            close_db(conn)
    except Exception as e:
        print(f"Error creating group: {str(e)}")
        return {"status": "Error", "message": f"❌ Error: {str(e)}"}, 500


@app.route("/api/message_count", methods=["GET"])
def api_message_count():
    """Get total unread message count across all groups"""
    if "employee" not in session and "admin" not in session:
        return {"unread": 0}

    user_id = session.get("employee") or session.get("admin")
    user_type = "employee" if "employee" in session else "admin"

    conn = get_db()
    try:
        # Count unread messages in groups user is member of
        count = conn.execute("""
            SELECT COUNT(*) as cnt FROM messages m
            WHERE m.group_id IN (
                SELECT group_id FROM group_members WHERE user_id=? AND user_type=?
            ) AND m.is_read=0
        """, (user_id, user_type)).fetchone()

        return {"unread": count['cnt'] if count else 0}
    finally:
        close_db(conn)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.errorhandler(404)
def page_not_found(error):
    return "❌ Page not found", 404


@app.errorhandler(500)
def server_error(error):
    return "❌ Server error occurred", 500


# ============================================
# AI CHATBOT ROUTES (Optional Feature)
# ============================================

@app.route("/chatbot")
def chatbot():
    """Chatbot page for employees and admins"""
    if "employee" not in session and "admin" not in session:
        if "employee" not in session:
            return redirect("/employee_login")
        return redirect("/admin_login")
    
    if not CHATBOT_AVAILABLE:
        return "Chatbot feature is not available. Please contact administrator.", 503
    
    return render_template("chatbot.html")


@app.route("/api/chatbot/send_message", methods=["POST"])
def api_chatbot_send_message():
    """Handle chatbot message and return AI response"""
    if "employee" not in session and "admin" not in session:
        return {"error": "Not authenticated"}, 401
    
    if not CHATBOT_AVAILABLE:
        return {"error": "Chatbot service is not available"}, 503
    
    try:
        user_message = request.json.get("message", "").strip()
        
        if not user_message or len(user_message) < 2:
            return {"error": "Message too short"}, 400
        
        user_id = session.get("employee") or session.get("admin")
        user_type = "employee" if "employee" in session else "admin"
        
        # Initialize AI Assistant
        ai_assistant = get_ai_assistant()
        if not ai_assistant:
            return {"error": "AI service not configured. Please set GOOGLE_API_KEY environment variable."}, 503
        
        # Get conversation history for context
        conversation_context = ai_assistant.get_conversation_history(user_id, user_type, limit=3)
        
        # Get AI response
        result = ai_assistant.get_response(user_message, user_type, conversation_context)
        
        if result['success']:
            # Save to database
            ai_assistant.save_conversation_message(
                user_id, user_type, user_message, result['response'], result['category']
            )
            
            return {
                "success": True,
                "response": result['response'],
                "category": result['category']
            }
        else:
            return {
                "success": False,
                "response": result['response']
            }, 500
    
    except Exception as e:
        return {"error": str(e)}, 500


@app.route("/api/chatbot/history", methods=["GET"])
def api_chatbot_history():
    """Get chatbot conversation history"""
    if "employee" not in session and "admin" not in session:
        return {"error": "Not authenticated"}, 401
    
    if not CHATBOT_AVAILABLE:
        return {"conversations": []}
    
    try:
        user_id = session.get("employee") or session.get("admin")
        user_type = "employee" if "employee" in session else "admin"
        limit = request.args.get("limit", 10, type=int)
        
        ai_assistant = get_ai_assistant()
        if not ai_assistant:
            return {"conversations": []}
        
        conversations = ai_assistant.get_user_conversations(user_id, user_type, limit)
        
        conv_list = []
        for conv in conversations:
            conv_list.append({
                "conversation_id": conv['conversation_id'],
                "topic": conv['topic'],
                "message_count": conv['message_count'],
                "created_at": conv['created_at'],
                "updated_at": conv['updated_at']
            })
        
        return {"conversations": conv_list}
    
    except Exception as e:
        return {"error": str(e)}, 500


@app.route("/api/chatbot/conversation/<conversation_id>", methods=["GET"])
def api_chatbot_conversation(conversation_id):
    """Get specific conversation messages"""
    if "employee" not in session and "admin" not in session:
        return {"error": "Not authenticated"}, 401
    
    if not CHATBOT_AVAILABLE:
        return {"error": "Chatbot feature is not available"}, 503
    
    try:
        user_id = session.get("employee") or session.get("admin")
        
        conn = get_db()
        try:
            # Verify user owns this conversation
            conversation = conn.execute(
                "SELECT * FROM chatbot_conversations WHERE conversation_id=? AND user_id=?",
                (conversation_id, user_id)
            ).fetchone()
            
            if not conversation:
                return {"error": "Conversation not found"}, 404
            
            # Get messages
            messages = conn.execute("""
                SELECT user_message, bot_response, message_category, created_at
                FROM chatbot_messages
                WHERE conversation_id=?
                ORDER BY created_at ASC
            """, (conversation_id,)).fetchall()
            
            msg_list = []
            for msg in messages:
                msg_list.append({
                    "user_message": msg['user_message'],
                    "bot_response": msg['bot_response'],
                    "category": msg['message_category'],
                    "timestamp": msg['created_at']
                })
            
            return {
                "conversation": {
                    "id": conversation['conversation_id'],
                    "topic": conversation['topic'],
                    "created_at": conversation['created_at']
                },
                "messages": msg_list
            }
        finally:
            close_db(conn)
    
    except Exception as e:
        return {"error": str(e)}, 500


# ============================================
# ANNOUNCEMENT PORTAL
# ============================================

@app.route("/announcements")
def announcements():
    """Announcements page for employees and admins"""
    if "employee" not in session and "admin" not in session:
        return redirect("/employee_login" if "employee" not in session else "/admin_login")
    
    user_id = session.get("employee") or session.get("admin")
    user_type = "employee" if "employee" in session else "admin"
    
    conn = get_db()
    try:
        # Get active announcements
        announcements_list = conn.execute("""
            SELECT * FROM announcements 
            WHERE status='active' 
            AND (expiry_date IS NULL OR expiry_date >= date('now'))
            ORDER BY created_at DESC
        """).fetchall()
        
        announcements_data = []
        for ann in announcements_list:
            ann_dict = dict(ann)
            # Check if employee has read this announcement
            if user_type == "employee":
                read = conn.execute(
                    "SELECT id FROM announcement_reads WHERE announcement_id=? AND employee_id=?",
                    (ann['announcement_id'], user_id)
                ).fetchone()
                ann_dict['is_read'] = 1 if read else 0
            announcements_data.append(ann_dict)
        
        return render_template("announcements.html", announcements=announcements_data, is_admin=user_type=="admin")
    finally:
        close_db(conn)


@app.route("/admin_announcements")
def admin_announcements():
    """Admin announcements management page"""
    if "admin" not in session:
        return redirect("/admin_login")
    
    conn = get_db()
    try:
        announcements_list = conn.execute("""
            SELECT * FROM announcements 
            ORDER BY created_at DESC
        """).fetchall()
        
        announcements_data = [dict(ann) for ann in announcements_list]
        return render_template("admin_announcements.html", announcements=announcements_data)
    finally:
        close_db(conn)


@app.route("/api/create_announcement", methods=["POST"])
def api_create_announcement():
    """Create a new announcement"""
    if "admin" not in session:
        return {"status": "Error", "message": "Only admins can create announcements"}, 403
    
    try:
        admin_id = session.get("admin")
        # Handle None values properly by converting to empty string before stripping
        title = (request.json.get("title") or "").strip()
        description = (request.json.get("description") or "").strip()
        content = (request.json.get("content") or "").strip()
        announcement_type = (request.json.get("announcement_type") or "general").strip()
        priority = (request.json.get("priority") or "normal").strip()
        expiry_date = (request.json.get("expiry_date") or "").strip()
        
        if not all([title, description]):
            return {"status": "Error", "message": "❌ Title and description are required"}, 400
        
        conn = get_db()
        try:
            announcement_id = str(uuid.uuid4())
            
            conn.execute("""
                INSERT INTO announcements 
                (announcement_id, title, description, content, announcement_type, priority, created_by, expiry_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (announcement_id, title, description, content, announcement_type, priority, admin_id, expiry_date if expiry_date else None))
            conn.commit()
            
            return {"status": "Success", "message": "✅ Announcement created successfully", "announcement_id": announcement_id}, 200
        finally:
            close_db(conn)
    except Exception as e:
        print(f"Error creating announcement: {str(e)}")
        return {"status": "Error", "message": f"❌ Error: {str(e)}"}, 500


@app.route("/api/mark_announcement_read", methods=["POST"])
def api_mark_announcement_read():
    """Mark announcement as read by employee"""
    if "employee" not in session:
        return {"status": "Error", "message": "Only employees can mark announcements as read"}, 403
    
    try:
        employee_id = session.get("employee")
        announcement_id = (request.json.get("announcement_id") or "").strip()
        
        if not announcement_id:
            return {"status": "Error", "message": "❌ Announcement ID required"}, 400
        
        conn = get_db()
        try:
            # Check if already marked as read
            existing = conn.execute(
                "SELECT id FROM announcement_reads WHERE announcement_id=? AND employee_id=?",
                (announcement_id, employee_id)
            ).fetchone()
            
            if not existing:
                conn.execute("""
                    INSERT INTO announcement_reads (announcement_id, employee_id)
                    VALUES (?, ?)
                """, (announcement_id, employee_id))
                conn.commit()
            
            return {"status": "Success", "message": "✅ Marked as read"}, 200
        finally:
            close_db(conn)
    except Exception as e:
        print(f"Error marking announcement as read: {str(e)}")
        return {"status": "Error", "message": f"❌ Error: {str(e)}"}, 500


@app.route("/api/delete_announcement/<announcement_id>", methods=["DELETE"])
def api_delete_announcement(announcement_id):
    """Delete announcement (soft delete by setting status)"""
    if "admin" not in session:
        return {"status": "Error", "message": "Only admins can delete announcements"}, 403
    
    try:
        conn = get_db()
        try:
            conn.execute(
                "UPDATE announcements SET status='inactive' WHERE announcement_id=?",
                (announcement_id,)
            )
            conn.commit()
            return {"status": "Success", "message": "✅ Announcement deleted"}, 200
        finally:
            close_db(conn)
    except Exception as e:
        print(f"Error deleting announcement: {str(e)}")
        return {"status": "Error", "message": f"❌ Error: {str(e)}"}, 500


@app.route("/api/get_announcements", methods=["GET"])
def api_get_announcements():
    """Get announcements via API"""
    if "employee" not in session and "admin" not in session:
        return {"error": "Not authenticated"}, 401
    
    user_id = session.get("employee") or session.get("admin")
    user_type = "employee" if "employee" in session else "admin"
    
    try:
        conn = get_db()
        try:
            announcements_list = conn.execute("""
                SELECT * FROM announcements 
                WHERE status='active' 
                AND (expiry_date IS NULL OR expiry_date >= date('now'))
                ORDER BY created_at DESC
            """).fetchall()
            
            announcements_data = []
            for ann in announcements_list:
                ann_dict = dict(ann)
                if user_type == "employee":
                    read = conn.execute(
                        "SELECT id FROM announcement_reads WHERE announcement_id=? AND employee_id=?",
                        (ann['announcement_id'], user_id)
                    ).fetchone()
                    ann_dict['is_read'] = 1 if read else 0
                announcements_data.append(ann_dict)
            
            return {"success": True, "announcements": announcements_data}, 200
        finally:
            close_db(conn)
    except Exception as e:
        return {"error": str(e)}, 500


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)