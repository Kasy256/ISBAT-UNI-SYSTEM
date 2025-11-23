"""Seed lecturer data for ISBAT Timetable System based on client-provided data"""

from typing import List, Dict


def get_all_lecturers() -> List[Dict]:
    """
    Get all lecturer data for ISBAT based on client-provided list.
    
    Updated to match exact client data from provided JSON.

    Returns:
        List of lecturer dictionaries ready for MongoDB insertion
    """
    lecturers = [
        {
            'id': 'L001',
            'name': 'KENNETH KATO',
            'role': 'Full-Time',  # Full time in client data
            'faculty': 'Computing',
            'specializations': ['COMP_OFFICE_APP', 'PROG_C'],  # Updated to use combined canonical ID
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L002',
            'name': 'BRAVE AFRICANO',
            'role': 'Full-Time',  # Full time in client data
            'faculty': 'Computing',
            'specializations': ['COMP_ORG_ARCH', 'MOBILE_APP_DEV'],
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L003',
            'name': 'AINEMBABAZI PAMELA',
            'role': 'Part-Time',  # Part time in client data
            'faculty': 'Computing',
            'specializations': ['SOFT_SKILLS'],
            'availability': {
                'MON': ['09:00-11:00', '14:00-16:00'],
                'WED': ['09:00-11:00', '14:00-16:00'],
                'FRI': ['09:00-11:00']
            },
            'sessions_per_day': 2,
            'max_weekly_hours': None
        },
        {
            'id': 'L004',
            'name': 'WANJIRU KAMAMI WILSON',
            'role': 'Full-Time',  # Full time in client data (note: client shows "WANJIRU KAMIAMI WILSON")
            'faculty': 'Computing',
            'specializations': ['MATH_STATS_FOUNDATION'],
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L005',
            'name': 'NASURUDIN KIBWIKA BASHIR',
            'role': 'Full-Time',  # Full time in client data
            'faculty': 'Computing',
            'specializations': ['COMP_HARDWARE_OS', 'OOP_JAVA', 'WEB_TECH', 'SOFTWARE_ENGINEERING', 'PROJECT'],  # Updated to use combined canonical IDs
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L006',
            'name': 'PETER MUHUMUZA',
            'role': 'Full-Time',  # Full time in client data (note: client shows "PETER MUHIMUZA")
            'faculty': 'Computing',
            'specializations': ['DIGITAL_SYSTEMS'],
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L007',
            'name': 'DALLINGTON ASINGWIRE',
            'role': 'Full-Time',  # Full time in client data
            'faculty': 'Computing',
            'specializations': ['DATA_STRUCTURES'],
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L008',
            'name': 'KUKUTLA ALEKYA',
            'role': 'Faculty Dean',  # Dean in client data
            'faculty': 'Computing',
            'specializations': ['DATABASE_MGMT_SYSTEM', 'PYTHON_PROG', 'BUSINESS_INTELLIGENCE'],  # Updated to use combined canonical IDs
            'sessions_per_day': 2,
            'max_weekly_hours': 15
        },
        {
            'id': 'L009',
            'name': 'JIMMY OKELLO OBIRA',
            'role': 'Full-Time',  # Full time in client data
            'faculty': 'Computing',
            'specializations': ['DATA_COMM_NETWORKING'],
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L010',
            'name': 'HENRY MALE KENNETH',
            'role': 'Full-Time',  # Full time in client data
            'faculty': 'Computing',
            'specializations': ['LINUX_ADMIN', 'DEVOPS', 'VIRTUALIZATION_CLOUD'],  # Updated to use combined canonical ID
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L011',
            'name': 'KUMAR THILAK DEVARAJ',
            'role': 'Full-Time',  # Full time in client data
            'faculty': 'Computing',
            'specializations': ['GRAPHICS_MULTIMEDIA'],
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L012',
            'name': 'JUSTIN OPOLOT',
            'role': 'Full-Time',  # Full time in client data
            'faculty': 'Computing',
            'specializations': ['ARTIFICIAL_INTELLIGENCE', 'IOT', 'DIGITAL_MARKETING'],
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L013',
            'name': 'KUMAR UMESH',
            'role': 'Full-Time',  # Full time in client data
            'faculty': 'Computing',
            'specializations': ['ASP_NET'],  # Updated to use combined canonical ID
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L014',
            'name': 'SOLOMON MUGISA',
            'role': 'Part-Time',  # Part time in client data
            'faculty': 'Computing',
            'specializations': ['WEB_DATABASE_SECURITY', 'CYBER_SECURITY_INTRO'],
            'availability': {
                'TUE': ['09:00-11:00', '14:00-16:00'],
                'THU': ['09:00-11:00', '14:00-16:00'],
                'FRI': ['09:00-11:00', '14:00-16:00']
            },
            'sessions_per_day': 2,
            'max_weekly_hours': None
        },
        {
            'id': 'L015',
            'name': 'KUMAR PRADEEP',
            'role': 'Faculty Dean',  # Dean in client data
            'faculty': 'Computing',
            'specializations': ['RESEARCH_PAPER'],
            'sessions_per_day': 2,
            'max_weekly_hours': 15
        },
        {
            'id': 'L016',
            'name': 'DOUGLAS ONENCAN',
            'role': 'Full-Time',  # Full time in client data
            'faculty': 'Computing',
            'specializations': ['GREEN_COMPUTING'],
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L017',
            'name': 'SURVE SAJJAD',
            'role': 'Full-Time',  # Full time in client data
            'faculty': 'Computing',
            'specializations': ['TECH_ENTREPRENEURSHIP'],
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L020',
            'name': 'ANDREW MWANGI',
            'role': 'Full-Time',  # Full time in client data
            'faculty': 'Computing',
            'specializations': ['THEORIES_COMPUTATION'],
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L021',
            'name': 'GRACE MUMBERE',
            'role': 'Full-Time',  # Full time in client data
            'faculty': 'Computing',
            'specializations': ['NEW_PRODUCT_DEV'],
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L022',
            'name': 'JAMES OPIO',
            'role': 'Full-Time',  # Full time in client data
            'faculty': 'Computing',
            'specializations': ['MACHINE_LEARNING'],
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L023',
            'name': 'MARIA CHEN',
            'role': 'Full-Time',  # Full time in client data
            'faculty': 'Computing',
            'specializations': ['DATA_SCIENCE'],
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L024',
            'name': 'ROBERT OUMA',
            'role': 'Full-Time',  # Full time in client data
            'faculty': 'Computing',
            'specializations': ['GAME_PROGRAMMING'],
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L025',
            'name': 'SARAH NAKATO',
            'role': 'Full-Time',  # Full time in client data
            'faculty': 'Computing',
            'specializations': ['COMPILER_DESIGN'],
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
    ]

    return lecturers


def seed_lecturers_to_db(db):
    """
    Seed all lecturer data to MongoDB database

    Args:
        db: MongoDB database instance
    """
    lecturers_data = get_all_lecturers()

    db.lecturers.delete_many({})
    result = db.lecturers.insert_many(lecturers_data)

    print(f"Successfully seeded {len(result.inserted_ids)} lecturers")
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
            'Faculty Dean': sum(1 for l in lecturers_data if l['role'] == 'Faculty Dean'),
        },
        'by_faculty': {},
        'total_capacity': {
            'max_weekly_hours': sum(l.get('max_weekly_hours', 0) or 0 for l in lecturers_data),
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
    print(f"\nTotal Lecturers: {stats['total_lecturers']}")

    print(f"\nBy Role:")
    for role, count in stats['by_role'].items():
        print(f"   - {role}: {count}")

    print(f"\nBy Faculty:")
    for faculty, count in stats['by_faculty'].items():
        print(f"   - {faculty}: {count}")

    print(f"\nCourse Coverage:")
    print(f"   - Total Specializations: {stats['specializations_count']}")

    print(f"\nTeaching Capacity:")
    print(f"   - Max Weekly Hours: {stats['total_capacity']['max_weekly_hours']}")
    print(f"   - Max Sessions/Week: {stats['total_capacity']['max_daily_sessions']}")

    print("\n" + "="*60)
    print("Lecturer data ready for seeding!")
    print("="*60 + "\n")
