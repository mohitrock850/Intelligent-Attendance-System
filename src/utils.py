import os
from datetime import datetime, time
from .database import get_db_connection

def mark_attendance_in_db(name, role):
    """
    Marks attendance in the MongoDB database.
    Checks if the user was already marked today before inserting.
    Returns a status message.
    """
    db = get_db_connection()
    if not db:
        return "DB Connection Failed"

    users_collection = db.users
    attendance_collection = db.attendance

    # Find the user in the 'users' collection
    user = users_collection.find_one({"name": name, "role": role})
    if not user:
        print(f"User '{name}' with role '{role}' not found in the database.")
        return "Unregistered User"

    # Define the start and end of today for the query
    today_start = datetime.combine(datetime.today(), time.min)
    today_end = datetime.combine(datetime.today(), time.max)

    # Check if attendance was already marked for this user today
    already_marked = attendance_collection.find_one({
        "user_id": user["_id"],
        "timestamp": {"$gte": today_start, "$lt": today_end}
    })

    if already_marked:
        return "Already Marked"
    else:
        # Insert a new attendance record
        attendance_collection.insert_one({
            "user_id": user["_id"],
            "name": user["name"], # Denormalize for easier querying/viewing
            "role": user["role"], # Denormalize
            "timestamp": datetime.now()
        })
        print(f"Marked attendance for {name}")
        return "Marked Present!"