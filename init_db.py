from database import get_db, close_db


def column_exists(conn, table_name, column_name):
    """Check if a column exists in a table"""
    try:
        cursor = conn.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        for col in columns:
            if col[1] == column_name:
                return True
        return False
    except:
        return False


def table_exists(conn, table_name):
    """Check if a table exists"""
    try:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )
        return cursor.fetchone() is not None
    except:
        return False


def add_missing_columns(conn):
    """Add missing columns to existing tables"""
    try:
        # Add missing columns to admin table
        if not column_exists(conn, "admin", "name"):
            conn.execute("ALTER TABLE admin ADD COLUMN name TEXT DEFAULT 'Administrator'")
            print("[OK] Added name column to admin table")
        
        # Add missing columns to employees table
        if not column_exists(conn, "employees", "email"):
            conn.execute("ALTER TABLE employees ADD COLUMN email TEXT")
            print("[OK] Added email column to employees table")
        
        if not column_exists(conn, "employees", "contact_number"):
            conn.execute("ALTER TABLE employees ADD COLUMN contact_number TEXT")
            print("[OK] Added contact_number column to employees table")
        
        # Add missing columns to attendance table
        if not column_exists(conn, "attendance", "latitude"):
            conn.execute("ALTER TABLE attendance ADD COLUMN latitude REAL")
            print("[OK] Added latitude column to attendance table")
        
        if not column_exists(conn, "attendance", "longitude"):
            conn.execute("ALTER TABLE attendance ADD COLUMN longitude REAL")
            print("[OK] Added longitude column to attendance table")
        
        if not column_exists(conn, "attendance", "is_manual"):
            conn.execute("ALTER TABLE attendance ADD COLUMN is_manual INTEGER DEFAULT 0")
            print("[OK] Added is_manual column to attendance table")
        
        if not column_exists(conn, "attendance", "marked_by_admin"):
            conn.execute("ALTER TABLE attendance ADD COLUMN marked_by_admin TEXT")
            print("[OK] Added marked_by_admin column to attendance table")
        
        # Add missing columns to messages table
        if not column_exists(conn, "messages", "group_id"):
            conn.execute("ALTER TABLE messages ADD COLUMN group_id TEXT DEFAULT 'general'")
            print("[OK] Added group_id column to messages table")
        
        if not column_exists(conn, "messages", "is_read"):
            conn.execute("ALTER TABLE messages ADD COLUMN is_read INTEGER DEFAULT 0")
            print("[OK] Added is_read column to messages table")
        
        # Create default general group if not exists
        cursor = conn.execute("SELECT COUNT(*) as cnt FROM groups WHERE group_id='general'")
        if cursor.fetchone()['cnt'] == 0:
            conn.execute(
                "INSERT INTO groups (group_id, group_name, description, created_by) VALUES (?, ?, ?, ?)",
                ('general', 'General Discussion', 'General chat for all users', 'system')
            )
            print("[OK] Created default general group")
        
        conn.commit()
    except Exception as e:
        print(f"[WARN] Error adding columns: {e}")
        conn.rollback()


def add_default_leave_types(conn):
    """Add default leave types to the database"""
    try:
        # Check if leave types already exist
        count = conn.execute("SELECT COUNT(*) as cnt FROM leave_types").fetchone()['cnt']
        
        if count == 0:
            # Insert default leave types
            leave_types = [
                ('Sick Leave', 12),
                ('Casual Leave', 10),
                ('Earned Leave', 20),
                ('Unpaid Leave', 0),
                ('Maternity Leave', 90),
                ('Paternity Leave', 10),
                ('Marriage Leave', 5),
                ('Bereavement Leave', 3),
            ]
            
            for leave_type, days in leave_types:
                conn.execute(
                    "INSERT INTO leave_types (type_name, days_per_year) VALUES (?, ?)",
                    (leave_type, days)
                )
            
            conn.commit()
            print("[OK] Default leave types added successfully")
    except Exception as e:
        print(f"[WARN] Error adding leave types: {e}")
        conn.rollback()


def init_db():
    """Initialize database with required tables"""
    conn = get_db()

    try:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id TEXT UNIQUE NOT NULL,
            name TEXT DEFAULT 'Administrator',
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT,
            contact_number TEXT,
            joining_date TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            photo_path TEXT NOT NULL,
            face_encoding BLOB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            status TEXT DEFAULT 'Present',
            captured_image_path TEXT,
            latitude REAL,
            longitude REAL,
            is_manual INTEGER DEFAULT 0,
            marked_by_admin TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(employee_id, date),
            FOREIGN KEY(employee_id) REFERENCES employees(employee_id)
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS work_updates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            date TEXT NOT NULL,
            work_description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(employee_id) REFERENCES employees(employee_id)
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS payroll (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            month TEXT NOT NULL,
            year INTEGER NOT NULL,
            base_salary REAL DEFAULT 0.0,
            attendance_bonus REAL DEFAULT 0.0,
            deductions REAL DEFAULT 0.0,
            net_salary REAL DEFAULT 0.0,
            payment_status TEXT DEFAULT 'Pending',
            payment_date TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(employee_id, month, year),
            FOREIGN KEY(employee_id) REFERENCES employees(employee_id)
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT UNIQUE NOT NULL,
            project_name TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'Active',
            start_date TEXT NOT NULL,
            end_date TEXT,
            budget REAL DEFAULT 0.0,
            priority TEXT DEFAULT 'Medium',
            created_by TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(created_by) REFERENCES admin(admin_id)
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS project_assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT NOT NULL,
            employee_id TEXT NOT NULL,
            role TEXT DEFAULT 'Team Member',
            assignment_date TEXT NOT NULL,
            status TEXT DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(project_id, employee_id),
            FOREIGN KEY(project_id) REFERENCES projects(project_id),
            FOREIGN KEY(employee_id) REFERENCES employees(employee_id)
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS project_updates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT NOT NULL,
            employee_id TEXT NOT NULL,
            update_date TEXT NOT NULL,
            progress_percentage INTEGER DEFAULT 0,
            description TEXT,
            hours_worked REAL DEFAULT 0.0,
            status TEXT DEFAULT 'In Progress',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(project_id) REFERENCES projects(project_id),
            FOREIGN KEY(employee_id) REFERENCES employees(employee_id)
        )
        """)

        # NEW FEATURE: Performance Reviews & Appraisals
        conn.execute("""
        CREATE TABLE IF NOT EXISTS performance_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            review_date TEXT NOT NULL,
            reviewer_id TEXT NOT NULL,
            rating INTEGER CHECK(rating >= 1 AND rating <= 5),
            feedback TEXT,
            goals TEXT,
            review_type TEXT DEFAULT 'Monthly',
            status TEXT DEFAULT 'Completed',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(employee_id) REFERENCES employees(employee_id),
            FOREIGN KEY(reviewer_id) REFERENCES admin(admin_id)
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS kpi_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            kpi_name TEXT NOT NULL,
            target_value REAL NOT NULL,
            actual_value REAL DEFAULT 0.0,
            month TEXT NOT NULL,
            year INTEGER NOT NULL,
            status TEXT DEFAULT 'In Progress',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(employee_id) REFERENCES employees(employee_id)
        )
        """)

        # NEW FEATURE: Leave Management System
        conn.execute("""
        CREATE TABLE IF NOT EXISTS leave_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type_name TEXT UNIQUE NOT NULL,
            days_per_year INTEGER NOT NULL,
            accrual_rate REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS leave_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            leave_type TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            reason TEXT,
            status TEXT DEFAULT 'Pending',
            approved_by TEXT,
            approval_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(employee_id) REFERENCES employees(employee_id),
            FOREIGN KEY(approved_by) REFERENCES admin(admin_id)
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS leave_balances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            leave_type TEXT NOT NULL,
            total_days INTEGER NOT NULL,
            used_days INTEGER DEFAULT 0,
            remaining_days INTEGER NOT NULL,
            year INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(employee_id, leave_type, year),
            FOREIGN KEY(employee_id) REFERENCES employees(employee_id)
        )
        """)

        # NEW FEATURE: Real-time Notifications & Alerts
        conn.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            user_type TEXT DEFAULT 'employee',
            message TEXT NOT NULL,
            notification_type TEXT DEFAULT 'info',
            read_status INTEGER DEFAULT 0,
            related_table TEXT,
            related_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES employees(employee_id)
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS notification_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            notification_type TEXT NOT NULL,
            enabled INTEGER DEFAULT 1,
            method TEXT DEFAULT 'in_app',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES employees(employee_id)
        )
        """)

        # NEW FEATURE: Email Integration
        conn.execute("""
        CREATE TABLE IF NOT EXISTS email_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            smtp_server TEXT NOT NULL,
            smtp_port INTEGER NOT NULL,
            sender_email TEXT NOT NULL,
            sender_password TEXT NOT NULL,
            enable_notifications INTEGER DEFAULT 1,
            enable_reports INTEGER DEFAULT 1,
            enable_leave_emails INTEGER DEFAULT 1,
            enable_payroll_emails INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # NEW FEATURE: Dark Mode Theme & User Preferences
        conn.execute("""
        CREATE TABLE IF NOT EXISTS user_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL UNIQUE,
            user_type TEXT DEFAULT 'employee',
            dark_mode INTEGER DEFAULT 0,
            language TEXT DEFAULT 'en',
            timezone TEXT DEFAULT 'Asia/Kolkata',
            email_digest INTEGER DEFAULT 1,
            notification_frequency TEXT DEFAULT 'instant',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES employees(employee_id)
        )
        """)

        # NEW FEATURE: Group Messaging System
        conn.execute("""
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id TEXT UNIQUE NOT NULL,
            group_name TEXT NOT NULL,
            description TEXT,
            created_by TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS group_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            user_type TEXT NOT NULL,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(group_id, user_id, user_type),
            FOREIGN KEY(group_id) REFERENCES groups(group_id)
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id TEXT NOT NULL,
            sender_id TEXT NOT NULL,
            sender_type TEXT NOT NULL,
            sender_name TEXT NOT NULL,
            message_text TEXT NOT NULL,
            is_read INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(group_id) REFERENCES groups(group_id)
        )
        """)

        # NEW FEATURE: AI Chatbot System
        conn.execute("""
        CREATE TABLE IF NOT EXISTS chatbot_conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            user_type TEXT NOT NULL,
            conversation_id TEXT UNIQUE NOT NULL,
            topic TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES employees(employee_id)
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS chatbot_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            user_message TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            message_category TEXT DEFAULT 'general',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(conversation_id) REFERENCES chatbot_conversations(conversation_id)
        )
        """)

        # NEW FEATURE: Announcement Portal
        conn.execute("""
        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            announcement_id TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            content TEXT,
            announcement_type TEXT DEFAULT 'general',
            priority TEXT DEFAULT 'normal',
            created_by TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            published_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expiry_date TEXT,
            status TEXT DEFAULT 'active',
            FOREIGN KEY(created_by) REFERENCES admin(admin_id)
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS announcement_reads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            announcement_id TEXT NOT NULL,
            employee_id TEXT NOT NULL,
            read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(announcement_id, employee_id),
            FOREIGN KEY(announcement_id) REFERENCES announcements(announcement_id),
            FOREIGN KEY(employee_id) REFERENCES employees(employee_id)
        )
        """)

        conn.commit()
        
        # Add default leave types
        add_default_leave_types(conn)
        
        # Add any missing columns to existing tables
        add_missing_columns(conn)
        
        print("[OK] Database initialized successfully")
    except Exception as e:
        print(f"[ERROR] Database initialization error: {e}")
        conn.rollback()
    finally:
        close_db(conn)


if __name__ == "__main__":
    init_db()