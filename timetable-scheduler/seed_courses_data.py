"""Seed course unit data for ISBAT Timetable System"""

from typing import List, Dict

def get_all_courses() -> List[Dict]:
    """
    Get all course unit data for BSCAIT program
    
    Returns:
        List of course dictionaries ready for MongoDB insertion
    """
    courses = []
    
    # Semester 1 Courses (Split: 3 in Term1, 2 in Term2)
    courses.extend([
        {
            'id': 'CS101',
            'code': 'CS101',
            'name': 'Java Programming',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Medium',
            'is_foundational': True,
            'prerequisites': [],
            'corequisites': [],
            'preferred_term': 'Term 1',  # Term 1
            'semester': 'S1',
            'program': 'BSCAIT'
        },
        {
            'id': 'CS102',
            'code': 'CS102',
            'name': 'Data Structures',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': True,
            'prerequisites': ['CS101'],
            'corequisites': [],
            'preferred_term': 'Term 2',  # Term 2 (needs CS101 first)
            'semester': 'S1',
            'program': 'BSCAIT'
        },
        {
            'id': 'CS103',
            'code': 'CS103',
            'name': 'Database Systems',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Medium',
            'is_foundational': True,
            'prerequisites': [],
            'corequisites': [],
            'preferred_term': 'Term 1',  # Term 1
            'semester': 'S1',
            'program': 'BSCAIT'
        },
        {
            'id': 'CS104',
            'code': 'CS104',
            'name': 'Networking',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Medium',
            'is_foundational': True,
            'prerequisites': [],
            'corequisites': [],
            'preferred_term': 'Term 2',  # Term 2
            'semester': 'S1',
            'program': 'BSCAIT'
        },
        {
            'id': 'CS105',
            'code': 'CS105',
            'name': 'IT Fundamentals',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': False,
            'difficulty': 'Easy',
            'is_foundational': True,
            'prerequisites': [],
            'corequisites': [],
            'preferred_term': 'Term 1',  # Term 1
            'semester': 'S1',
            'program': 'BSCAIT'
        }
    ])
    
    # Semester 2 Courses
    courses.extend([
        {
            'id': 'CS106',
            'code': 'CS106',
            'name': 'Operating Systems',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['CS105'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S2',
            'program': 'BSCAIT'
        },
        {
            'id': 'CS107',
            'code': 'CS107',
            'name': 'Software Engineering',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': False,
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['CS101', 'CS102'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S2',
            'program': 'BSCAIT'
        },
        {
            'id': 'CS108',
            'code': 'CS108',
            'name': 'Web Development',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['CS103'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S2',
            'program': 'BSCAIT'
        },
        {
            'id': 'CS109',
            'code': 'CS109',
            'name': 'Cybersecurity',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['CS104'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S2',
            'program': 'BSCAIT'
        },
        {
            'id': 'CS110',
            'code': 'CS110',
            'name': 'Python Programming',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Easy',
            'is_foundational': False,
            'prerequisites': ['CS101'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S2',
            'program': 'BSCAIT'
        }
    ])
    
    # Semester 3 Courses
    courses.extend([
        {
            'id': 'CS201',
            'code': 'CS201',
            'name': 'Mobile App Development',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['CS101', 'CS110'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S3',
            'program': 'BSCAIT'
        },
        {
            'id': 'CS202',
            'code': 'CS202',
            'name': 'Networking II',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['CS104'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S3',
            'program': 'BSCAIT'
        },
        {
            'id': 'CS203',
            'code': 'CS203',
            'name': 'Data Analytics',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['CS103', 'CS110'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S3',
            'program': 'BSCAIT'
        },
        {
            'id': 'CS204',
            'code': 'CS204',
            'name': 'Cloud Computing',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['CS106', 'CS104'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S3',
            'program': 'BSCAIT'
        },
        {
            'id': 'CS205',
            'code': 'CS205',
            'name': 'C Programming',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['CS101'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S3',
            'program': 'BSCAIT'
        }
    ])
    
    # Semester 4 Courses
    courses.extend([
        {
            'id': 'CS206',
            'code': 'CS206',
            'name': 'Advanced Python',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['CS110'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S4',
            'program': 'BSCAIT'
        },
        {
            'id': 'CS207',
            'code': 'CS207',
            'name': 'Web Development II',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['CS108'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S4',
            'program': 'BSCAIT'
        },
        {
            'id': 'CS208',
            'code': 'CS208',
            'name': 'Cybersecurity II',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['CS109'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S4',
            'program': 'BSCAIT'
        },
        {
            'id': 'CS209',
            'code': 'CS209',
            'name': 'AI Basics',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['CS102', 'CS110'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S4',
            'program': 'BSCAIT'
        },
        {
            'id': 'CS210',
            'code': 'CS210',
            'name': 'Project Management',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': False,
            'difficulty': 'Easy',
            'is_foundational': False,
            'prerequisites': ['CS107'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S4',
            'program': 'BSCAIT'
        }
    ])
    
    # Semester 5 Courses
    courses.extend([
        {
            'id': 'CS301',
            'code': 'CS301',
            'name': 'Machine Learning',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['CS209', 'CS203'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S5',
            'program': 'BSCAIT'
        },
        {
            'id': 'CS302',
            'code': 'CS302',
            'name': 'Big Data',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['CS203', 'CS204'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S5',
            'program': 'BSCAIT'
        },
        {
            'id': 'CS303',
            'code': 'CS303',
            'name': 'DevOps',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['CS106', 'CS204'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S5',
            'program': 'BSCAIT'
        },
        {
            'id': 'CS304',
            'code': 'CS304',
            'name': 'Blockchain',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['CS109', 'CS205'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S5',
            'program': 'BSCAIT'
        },
        {
            'id': 'CS305',
            'code': 'CS305',
            'name': 'Enterprise Systems',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': False,
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['CS103', 'CS107'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S5',
            'program': 'BSCAIT'
        }
    ])
    
    # Semester 6 Courses
    courses.extend([
        {
            'id': 'CS306',
            'code': 'CS306',
            'name': 'Capstone Project',
            'weekly_hours': 6,
            'credits': 6,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['CS301', 'CS302', 'CS303'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S6',
            'program': 'BSCAIT'
        },
        {
            'id': 'CS307',
            'code': 'CS307',
            'name': 'AI Applications',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['CS301'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S6',
            'program': 'BSCAIT'
        },
        {
            'id': 'CS308',
            'code': 'CS308',
            'name': 'Advanced Networking',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['CS202', 'CS208'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S6',
            'program': 'BSCAIT'
        },
        {
            'id': 'CS309',
            'code': 'CS309',
            'name': 'Software Testing',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['CS107'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S6',
            'program': 'BSCAIT'
        },
        {
            'id': 'CS310',
            'code': 'CS310',
            'name': 'IT Governance',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': False,
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['CS210', 'CS305'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S6',
            'program': 'BSCAIT'
        }
    ])
    
    return courses


def seed_courses_to_db(db):
    """Seed all course data to MongoDB database"""
    courses_data = get_all_courses()
    
    # Clear existing courses
    db.course_units.delete_many({})
    
    # Insert all courses
    result = db.course_units.insert_many(courses_data)
    
    print(f"✅ Successfully seeded {len(result.inserted_ids)} courses")
    print(f"   - Lab courses: {sum(1 for c in courses_data if c['is_lab'])}")
    print(f"   - Theory courses: {sum(1 for c in courses_data if not c['is_lab'])}")
    print(f"   - Foundational: {sum(1 for c in courses_data if c['is_foundational'])}")
    
    return result


def get_course_statistics():
    """Get statistics about courses"""
    courses_data = get_all_courses()
    
    stats = {
        'total_courses': len(courses_data),
        'by_semester': {},
        'by_type': {
            'Lab': sum(1 for c in courses_data if c['is_lab']),
            'Theory': sum(1 for c in courses_data if not c['is_lab'])
        },
        'by_difficulty': {
            'Easy': sum(1 for c in courses_data if c['difficulty'] == 'Easy'),
            'Medium': sum(1 for c in courses_data if c['difficulty'] == 'Medium'),
            'Hard': sum(1 for c in courses_data if c['difficulty'] == 'Hard')
        },
        'total_weekly_hours': sum(c['weekly_hours'] for c in courses_data),
        'total_credits': sum(c['credits'] for c in courses_data)
    }
    
    for course in courses_data:
        sem = course['semester']
        stats['by_semester'][sem] = stats['by_semester'].get(sem, 0) + 1
    
    return stats


if __name__ == '__main__':
    stats = get_course_statistics()
    
    print("\n" + "="*60)
    print("ISBAT COURSE STATISTICS")
    print("="*60)
    print(f"\n📚 Total Courses: {stats['total_courses']}")
    
    print(f"\n📊 By Semester:")
    for sem in sorted(stats['by_semester'].keys()):
        print(f"   - {sem}: {stats['by_semester'][sem]} courses")
    
    print(f"\n🔬 By Type:")
    for type_name, count in stats['by_type'].items():
        print(f"   - {type_name}: {count} courses")
    
    print(f"\n📈 By Difficulty:")
    for diff, count in stats['by_difficulty'].items():
        print(f"   - {diff}: {count} courses")
    
    print(f"\n⏰ Workload:")
    print(f"   - Total Weekly Hours: {stats['total_weekly_hours']}")
    print(f"   - Total Credits: {stats['total_credits']}")
    
    print("\n" + "="*60)
    print("✅ Course data ready for seeding!")
    print("="*60 + "\n")

