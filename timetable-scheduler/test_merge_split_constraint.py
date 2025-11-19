"""
Test script to verify merge/split constraints by increasing S1 student group size
This will test if the system properly handles groups that exceed room capacity
"""

import sys
sys.path.insert(0, '.')

from pymongo import MongoClient
from app.config import Config

def update_s1_student_groups(new_size=100):
    """
    Update S1 student group sizes to test split constraint
    Setting to 100 students will exceed most room capacities (largest lab is 88, largest classroom is 500)
    """
    client = MongoClient(Config.MONGODB_URI)
    db = client[Config.MONGODB_DB_NAME]
    
    print("="*70)
    print("          TESTING MERGE/SPLIT CONSTRAINT")
    print("="*70)
    print(f"\n📝 Updating S1 student group sizes to {new_size} students...")
    print("   This will test if groups exceeding room capacity are properly split\n")
    
    # Find all S1 student groups
    s1_groups = list(db.student_groups.find({'semester': 'S1'}))
    
    if not s1_groups:
        print("❌ No S1 student groups found!")
        return
    
    print(f"Found {len(s1_groups)} S1 student groups:")
    for group in s1_groups:
        old_size = group.get('size', 0)
        print(f"   • {group['id']}: {old_size} → {new_size} students")
    
    # Update all S1 groups
    result = db.student_groups.update_many(
        {'semester': 'S1'},
        {'$set': {'size': new_size}}
    )
    
    print(f"\n✅ Updated {result.modified_count} student groups")
    print(f"\n📊 Summary:")
    print(f"   • New size: {new_size} students per S1 group")
    print(f"   • Largest Lab capacity: 88 students")
    print(f"   • Largest Classroom capacity: 500 students")
    print(f"   • Expected behavior: Groups should be split before scheduling")
    
    print("\n" + "="*70)
    print("Next steps:")
    print("1. Run: python generate_term_timetable.py --term 1")
    print("2. Check if groups are split (should have _SPLIT_ suffix)")
    print("3. Run: python verify_constraints_comprehensive.py TIMETABLE_TERM1_COMPLETE.csv")
    print("="*70 + "\n")
    
    client.close()

def restore_original_sizes():
    """Restore original S1 group sizes"""
    client = MongoClient(Config.MONGODB_URI)
    db = client[Config.MONGODB_DB_NAME]
    
    print("="*70)
    print("          RESTORING ORIGINAL S1 GROUP SIZES")
    print("="*70)
    
    # Restore original sizes
    original_sizes = {
        'SG_BSCAIT_126_S1': 25,
        'SG_BSCAIT_226_S1': 28
    }
    
    for group_id, size in original_sizes.items():
        result = db.student_groups.update_one(
            {'id': group_id},
            {'$set': {'size': size}}
        )
        if result.modified_count > 0:
            print(f"   ✅ {group_id}: Restored to {size} students")
        else:
            print(f"   ⚠️  {group_id}: Not found or already correct")
    
    print("\n✅ Restoration complete\n")
    client.close()

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--restore':
        restore_original_sizes()
    else:
        # Default: set to 100 students to exceed lab capacity
        new_size = int(sys.argv[1]) if len(sys.argv) > 1 else 100
        update_s1_student_groups(new_size)

