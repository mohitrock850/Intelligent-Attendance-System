import os
import shutil
from src.database import get_db_connection

def register_face(name, role, img_path):
    # --- Part 1: Save image file for DeepFace (No changes here) ---
    save_dir = f"data/face_db/{role}/{name}"
    os.makedirs(save_dir, exist_ok=True)
    target_path = os.path.join(save_dir, os.path.basename(img_path))
    shutil.copy(img_path, target_path)
    print(f"✅ Image file registered for {role}: {name}")

    # --- Part 2: Add user to MongoDB database ---
    db = get_db_connection()
    if not db:
        print("❌ Cannot register user in database. Connection failed.")
        return
        
    users_collection = db.users
    
    # Use update_one with upsert=True to insert if not exists, or do nothing if exists.
    # This prevents creating duplicate users.
    users_collection.update_one(
        {"name": name, "role": role},
        {"$setOnInsert": {"name": name, "role": role, "registered_on": datetime.now()}},
        upsert=True
    )
    print(f"✅ User '{name}' registered in the database.")


if __name__ == "__main__":
    from datetime import datetime

    # Make sure you've tested your DB connection first by running `python src/database.py`
    
    # Register students
    register_face("sachin", "students", "data/students/sachin.jpg")
    register_face("siddhart", "students", "data/students/siddhart.jpg")

    # Register teachers
    register_face("himanshu", "teachers", "data/teachers/himanshu.jpg")
    register_face("mohit", "teachers", "data/teachers/mohit.jpg")