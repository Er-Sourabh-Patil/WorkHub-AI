# -*- coding: utf-8 -*-
"""
SMS Notification Service using Fast2SMS
Sends SMS notifications for employee events:
- Employee Registration
- Attendance Marked
- Leave Approval/Rejection
- Project Assignment
- Payroll Generated
"""

import requests
import logging
import os
from typing import Optional, Dict
from dotenv import load_dotenv
from database import get_db, close_db

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fast2SMS Configuration - Load from environment variable
FAST2SMS_API_KEY = os.getenv('FAST2SMS_API_KEY')
FAST2SMS_API_URL = "https://www.fast2sms.com/dev/bulkV2"

# Validate API Key at module load time
if not FAST2SMS_API_KEY:
    logger.warning(
        "[WARN] FAST2SMS_API_KEY not found in environment variables. "
        "SMS notifications will not work. Set FAST2SMS_API_KEY in .env file."
    )

def get_employee_contact_number(employee_id: str) -> Optional[str]:
    """
    Fetch contact number from employees table in database
    
    Args:
        employee_id: Employee ID to fetch contact number for
    
    Returns:
        Contact number (10 digits) or None if not found
    """
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT contact_number FROM employees WHERE employee_id = ?", (employee_id,))
        result = cursor.fetchone()
        close_db(conn)
        
        if result and result[0]:
            return str(result[0]).strip()
        return None
    except Exception as e:
        logger.error(f"Error fetching contact number for {employee_id}: {str(e)}")
        return None

class SMSService:
    """Service for sending SMS notifications via Fast2SMS"""
    
    @staticmethod
    def send_sms(phone_number: str, message: str) -> Dict:
        """
        Send SMS message using Fast2SMS API
        
        Args:
            phone_number: Indian phone number (10 digits without country code)
            message: SMS message text (max 160 chars for single SMS)
        
        Returns:
            Response dictionary with status and message
        """
        try:
            # Validate phone number
            phone_number = str(phone_number).strip()
            if not phone_number.isdigit() or len(phone_number) != 10:
                logger.warning(f"Invalid phone number format: {phone_number}")
                return {
                    "status": "Error",
                    "message": f"Invalid phone number format. Expected 10 digits, got {phone_number}"
                }
            
            # Prepare request payload
            headers = {
                "authorization": FAST2SMS_API_KEY,
                "Content-Type": "application/json"
            }
            
            payload = {
                "route": "v3",
                "numbers": phone_number,
                "message": message
            }
            
            # Make API request
            response = requests.post(
                FAST2SMS_API_URL,
                headers=headers,
                json=payload,
                timeout=10
            )
            
            response.raise_for_status()
            result = response.json()
            
            if result.get("return"):
                logger.info(f"SMS sent successfully to {phone_number}")
                return {
                    "status": "Success",
                    "message": f"✅ SMS sent to {phone_number}",
                    "details": result
                }
            else:
                logger.error(f"SMS sending failed: {result}")
                return {
                    "status": "Error",
                    "message": f"❌ SMS sending failed: {result.get('message', 'Unknown error')}",
                    "details": result
                }
        
        except requests.exceptions.Timeout:
            logger.error("SMS API request timed out")
            return {
                "status": "Error",
                "message": "❌ SMS API request timed out"
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"SMS API request failed: {str(e)}")
            return {
                "status": "Error",
                "message": f"❌ SMS API error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error sending SMS: {str(e)}")
            return {
                "status": "Error",
                "message": f"❌ Unexpected error: {str(e)}"
            }
    
    @staticmethod
    def notify_employee_registration(employee_id: str, name: str, phone_number: str = None, password: str = None) -> Dict:
        """
        Send registration confirmation SMS to new employee
        
        Args:
            employee_id: Employee ID
            name: Employee name
            phone_number: Employee phone number (if None, fetches from database)
            password: Temporary password
        
        Returns:
            Response dictionary
        """
        # Fetch phone number from database if not provided
        if not phone_number:
            phone_number = get_employee_contact_number(employee_id)
        
        if not phone_number:
            logger.error(f"No contact number available for employee {employee_id}")
            return {
                "status": "Error",
                "message": f"❌ No contact number found for employee {employee_id}"
            }
        
        message = f"Welcome {name}! Your Employee ID: {employee_id}. Password: {password}. Login at WorkHub AI. Reply STOP to unsubscribe."
        
        # Truncate if message is too long
        if len(message) > 160:
            message = f"Welcome {name}! ID: {employee_id}. Pass: {password}. Login to WorkHub AI. Reply STOP to unsubscribe."
        
        logger.info(f"Sending registration SMS to {employee_id}")
        return SMSService.send_sms(phone_number, message)
    
    @staticmethod
    def notify_attendance_marked(employee_id: str, name: str, phone_number: str = None, date: str = None, time: str = None, status: str = "Present") -> Dict:
        """
        Send attendance confirmation SMS
        
        Args:
            employee_id: Employee ID
            name: Employee name
            phone_number: Employee phone number (if None, fetches from database)
            date: Attendance date
            time: Time marked
            status: Attendance status (Present/Absent/Leave)
        
        Returns:
            Response dictionary
        """
        # Fetch phone number from database if not provided
        if not phone_number:
            phone_number = get_employee_contact_number(employee_id)
        
        if not phone_number:
            logger.error(f"No contact number available for employee {employee_id}")
            return {
                "status": "Error",
                "message": f"❌ No contact number found for employee {employee_id}"
            }
        
        message = f"Hi {name}, your attendance marked {status} on {date} at {time}. WorkHub AI"
        
        if len(message) > 160:
            message = f"{name}, attendance: {status} on {date} {time}. WorkHub AI"
        
        logger.info(f"Sending attendance SMS to {employee_id}")
        return SMSService.send_sms(phone_number, message)
    
    @staticmethod
    def notify_leave_approved(employee_id: str, name: str, phone_number: str = None, start_date: str = None, end_date: str = None) -> Dict:
        """
        Send leave approval notification SMS
        
        Args:
            employee_id: Employee ID
            name: Employee name
            phone_number: Employee phone number (if None, fetches from database)
            start_date: Leave start date
            end_date: Leave end date
        
        Returns:
            Response dictionary
        """
        # Fetch phone number from database if not provided
        if not phone_number:
            phone_number = get_employee_contact_number(employee_id)
        
        if not phone_number:
            logger.error(f"No contact number available for employee {employee_id}")
            return {
                "status": "Error",
                "message": f"❌ No contact number found for employee {employee_id}"
            }
        
        message = f"Hi {name}, your leave from {start_date} to {end_date} has been APPROVED. WorkHub AI"
        
        if len(message) > 160:
            message = f"{name}, leave {start_date} to {end_date} APPROVED. WorkHub AI"
        
        logger.info(f"Sending leave approval SMS to {employee_id}")
        return SMSService.send_sms(phone_number, message)
    
    @staticmethod
    def notify_leave_rejected(employee_id: str, name: str, phone_number: str = None, start_date: str = None, end_date: str = None, reason: str = "") -> Dict:
        """
        Send leave rejection notification SMS
        
        Args:
            employee_id: Employee ID
            name: Employee name
            phone_number: Employee phone number (if None, fetches from database)
            start_date: Leave start date
            end_date: Leave end date
            reason: Rejection reason
        
        Returns:
            Response dictionary
        """
        # Fetch phone number from database if not provided
        if not phone_number:
            phone_number = get_employee_contact_number(employee_id)
        
        if not phone_number:
            logger.error(f"No contact number available for employee {employee_id}")
            return {
                "status": "Error",
                "message": f"❌ No contact number found for employee {employee_id}"
            }
        
        message = f"Hi {name}, your leave from {start_date} to {end_date} has been REJECTED. WorkHub AI"
        
        if len(message) > 160:
            message = f"{name}, leave {start_date}-{end_date} REJECTED. WorkHub AI"
        
        logger.info(f"Sending leave rejection SMS to {employee_id}")
        return SMSService.send_sms(phone_number, message)
    
    @staticmethod
    def notify_project_assignment(employee_id: str, name: str, phone_number: str = None, project_name: str = None, role: str = None) -> Dict:
        """
        Send project assignment notification SMS
        
        Args:
            employee_id: Employee ID
            name: Employee name
            phone_number: Employee phone number (if None, fetches from database)
            project_name: Project name
            role: Role in project
        
        Returns:
            Response dictionary
        """
        # Fetch phone number from database if not provided
        if not phone_number:
            phone_number = get_employee_contact_number(employee_id)
        
        if not phone_number:
            logger.error(f"No contact number available for employee {employee_id}")
            return {
                "status": "Error",
                "message": f"❌ No contact number found for employee {employee_id}"
            }
        
        message = f"Hi {name}, you have been assigned to project '{project_name}' as {role}. WorkHub AI"
        
        if len(message) > 160:
            message = f"{name}, assigned to '{project_name}' as {role}. WorkHub AI"
        
        logger.info(f"Sending project assignment SMS to {employee_id}")
        return SMSService.send_sms(phone_number, message)
    
    @staticmethod
    def notify_payroll_generated(employee_id: str, name: str, phone_number: str = None, month: str = None, net_salary: float = 0) -> Dict:
        """
        Send payroll generation notification SMS
        
        Args:
            employee_id: Employee ID
            name: Employee name
            phone_number: Employee phone number (if None, fetches from database)
            month: Payroll month (YYYY-MM)
            net_salary: Net salary amount
        
        Returns:
            Response dictionary
        """
        # Fetch phone number from database if not provided
        if not phone_number:
            phone_number = get_employee_contact_number(employee_id)
        
        if not phone_number:
            logger.error(f"No contact number available for employee {employee_id}")
            return {
                "status": "Error",
                "message": f"❌ No contact number found for employee {employee_id}"
            }
        
        message = f"Hi {name}, your payroll for {month} has been generated. Net Salary: Rs.{net_salary}. WorkHub AI"
        
        if len(message) > 160:
            message = f"{name}, payroll {month} generated. Salary: Rs.{net_salary}. WorkHub AI"
        
        logger.info(f"Sending payroll SMS to {employee_id}")
        return SMSService.send_sms(phone_number, message)
    
    @staticmethod
    def notify_project_completion(employee_id: str, name: str, phone_number: str = None, project_name: str = None) -> Dict:
        """
        Send project completion notification SMS
        
        Args:
            employee_id: Employee ID
            name: Employee name
            phone_number: Employee phone number (if None, fetches from database)
            project_name: Project name
        
        Returns:
            Response dictionary
        """
        # Fetch phone number from database if not provided
        if not phone_number:
            phone_number = get_employee_contact_number(employee_id)
        
        if not phone_number:
            logger.error(f"No contact number available for employee {employee_id}")
            return {
                "status": "Error",
                "message": f"❌ No contact number found for employee {employee_id}"
            }
        
        message = f"Hi {name}, project '{project_name}' has been marked as completed. WorkHub AI"
        
        if len(message) > 160:
            message = f"{name}, project '{project_name}' completed. WorkHub AI"
        
        logger.info(f"Sending project completion SMS to {employee_id}")
        return SMSService.send_sms(phone_number, message)


# Convenience functions for direct usage
def send_registration_sms(employee_id: str, name: str, phone_number: str, password: str) -> Dict:
    """Send registration SMS"""
    return SMSService.notify_employee_registration(employee_id, name, phone_number, password)


def send_attendance_sms(employee_id: str, name: str, phone_number: str, date: str, time: str, status: str = "Present") -> Dict:
    """Send attendance SMS"""
    return SMSService.notify_attendance_marked(employee_id, name, phone_number, date, time, status)


def send_leave_approval_sms(employee_id: str, name: str, phone_number: str, start_date: str, end_date: str) -> Dict:
    """Send leave approval SMS"""
    return SMSService.notify_leave_approved(employee_id, name, phone_number, start_date, end_date)


def send_leave_rejection_sms(employee_id: str, name: str, phone_number: str, start_date: str, end_date: str, reason: str = "") -> Dict:
    """Send leave rejection SMS"""
    return SMSService.notify_leave_rejected(employee_id, name, phone_number, start_date, end_date, reason)


def send_project_assignment_sms(employee_id: str, name: str, phone_number: str, project_name: str, role: str) -> Dict:
    """Send project assignment SMS"""
    return SMSService.notify_project_assignment(employee_id, name, phone_number, project_name, role)


def send_payroll_sms(employee_id: str, name: str, phone_number: str, month: str, net_salary: float) -> Dict:
    """Send payroll SMS"""
    return SMSService.notify_payroll_generated(employee_id, name, phone_number, month, net_salary)


def send_project_completion_sms(employee_id: str, name: str, phone_number: str, project_name: str) -> Dict:
    """Send project completion SMS"""
    return SMSService.notify_project_completion(employee_id, name, phone_number, project_name)
