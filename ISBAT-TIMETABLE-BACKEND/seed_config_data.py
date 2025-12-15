"""
Seed script for configurable system data:
- Room Specializations
- Time Slots
"""

from typing import List, Dict

# Default room specializations
DEFAULT_ROOM_SPECIALIZATIONS = [
    {"id": "ICT", "name": "ICT", "description": "Information and Communication Technology"},
    {"id": "Programming", "name": "Programming", "description": "Programming and Software Development"},
    {"id": "Networking & Cyber Security", "name": "Networking & Cyber Security", "description": "Networking and Cybersecurity"},
    {"id": "LINUX", "name": "LINUX", "description": "Linux Administration"},
    {"id": "Multimedia", "name": "Multimedia", "description": "Multimedia and Graphics"},
    {"id": "Statistics", "name": "Statistics", "description": "Statistics and Data Analysis"},
    {"id": "Management Lab", "name": "Management Lab", "description": "Management Laboratory"},
    {"id": "BHM", "name": "BHM", "description": "Business and Hospitality Management"},
    {"id": "Electronics Lab", "name": "Electronics Lab", "description": "Electronics Laboratory"},
    {"id": "Physics Lab", "name": "Physics Lab", "description": "Physics Laboratory"},
    {"id": "AI & ML", "name": "AI & ML", "description": "Artificial Intelligence and Machine Learning"},
    {"id": "Theory", "name": "Theory", "description": "Theory Room"},
]

# Default time slots
DEFAULT_TIME_SLOTS = [
    {"period": "SLOT_1", "start": "09:00", "end": "11:00", "is_afternoon": False, "display_name": "09:00 AM - 11:00 AM", "order": 1},
    {"period": "SLOT_2", "start": "11:00", "end": "13:00", "is_afternoon": False, "display_name": "11:00 AM - 01:00 PM", "order": 2},
    {"period": "SLOT_3", "start": "14:00", "end": "16:00", "is_afternoon": True, "display_name": "02:00 PM - 04:00 PM", "order": 3},
    {"period": "SLOT_4", "start": "16:00", "end": "18:00", "is_afternoon": True, "display_name": "04:00 PM - 06:00 PM", "order": 4},
]


def seed_room_specializations_to_db(db):
    """
    Seed room specializations to MongoDB database.
    Only seeds if collection is empty (preserves user modifications).
    
    Args:
        db: MongoDB database instance
    """
    # Check if specializations already exist
    existing_count = db.room_specializations.count_documents({})
    
    if existing_count > 0:
        print(f"⚠️  Room specializations already exist ({existing_count} items). Skipping seed.")
        print("   To reset, manually clear the collection first.")
        return
    
    # Insert default specializations
    result = db.room_specializations.insert_many(DEFAULT_ROOM_SPECIALIZATIONS)
    
    print(f"✅ Successfully seeded {len(result.inserted_ids)} room specializations")
    for spec in DEFAULT_ROOM_SPECIALIZATIONS:
        print(f"   - {spec['id']}: {spec['name']}")
    
    return result


def seed_time_slots_to_db(db):
    """
    Seed time slots to MongoDB database.
    Only seeds if collection is empty (preserves user modifications).
    
    Args:
        db: MongoDB database instance
    """
    # Check if time slots already exist
    existing_count = db.time_slots.count_documents({})
    
    if existing_count > 0:
        print(f"⚠️  Time slots already exist ({existing_count} items). Skipping seed.")
        print("   To reset, manually clear the collection first.")
        return
    
    # Insert default time slots
    result = db.time_slots.insert_many(DEFAULT_TIME_SLOTS)
    
    print(f"✅ Successfully seeded {len(result.inserted_ids)} time slots")
    for slot in DEFAULT_TIME_SLOTS:
        period_type = "Afternoon" if slot['is_afternoon'] else "Morning"
        print(f"   - {slot['period']}: {slot['start']}-{slot['end']} ({period_type})")
    
    return result


def seed_config_to_db(db):
    """
    Seed all configurable data to MongoDB database.
    
    Args:
        db: MongoDB database instance
    """
    print("-" * 70)
    print("SEEDING ROOM SPECIALIZATIONS...")
    print("-" * 70)
    seed_room_specializations_to_db(db)
    
    print("\n" + "-" * 70)
    print("SEEDING TIME SLOTS...")
    print("-" * 70)
    seed_time_slots_to_db(db)
    
    print("\n✅ Config data seeding complete!")


if __name__ == '__main__':
    from pymongo import MongoClient
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Connect to MongoDB
    try:
        mongo_uri = os.getenv('MONGO_URI', 'mongodb+srv://philiphinny436:hinny123@cluster0.h3zklgk.mongodb.net/')
        db_name = os.getenv('MONGO_DB_NAME', 'timetable_scheduler')
        client = MongoClient(mongo_uri)
        db = client[db_name]
        print(f"Connected to MongoDB: {db_name}\n")
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        exit(1)
    
    try:
        seed_config_to_db(db)
    finally:
        client.close()

