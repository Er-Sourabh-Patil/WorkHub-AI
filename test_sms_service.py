#!/usr/bin/env python3
"""
SMS Service Quick Testing Script
Test individual SMS notification functions without running the full Flask app
"""

import sys
import os

# Add the project directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sms_service import (
    send_registration_sms,
    send_attendance_sms,
    send_leave_approval_sms,
    send_leave_rejection_sms,
    send_project_assignment_sms,
    send_payroll_sms,
    SMSService
)

def test_raw_sms():
    """Test sending raw SMS"""
    print("\n" + "="*60)
    print("TEST 1: Raw SMS Send")
    print("="*60)
    
    phone = input("Enter phone number (10 digits): ").strip()
    message = input("Enter message (max 160 chars): ").strip()
    
    result = SMSService.send_sms(phone, message)
    print(f"\nResult: {result}")
    return result.get("status") == "Success"


def test_registration_sms():
    """Test employee registration SMS"""
    print("\n" + "="*60)
    print("TEST 2: Employee Registration SMS")
    print("="*60)
    
    emp_id = input("Enter employee ID (e.g., EMP001): ").strip()
    name = input("Enter employee name: ").strip()
    phone = input("Enter phone number (10 digits): ").strip()
    password = input("Enter temporary password: ").strip()
    
    result = send_registration_sms(emp_id, name, phone, password)
    print(f"\nResult: {result}")
    return result.get("status") == "Success"


def test_attendance_sms():
    """Test attendance notification SMS"""
    print("\n" + "="*60)
    print("TEST 3: Attendance Marked SMS")
    print("="*60)
    
    emp_id = input("Enter employee ID: ").strip()
    name = input("Enter employee name: ").strip()
    phone = input("Enter phone number (10 digits): ").strip()
    date = input("Enter date (YYYY-MM-DD): ").strip()
    time = input("Enter time (HH:MM:SS): ").strip()
    
    result = send_attendance_sms(emp_id, name, phone, date, time, "Present")
    print(f"\nResult: {result}")
    return result.get("status") == "Success"


def test_leave_approval_sms():
    """Test leave approval SMS"""
    print("\n" + "="*60)
    print("TEST 4: Leave Approval SMS")
    print("="*60)
    
    emp_id = input("Enter employee ID: ").strip()
    name = input("Enter employee name: ").strip()
    phone = input("Enter phone number (10 digits): ").strip()
    start_date = input("Enter start date (YYYY-MM-DD): ").strip()
    end_date = input("Enter end date (YYYY-MM-DD): ").strip()
    
    result = send_leave_approval_sms(emp_id, name, phone, start_date, end_date)
    print(f"\nResult: {result}")
    return result.get("status") == "Success"


def test_leave_rejection_sms():
    """Test leave rejection SMS"""
    print("\n" + "="*60)
    print("TEST 5: Leave Rejection SMS")
    print("="*60)
    
    emp_id = input("Enter employee ID: ").strip()
    name = input("Enter employee name: ").strip()
    phone = input("Enter phone number (10 digits): ").strip()
    start_date = input("Enter start date (YYYY-MM-DD): ").strip()
    end_date = input("Enter end date (YYYY-MM-DD): ").strip()
    reason = input("Enter rejection reason (optional): ").strip()
    
    result = send_leave_rejection_sms(emp_id, name, phone, start_date, end_date, reason)
    print(f"\nResult: {result}")
    return result.get("status") == "Success"


def test_project_assignment_sms():
    """Test project assignment SMS"""
    print("\n" + "="*60)
    print("TEST 6: Project Assignment SMS")
    print("="*60)
    
    emp_id = input("Enter employee ID: ").strip()
    name = input("Enter employee name: ").strip()
    phone = input("Enter phone number (10 digits): ").strip()
    project = input("Enter project name: ").strip()
    role = input("Enter assigned role: ").strip()
    
    result = send_project_assignment_sms(emp_id, name, phone, project, role)
    print(f"\nResult: {result}")
    return result.get("status") == "Success"


def test_payroll_sms():
    """Test payroll generation SMS"""
    print("\n" + "="*60)
    print("TEST 7: Payroll Generated SMS")
    print("="*60)
    
    emp_id = input("Enter employee ID: ").strip()
    name = input("Enter employee name: ").strip()
    phone = input("Enter phone number (10 digits): ").strip()
    month = input("Enter month (YYYY-MM): ").strip()
    salary = float(input("Enter net salary amount: ").strip())
    
    result = send_payroll_sms(emp_id, name, phone, month, salary)
    print(f"\nResult: {result}")
    return result.get("status") == "Success"


def main():
    """Main menu"""
    print("\n" + "="*60)
    print("🔔 SMS SERVICE QUICK TEST MENU")
    print("="*60)
    print("\nSelect a test to run:")
    print("1. Raw SMS Send")
    print("2. Employee Registration SMS")
    print("3. Attendance Marked SMS")
    print("4. Leave Approval SMS")
    print("5. Leave Rejection SMS")
    print("6. Project Assignment SMS")
    print("7. Payroll Generated SMS")
    print("8. Run All Tests")
    print("0. Exit")
    
    choice = input("\nEnter your choice (0-8): ").strip()
    
    test_functions = {
        "1": test_raw_sms,
        "2": test_registration_sms,
        "3": test_attendance_sms,
        "4": test_leave_approval_sms,
        "5": test_leave_rejection_sms,
        "6": test_project_assignment_sms,
        "7": test_payroll_sms,
    }
    
    if choice == "0":
        print("\n✅ Exiting...")
        return
    
    elif choice == "8":
        print("\n⏳ Running all tests...")
        results = {}
        for test_name, test_func in test_functions.items():
            try:
                results[test_name] = test_func()
            except KeyboardInterrupt:
                print("\n\n⚠️ Test interrupted by user")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                results[test_name] = False
        
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        print(f"Passed: {passed}/{total}")
        
    elif choice in test_functions:
        try:
            test_functions[choice]()
        except KeyboardInterrupt:
            print("\n\n⚠️ Test interrupted by user")
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
    else:
        print("\n❌ Invalid choice!")
    
    # Ask if user wants to run another test
    again = input("\n\nRun another test? (y/n): ").strip().lower()
    if again == 'y':
        main()
    else:
        print("\n✅ Thank you for testing!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
