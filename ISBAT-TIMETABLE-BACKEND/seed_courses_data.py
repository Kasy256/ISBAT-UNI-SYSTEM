"""Seed course unit data for ISBAT Timetable System - UPDATED WITH CLIENT SUBJECT NAMES"""

from typing import List, Dict

def get_all_courses() -> List[Dict]:
    """
    Get all course unit data for Computing Faculty programs at ISBAT University Kampala
    Programs: BSCAIT, BCS
    All semesters S1-S6
    
    Subject Structure:
    - All subjects have standardized weekly_hours: 4
    - preferred_term is MANDATORY and must be set for all subjects (Term 1 or Term 2)
      * Frontend will require this field to be filled
      * Term splitting is based ONLY on preferred_term from database
      * Canonical alignment may override preferred_term for merging equivalent subjects
    - preferred_room_type is REQUIRED and must be set for all subjects:
      * "Lab" for practical/lab subjects
      * "Theory" for theory subjects
      * Users can set this in the UI when creating/editing subjects
    - Theory/Practical pairs are linked via course_group field:
      * Subjects with same course_group must be in same term
      * They are considered as ONE course unit for term splitting
      * Example: Programming in C Theory + Practical = 1 course unit
    
    Returns:
        List of subject dictionaries ready for MongoDB insertion
    """
    subjects = []
    
    # ========================================
    # BSCAIT SUBJECTS
    # ========================================
    
    # Semester 1
    subjects.extend([
        {
            'id': 'BIT1101',
            'code': 'BIT1101',
            'name': 'Fundamentals of Computer and Office Applications - Theory',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Theory',
            'difficulty': 'Easy',
            'is_foundational': True,
            'prerequisites': [],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'course_group': 'BIT1101_GROUP',
            'semester': 'S1',
            'program': 'BSCAIT'
        },
        {
            'id': 'BIT1102',
            'code': 'BIT1102',
            'name': 'Computer Organization and Architecture',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Lab',
            'difficulty': 'Medium',
            'is_foundational': True,
            'prerequisites': [],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'course_group': None,
            'semester': 'S1',
            'program': 'BSCAIT'
        },
        {
            'id': 'BIT1103',
            'code': 'BIT1103',
            'name': 'Programming in C - Theory',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Theory',
            'difficulty': 'Medium',
            'is_foundational': True,
            'prerequisites': [],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'course_group': 'BIT1103_GROUP',
            'semester': 'S1',
            'program': 'BSCAIT'
        },
        {
            'id': 'BIT1104',
            'code': 'BIT1104',
            'name': 'Soft Skills Development',
            'weekly_hours': 4,
            'credits': 2,
            'preferred_room_type': 'Theory',
            'difficulty': 'Easy',
            'is_foundational': True,
            'prerequisites': [],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'course_group': None,
            'semester': 'S1',
            'program': 'BSCAIT'
        },
        {
            'id': 'BIT1105',
            'code': 'BIT1105',
            'name': 'Foundation of Mathematics & Statistics',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Theory',
            'difficulty': 'Medium',
            'is_foundational': True,
            'prerequisites': [],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'course_group': None,
            'semester': 'S1',
            'program': 'BSCAIT'
        },
        {
            'id': 'BIT1106',
            'code': 'BIT1106',
            'name': 'Fundamentals of Computer and Office Applications -- Practical',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Lab',
            'difficulty': 'Easy',
            'is_foundational': True,
            'prerequisites': [],
            'corequisites': ['BIT1101'],
            'preferred_term': 'Term 2',
            'course_group': 'BIT1101_GROUP',
            'semester': 'S1',
            'program': 'BSCAIT'
        },
        {
            'id': 'BIT1107',
            'code': 'BIT1107',
            'name': 'Programming in C - Practical',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Lab',
            'difficulty': 'Medium',
            'is_foundational': True,
            'prerequisites': [],
            'corequisites': ['BIT1103'],
            'preferred_term': 'Term 1',
            'course_group': 'BIT1103_GROUP',
            'semester': 'S1',
            'program': 'BSCAIT'
        }
    ])
    
    # Semester 2
    subjects.extend([
        {
            'id': 'BIT1208',
            'code': 'BIT1208',
            'name': 'Object Oriented Programming Using JAVA - Theory',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Theory',
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['BIT1103', 'BIT1107'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'course_group': 'BIT1208_GROUP',
            'semester': 'S2',
            'program': 'BSCAIT'
        },
        {
            'id': 'BIT1209',
            'code': 'BIT1209',
            'name': 'Fundamentals of Digital Systems',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Lab',
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['BIT1102'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'course_group': None,
            'semester': 'S2',
            'program': 'BSCAIT'
        },
        {
            'id': 'BIT1210',
            'code': 'BIT1210',
            'name': 'Data Structures and Algorithms',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Lab',
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['BIT1103', 'BIT1107'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'course_group': None,
            'semester': 'S2',
            'program': 'BSCAIT'
        },
        {
            'id': 'BIT1211',
            'code': 'BIT1211',
            'name': 'Computer Hardware and Operating Systems',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Lab',
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['BIT1102'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'course_group': None,
            'semester': 'S2',
            'program': 'BSCAIT'
        },
        {
            'id': 'BIT1212',
            'code': 'BIT1212',
            'name': 'Database Management System - Theory',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Theory',
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['BIT1102'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'course_group': 'BIT1212_GROUP',
            'semester': 'S2',
            'program': 'BSCAIT'
        },
        {
            'id': 'BIT1213',
            'code': 'BIT1213',
            'name': 'Object Oriented Programming Using JAVA – Practical',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Lab',
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': [],
            'corequisites': ['BIT1208'],
            'preferred_term': 'Term 1',
            'course_group': 'BIT1208_GROUP',
            'semester': 'S2',
            'program': 'BSCAIT'
        },
        {
            'id': 'BIT1214',
            'code': 'BIT1214',
            'name': 'Database Management System -Practical',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Lab',
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': [],
            'corequisites': ['BIT1212'],
            'preferred_term': 'Term 2',
            'course_group': 'BIT1212_GROUP',
            'semester': 'S2',
            'program': 'BSCAIT'
        }
    ])
    
    # Semester 3
    subjects.extend([
        {
            'id': 'BIT2115',
            'code': 'BIT2115',
            'name': 'Web Technology- Theory',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Theory',
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['BIT1208', 'BIT1213'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'course_group': 'BIT2115_GROUP',
            'semester': 'S3',
            'program': 'BSCAIT'
        },
        {
            'id': 'BIT2116',
            'code': 'BIT2116',
            'name': 'Data Communication & Networking',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Lab',
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['BIT1211'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'course_group': None,
            'semester': 'S3',
            'program': 'BSCAIT'
        },
        {
            'id': 'BIT2117',
            'code': 'BIT2117',
            'name': 'Software Engineering & Project Management',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Theory',
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['BIT1210'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'course_group': None,
            'semester': 'S3',
            'program': 'BSCAIT'
        },
        {
            'id': 'BIT2118',
            'code': 'BIT2118',
            'name': 'Linux Administration -Theory',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Theory',
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['BIT1211'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'course_group': 'BIT2118_GROUP',
            'semester': 'S3',
            'program': 'BSCAIT'
        },
        {
            'id': 'BIT2119',
            'code': 'BIT2119',
            'name': 'Graphics and Multimedia Systems',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Lab',
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['BIT1208'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'course_group': None,
            'semester': 'S3',
            'program': 'BSCAIT'
        },
        {
            'id': 'BIT2120',
            'code': 'BIT2120',
            'name': 'Web Technology- Practical',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Lab',
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': [],
            'corequisites': ['BIT2115'],
            'preferred_term': 'Term 1',
            'course_group': 'BIT2115_GROUP',
            'semester': 'S3',
            'program': 'BSCAIT'
        },
        {
            'id': 'BIT2121',
            'code': 'BIT2121',
            'name': 'Linux Administration - Practical',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Lab',
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': [],
            'corequisites': ['BIT2118'],
            'preferred_term': 'Term 2',
            'course_group': 'BIT2118_GROUP',
            'semester': 'S3',
            'program': 'BSCAIT'
        }
    ])
    
    # Semester 4
    subjects.extend([
        {
            'id': 'BIT2222',
            'code': 'BIT2222',
            'name': 'Python Programming-Theory',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Theory',
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['BIT1208'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'course_group': 'BIT2222_GROUP',
            'semester': 'S4',
            'program': 'BSCAIT'
        },
        {
            'id': 'BIT2223',
            'code': 'BIT2223',
            'name': 'Artificial Intelligence',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Lab',
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['BIT1210'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'course_group': None,
            'semester': 'S4',
            'program': 'BSCAIT'
        },
        {
            'id': 'BIT2224',
            'code': 'BIT2224',
            'name': 'Internet of Things',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Lab',
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['BIT2116'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'course_group': None,
            'semester': 'S4',
            'program': 'BSCAIT'
        },
        {
            'id': 'BIT2225',
            'code': 'BIT2225',
            'name': 'Virtualization and Cloud Computing -Theory',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Theory',
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['BIT2116'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'course_group': 'BIT2225_GROUP',
            'semester': 'S4',
            'program': 'BSCAIT'
        },
        {
            'id': 'BIT2226',
            'code': 'BIT2226',
            'name': 'DEVOPS',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Lab',
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['BIT2117', 'BIT2121'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'course_group': None,
            'semester': 'S4',
            'program': 'BSCAIT'
        },
        {
            'id': 'BIT2227',
            'code': 'BIT2227',
            'name': 'Python Programming-Practical',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Lab',
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': [],
            'corequisites': ['BIT2222'],
            'preferred_term': 'Term 1',
            'course_group': 'BIT2222_GROUP',
            'semester': 'S4',
            'program': 'BSCAIT'
        },
        {
            'id': 'BIT2228',
            'code': 'BIT2228',
            'name': 'Virtualization and Cloud Computing - Practical',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Lab',
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': [],
            'corequisites': ['BIT2225'],
            'preferred_term': 'Term 2',
            'course_group': 'BIT2225_GROUP',
            'semester': 'S4',
            'program': 'BSCAIT'
        }
    ])
    
    # Semester 5
    subjects.extend([
        {
            'id': 'BIT3129',
            'code': 'BIT3129',
            'name': 'Programming in ASP.NET Core Using C# - Theory',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Theory',
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['BIT1208', 'BIT1212'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'course_group': 'BIT3129_GROUP',
            'semester': 'S5',
            'program': 'BSCAIT'
        },
        {
            'id': 'BIT3130',
            'code': 'BIT3130',
            'name': 'Business Intelligence and Analytics',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Lab',
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['BIT1212', 'BIT1214'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'course_group': None,
            'semester': 'S5',
            'program': 'BSCAIT'
        },
        {
            'id': 'BIT3131',
            'code': 'BIT3131',
            'name': 'Mobile Application Development Using Android Technology - Theory',
            'weekly_hours': 4,
            'credits': 3,
            'preferred_room_type': 'Theory',
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['BIT1208', 'BIT2115'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'course_group': 'BIT3131_GROUP',
            'semester': 'S5',
            'program': 'BSCAIT'
        },
        {
            'id': 'BIT3132',
            'code': 'BIT3132',
            'name': 'Web and Database Security',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Lab',
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['BIT1212', 'BIT2115'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'course_group': None,
            'semester': 'S5',
            'program': 'BSCAIT'
        },
        {
            'id': 'BIT3133',
            'code': 'BIT3133',
            'name': 'Programming in ASP.NET Core Using C# - Practical',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Lab',
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': [],
            'corequisites': ['BIT3129'],
            'preferred_term': 'Term 1',
            'course_group': 'BIT3129_GROUP',
            'semester': 'S5',
            'program': 'BSCAIT'
        },
        {
            'id': 'BIT3134',
            'code': 'BIT3134',
            'name': 'Mobile Application Development Using Android Technology - Practical',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Lab',
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': [],
            'corequisites': ['BIT3131'],
            'preferred_term': 'Term 2',
            'course_group': 'BIT3131_GROUP',
            'semester': 'S5',
            'program': 'BSCAIT'
        },
        {
            'id': 'BIT3135',
            'code': 'BIT3135',
            'name': 'Research Paper',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Theory',
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': [],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'course_group': None,
            'semester': 'S5',
            'program': 'BSCAIT'
        }
    ])
    
    # Semester 6
    subjects.extend([
        {
            'id': 'BIT3236',
            'code': 'BIT3236',
            'name': 'Green Computing',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Theory',
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['BIT2225'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'course_group': None,
            'semester': 'S6',
            'program': 'BSCAIT'
        },
        {
            'id': 'BIT3237',
            'code': 'BIT3237',
            'name': 'Technological Entrepreneurship',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Theory',
            'difficulty': 'Easy',
            'is_foundational': False,
            'prerequisites': [],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'course_group': None,
            'semester': 'S6',
            'program': 'BSCAIT'
        },
        {
            'id': 'BIT3238',
            'code': 'BIT3238',
            'name': 'Digital Marketing',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Theory',
            'difficulty': 'Easy',
            'is_foundational': False,
            'prerequisites': [],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'course_group': None,
            'semester': 'S6',
            'program': 'BSCAIT'
        },
        {
            'id': 'BIT3239',
            'code': 'BIT3239',
            'name': 'Project',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Lab',
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['BIT3135'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'course_group': None,
            'semester': 'S6',
            'program': 'BSCAIT'
        }
    ])
    
    # ========================================
    # BCS SUBJECTS
    # ========================================
    
    # Semester 1
    subjects.extend([
        {
            'id': 'BCS1101',
            'code': 'BCS1101',
            'name': 'Fundamentals of Computer and Office Applications - Theory',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Theory',
            'difficulty': 'Easy',
            'is_foundational': True,
            'prerequisites': [],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'course_group': None,
            'semester': 'S1',
            'program': 'BCS'
        },
        {
            'id': 'BCS1102',
            'code': 'BCS1102',
            'name': 'Computer Organization and Architecture',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Lab',
            'difficulty': 'Medium',
            'is_foundational': True,
            'prerequisites': [],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'course_group': None,
            'semester': 'S1',
            'program': 'BCS'
        },
        {
            'id': 'BCS1103',
            'code': 'BCS1103',
            'name': 'Programming in C - Theory',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Theory',
            'difficulty': 'Medium',
            'is_foundational': True,
            'prerequisites': [],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'course_group': 'BCS1103_GROUP',
            'semester': 'S1',
            'program': 'BCS'
        },
        {
            'id': 'BCS1104',
            'code': 'BCS1104',
            'name': 'Programming in C - Practical',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Lab',
            'difficulty': 'Medium',
            'is_foundational': True,
            'prerequisites': [],
            'corequisites': ['BCS1103'],
            'preferred_term': 'Term 1',
            'course_group': 'BCS1103_GROUP',
            'semester': 'S1',
            'program': 'BCS'
        },
        {
            'id': 'BCS1105',
            'code': 'BCS1105',
            'name': 'Soft Skills Development',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Theory',
            'difficulty': 'Easy',
            'is_foundational': True,
            'prerequisites': [],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'course_group': None,
            'semester': 'S1',
            'program': 'BCS'
        },
        {
            'id': 'BCS1106',
            'code': 'BCS1106',
            'name': 'Foundation of Mathematics & Statistics',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Theory',
            'difficulty': 'Medium',
            'is_foundational': True,
            'prerequisites': [],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'course_group': None,
            'semester': 'S1',
            'program': 'BCS'
        }
    ])
    
    # Semester 2
    subjects.extend([
        {
            'id': 'BCS1207',
            'code': 'BCS1207',
            'name': 'Fundamentals of Digital Systems',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Lab',
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['BCS1102'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'course_group': None,
            'semester': 'S2',
            'program': 'BCS'
        },
        {
            'id': 'BCS1208',
            'code': 'BCS1208',
            'name': 'Object Oriented Programming Using Java - Theory',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Theory',
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['BCS1103', 'BCS1104'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'course_group': 'BCS1208_GROUP',
            'semester': 'S2',
            'program': 'BCS'
        },
        {
            'id': 'BCS1209',
            'code': 'BCS1209',
            'name': 'Object Oriented Programming Using JAVA – Practical',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Lab',
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': [],
            'corequisites': ['BCS1208'],
            'preferred_term': 'Term 1',
            'course_group': 'BCS1208_GROUP',
            'semester': 'S2',
            'program': 'BCS'
        },
        {
            'id': 'BCS1210',
            'code': 'BCS1210',
            'name': 'Data Structures and Algorithms',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Lab',
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['BCS1103', 'BCS1104'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'course_group': None,
            'semester': 'S2',
            'program': 'BCS'
        },
        {
            'id': 'BCS1211',
            'code': 'BCS1211',
            'name': 'Computer Hardware and Operating Systems',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Lab',
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['BCS1102'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'course_group': None,
            'semester': 'S2',
            'program': 'BCS'
        },
        {
            'id': 'BCS1212',
            'code': 'BCS1212',
            'name': 'Database Management System - Theory',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Theory',
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['BCS1102'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'course_group': None,
            'semester': 'S2',
            'program': 'BCS'
        }
    ])
    
    # Semester 3
    subjects.extend([
        {
            'id': 'BCS2113',
            'code': 'BCS2113',
            'name': 'Introduction to Cyber Security',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Lab',
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['BCS1211'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'course_group': None,
            'semester': 'S3',
            'program': 'BCS'
        },
        {
            'id': 'BCS2114',
            'code': 'BCS2114',
            'name': 'Web Technology- Theory',
            'weekly_hours': 4,
            'credits': 3,
            'preferred_room_type': 'Theory',
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['BCS1208', 'BCS1209'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'course_group': 'BCS2114_GROUP',
            'semester': 'S3',
            'program': 'BCS'
        },
        {
            'id': 'BCS2115',
            'code': 'BCS2115',
            'name': 'Web Technology- Practical',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Lab',
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': [],
            'corequisites': ['BCS2114'],
            'preferred_term': 'Term 1',
            'course_group': 'BCS2114_GROUP',
            'semester': 'S3',
            'program': 'BCS'
        },
        {
            'id': 'BCS2116',
            'code': 'BCS2116',
            'name': 'Artificial Intelligence',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Lab',
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['BCS1210'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'course_group': None,
            'semester': 'S3',
            'program': 'BCS'
        },
        {
            'id': 'BCS2117',
            'code': 'BCS2117',
            'name': 'Graphics and Multimedia Systems',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Lab',
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['BCS1208'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'course_group': None,
            'semester': 'S3',
            'program': 'BCS'
        },
        {
            'id': 'BCS2118',
            'code': 'BCS2118',
            'name': 'Software Engineering & Project Management',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Theory',
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['BCS1210'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'course_group': None,
            'semester': 'S3',
            'program': 'BCS'
        }
    ])
    
    # Semester 4
    subjects.extend([
        {
            'id': 'BCS2219',
            'code': 'BCS2219',
            'name': 'Theories of Computation',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Theory',
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['BCS1210'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'course_group': None,
            'semester': 'S4',
            'program': 'BCS'
        },
        {
            'id': 'BCS2220',
            'code': 'BCS2220',
            'name': 'Python Programming-Theory',
            'weekly_hours': 4,
            'credits': 3,
            'preferred_room_type': 'Theory',
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': ['BCS1208'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'course_group': 'BCS2220_GROUP',
            'semester': 'S4',
            'program': 'BCS'
        },
        {
            'id': 'BCS2221',
            'code': 'BCS2221',
            'name': 'Python Programming-Practical',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Lab',
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': [],
            'corequisites': ['BCS2220'],
            'preferred_term': 'Term 1',
            'course_group': 'BCS2220_GROUP',
            'semester': 'S4',
            'program': 'BCS'
        },
        {
            'id': 'BCS2222',
            'code': 'BCS2222',
            'name': 'Data Science Algorithms and Tools',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Lab',
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['BCS1212', 'BCS2220'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'course_group': None,
            'semester': 'S4',
            'program': 'BCS'
        },
        {
            'id': 'BCS2223',
            'code': 'BCS2223',
            'name': 'Game Programming',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Lab',
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['BCS2117'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'course_group': None,
            'semester': 'S4',
            'program': 'BCS'
        },
        {
            'id': 'BCS2224',
            'code': 'BCS2224',
            'name': 'DEVOPS',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Lab',
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['BCS2118'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'course_group': None,
            'semester': 'S4',
            'program': 'BCS'
        }
    ])
    
    # Semester 5
    subjects.extend([
        {
            'id': 'BCS3125',
            'code': 'BCS3125',
            'name': 'Programming in ASP.NET Core Using C# - Theory',
            'weekly_hours': 4,
            'credits': 3,
            'preferred_room_type': 'Theory',
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['BCS1208', 'BCS1212'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'course_group': 'BCS3125_GROUP',
            'semester': 'S5',
            'program': 'BCS'
        },
        {
            'id': 'BCS3126',
            'code': 'BCS3126',
            'name': 'Programming in ASP.NET Core Using C# - Practical',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Lab',
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': [],
            'corequisites': ['BCS3125'],
            'preferred_term': 'Term 1',
            'course_group': 'BCS3125_GROUP',
            'semester': 'S5',
            'program': 'BCS'
        },
        {
            'id': 'BCS3127',
            'code': 'BCS3127',
            'name': 'Compiler Design',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Lab',
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['BCS2219'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'course_group': None,
            'semester': 'S5',
            'program': 'BCS'
        },
        {
            'id': 'BCS3128',
            'code': 'BCS3128',
            'name': 'Machine Learning',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Lab',
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['BCS2116', 'BCS2222'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'course_group': None,
            'semester': 'S5',
            'program': 'BCS'
        },
        {
            'id': 'BCS3129',
            'code': 'BCS3129',
            'name': 'Mobile Application Development Using Android Technology - Theory',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Theory',
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['BCS1208', 'BCS2114'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'course_group': None,
            'semester': 'S5',
            'program': 'BCS'
        },
        {
            'id': 'BCS3130',
            'code': 'BCS3130',
            'name': 'Research Paper',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Theory',
            'difficulty': 'Medium',
            'is_foundational': False,
            'prerequisites': [],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'course_group': None,
            'semester': 'S5',
            'program': 'BCS'
        }
    ])
    
    # Semester 6
    subjects.extend([
        {
            'id': 'BCS3231',
            'code': 'BCS3231',
            'name': 'New Product Development and Innovation',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Theory',
            'difficulty': 'Easy',
            'is_foundational': False,
            'prerequisites': [],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'course_group': None,
            'semester': 'S6',
            'program': 'BCS'
        },
        {
            'id': 'BCS3232',
            'code': 'BCS3232',
            'name': 'Virtualization and Cloud Computing -Theory',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Theory',
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['BCS2224'],
            'corequisites': [],
            'preferred_term': 'Term 2',
            'course_group': None,
            'semester': 'S6',
            'program': 'BCS'
        },
        {
            'id': 'BCS3233',
            'code': 'BCS3233',
            'name': 'Digital Marketing',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Theory',
            'difficulty': 'Easy',
            'is_foundational': False,
            'prerequisites': [],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'course_group': None,
            'semester': 'S6',
            'program': 'BCS'
        },
        {
            'id': 'BCS3234',
            'code': 'BCS3234',
            'name': 'Project',
            'weekly_hours': 4,
            'credits': 4,
            'preferred_room_type': 'Lab',
            'difficulty': 'Hard',
            'is_foundational': False,
            'prerequisites': ['BCS3130'],
            'corequisites': [],
            'preferred_term': 'Term 1',
            'course_group': None,
            'semester': 'S6',
            'program': 'BCS'
        }
    ])
    
    return subjects


def seed_courses_to_db(db):
    """Seed all subject data to MongoDB database"""
    courses_data = get_all_courses()
    
    # Clear existing subjects
    db.course_units.delete_many({})
    
    # Insert all subjects
    result = db.course_units.insert_many(courses_data)
    
    print(f"✅ Successfully seeded {len(result.inserted_ids)} subjects")
    print(f"   - Lab subjects: {sum(1 for c in courses_data if c.get('preferred_room_type') == 'Lab')}")
    print(f"   - Theory subjects: {sum(1 for c in courses_data if c.get('preferred_room_type') == 'Theory')}")
    print(f"   - Foundational: {sum(1 for c in courses_data if c['is_foundational'])}")
    
    return result


def get_course_statistics():
    """Get statistics about subjects"""
    courses_data = get_all_courses()
    
    stats = {
        'total_courses': len(courses_data),
        'by_semester': {},
        'by_program': {},
        'by_type': {
            'Lab': sum(1 for c in courses_data if c.get('preferred_room_type') == 'Lab'),
            'Theory': sum(1 for c in courses_data if c.get('preferred_room_type') == 'Theory')
        },
        'by_difficulty': {
            'Easy': sum(1 for c in courses_data if c['difficulty'] == 'Easy'),
            'Medium': sum(1 for c in courses_data if c['difficulty'] == 'Medium'),
            'Hard': sum(1 for c in courses_data if c['difficulty'] == 'Hard')
        },
        'total_weekly_hours': sum(c['weekly_hours'] for c in courses_data),
        'total_credits': sum(c['credits'] for c in courses_data)
    }
    
    for subject in courses_data:
        sem = subject['semester']
        prog = subject['program']
        stats['by_semester'][sem] = stats['by_semester'].get(sem, 0) + 1
        stats['by_program'][prog] = stats['by_program'].get(prog, 0) + 1
    
    return stats


if __name__ == '__main__':
    stats = get_course_statistics()
    
    print("\n" + "="*60)
    print("ISBAT SUBJECT STATISTICS - UPDATED WITH CLIENT SUBJECT NAMES")
    print("="*60)
    print(f"\n📚 Total Subjects: {stats['total_courses']}")
    
    print(f"\n📊 By Program:")
    for prog in sorted(stats['by_program'].keys()):
        print(f"   - {prog}: {stats['by_program'][prog]} subjects")
    
    print(f"\n📊 By Semester:")
    for sem in sorted(stats['by_semester'].keys()):
        print(f"   - {sem}: {stats['by_semester'][sem]} subjects")
    
    print(f"\n🔬 By Type:")
    for type_name, count in stats['by_type'].items():
        print(f"   - {type_name}: {count} subjects")
    
    print(f"\n📈 By Difficulty:")
    for diff, count in stats['by_difficulty'].items():
        print(f"   - {diff}: {count} subjects")
    
    print(f"\n⏰ Workload:")
    print(f"   - Total Weekly Hours: {stats['total_weekly_hours']}")
    print(f"   - Total Credits: {stats['total_credits']}")
    
    print("\n" + "="*60)
    print("✅ Subject data ready for seeding!")
    print("="*60 + "\n")