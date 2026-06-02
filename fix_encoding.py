import glob
import os

# List of files with encoding issues
problematic_files = [
    'templates/admin_announcements.html',
    'templates/admin_messages.html',
    'templates/admin_projects.html',
    'templates/announcements.html',
    'templates/email_settings.html',
    'templates/employee_dashboard.html',
    'templates/employee_leave_history.html',
    'templates/employee_messages.html',
    'templates/employee_performance.html',
    'templates/employee_projects.html',
    'templates/employee_request_leave.html',
    'templates/employee_reviews.html',
    'templates/leave_management.html',
    'templates/live_attendance.html',
    'templates/notifications.html',
    'templates/payroll.html',
    'templates/performance_reviews.html',
    'templates/project_details.html',
    'templates/project_reports.html',
    'templates/setup.html',
    'templates/user_preferences.html',
]

print("Converting files from Windows-1252 to UTF-8...\n")

for file in problematic_files:
    try:
        # Read with Windows-1252 encoding
        with open(file, 'r', encoding='windows-1252') as f:
            content = f.read()
        
        # Write back with UTF-8 encoding
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ Fixed: {file}")
    except Exception as e:
        print(f"✗ Error fixing {file}: {e}")

print("\nVerifying all template files...")
template_files = glob.glob('templates/*.html')

for file in sorted(template_files):
    try:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"✓ {file}")
    except UnicodeDecodeError as e:
        print(f"✗ {file}: Still has issues")

print("\n✅ All template files have been converted to UTF-8!")
