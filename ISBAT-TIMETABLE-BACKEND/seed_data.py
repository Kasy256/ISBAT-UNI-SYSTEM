"""
Master data seeding script for ISBAT Timetable Scheduler
Uses modular seed data files for cleaner organization
"""

from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash
import uuid

# Import modular seed functions
from seed_lecturers_data import seed_lecturers_to_db
from seed_courses_data import seed_courses_to_db
from seed_programs_data import seed_programs_to_db
from seed_rooms_data import seed_rooms_to_db
from seed_config_data import seed_config_to_db

load_dotenv()

def seed_all():
    """Main seeding function"""
    
    print("\n" + "="*70)
    print(" "*20 + "ISBAT DATA SEEDING")
    print("="*70 + "\n")
    
    # Connect to MongoDB
    try:
        mongo_uri = os.getenv('MONGO_URI', 'mongodb+srv://philiphinny436:hinny123@cluster0.h3zklgk.mongodb.net/')
        db_name = os.getenv('MONGO_DB_NAME', 'timetable_scheduler')
        client = MongoClient(mongo_uri)
        db = client[db_name]
        print(f"Connected to MongoDB: {db_name}\n")
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return False
    
    # Clear existing data
    print("-" * 70)
    print("CLEARING EXISTING DATA...")
    print("-" * 70)
    db.lecturers.delete_many({})
    db.rooms.delete_many({})
    db.course_units.delete_many({})
    db.programs.delete_many({})
    db.users.delete_many({})
    db.schedules.delete_many({})
    print("All collections cleared\n")
    
    # Create default users
    print("-" * 70)
    print("CREATING DEFAULT USERS...")
    print("-" * 70)
    
    default_users = [
        {
            'id': str(uuid.uuid4()),
            'email': 'admin@isbat.ac.ug',
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
            'email': 'scheduler@isbat.ac.ug',
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
            'email': 'viewer@isbat.ac.ug',
            'password_hash': generate_password_hash('Viewer@123'),
            'full_name': 'Timetable Viewer',
            'role': 'viewer',
            'department': 'General',
            'is_active': True,
            'created_at': datetime.now(timezone.utc),
            'last_login': None
        }
    ]
    
    db.users.insert_many(default_users)
    print("Created 3 default users\n")
    
    # Seed all data using modular functions
    try:
        print("-" * 70)
        print("SEEDING SUBJECTS...")
        print("-" * 70)
        seed_courses_to_db(db)
        
        print("\n" + "-" * 70)
        print("SEEDING LECTURERS...")
        print("-" * 70)
        seed_lecturers_to_db(db)
        
        print("\n" + "-" * 70)
        print("SEEDING ROOMS...")
        print("-" * 70)
        seed_rooms_to_db(db)
        
        print("\n" + "-" * 70)
        print("SEEDING PROGRAMS...")
        print("-" * 70)
        seed_programs_to_db(db)
        
        print("\n" + "-" * 70)
        print("SEEDING CONFIG DATA (Room Specializations & Time Slots)...")
        print("-" * 70)
        seed_config_to_db(db)
        
        print("\n" + "="*70)
        print(" "*20 + "SEEDING COMPLETE!")
        print("="*70 + "\n")
        
        # Display summary
        display_summary(db)
        
        return True
        
    except Exception as e:
        print(f"\nError during seeding: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        client.close()


def display_summary(db):
    """Display a summary of seeded data"""
    
    print("\n" + "="*70)
    print(" "*22 + "DATABASE SUMMARY")
    print("="*70 + "\n")
    
    # Count documents in each collection
    lecturer_count = db.lecturers.count_documents({})
    course_count = db.course_units.count_documents({})
    room_count = db.rooms.count_documents({})
    program_count = db.programs.count_documents({})
    user_count = db.users.count_documents({})
    
    print(f"Collection Counts:")
    print(f"   Users: {user_count}")
    print(f"   Lecturers: {lecturer_count}")
    print(f"   Subjects: {course_count}")
    print(f"   Rooms: {room_count}")
    print(f"   Programs: {program_count}")
    
    # Lecturers by role
    full_time = db.lecturers.count_documents({'role': 'Full-Time'})
    part_time = db.lecturers.count_documents({'role': 'Part-Time'})
    dean = db.lecturers.count_documents({'role': 'Faculty Dean'})
    
    print(f"\nLecturer Distribution:")
    print(f"   Full-Time: {full_time}")
    print(f"   Part-Time: {part_time}")
    print(f"   Faculty Dean: {dean}")
    
    print("\n" + "="*70)
    print("SYSTEM READY FOR USE!")
    print("="*70 + "\n")


if __name__ == '__main__':
    import sys
    
    success = seed_all()
    
    if success:
        print("All data seeded successfully!\n")
        sys.exit(0)
    else:
        print("Seeding failed. Please check the error messages above.\n")
        sys.exit(1)
