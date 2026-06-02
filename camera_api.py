# -*- coding: utf-8 -*-
"""
Camera API Module
Real-time video streaming and face detection for attendance tracking
"""
from flask import Blueprint, Response, request
import cv2
import numpy as np
from datetime import datetime

from config import DETECTION_STABILITY_FRAMES, FRAME_SKIP_INTERVAL
from face_utils import recognize_face, detect_face, detect_all_faces
from database import get_db, close_db
from sms_service import send_attendance_sms

camera_bp = Blueprint("camera", __name__)

# RetinaFace detector is now handled in face_utils.py for consistency
# No need for separate cascade classifier here

# Global location storage
current_location = {'latitude': None, 'longitude': None}

# Load known faces
def load_known_faces():
    conn = get_db()
    try:
        # First check how many employees exist
        total_employees = conn.execute("SELECT COUNT(*) as cnt FROM employees").fetchone()
        total_count = total_employees['cnt'] if total_employees else 0
        print(f"\n[INFO] Total employees in database: {total_count}")
        
        if total_count == 0:
            print("[WARN] WARNING: No employees registered in database!")
            close_db(conn)
            return [], []
        
        data = conn.execute("SELECT employee_id, face_encoding FROM employees").fetchall()
        print(f"[INFO] Fetched {len(data)} employees from database")
        
        encodings = []
        ids = []
        
        for row in data:
            try:
                employee_id = row["employee_id"]
                face_encoding = row["face_encoding"]
                
                # Check if encoding exists
                if face_encoding is None:
                    print(f"[WARN] NULL encoding for {employee_id}, skipping")
                    continue
                
                if len(face_encoding) == 0:
                    print(f"[WARN] Empty encoding for {employee_id}, skipping")
                    continue
                
                enc = np.frombuffer(face_encoding, dtype=np.float32)
                print(f"   Encoding size for {employee_id}: {len(enc)} dimensions")
                
                # Validate encoding (Facenet512 = 512-dim, ArcFace = 128-dim)
                if len(enc) not in [128, 512]:
                    print(f"   [ERROR] Invalid size for {employee_id}: {len(enc)} (expected 128 or 512), skipping")
                    continue
                
                encodings.append(enc)
                ids.append(employee_id)
                print(f"   [OK] Loaded: {employee_id} ({len(enc)}-dim vector)")
            except Exception as e:
                print(f"   [ERROR] Error processing {row['employee_id']}: {e}")
                continue
        
        print(f"\n[OK] Successfully loaded {len(encodings)} valid encodings out of {total_count} employees\n")
        
        if len(encodings) == 0:
            print("[CRITICAL] CRITICAL: No valid encodings loaded! Check that:")
            print("   1. Employees are registered in database")
            print("   2. Photos were uploaded with clear faces")
            print("   3. Face encodings were generated successfully")
            print("   4. Encodings are stored as 128 or 512-dimensional vectors")
        
        return encodings, ids
    except Exception as e:
        print(f"[ERROR] Error loading known faces: {e}")
        return [], []
    finally:
        close_db(conn)


# Check if already marked today
def already_marked(conn, employee_id, date):
    res = conn.execute(
        "SELECT * FROM attendance WHERE employee_id=? AND date=?",
        (employee_id, date)
    ).fetchone()

    return res is not None


@camera_bp.route("/update_location", methods=["POST"])
def update_location():
    """Update current location for attendance marking"""
    global current_location
    try:
        data = request.get_json()
        current_location['latitude'] = data.get('latitude')
        current_location['longitude'] = data.get('longitude')
        return {"status": "Success", "message": "Location updated"}
    except Exception as e:
        return {"status": "Error", "message": str(e)}, 400


@camera_bp.route("/video_feed")
def video_feed():
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("[ERROR] Camera not accessible")
        return "Camera Error", 500

    known_encodings, ids = load_known_faces()

    # 🔥 Stability tracker
    detection_counter = {}
    already_marked_today = {}  # Track who's already marked today
    MARK_THRESHOLD = DETECTION_STABILITY_FRAMES  # frames

    def generate():
        try:
            frame_count = 0
            FRAME_SKIP = FRAME_SKIP_INTERVAL  # Process every nth frame for speed
            
            while True:
                success, frame = cap.read()
                if not success:
                    break

                frame_count += 1
                
                # Skip frames for performance
                should_process = (frame_count % FRAME_SKIP) == 0

                frame = cv2.resize(frame, (640, 480))

                # 🔥 Detect all faces using hybrid detection (Haar fast + RetinaFace fallback)
                detected_faces = []
                if should_process:
                    detected_faces = detect_all_faces(frame)
                    if len(detected_faces) > 0:
                        print(f"[INFO] Detected {len(detected_faces)} face(s) using {detected_faces[0].get('detector', 'Unknown')}")

                label = "No Face"
                color = (255, 255, 255)
                similarity_text = ""
                detected_people = set()  # Track who was detected in this frame
                unknown_faces = []  # Store unknown face data

                for face_data in detected_faces:
                    x = face_data['x']
                    y = face_data['y']
                    w = face_data['w']
                    h = face_data['h']
                    face_img = face_data['face_crop']

                    # Only process if face is large enough
                    if w < 20 or h < 20:
                        print(f"[WARN] Face too small ({w}x{h}), skipping")
                        continue

                    matched_id, similarity = recognize_face(face_img, known_encodings, ids)

                    if matched_id:
                        detected_people.add(matched_id)
                        label = matched_id
                        similarity_text = f"{similarity:.1f}%"
                        color = (0, 255, 0)  # Green for match

                        # Count frames for stable detection
                        detection_counter[matched_id] = detection_counter.get(matched_id, 0) + 1

                        # Mark attendance after stable detection (5+ consecutive frames)
                        # Use >= instead of == to handle cases where detection continues beyond threshold
                        if (detection_counter[matched_id] >= MARK_THRESHOLD and 
                            matched_id not in already_marked_today):
                            conn = get_db()
                            try:
                                now = datetime.now()
                                date = now.strftime("%Y-%m-%d")
                                time_str = now.strftime("%H:%M:%S")

                                # Final check in DB to prevent double marking
                                if not already_marked(conn, matched_id, date):
                                    # Get current location
                                    latitude = current_location.get('latitude')
                                    longitude = current_location.get('longitude')

                                    conn.execute("""
                                        INSERT INTO attendance (employee_id, date, time, status, latitude, longitude, is_manual)
                                        VALUES (?, ?, ?, ?, ?, ?, ?)
                                    """, (matched_id, date, time_str, "Present", latitude, longitude, 0))
                                    conn.commit()

                                    # Get employee details for SMS
                                    employee = conn.execute(
                                        "SELECT * FROM employees WHERE employee_id=?",
                                        (matched_id,)
                                    ).fetchone()

                                    # Send attendance SMS notification
                                    if employee:
                                        try:
                                            sms_result = send_attendance_sms(
                                                matched_id,
                                                employee['name'],
                                                employee['contact_number'],
                                                date,
                                                time_str,
                                                "Present"
                                            )
                                            print(f"[SMS] Attendance SMS result: {sms_result}")
                                        except Exception as sms_error:
                                            print(f"[WARN] Failed to send attendance SMS: {sms_error}")

                                    already_marked_today[matched_id] = True  # Mark in session
                                    detection_counter[matched_id] = 0  # Reset counter
                                    print(f"[OK] Attendance marked for {matched_id} ({similarity:.1f}% confidence)")
                            except Exception as e:
                                print(f"[ERROR] Error marking attendance: {e}")
                            finally:
                                close_db(conn)

                    else:
                        label = "Unknown"
                        color = (0, 0, 255)  # Red for unknown
                        similarity_text = ""
                        # Store unknown face data with position
                        unknown_faces.append({
                            'x': x, 'y': y, 'w': w, 'h': h,
                            'label': label
                        })

                    # 🔥 Draw face box with label and similarity
                    cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                    cv2.putText(frame, label, (x, y-30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
                    
                    # Draw similarity percentage
                    if similarity_text:
                        cv2.putText(frame, similarity_text, (x, y-10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

                # Reset counter ONLY on processed frames when person is not detected
                # (Don't reset on skipped frames - that breaks the accumulation!)
                if should_process:
                    for person in list(detection_counter.keys()):
                        if person not in detected_people:
                            detection_counter[person] = 0

                # Add timestamp
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cv2.putText(frame, now, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Add status text
                status = f"Frame: {frame_count} | FPS: ~25 | Skip: {FRAME_SKIP}x | Models: Enhanced"
                cv2.putText(frame, status, (10, 470), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)

                # Encode frame
                _, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()

                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        finally:
            cap.release()

    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@camera_bp.route("/live_attendance")
def live_attendance():
    """Live attendance page with camera stream"""
    from flask import render_template
    conn = get_db()
    try:
        employees = conn.execute("SELECT employee_id, name FROM employees").fetchall()
        return render_template("live_attendance.html", employees=employees)
    except Exception as e:
        print(f"Error: {e}")
        return "Error loading page", 500
    finally:
        close_db(conn)


@camera_bp.route("/api/marked_today")
def get_marked_today():
    """Get list of employees marked today"""
    from datetime import date
    
    conn = get_db()
    try:
        today = date.today().isoformat()
        marked = conn.execute(
            "SELECT DISTINCT employee_id, time FROM attendance WHERE date=? AND status='Present' ORDER BY time DESC",
            (today,)
        ).fetchall()
        
        result = [{"employee_id": m['employee_id'], "time": m['time']} for m in marked]
        return {"status": "Success", "data": result}
    finally:
        close_db(conn)


@camera_bp.route("/api/camera_stats")
def camera_stats():
    """Get real-time camera statistics"""
    from datetime import date
    
    conn = get_db()
    try:
        today = date.today().isoformat()
        
        total_employees = conn.execute("SELECT COUNT(*) as cnt FROM employees").fetchone()['cnt']
        marked_today = conn.execute(
            "SELECT COUNT(DISTINCT employee_id) as cnt FROM attendance WHERE date=? AND status='Present'",
            (today,)
        ).fetchone()['cnt']
        
        return {
            "status": "Success",
            "total_employees": total_employees,
            "marked_today": marked_today,
            "pending": total_employees - marked_today
        }
    finally:
        close_db(conn)


@camera_bp.route("/api/debug_encodings")
def debug_encodings():
    """Debug endpoint to check encoding status in database"""
    conn = get_db()
    try:
        employees = conn.execute("SELECT employee_id, name, face_encoding FROM employees").fetchall()
        
        debug_info = {
            "total_employees": len(employees),
            "employees": []
        }
        
        for employee in employees:
            encoding = employee["face_encoding"]
            
            if encoding is None:
                encoding_status = "NULL (not set)"
            elif len(encoding) == 0:
                encoding_status = "Empty (0 bytes)"
            else:
                enc_array = np.frombuffer(encoding, dtype=np.float32)
                encoding_status = f"Valid ({len(enc_array)} dimensions)"
                if len(enc_array) not in [128, 512]:
                    encoding_status += " ⚠️ INVALID SIZE"
            
            debug_info["employees"].append({
                "employee_id": employee["employee_id"],
                "name": employee["name"],
                "encoding_status": encoding_status
            })
        
        return {
            "status": "Success",
            "debug": debug_info,
            "message": "Check encoding_status for each employee. Should be '128 dimensions' for valid encodings."
        }
    except Exception as e:
        return {
            "status": "Error",
            "message": str(e)
        }
    finally:
        close_db(conn)
