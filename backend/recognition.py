import cv2
import os
from deepface import DeepFace
from datetime import datetime
from .database import get_db_connection
from bson.objectid import ObjectId

FACE_DB_PATH = "data/face_db"

def is_real_face(face_roi):
    """Basic anti-spoofing check based on image sharpness."""
    if face_roi is None or face_roi.size == 0: return 0.0, False
    laplacian_var = cv2.Laplacian(face_roi, cv2.CV_64F).var()
    LIVENESS_THRESHOLD = 25.0
    return laplacian_var, laplacian_var >= LIVENESS_THRESHOLD

def mark_db_attendance(name, role, schedule_id):
    """Marks attendance in MongoDB for a specific class schedule."""
    db = get_db_connection()
    if db is None: return "DB Error"
    
    user = db.users.find_one({"name": name, "role": role})
    if not user: return "Unregistered"

    # Check if already marked for this specific session
    already_marked = db.attendance.find_one({
        "user_id": user["_id"],
        "schedule_id": ObjectId(schedule_id)
    })

    if already_marked:
        return "Already Marked"
    else:
        db.attendance.insert_one({
            "user_id": user["_id"],
            "schedule_id": ObjectId(schedule_id),
            "name": user["name"], "role": user["role"],
            "timestamp": datetime.now()
        })
        return "Marked Present!"

def find_and_mark(frame, schedule_id):
    """Processes a frame, recognizes faces, and marks attendance for the given schedule_id."""
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    try:
        results = DeepFace.find(
            img_path=frame, db_path=FACE_DB_PATH,
            enforce_detection=False, silent=True
        )
        if results and not results[0].empty:
            best_match = results[0].iloc[0]
            x, y, w, h = best_match['source_x'], best_match['source_y'], best_match['source_w'], best_match['source_h']
            face_roi_gray = gray_frame[y:y+h, x:x+w]

            liveness_score, is_live = is_real_face(face_roi_gray)
            debug_text = f"Liveness: {liveness_score:.1f}"
            
            if not is_live:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(frame, "SPOOF", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.putText(frame, debug_text, (x, y + h + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            else:
                identity_path = best_match['identity']
                name = os.path.basename(os.path.dirname(identity_path))
                role = os.path.basename(os.path.dirname(os.path.dirname(identity_path)))
                
                # Pass the schedule_id to the marking function
                message = mark_db_attendance(name, role, schedule_id)
                
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, message, (x, y + h + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(frame, debug_text, (x, y + h + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    except Exception:
        pass
    return frame