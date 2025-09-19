from datetime import datetime, timedelta, timezone
from backend.database import get_db_connection

def setup_data():
    """
    Populates the database with timezone-aware class and schedule data, including a status.
    """
    db = get_db_connection()
    if db is None:
        print("Could not connect to the database. Aborting setup.")
        return

    users_collection = db.users
    classes_collection = db.classes
    schedules_collection = db.schedules

    teacher_mohit = users_collection.find_one({"name": "Prof.Mohit"})
    teacher_himanshu = users_collection.find_one({"name": "Dr. Himanshu"})

    if not teacher_mohit or not teacher_himanshu:
        print("Please register 'mohit' and 'himanshu' as teachers before running this setup.")
        return

    print("Setting up classes...")
    classes_collection.update_one(
        {"subject": "Physics 101"},
        {"$setOnInsert": {"subject": "Physics 101", "default_teacher_id": teacher_mohit["_id"]}},
        upsert=True
    )
    classes_collection.update_one(
        {"subject": "Chemistry Lab"},
        {"$setOnInsert": {"subject": "Chemistry Lab", "default_teacher_id": teacher_himanshu["_id"]}},
        upsert=True
    )
    print("Classes are set up.")

    print("Setting up today's schedule...")
    schedules_collection.delete_many({})

    physics_class = classes_collection.find_one({"subject": "Physics 101"})
    chem_class = classes_collection.find_one({"subject": "Chemistry Lab"})

    now_utc = datetime.now(timezone.utc)

    # Schedule Physics (Offline)
    physics_start = now_utc + timedelta(minutes=1) # Start sooner for easier testing
    physics_end = physics_start + timedelta(hours=1)
    schedules_collection.insert_one({
        "class_id": physics_class["_id"],
        "subject": physics_class["subject"],
        "teacher_name": teacher_mohit["name"],
        "start_time": physics_start,
        "end_time": physics_end,
        "mode": "Offline",
        "status": "active"  # --- NEW ---
    })

    # Schedule Chemistry (Online)
    chem_start = now_utc + timedelta(minutes=5)
    chem_end = chem_start + timedelta(hours=2)
    schedules_collection.insert_one({
        "class_id": chem_class["_id"],
        "subject": chem_class["subject"],
        "teacher_name": teacher_himanshu["name"],
        "start_time": chem_start,
        "end_time": chem_end,
        "mode": "Online",
        "status": "active"  # --- NEW ---
    })
    
    print("Today's schedule has been created successfully using UTC time.")

if __name__ == "__main__":
    setup_data()