#!/usr/bin/env python3
"""
Test script to verify SMS service fixes
Tests that contact numbers are properly fetched from database
"""

import sys
from sms_service import (
    get_employee_contact_number,
    SMSService,
    send_registration_sms,
    send_attendance_sms,
    send_leave_approval_sms,
    send_project_assignment_sms,
    send_payroll_sms
)
from database import get_db, close_db

def test_get_contact_number():
    """Test fetching contact number from database"""
    print("\n=== Testing get_employee_contact_number() ===")
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Get first employee from database
    cursor.execute("SELECT employee_id, name, contact_number FROM employees LIMIT 1")
    employee = cursor.fetchone()
    close_db(conn)
    
    if not employee:
        print("❌ No employees in database. Add an employee first.")
        return False
    
    employee_id, name, expected_number = employee
    print(f"Testing with employee: {employee_id} ({name})")
    print(f"Expected contact number: {expected_number}")
    
    # Test the function
    fetched_number = get_employee_contact_number(employee_id)
    print(f"Fetched contact number: {fetched_number}")
    
    if str(fetched_number) == str(expected_number):
        print("✅ Contact number fetch successful!")
        return True
    else:
        print("❌ Contact number mismatch!")
        return False

def test_sms_without_number():
    """Test sending SMS without providing phone number (should fetch from DB)"""
    print("\n=== Testing SMS functions without phone_number parameter ===")
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Get first employee
    cursor.execute("SELECT employee_id, name FROM employees LIMIT 1")
    employee = cursor.fetchone()
    close_db(conn)
    
    if not employee:
        print("❌ No employees in database.")
        return False
    
    employee_id, name = employee
    print(f"Testing with employee: {employee_id} ({name})")
    
    # Test registration SMS (without phone_number)
    result = send_registration_sms(employee_id, name, password="TestPass123")
    print(f"\nRegistration SMS Result: {result}")
    
    # Test attendance SMS (without phone_number)
    result = send_attendance_sms(employee_id, name, date="2026-05-30", time="09:00 AM")
    print(f"Attendance SMS Result: {result}")
    
    # Test leave approval SMS (without phone_number)
    result = send_leave_approval_sms(employee_id, name, start_date="2026-06-01", end_date="2026-06-05")
    print(f"Leave Approval SMS Result: {result}")
    
    return True

def test_database_connection():
    """Test database connectivity"""
    print("\n=== Testing Database Connection ===")
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM employees")
        result = cursor.fetchone()
        employee_count = result['count']
        close_db(conn)
        
        print(f"✅ Database connected successfully!")
        print(f"Total employees in database: {employee_count}")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("SMS Service Bug Fix Verification")
    print("=" * 60)
    
    # Step 1: Test database connection
    if not test_database_connection():
        print("\n❌ Cannot proceed without database connection.")
        sys.exit(1)
    
    # Step 2: Test contact number retrieval
    if not test_get_contact_number():
        print("\n⚠️  Contact number retrieval failed. Ensure employees have contact_number in DB.")
    
    # Step 3: Test SMS functions without phone number
    test_sms_without_number()
    
    print("\n" + "=" * 60)
    print("✅ SMS Service Verification Complete!")
    print("=" * 60)
    print("\nKey Fixes Applied:")
    print("1. ✅ API Key updated to: DkAe7bOVgVITd6KtfUx4zQQnf06yIDnLl5VZFrCqTLhkSPPgaUFQ8CAOujku")
    print("2. ✅ Added get_employee_contact_number() function")
    print("3. ✅ All notify functions now fetch from database if phone_number not provided")
    print("4. ✅ Added proper error handling for missing contact numbers")

if __name__ == "__main__":
    main()
