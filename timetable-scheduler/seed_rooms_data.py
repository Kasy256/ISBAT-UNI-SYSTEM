"""Seed room data for ISBAT Timetable System"""

from app.models.room import Room
from typing import List, Dict

def get_all_rooms() -> List[Dict]:
    """
    Get all room data from ISBAT campuses
    
    Returns:
        List of room dictionaries ready for MongoDB insertion
    """
    clean_rooms = [
        # 1ST FLOOR
        {
            "id": "R104",
            "room_number": "104",
            "capacity": 16,
            "room_type": "Lab",
            "floor": 1,
            "campus": "Main",
            "facilities": ["Computers", "Projector"],
            "specializations": ["ICT", "Programming", "Networking & Cyber Security"],
            "is_available": True
        },
        # 2ND FLOOR
        {
            "id": "R203",
            "room_number": "203",
            "capacity": 32,
            "room_type": "Lab",
            "floor": 2,
            "campus": "Main",
            "facilities": ["Computers", "Projector"],
            "specializations": ["ICT", "Programming", "Multimedia"],
            "is_available": True
        },
        {
            "id": "R204",
            "room_number": "204",
            "capacity": 32,
            "room_type": "Lab",
            "floor": 2,
            "campus": "Main",
            "facilities": ["Computers", "Projector"],
            "specializations": ["ICT", "Programming"],
            "is_available": True
        },
        {
            "id": "R205",
            "room_number": "205",
            "capacity": 32,
            "room_type": "Lab",
            "floor": 2,
            "campus": "Main",
            "facilities": ["Computers", "Projector"],
            "specializations": ["ICT", "Programming"],
            "is_available": True
        },
        {
            "id": "R206",
            "room_number": "206",
            "capacity": 64,
            "room_type": "Lab",
            "floor": 2,
            "campus": "Main",
            "facilities": ["Computers", "Projector"],
            "specializations": ["ICT", "Programming"],
            "is_available": True
        },
        {
            "id": "R207",
            "room_number": "207",
            "capacity": 24,
            "room_type": "Lab",
            "floor": 2,
            "campus": "Main",
            "facilities": ["Computers", "Projector", "Multimedia Equipment"],
            "specializations": ["ICT", "Programming", "Multimedia"],
            "is_available": True
        },
        # 3RD FLOOR (Theory rooms)
        {"id": "R300", "room_number": "300", "capacity": 32, "room_type": "Theory", "floor": 3,
         "campus": "Main", "facilities": ["Whiteboard", "Projector"], "specializations": [], "is_available": True},
        {"id": "R301", "room_number": "301", "capacity": 32, "room_type": "Theory", "floor": 3,
         "campus": "Main", "facilities": ["Whiteboard", "Projector"], "specializations": [], "is_available": True},
        {"id": "R302", "room_number": "302", "capacity": 32, "room_type": "Theory", "floor": 3,
         "campus": "Main", "facilities": ["Whiteboard", "Projector"], "specializations": [], "is_available": True},
        {"id": "R303", "room_number": "303", "capacity": 32, "room_type": "Theory", "floor": 3,
         "campus": "Main", "facilities": ["Whiteboard", "Projector"], "specializations": [], "is_available": True},
        {"id": "R304", "room_number": "304", "capacity": 32, "room_type": "Theory", "floor": 3,
         "campus": "Main", "facilities": ["Whiteboard", "Projector"], "specializations": [], "is_available": True},
        {"id": "R305", "room_number": "305", "capacity": 80, "room_type": "Theory", "floor": 3,
         "campus": "Main", "facilities": ["Whiteboard", "Projector", "Sound System"], "specializations": [], "is_available": True},
        {"id": "R306", "room_number": "306", "capacity": 30, "room_type": "Theory", "floor": 3,
         "campus": "Main", "facilities": ["Whiteboard", "Projector"], "specializations": [], "is_available": True},
        {
            "id": "R308",
            "room_number": "308",
            "capacity": 32,
            "room_type": "Lab",
            "floor": 3,
            "campus": "Main",
            "facilities": ["Computers", "Networking Equipment", "Projector"],
            "specializations": ["Networking & Cyber Security", "Statistics", "Management Lab"],
            "is_available": True
        },
        # 4TH FLOOR
        {"id": "R401", "room_number": "401", "capacity": 12, "room_type": "Lab", "floor": 4,
         "campus": "Main", "facilities": ["Specialized Equipment"], "specializations": ["BHM"], "is_available": True},
        {"id": "R402", "room_number": "402", "capacity": 20, "room_type": "Lab", "floor": 4,
         "campus": "Main", "facilities": ["Electronics Equipment", "Workbenches"], "specializations": ["Electronics"], "is_available": True},
        {"id": "R403", "room_number": "403", "capacity": 10, "room_type": "Lab", "floor": 4,
         "campus": "Main", "facilities": ["Physics Equipment"], "specializations": ["Physics"], "is_available": True},
        {"id": "R404", "room_number": "404", "capacity": 36, "room_type": "Theory", "floor": 4,
         "campus": "Main", "facilities": ["Whiteboard", "Projector"], "specializations": [], "is_available": True},
        {"id": "R406", "room_number": "406", "capacity": 32, "room_type": "Lab", "floor": 4,
         "campus": "Main", "facilities": ["Computers", "Projector", "Multimedia Equipment"],
         "specializations": ["ICT", "Programming", "Multimedia"], "is_available": True},
        {"id": "R407", "room_number": "407", "capacity": 32, "room_type": "Theory", "floor": 4,
         "campus": "Main", "facilities": ["Whiteboard", "Projector"], "specializations": [], "is_available": True},
        # 5TH FLOOR
        {"id": "R501", "room_number": "501", "capacity": 40, "room_type": "Theory", "floor": 5,
         "campus": "Main", "facilities": ["Whiteboard", "Projector"], "specializations": [], "is_available": True},
        {"id": "R502", "room_number": "502", "capacity": 56, "room_type": "Theory", "floor": 5,
         "campus": "Main", "facilities": ["Whiteboard", "Projector", "Sound System"], "specializations": [], "is_available": True},
        {"id": "R503", "room_number": "503", "capacity": 32, "room_type": "Theory", "floor": 5,
         "campus": "Main", "facilities": ["Whiteboard", "Projector"], "specializations": [], "is_available": True},
        {"id": "R504", "room_number": "504", "capacity": 50, "room_type": "Theory", "floor": 5,
         "campus": "Main", "facilities": ["Whiteboard", "Projector"], "specializations": [], "is_available": True},
        {"id": "R505", "room_number": "505", "capacity": 56, "room_type": "Lab", "floor": 5,
         "campus": "Main", "facilities": ["Computers", "Security Equipment", "Projector"],
         "specializations": ["Networking & Cyber Security"], "is_available": True},
        {"id": "R506", "room_number": "506", "capacity": 25, "room_type": "Lab", "floor": 5,
         "campus": "Main", "facilities": ["Computers", "AI Tools", "ML Tools", "Projector"],
         "specializations": ["AI & ML", "ICT & Programming"], "is_available": True},
        {"id": "R507", "room_number": "507", "capacity": 36, "room_type": "Theory", "floor": 5,
         "campus": "Main", "facilities": ["Whiteboard", "Projector"], "specializations": [], "is_available": True},
        # 6TH FLOOR
        {"id": "R601", "room_number": "601", "capacity": 88, "room_type": "Lab", "floor": 6,
         "campus": "Main", "facilities": ["Computers", "Projector"], "specializations": ["ICT & Programming"], "is_available": True},
        {"id": "R602", "room_number": "602", "capacity": 80, "room_type": "Theory", "floor": 6,
         "campus": "Main", "facilities": ["Whiteboard", "Projector", "Sound System"], "specializations": [], "is_available": True},
        {"id": "R605", "room_number": "605", "capacity": 32, "room_type": "Theory", "floor": 6,
         "campus": "Main", "facilities": ["Whiteboard", "Projector"], "specializations": [], "is_available": True},
        {"id": "R604", "room_number": "604", "capacity": 15, "room_type": "Lab", "floor": 6,
         "campus": "Main", "facilities": ["Multimedia Equipment", "Editing Stations", "Cameras"],
         "specializations": ["Multimedia Studio"], "is_available": True},
        # 7TH FLOOR
        {"id": "R700", "room_number": "700", "capacity": 500, "room_type": "Theory", "floor": 7,
         "campus": "Main", "facilities": ["Projector", "Sound System", "Stage"], "specializations": [], "is_available": True},
        # NEW EXTENSION BLOCK
        {"id": "RB101", "room_number": "B-101", "capacity": 30, "room_type": "Theory", "floor": 1,
         "campus": "Main", "facilities": ["Whiteboard", "Projector"], "specializations": [], "is_available": True},
        {"id": "RB201", "room_number": "B-201", "capacity": 70, "room_type": "Theory", "floor": 2,
         "campus": "Main", "facilities": ["Whiteboard", "Projector", "Sound System"], "specializations": [], "is_available": True},
        {"id": "RB202", "room_number": "B-202", "capacity": 30, "room_type": "Theory", "floor": 2,
         "campus": "Main", "facilities": ["Whiteboard", "Projector"], "specializations": [], "is_available": True},
        {"id": "RB301", "room_number": "B-301", "capacity": 70, "room_type": "Theory", "floor": 3,
         "campus": "Main", "facilities": ["Whiteboard", "Projector", "Sound System"], "specializations": [], "is_available": True},
        {"id": "RB302", "room_number": "B-302", "capacity": 30, "room_type": "Theory", "floor": 3,
         "campus": "Main", "facilities": ["Whiteboard", "Projector"], "specializations": [], "is_available": True},
    ]
    
    return clean_rooms


def seed_rooms_to_db(db):
    """
    Seed all room data to MongoDB database
    
    Args:
        db: MongoDB database instance
    """
    rooms_data = get_all_rooms()
    
    # Clear existing rooms
    db.rooms.delete_many({})
    
    # Insert all rooms
    result = db.rooms.insert_many(rooms_data)
    
    print(f"✅ Successfully seeded {len(result.inserted_ids)} rooms")
    print(f"   - Main Campus: {sum(1 for r in rooms_data if r['campus'] == 'Main')}")
    print(f"   - Theory Rooms: {sum(1 for r in rooms_data if r['room_type'] == 'Theory')}")
    print(f"   - Labs: {sum(1 for r in rooms_data if r['room_type'] == 'Lab')}")
    
    return result


def get_room_statistics():
    """Get statistics about the room inventory"""
    rooms_data = get_all_rooms()
    
    stats = {
        'total_rooms': len(rooms_data),
        'by_campus': {},
        'by_type': {
            'Lab': sum(1 for r in rooms_data if r['room_type'] == 'Lab'),
            'Theory': sum(1 for r in rooms_data if r['room_type'] == 'Theory')
        },
        'capacity_range': {
            'min': min(r['capacity'] for r in rooms_data),
            'max': max(r['capacity'] for r in rooms_data),
            'avg': sum(r['capacity'] for r in rooms_data) / len(rooms_data),
            'total': sum(r['capacity'] for r in rooms_data)
        },
        'specialized_labs': sum(1 for r in rooms_data if r['specializations'])
    }
    
    # Count by campus
    for room in rooms_data:
        campus = room.get('campus', 'Unknown')
        stats['by_campus'][campus] = stats['by_campus'].get(campus, 0) + 1
    
    # Count by building (if building field exists)
    for room in rooms_data:
        if 'building' in room:
            building = room['building']
            stats['by_building'][building] = stats['by_building'].get(building, 0) + 1
    
    return stats


if __name__ == '__main__':
    # Display statistics
    stats = get_room_statistics()
    
    print("\n" + "="*60)
    print("ISBAT ROOM INVENTORY STATISTICS")
    print("="*60)
    print(f"\n📊 Total Rooms: {stats['total_rooms']}")
    
    print(f"\n🏢 By Campus:")
    for campus, count in stats['by_campus'].items():
        print(f"   - {campus}: {count} rooms")
    
    if stats['by_building']:
        print(f"\n🏛️ By Building:")
        for building, count in stats['by_building'].items():
            print(f"   - {building}: {count} rooms")
    
    print(f"\n🚪 By Type:")
    for room_type, count in stats['by_type'].items():
        print(f"   - {room_type}: {count} rooms")
    
    print(f"\n👥 Capacity:")
    print(f"   - Minimum: {stats['capacity_range']['min']} seats")
    print(f"   - Maximum: {stats['capacity_range']['max']} seats")
    print(f"   - Average: {stats['capacity_range']['avg']:.1f} seats")
    print(f"   - Total: {stats['capacity_range']['total']} seats")
    
    print(f"\n🔬 Specialized Labs: {stats['specialized_labs']}")
    
    print("\n" + "="*60)
    print("✅ Room data ready for seeding!")
    print("="*60 + "\n")

