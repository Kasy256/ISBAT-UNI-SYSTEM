"""Seed course unit data for ISBAT Timetable System"""

from typing import List, Dict

def get_all_courses() -> List[Dict]:
    """
    Get all course unit data for Computing Faculty programs
    Programs: BSCAIT, BCS, BML&AI, BSCE
    
    Shared courses:
    - CS105 (IT Fundamentals): All programs S1
    - CS110 (Python Programming): All programs S2
    - CS102 (Data Structures): BSCAIT & BCS S1
    - CS103 (Database Systems): BSCAIT & BCS S1
    - CS203 (Data Analytics): BSCAIT & BCS S3
    - CS209 (AI Basics): BSCAIT, BCS, BML&AI S4
    
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
        },
        # Shared: IT Fundamentals (All Computing programs)
        {
            'id': 'CS105_SHARED',
            'code': 'CS105',
            'name': 'IT Fundamentals',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': False,
            'difficulty': 'Easy',
            'is_foundational': True,
            'prerequisites': [],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S1',
            'program': 'BCS'  # Shared with BSCAIT
        },
        {
            'id': 'CS105_BML',
            'code': 'CS105',
            'name': 'IT Fundamentals',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': False,
            'difficulty': 'Easy',
            'is_foundational': True,
            'prerequisites': [],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S1',
            'program': 'BML&AI'
        },
        {
            'id': 'CS105_BSCE',
            'code': 'CS105',
            'name': 'IT Fundamentals',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': False,
            'difficulty': 'Easy',
            'is_foundational': True,
            'prerequisites': [],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S1',
            'program': 'BSCE'
        }
    ])
    
    # ========================================
    # BCS Program Courses (S1)
    # ========================================
    courses.extend([
        {
            'id': 'BCS101',
            'code': 'BCS101',
            'name': 'C++ Programming',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Medium',
            'is_foundational': True,
            'prerequisites': [],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S1',
            'program': 'BCS'
        },
        # Shared: Data Structures (BSCAIT & BCS)
        {
            'id': 'CS102_BCS',
            'code': 'CS102',
            'name': 'Data Structures',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': True,
            'prerequisites': ['BCS101'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S1',
            'program': 'BCS'
        },
        # Shared: Database Systems (BSCAIT & BCS)
        {
            'id': 'CS103_BCS',
            'code': 'CS103',
            'name': 'Database Systems',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Medium',
            'is_foundational': True,
            'prerequisites': [],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S1',
            'program': 'BCS'
        },
        {
            'id': 'BCS104',
            'code': 'BCS104',
            'name': 'Computer Architecture',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Medium',
            'is_foundational': True,
            'prerequisites': [],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S1',
            'program': 'BCS'
        }
    ])
    
    # ========================================
    # BML&AI Program Courses (S1)
    # ========================================
    courses.extend([
        {
            'id': 'ML101',
            'code': 'ML101',
            'name': 'Introduction to AI',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Medium',
            'is_foundational': True,
            'prerequisites': [],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S1',
            'program': 'BML&AI'
        },
        {
            'id': 'ML102',
            'code': 'ML102',
            'name': 'Programming for AI',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Medium',
            'is_foundational': True,
            'prerequisites': [],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S1',
            'program': 'BML&AI'
        },
        {
            'id': 'ML103',
            'code': 'ML103',
            'name': 'Mathematics for AI',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': False,
            'difficulty': 'Hard',
            'is_foundational': True,
            'prerequisites': [],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S1',
            'program': 'BML&AI'
        },
        {
            'id': 'ML104',
            'code': 'ML104',
            'name': 'Statistics for Data Science',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': False,
            'difficulty': 'Medium',
            'is_foundational': True,
            'prerequisites': [],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S1',
            'program': 'BML&AI'
        }
    ])
    
    # ========================================
    # BSCE Program Courses (S1) - Computing-related courses
    # ========================================
    courses.extend([
        {
            'id': 'CE101',
            'code': 'CE101',
            'name': 'Programming Fundamentals',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Medium',
            'is_foundational': True,
            'prerequisites': [],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S1',
            'program': 'BSCE'
        },
        {
            'id': 'CE102',
            'code': 'CE102',
            'name': 'CAD Systems',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Medium',
            'is_foundational': True,
            'prerequisites': [],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S1',
            'program': 'BSCE'
        },
        {
            'id': 'CE103',
            'code': 'CE103',
            'name': 'Engineering Mathematics I',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': False,
            'difficulty': 'Hard',
            'is_foundational': True,
            'prerequisites': [],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S1',
            'program': 'BSCE'
        },
        {
            'id': 'CE104',
            'code': 'CE104',
            'name': 'Introduction to Civil Engineering',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': False,
            'difficulty': 'Easy',
            'is_foundational': True,
            'prerequisites': [],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S1',
            'program': 'BSCE'
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
        },
        # Shared: Python Programming (All Computing programs)
        {
            'id': 'CS110_BCS',
            'code': 'CS110',
            'name': 'Python Programming',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Easy',
            'is_foundational': False,
            'prerequisites': ['BCS101'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S2',
            'program': 'BCS'
        },
        {
            'id': 'CS110_BML',
            'code': 'CS110',
            'name': 'Python Programming',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Easy',
            'is_foundational': False,
            'prerequisites': ['ML102'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S2',
            'program': 'BML&AI'
        },
        {
            'id': 'CS110_BSCE',
            'code': 'CS110',
            'name': 'Python Programming',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Easy',
            'is_foundational': False,
            'prerequisites': ['CE101'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S2',
            'program': 'BSCE'
        }
    ])
    
    # ========================================
    # BCS Program Courses (S2)
    # ========================================
    courses.extend([
        {
            'id': 'BCS201',
            'code': 'BCS201',
            'name': 'System Programming',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['BCS101', 'BCS104'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S2',
            'program': 'BCS'
        },
        {
            'id': 'BCS202',
            'code': 'BCS202',
            'name': 'Software Design Patterns',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': False,
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['CS102'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S2',
            'program': 'BCS'
        },
        {
            'id': 'BCS203',
            'code': 'BCS203',
            'name': 'Web Technologies',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['CS103'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S2',
            'program': 'BCS'
        },
        {
            'id': 'BCS204',
            'code': 'BCS204',
            'name': 'Network Programming',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['BCS201'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S2',
            'program': 'BCS'
        }
    ])
    
    # ========================================
    # BML&AI Program Courses (S2)
    # ========================================
    courses.extend([
        {
            'id': 'ML201',
            'code': 'ML201',
            'name': 'Linear Algebra for ML',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': False,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['ML103'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S2',
            'program': 'BML&AI'
        },
        {
            'id': 'ML202',
            'code': 'ML202',
            'name': 'Data Science Fundamentals',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['ML104', 'CS110'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S2',
            'program': 'BML&AI'
        },
        {
            'id': 'ML203',
            'code': 'ML203',
            'name': 'Data Visualization',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['CS110'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S2',
            'program': 'BML&AI'
        },
        {
            'id': 'ML204',
            'code': 'ML204',
            'name': 'Probability for ML',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': False,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['ML104'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S2',
            'program': 'BML&AI'
        }
    ])
    
    # ========================================
    # BSCE Program Courses (S2)
    # ========================================
    courses.extend([
        {
            'id': 'CE201',
            'code': 'CE201',
            'name': 'Structural Analysis Basics',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': False,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['CE103'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S2',
            'program': 'BSCE'
        },
        {
            'id': 'CE202',
            'code': 'CE202',
            'name': 'Engineering Software Applications',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['CS110'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S2',
            'program': 'BSCE'
        },
        {
            'id': 'CE203',
            'code': 'CE203',
            'name': 'Materials Science',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['CE103'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S2',
            'program': 'BSCE'
        },
        {
            'id': 'CE204',
            'code': 'CE204',
            'name': 'Surveying',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': [],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S2',
            'program': 'BSCE'
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
        },
        # Shared: Data Analytics (BSCAIT & BCS)
        {
            'id': 'CS203_BCS',
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
            'program': 'BCS'
        }
    ])
    
    # ========================================
    # BCS Program Courses (S3)
    # ========================================
    courses.extend([
        {
            'id': 'BCS301',
            'code': 'BCS301',
            'name': 'Advanced Algorithms',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['CS102'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S3',
            'program': 'BCS'
        },
        {
            'id': 'BCS302',
            'code': 'BCS302',
            'name': 'Compiler Design',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['BCS201', 'CS102'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S3',
            'program': 'BCS'
        },
        {
            'id': 'BCS303',
            'code': 'BCS303',
            'name': 'Distributed Systems',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['BCS204'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S3',
            'program': 'BCS'
        },
        {
            'id': 'BCS304',
            'code': 'BCS304',
            'name': 'Software Quality Assurance',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': False,
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['BCS202'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S3',
            'program': 'BCS'
        }
    ])
    
    # ========================================
    # BML&AI Program Courses (S3)
    # ========================================
    courses.extend([
        {
            'id': 'ML301',
            'code': 'ML301',
            'name': 'Machine Learning Basics',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['ML201', 'ML202'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S3',
            'program': 'BML&AI'
        },
        {
            'id': 'ML302',
            'code': 'ML302',
            'name': 'Deep Learning Fundamentals',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['ML301'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S3',
            'program': 'BML&AI'
        },
        {
            'id': 'ML303',
            'code': 'ML303',
            'name': 'Natural Language Processing',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['ML301'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S3',
            'program': 'BML&AI'
        },
        {
            'id': 'ML304',
            'code': 'ML304',
            'name': 'Computer Vision Basics',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['ML302'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S3',
            'program': 'BML&AI'
        }
    ])
    
    # ========================================
    # BSCE Program Courses (S3)
    # ========================================
    courses.extend([
        {
            'id': 'CE301',
            'code': 'CE301',
            'name': 'Concrete Technology',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['CE203'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S3',
            'program': 'BSCE'
        },
        {
            'id': 'CE302',
            'code': 'CE302',
            'name': 'Geotechnical Engineering',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['CE201'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S3',
            'program': 'BSCE'
        },
        {
            'id': 'CE303',
            'code': 'CE303',
            'name': 'Structural Design I',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': False,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['CE201'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S3',
            'program': 'BSCE'
        },
        {
            'id': 'CE304',
            'code': 'CE304',
            'name': 'Fluid Mechanics',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['CE103'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S3',
            'program': 'BSCE'
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
        },
        # Shared: AI Basics (BSCAIT, BCS, BML&AI)
        {
            'id': 'CS209_BCS',
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
            'program': 'BCS'
        },
        {
            'id': 'CS209_BML',
            'code': 'CS209',
            'name': 'AI Basics',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['ML302'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S4',
            'program': 'BML&AI'
        }
    ])
    
    # ========================================
    # BCS Program Courses (S4)
    # ========================================
    courses.extend([
        {
            'id': 'BCS401',
            'code': 'BCS401',
            'name': 'Operating Systems Design',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['BCS302'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S4',
            'program': 'BCS'
        },
        {
            'id': 'BCS402',
            'code': 'BCS402',
            'name': 'Computer Graphics',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['BCS301'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S4',
            'program': 'BCS'
        },
        {
            'id': 'BCS403',
            'code': 'BCS403',
            'name': 'Parallel Computing',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['BCS303'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S4',
            'program': 'BCS'
        },
        {
            'id': 'BCS404',
            'code': 'BCS404',
            'name': 'Software Project Management',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': False,
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['BCS202'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S4',
            'program': 'BCS'
        }
    ])
    
    # ========================================
    # BML&AI Program Courses (S4)
    # ========================================
    courses.extend([
        {
            'id': 'ML401',
            'code': 'ML401',
            'name': 'Advanced Machine Learning',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['ML301'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S4',
            'program': 'BML&AI'
        },
        {
            'id': 'ML402',
            'code': 'ML402',
            'name': 'Reinforcement Learning',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['ML302'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S4',
            'program': 'BML&AI'
        },
        {
            'id': 'ML403',
            'code': 'ML403',
            'name': 'Advanced NLP',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['ML303'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S4',
            'program': 'BML&AI'
        },
        {
            'id': 'ML404',
            'code': 'ML404',
            'name': 'Advanced Computer Vision',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['ML304'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S4',
            'program': 'BML&AI'
        }
    ])
    
    # ========================================
    # BSCE Program Courses (S4)
    # ========================================
    courses.extend([
        {
            'id': 'CE401',
            'code': 'CE401',
            'name': 'Highway Engineering',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': False,
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['CE204'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S4',
            'program': 'BSCE'
        },
        {
            'id': 'CE402',
            'code': 'CE402',
            'name': 'Water Resources Engineering',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['CE304'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S4',
            'program': 'BSCE'
        },
        {
            'id': 'CE403',
            'code': 'CE403',
            'name': 'Structural Design II',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': False,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['CE303'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S4',
            'program': 'BSCE'
        },
        {
            'id': 'CE404',
            'code': 'CE404',
            'name': 'Construction Management',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': False,
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['CE103'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S4',
            'program': 'BSCE'
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
    
    # ========================================
    # BCS Program Courses (S5)
    # ========================================
    courses.extend([
        {
            'id': 'BCS501',
            'code': 'BCS501',
            'name': 'Information Security',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['BCS303'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S5',
            'program': 'BCS'
        },
        {
            'id': 'BCS502',
            'code': 'BCS502',
            'name': 'Mobile Computing',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['BCS203'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S5',
            'program': 'BCS'
        },
        {
            'id': 'BCS503',
            'code': 'BCS503',
            'name': 'Cloud Computing Systems',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['BCS403'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S5',
            'program': 'BCS'
        },
        {
            'id': 'BCS504',
            'code': 'BCS504',
            'name': 'Database Administration',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['CS103'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S5',
            'program': 'BCS'
        }
    ])
    
    # ========================================
    # BML&AI Program Courses (S5)
    # ========================================
    courses.extend([
        {
            'id': 'ML501',
            'code': 'ML501',
            'name': 'Deep Learning Applications',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['ML302', 'ML401'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S5',
            'program': 'BML&AI'
        },
        {
            'id': 'ML502',
            'code': 'ML502',
            'name': 'Neural Networks',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['ML302'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S5',
            'program': 'BML&AI'
        },
        {
            'id': 'ML503',
            'code': 'ML503',
            'name': 'Big Data Analytics',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['ML202', 'CS203'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S5',
            'program': 'BML&AI'
        },
        {
            'id': 'ML504',
            'code': 'ML504',
            'name': 'AI Ethics and Governance',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': False,
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['CS209'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S5',
            'program': 'BML&AI'
        }
    ])
    
    # ========================================
    # BSCE Program Courses (S5)
    # ========================================
    courses.extend([
        {
            'id': 'CE501',
            'code': 'CE501',
            'name': 'Structural Engineering',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': False,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['CE403'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S5',
            'program': 'BSCE'
        },
        {
            'id': 'CE502',
            'code': 'CE502',
            'name': 'Environmental Engineering',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['CE402'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S5',
            'program': 'BSCE'
        },
        {
            'id': 'CE503',
            'code': 'CE503',
            'name': 'Transportation Engineering',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': False,
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['CE401'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S5',
            'program': 'BSCE'
        },
        {
            'id': 'CE504',
            'code': 'CE504',
            'name': 'Project Management for Engineers',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': False,
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['CE404'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S5',
            'program': 'BSCE'
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
    
    # ========================================
    # BCS Program Courses (S6)
    # ========================================
    courses.extend([
        {
            'id': 'BCS601',
            'code': 'BCS601',
            'name': 'Capstone Project',
            'weekly_hours': 6,
            'credits': 6,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['BCS401', 'BCS402'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S6',
            'program': 'BCS'
        },
        {
            'id': 'BCS602',
            'code': 'BCS602',
            'name': 'Advanced System Design',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['BCS401'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S6',
            'program': 'BCS'
        },
        {
            'id': 'BCS603',
            'code': 'BCS603',
            'name': 'Enterprise Architecture',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': False,
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['BCS503'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S6',
            'program': 'BCS'
        },
        {
            'id': 'BCS604',
            'code': 'BCS604',
            'name': 'IT Professional Practice',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': False,
            'difficulty': 'Easy',
            'is_foundational': False,
            'prerequisites': ['BCS404'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S6',
            'program': 'BCS'
        }
    ])
    
    # ========================================
    # BML&AI Program Courses (S6)
    # ========================================
    courses.extend([
        {
            'id': 'ML601',
            'code': 'ML601',
            'name': 'AI Capstone Project',
            'weekly_hours': 6,
            'credits': 6,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['ML501', 'ML502'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S6',
            'program': 'BML&AI'
        },
        {
            'id': 'ML602',
            'code': 'ML602',
            'name': 'Advanced AI Systems',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['ML501'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S6',
            'program': 'BML&AI'
        },
        {
            'id': 'ML603',
            'code': 'ML603',
            'name': 'AI Deployment and Production',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['ML503'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S6',
            'program': 'BML&AI'
        },
        {
            'id': 'ML604',
            'code': 'ML604',
            'name': 'Research Methods in AI',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': False,
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['ML504'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S6',
            'program': 'BML&AI'
        }
    ])
    
    # ========================================
    # BSCE Program Courses (S6)
    # ========================================
    courses.extend([
        {
            'id': 'CE601',
            'code': 'CE601',
            'name': 'Capstone Design Project',
            'weekly_hours': 6,
            'credits': 6,
            'is_lab': True,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['CE501', 'CE502'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S6',
            'program': 'BSCE'
        },
        {
            'id': 'CE602',
            'code': 'CE602',
            'name': 'Advanced Structural Design',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': False,
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['CE501'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'semester': 'S6',
            'program': 'BSCE'
        },
        {
            'id': 'CE603',
            'code': 'CE603',
            'name': 'Infrastructure Planning',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': False,
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['CE503'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S6',
            'program': 'BSCE'
        },
        {
            'id': 'CE604',
            'code': 'CE604',
            'name': 'Professional Engineering Practice',
            'weekly_hours': 4,
            'credits': 4,
            'is_lab': False,
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['CE504'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'semester': 'S6',
            'program': 'BSCE'
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

