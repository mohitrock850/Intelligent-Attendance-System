import os
import shutil
from datetime import datetime
from backend.database import get_db_connection

# Path where DeepFace will look for images for recognition
FACE_DB_PATH = "data/face_db"

def register_user(name, role, source_img_path):
    """Copies the user's image and adds their record to the MongoDB database."""
    # 1. Save the image file for DeepFace
    save_dir = os.path.join(FACE_DB_PATH, role, name)
    os.makedirs(save_dir, exist_ok=True)
    
    if not os.path.exists(source_img_path):
        print(f"Error: Source image path does not exist: {source_img_path}")
        return

    target_path = os.path.join(save_dir, os.path.basename(source_img_path))
    shutil.copy(source_img_path, target_path)
    print(f"✅ Image file registered for {role}: {name}")

    # 2. Add the user's information to MongoDB
    db = get_db_connection()
    if db is None: # Explicitly check for None
        print("Database connection failed. Cannot register user.")
        return
        
    users_collection = db.users
    
    # 'update_one' with 'upsert=True' will insert if the user doesn't exist, 
    # or do nothing if they already do.
    result = users_collection.update_one(
        {"name": name, "role": role},
        {"$setOnInsert": {"name": name, "role": role, "registered_on": datetime.now()}},
        upsert=True
    )
    
    if result.upserted_id is not None:
        print(f"✅ User '{name}' successfully inserted into the database.")
    else:
        print(f"✅ User '{name}' already exists in the database.")


if __name__ == "__main__":
    # Ensure you can connect to your DB by running `python backend/database.py` first.
    
    print("Registering users...")
    register_user("Sachin", "students", "data/students/sachin.jpg")
    register_user("Siddhart", "students", "data/students/siddhart.jpg")
    register_user("Dr. Himanshu", "teachers", "data/teachers/himanshu.jpg")
    register_user("Prof.Mohit", "teachers", "data/teachers/mohit.jpg")
    register_user("Harshit", "students", "data/students/harshit.jpg")
    register_user("Siddhesh", "students", "data/students/siddhesh.jpg")
    register_user("Yash", "students", "data/students/yash.jpg")
    print("\nRegistration complete.")