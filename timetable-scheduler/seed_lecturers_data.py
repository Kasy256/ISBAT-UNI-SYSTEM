"""Seed lecturer data for ISBAT Timetable System"""

from typing import List, Dict

def get_all_lecturers() -> List[Dict]:
    """
    Get all lecturer data for ISBAT
    
    Returns:
        List of lecturer dictionaries ready for MongoDB insertion
    """
    lecturers = []
    
    # Sample lecturers provided by user + expanded
    lecturers.extend([
        {
            'id': 'L001',
            'name': 'Dr. Jane Achieng',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['CS101', 'CS205'],  # Java Programming, C Programming
            'availability': {
                'MON': ['09:00-11:00'],
                'TUE': ['14:00-16:00']
            },
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L002',
            'name': 'Dr. Peter Ouma',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['CS102', 'CS206'],  # Data Structures, Python Programming
            'availability': {
                'WED': ['10:00-12:00'],
                'THU': ['13:00-15:00']
            },
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L003',
            'name': 'Ms. Alice Nakitende',
            'role': 'Part-Time',
            'faculty': 'Computing',
            'specializations': ['CS103', 'CS207'],  # Database Systems, Web Development
            'availability': {
                'MON': ['13:00-15:00'],
                'FRI': ['09:00-11:00']
            },
            'sessions_per_day': 1,
            'max_weekly_hours': 3
        },
        {
            'id': 'L004',
            'name': 'Dr. Samuel Kato',
            'role': 'Faculty Dean',
            'faculty': 'Computing',
            'specializations': ['CS104', 'CS208'],  # Networking, Cybersecurity
            'availability': {
                'TUE': ['10:00-12:00'],
                'THU': ['14:00-16:00']
            },
            'sessions_per_day': 2,
            'max_weekly_hours': 15
        },
        
        # Additional lecturers to cover all courses
        {
            'id': 'L005',
            'name': 'Dr. Mary Ssemakula',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['CS105', 'CS106', 'CS107'],  # IT Fundamentals, OS, Software Eng
            'availability': None,  # Available all times
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L006',
            'name': 'Mr. David Mukasa',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['CS108', 'CS109', 'CS110'],  # Web Dev, Cybersecurity, Python
            'availability': None,
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L007',
            'name': 'Dr. Grace Nalwoga',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['CS201', 'CS202', 'CS203'],  # Mobile App, Networking II, Data Analytics
            'availability': None,
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L008',
            'name': 'Prof. John Walusimbi',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['CS204', 'CS209', 'CS210'],  # Cloud Computing, AI Basics, Project Mgmt
            'availability': None,
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L009',
            'name': 'Dr. Sarah Namugga',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['CS301', 'CS302', 'CS307'],  # Machine Learning, Big Data, AI Applications
            'availability': None,
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L010',
            'name': 'Mr. Patrick Okello',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['CS303', 'CS304', 'CS305'],  # DevOps, Blockchain, Enterprise Systems
            'availability': None,
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L011',
            'name': 'Dr. Rebecca Namutebi',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['CS306', 'CS308', 'CS309'],  # Capstone, Advanced Networking, Testing
            'availability': None,
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L012',
            'name': 'Ms. Florence Nantongo',
            'role': 'Part-Time',
            'faculty': 'Computing',
            'specializations': ['CS310', 'CS105'],  # IT Governance, IT Fundamentals
            'availability': {
                'MON': ['14:00-16:00'],
                'WED': ['14:00-16:00']
            },
            'sessions_per_day': 1,
            'max_weekly_hours': 3
        },
        
        # Additional backup lecturers
        {
            'id': 'L013',
            'name': 'Dr. James Mugisha',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['CS101', 'CS102', 'CS103'],  # Can teach intro courses
            'availability': None,
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L014',
            'name': 'Ms. Christine Atuhaire',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['CS104', 'CS106', 'CS108'],
            'availability': None,
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L015',
            'name': 'Dr. Moses Kibirige',
            'role': 'Part-Time',
            'faculty': 'Computing',
            'specializations': ['CS201', 'CS301'],
            'availability': {
                'TUE': ['09:00-11:00', '14:00-16:00'],
                'THU': ['09:00-11:00']
            },
            'sessions_per_day': 1,
            'max_weekly_hours': 3
        }
    ])
    
    return lecturers


def seed_lecturers_to_db(db):
    """
    Seed all lecturer data to MongoDB database
    
    Args:
        db: MongoDB database instance
    """
    lecturers_data = get_all_lecturers()
    
    # Clear existing lecturers
    db.lecturers.delete_many({})
    
    # Insert all lecturers
    result = db.lecturers.insert_many(lecturers_data)
    
    print(f"✅ Successfully seeded {len(result.inserted_ids)} lecturers")
    print(f"   - Full-Time: {sum(1 for l in lecturers_data if l['role'] == 'Full-Time')}")
    print(f"   - Part-Time: {sum(1 for l in lecturers_data if l['role'] == 'Part-Time')}")
    print(f"   - Faculty Dean: {sum(1 for l in lecturers_data if l['role'] == 'Faculty Dean')}")
    
    return result


def get_lecturer_statistics():
    """Get statistics about lecturers"""
    lecturers_data = get_all_lecturers()
    
    stats = {
        'total_lecturers': len(lecturers_data),
        'by_role': {
            'Full-Time': sum(1 for l in lecturers_data if l['role'] == 'Full-Time'),
            'Part-Time': sum(1 for l in lecturers_data if l['role'] == 'Part-Time'),
            'Faculty Dean': sum(1 for l in lecturers_data if l['role'] == 'Faculty Dean')
        },
        'by_faculty': {},
        'total_capacity': {
            'max_weekly_hours': sum(l['max_weekly_hours'] for l in lecturers_data),
            'max_daily_sessions': sum(l['sessions_per_day'] * 5 for l in lecturers_data)
        },
        'specializations_count': sum(len(l['specializations']) for l in lecturers_data)
    }
    
    for lecturer in lecturers_data:
        faculty = lecturer['faculty']
        stats['by_faculty'][faculty] = stats['by_faculty'].get(faculty, 0) + 1
    
    return stats


if __name__ == '__main__':
    stats = get_lecturer_statistics()
    
    print("\n" + "="*60)
    print("ISBAT LECTURER STATISTICS")
    print("="*60)
    print(f"\n📊 Total Lecturers: {stats['total_lecturers']}")
    
    print(f"\n👔 By Role:")
    for role, count in stats['by_role'].items():
        print(f"   - {role}: {count}")
    
    print(f"\n🏢 By Faculty:")
    for faculty, count in stats['by_faculty'].items():
        print(f"   - {faculty}: {count}")
    
    print(f"\n📚 Course Coverage:")
    print(f"   - Total Specializations: {stats['specializations_count']}")
    
    print(f"\n⏰ Teaching Capacity:")
    print(f"   - Max Weekly Hours: {stats['total_capacity']['max_weekly_hours']}")
    print(f"   - Max Sessions/Week: {stats['total_capacity']['max_daily_sessions']}")
    
    print("\n" + "="*60)
    print("✅ Lecturer data ready for seeding!")
    print("="*60 + "\n")

