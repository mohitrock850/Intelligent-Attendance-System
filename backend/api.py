from flask import Flask, render_template, Response, jsonify, request, url_for
from flask_cors import CORS
import cv2
import time
from datetime import datetime, timezone
from backend.recognition import find_and_mark
from backend.database import get_db_connection
from bson.objectid import ObjectId

app = Flask(__name__, template_folder='../frontend/templates')
CORS(app)

active_sessions = {}

def generate_frames(schedule_id):
    """Generates video frames, checking session status from the DB."""
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("Error: Could not open camera.")
        return

    db = get_db_connection()
    if db is None: return

    last_recognition_time = 0
    RECOGNITION_INTERVAL = 1.0

    while True:
        success, frame = camera.read()
        if not success: break
        
        # --- MODIFIED ---
        # Fetch the LATEST schedule info in every loop to check status
        schedule_info = db.schedules.find_one({"_id": ObjectId(schedule_id)})
        if not schedule_info: break # Stop if schedule is deleted or invalid

        start_time = schedule_info["start_time"].replace(tzinfo=timezone.utc)
        end_time = schedule_info["end_time"].replace(tzinfo=timezone.utc)
        status = schedule_info.get("status", "active")
        
        now_utc = datetime.now(timezone.utc)
        
        # Check time AND status
        if start_time <= now_utc <= end_time and status == "active":
            if (time.time() - last_recognition_time) > RECOGNITION_INTERVAL:
                frame = find_and_mark(frame, schedule_id)
                last_recognition_time = time.time()
            cv2.putText(frame, "ATTENDANCE ACTIVE", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            final_status = status.upper() if status != "active" else ("ENDED" if now_utc > end_time else "NOT STARTED")
            cv2.putText(frame, f"ATTENDANCE {final_status}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    
    print("Releasing camera.")
    camera.release()

# --- (The /dashboard route and others are the same, adding the new one below) ---

@app.route('/')
def setup_page():
    return render_template('setup.html')

@app.route('/dashboard')
def dashboard_page():
    schedule_id = request.args.get('schedule_id')
    location = request.args.get('location', 'Online')
    if schedule_id not in active_sessions:
        return "Error: Session not properly started. Please go back to the setup page.", 400
    session_info = active_sessions.get(schedule_id)
    return render_template('dashboard.html', session_info=session_info, location=location)

@app.route('/video_feed/<schedule_id>')
def video_feed(schedule_id):
    return Response(generate_frames(schedule_id), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_scheduled_classes')
def get_scheduled_classes():
    db = get_db_connection()
    if db is None: return jsonify([]), 500
    now_utc = datetime.now(timezone.utc)
    # Only show classes that are active and haven't ended
    query = {"end_time": {"$gte": now_utc}, "status": "active"}
    schedules = list(db.schedules.find(query).sort("start_time", 1))
    for s in schedules:
        s["_id"] = str(s["_id"])
        s["class_id"] = str(s["class_id"])
        s["start_time"] = s["start_time"].isoformat()
        s["end_time"] = s["end_time"].isoformat()
    return jsonify(schedules)

@app.route('/start_session', methods=['POST'])
def start_session():
    data = request.get_json()
    schedule_id = data.get('schedule_id')
    location = data.get('location')
    db = get_db_connection()
    schedule_info = db.schedules.find_one({"_id": ObjectId(schedule_id)})
    if not schedule_info: return jsonify({"error": "Schedule not found"}), 404
    active_sessions[schedule_id] = {
        "schedule_id": str(schedule_info["_id"]),
        "subject": schedule_info["subject"],
        "teacher": schedule_info["teacher_name"],
        "start_time": schedule_info["start_time"].replace(tzinfo=timezone.utc),
        "end_time": schedule_info["end_time"].replace(tzinfo=timezone.utc)
    }
    dashboard_url = url_for('dashboard_page', schedule_id=schedule_id, location=location)
    return jsonify({"redirect_url": dashboard_url})

# --- NEW ENDPOINT ---
@app.route('/end_session', methods=['POST'])
def end_session():
    """API endpoint to manually end an attendance session."""
    data = request.get_json()
    schedule_id = data.get('schedule_id')
    if not schedule_id:
        return jsonify({"error": "Schedule ID is required"}), 400

    db = get_db_connection()
    if db is None:
        return jsonify({"error": "Database connection failed"}), 500

    # Update the status of the schedule in the database
    result = db.schedules.update_one(
        {"_id": ObjectId(schedule_id)},
        {"$set": {"status": "ended"}}
    )

    if result.modified_count > 0:
        # Also remove from in-memory active sessions if it exists
        if schedule_id in active_sessions:
            del active_sessions[schedule_id]
        return jsonify({"message": "Session ended successfully"}), 200
    else:
        return jsonify({"error": "Session not found or already ended"}), 404

@app.route('/get_attendance/<schedule_id>')
def get_attendance(schedule_id):
    db = get_db_connection()
    if db is None: return jsonify([]), 500
    records_cursor = db.attendance.find({"schedule_id": ObjectId(schedule_id)}).sort("timestamp", -1)
    attendance_list = []
    for record in records_cursor:
        attendance_list.append({
            "name": record.get("name"),
            "role": record.get("role"),
            "time": record.get("timestamp").strftime("%H:%M:%S")
        })
    return jsonify(attendance_list)