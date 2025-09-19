import os
from pymongo import MongoClient

# --- IMPORTANT ---
# Replace this with your own MongoDB connection string if it's different.
# If using MongoDB Atlas, you'll get the string from your cluster dashboard.
MONGO_CONNECTION_STRING = "mongodb://localhost:27017/"
DB_NAME = "attendance_system"

def get_db_connection():
    """
    Establishes a connection to the MongoDB database and returns the database object.
    """
    try:
        client = MongoClient(MONGO_CONNECTION_STRING)
        # Ping the server to check the connection
        client.admin.command('ping')
        print("✅ MongoDB connection successful.")
        return client[DB_NAME]
    except Exception as e:
        print(f"❌ Could not connect to MongoDB: {e}")
        return None

# You can run this file directly (python src/database.py) to test your connection
if __name__ == "__main__":
    db = get_db_connection()
    if db:
        print(f"Successfully connected to the '{DB_NAME}' database.")