from pymongo import MongoClient
from pymongo.server_api import ServerApi

MONGO_CONNECTION_STRING = "mongodb://localhost:27017/"
DB_NAME = "attendance_system"

def get_db_connection():
    """Establishes a connection to the MongoDB database."""
    try:
        client = MongoClient(MONGO_CONNECTION_STRING, server_api=ServerApi('1'))
        client.admin.command('ping')
        print("✅ MongoDB connection successful.")
        return client[DB_NAME]
    except Exception as e:
        print(f"❌ Could not connect to MongoDB: {e}")
        return None

if __name__ == "__main__":
    db = get_db_connection()
    if db is not None:
        # Ensure indexes for all collections
        db.users.create_index([("name", 1), ("role", 1)], unique=True)
        db.classes.create_index([("subject", 1)], unique=True)
        db.schedules.create_index("start_time")
        db.attendance.create_index("schedule_id")
        print(f"Successfully connected to '{DB_NAME}' and ensured all indexes.")