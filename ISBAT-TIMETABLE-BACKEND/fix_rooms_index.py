"""
Script to fix MongoDB indexes for rooms collection.
Drops the old 'id' index and creates a new 'room_number' unique index.
"""

from app import create_app, get_db

def fix_rooms_index():
    """Fix the rooms collection indexes"""
    app = create_app()
    
    with app.app_context():
        db = get_db()
        
        try:
            # Get all indexes
            indexes = db.rooms.list_indexes()
            print("Current indexes on rooms collection:")
            for idx in indexes:
                print(f"  - {idx['name']}: {idx.get('key', {})}")
            
            # Drop old 'id' index if it exists
            try:
                db.rooms.drop_index('id_1')
                print("\n[OK] Dropped old 'id_1' index")
            except Exception as e:
                print(f"\n[WARN] Could not drop 'id_1' index (may not exist): {e}")
            
            # Try to drop any other 'id' indexes
            try:
                indexes = list(db.rooms.list_indexes())
                for idx in indexes:
                    if 'id' in idx.get('key', {}):
                        db.rooms.drop_index(idx['name'])
                        print(f"[OK] Dropped index: {idx['name']}")
            except Exception as e:
                print(f"[WARN] Error dropping indexes: {e}")
            
            # Create unique index on room_number
            try:
                db.rooms.create_index('room_number', unique=True)
                print("[OK] Created unique index on 'room_number'")
            except Exception as e:
                print(f"[WARN] Could not create index on room_number: {e}")
            
            # Show final indexes
            print("\nFinal indexes on rooms collection:")
            indexes = db.rooms.list_indexes()
            for idx in indexes:
                print(f"  - {idx['name']}: {idx.get('key', {})}")
            
            print("\n[SUCCESS] Index fix completed!")
            
        except Exception as e:
            print(f"[ERROR] Error fixing indexes: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    fix_rooms_index()

