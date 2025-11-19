"""Clear all collections in the database"""

import sys
from pymongo import MongoClient

def main():
    print("\n" + "="*70)
    print(" "*20 + "CLEARING DATABASE")
    print("="*70 + "\n")

    try:
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        db = client['timetable_scheduler']
        
        # Clear all collections
        collections = ['lecturers', 'course_units', 'rooms', 'student_groups', 'users', 'schedules']
        
        for collection in collections:
            result = db[collection].delete_many({})
            print(f"✅ Cleared {collection}: {result.deleted_count} documents")
        
        print("\n" + "="*70)
        print("✅ Database cleared successfully!")
        print("="*70 + "\n")
        print("Next step: Run python seed_data.py\n")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure MongoDB is running!")
        print("   - Windows: net start MongoDB")
        print("   - Linux/Mac: sudo service mongod start\n")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

