"""
Script to create initial admin users for the Cartlyf Timetable Scheduler.
This script focuses only on user creation and is designed to be robust.
"""

import os
import uuid
from datetime import datetime, timezone
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_initial_users():
    # Configuration
    # Use the URI from .env or the one provided by the user
    mongo_uri = os.getenv('MONGO_URI')
    db_name = os.getenv('MONGO_DB_NAME', 'timetable_scheduler')
    
    if not mongo_uri:
        print("Error: MONGO_URI not found in .env file.")
        return False

    print(f"Connecting to MongoDB...")
    
    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        db = client[db_name]
        
        # Test connection
        client.admin.command('ping')
        print(f"Successfully connected to database: {db_name}")
        
        # Define users
        users = [
            {
                'id': str(uuid.uuid4()),
                'email': 'admin@Cartlyf.ac.ug',
                'password_hash': generate_password_hash('Admin@123'),
                'full_name': 'System Administrator',
                'role': 'admin',
                'department': 'IT',
                'is_active': True,
                'created_at': datetime.now(timezone.utc),
                'last_login': None
            },
            {
                'id': str(uuid.uuid4()),
                'email': 'scheduler@Cartlyf.ac.ug',
                'password_hash': generate_password_hash('Scheduler@123'),
                'full_name': 'Timetable Scheduler',
                'role': 'scheduler',
                'department': 'Academic Affairs',
                'is_active': True,
                'created_at': datetime.now(timezone.utc),
                'last_login': None
            },
            {
                'id': str(uuid.uuid4()),
                'email': 'viewer@Cartlyf.ac.ug',
                'password_hash': generate_password_hash('Viewer@123'),
                'full_name': 'Timetable Viewer',
                'role': 'viewer',
                'department': 'General',
                'is_active': True,
                'created_at': datetime.now(timezone.utc),
                'last_login': None
            }
        ]
        
        # Insert users
        print("Creating default users...")
        for user in users:
            # Check if user already exists
            existing = db.users.find_one({'email': user['email']})
            if existing:
                print(f"User {user['email']} already exists. Skipping.")
            else:
                db.users.insert_one(user)
                print(f"Created user: {user['email']} ({user['role']})")
        
        print("\nInitialization complete!")
        print("-" * 30)
        print("Default Credentials:")
        print("Admin: admin@Cartlyf.ac.ug / Admin@123")
        print("Scheduler: scheduler@Cartlyf.ac.ug / Scheduler@123")
        print("Viewer: viewer@Cartlyf.ac.ug / Viewer@123")
        print("-" * 30)
        
        client.close()
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    create_initial_users()
