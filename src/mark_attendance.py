import cv2
import os
from deepface import DeepFace
# Import the new database marking function
from src.utils import mark_attendance_in_db 
import time

DB_PATH = "data/face_db"
MODEL_NAME = "VGG-Face"
DISTANCE_METRIC = "cosine"

def recognize_and_draw(frame, role, known_names):
    try:
        results = DeepFace.find(
            img_path=frame,
            db_path=f"{DB_PATH}/{role}",
            model_name=MODEL_NAME,
            distance_metric=DISTANCE_METRIC,
            enforce_detection=False,
            silent=True
        )
        
        if len(results) > 0 and not results[0].empty:
            best_match_df = results[0].iloc[0]
            identity_path = best_match_df['identity']
            name = os.path.basename(os.path.dirname(identity_path))
            x, y, w, h = best_match_df['source_x'], best_match_df['source_y'], best_match_df['source_w'], best_match_df['source_h']
            
            # --- MODIFICATION ---
            # Mark attendance and get the status message
            status_message = ""
            if role == "students" and name not in known_names:
                status_message = mark_attendance_in_db(name, role)
                if status_message == "Marked Present!":
                    known_names.add(name)

            # Draw the box and name
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            
            # Display the status message below the box
            if status_message:
                cv2.putText(frame, status_message, (x, y + h + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # This function now just returns the name for teacher verification
            if role == "teachers":
                 return name

    except Exception as e:
        pass
    return None

def start_attendance():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Cannot open camera")
        return

    teacher_verified = False
    teacher_name = None

    print("📸 Please authenticate TEACHER...")
    
    while not teacher_verified:
        ret, frame = cap.read()
        if not ret: break
        
        # We pass an empty set because teacher doesn't need to be marked
        verified_name = recognize_and_draw(frame, "teachers", set())
        
        if verified_name:
            teacher_name = verified_name
            print(f"✅ Teacher {teacher_name} verified. Starting attendance...")
            cv2.imshow("Attendance", frame)
            cv2.waitKey(2000) # Wait 2 seconds
            teacher_verified = True
        else:
            cv2.imshow("Attendance", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            cap.release()
            cv2.destroyAllWindows()
            return

    present_students = set()
    print("📸 Scanning students... (Press Q to stop)")

    while True:
        ret, frame = cap.read()
        if not ret: break

        # recognize_and_draw will now handle the marking internally
        recognize_and_draw(frame, "students", present_students)
        
        info_text = f"Teacher: {teacher_name} | Present: {len(present_students)}"
        cv2.putText(frame, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.imshow("Attendance", frame)
        
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    print(f"\nAttendance session ended. Total students marked: {len(present_students)}")
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    start_attendance()