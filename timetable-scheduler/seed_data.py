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
from seed_student_groups_data import seed_student_groups_to_db
from seed_rooms_data import seed_rooms_to_db

load_dotenv()

def seed_all():
    """Main seeding function"""
    
    print("\n" + "="*70)
    print(" "*20 + "ISBAT DATA SEEDING")
    print("="*70 + "\n")
    
    # Connect to MongoDB
    try:
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        db_name = os.getenv('MONGO_DB_NAME', 'timetable_scheduler')
        client = MongoClient(mongo_uri)
        db = client[db_name]
        print(f"✅ Connected to MongoDB: {db_name}\n")
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return False
    
    # Clear existing data
    print("-" * 70)
    print("🗑️  CLEARING EXISTING DATA...")
    print("-" * 70)
    db.lecturers.delete_many({})
    db.rooms.delete_many({})
    db.course_units.delete_many({})
    db.student_groups.delete_many({})
    db.users.delete_many({})
    db.schedules.delete_many({})
    print("✅ All collections cleared\n")
    
    # Create default users
    print("-" * 70)
    print("👤 CREATING DEFAULT USERS...")
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
    print("✅ Created 3 default users:")
    print("   - admin@isbat.ac.ug / Admin@123 (Admin)")
    print("   - scheduler@isbat.ac.ug / Scheduler@123 (Scheduler)")
    print("   - viewer@isbat.ac.ug / Viewer@123 (Viewer)\n")
    
    # Seed all data using modular functions
    try:
        print("-" * 70)
        print("📚 SEEDING COURSES...")
        print("-" * 70)
        seed_courses_to_db(db)
        
        print("\n" + "-" * 70)
        print("👔 SEEDING LECTURERS...")
        print("-" * 70)
        seed_lecturers_to_db(db)
        
        print("\n" + "-" * 70)
        print("🚪 SEEDING ROOMS...")
        print("-" * 70)
        seed_rooms_to_db(db)
        
        print("\n" + "-" * 70)
        print("👥 SEEDING STUDENT GROUPS...")
        print("-" * 70)
        seed_student_groups_to_db(db)
        
        print("\n" + "="*70)
        print(" "*20 + "SEEDING COMPLETE!")
        print("="*70 + "\n")
        
        # Display summary
        display_summary(db)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
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
    student_group_count = db.student_groups.count_documents({})
    user_count = db.users.count_documents({})
    
    print(f"📊 Collection Counts:")
    print(f"   └─ Users: {user_count}")
    print(f"   └─ Lecturers: {lecturer_count}")
    print(f"   └─ Courses: {course_count}")
    print(f"   └─ Rooms: {room_count}")
    print(f"   └─ Student Groups: {student_group_count}")
    
    # Get additional statistics
    total_students = sum(g['size'] for g in db.student_groups.find({}, {'size': 1}))
    total_room_capacity = sum(r['capacity'] for r in db.rooms.find({}, {'capacity': 1}))
    
    print(f"\n📈 Capacity Statistics:")
    print(f"   └─ Total Students: {total_students}")
    print(f"   └─ Total Room Capacity: {total_room_capacity} seats")
    print(f"   └─ Capacity Ratio: {total_room_capacity / total_students:.2f}x")
    
    # Lecturers by role
    full_time = db.lecturers.count_documents({'role': 'Full-Time'})
    part_time = db.lecturers.count_documents({'role': 'Part-Time'})
    dean = db.lecturers.count_documents({'role': 'Faculty Dean'})
    
    print(f"\n👔 Lecturer Distribution:")
    print(f"   └─ Full-Time: {full_time}")
    print(f"   └─ Part-Time: {part_time}")
    print(f"   └─ Faculty Dean: {dean}")
    
    # Rooms by type
    labs = db.rooms.count_documents({'room_type': 'Lab'})
    classrooms = db.rooms.count_documents({'room_type': 'Classroom'})
    halls = db.rooms.count_documents({'room_type': 'Lecture Hall'})
    
    print(f"\n🚪 Room Distribution:")
    print(f"   └─ Labs: {labs}")
    print(f"   └─ Classrooms: {classrooms}")
    print(f"   └─ Lecture Halls: {halls}")
    
    print(f"\n✅ SYSTEM STATUS:")
    print(f"   └─ Database: Ready")
    print(f"   └─ Authentication: Configured")
    print(f"   └─ Scheduling: Ready to Start")
    
    print("\n" + "="*70)
    print(" "*15 + "🚀 SYSTEM READY FOR USE! 🚀")
    print("="*70 + "\n")
    
    print("📝 Quick Start:")
    print("   1. Start the application: python run.py")
    print("   2. Login with: admin@isbat.ac.ug / Admin@123")
    print("   3. Generate timetable: python test_generate_timetable.py")
    print()


if __name__ == '__main__':
    import sys
    
    print("\n🎓 ISBAT Timetable System - Master Seeding Script")
    print("=" * 70)
    print("This will seed all data using modular seed files:")
    print("  - seed_courses_data.py (30 courses)")
    print("  - seed_lecturers_data.py (15 lecturers)")
    print("  - seed_rooms_data.py (27 rooms)")
    print("  - seed_student_groups_data.py (12 groups)")
    print("=" * 70)
    
    success = seed_all()
    
    if success:
        print("\n✅ All data seeded successfully!")
        print("🎉 The system is ready to generate timetables!\n")
        sys.exit(0)
    else:
        print("\n❌ Seeding failed. Please check the error messages above.\n")
        sys.exit(1)
