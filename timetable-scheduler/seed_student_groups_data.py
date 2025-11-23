"""Seed student group data for ISBAT Timetable System - UPDATED WITH REAL COURSES"""

from typing import List, Dict

def get_all_student_groups():

    return [



        # ======================================================

        # BSCAIT-126 (Bachelor of Applied Information Technology)

        # ======================================================



        {

            'id': 'SG_BSCAIT_126_S1',

            'batch': 'BSCAIT-126',

            'program': 'BSCAIT',

            'semester': 'S1',

            'term': None,

            'size': 32,

            'course_units': [

                {'code': 'BIT1101', 'name': 'Basics of Computer and Office Application -Theory'},

                {'code': 'BIT1102', 'name': 'Computer Organization and Architecture'},

                {'code': 'BIT1103', 'name': 'Problem Solving Methodologies Using C - Theory'},

                {'code': 'BIT1104', 'name': 'Soft Skills Development'},

                {'code': 'BIT1105', 'name': 'Mathematics & Statistical Foundation for IT'},

                {'code': 'BIT1106', 'name': 'Basics of Computer and Office Application – Practical'},

                {'code': 'BIT1107', 'name': 'Programming in C - Practical'},

            ],

            'academic_year': '2024/2025',

            'is_active': True

        },



        {

            'id': 'SG_BSCAIT_126_S2',

            'batch': 'BSCAIT-126',

            'program': 'BSCAIT',

            'semester': 'S2',

            'term': None,

            'size': 31,

            'course_units': [

                {'code': 'BIT1208', 'name': 'Object Oriented Programming Using JAVA - Theory'},

                {'code': 'BIT1209', 'name': 'Fundamentals of Digital Systems'},

                {'code': 'BIT1210', 'name': 'Data Structures and Algorithms'},

                {'code': 'BIT1211', 'name': 'Computer Hardware and Operating Systems'},

                {'code': 'BIT1212', 'name': 'RDBMS Using MS-SQL Server - Theory'},

                {'code': 'BIT1213', 'name': 'Object Oriented Programming Using JAVA – Practical'},

                {'code': 'BIT1214', 'name': 'RDBMS Using MS-SQL Server -Practical'},

            ],

            'academic_year': '2024/2025',

            'is_active': True

        },



        {

            'id': 'SG_BSCAIT_126_S3',

            'batch': 'BSCAIT-126',

            'program': 'BSCAIT',

            'semester': 'S3',

            'term': None,

            'size': 30,

            'course_units': [

                {'code': 'BIT2115', 'name': 'Web Design- Theory'},

                {'code': 'BIT2116', 'name': 'Data Communication & Networking'},

                {'code': 'BIT2117', 'name': 'Software Engineering & Project Management'},

                {'code': 'BIT2118', 'name': 'Linux Administration'},

                {'code': 'BIT2119', 'name': 'Graphics and Multimedia Systems'},

                {'code': 'BIT2120', 'name': 'Web Design- Practical'},

                {'code': 'BIT2121', 'name': 'Linux Administration - Practical'},

            ],

            'academic_year': '2024/2025',

            'is_active': True

        },



        {

            'id': 'SG_BSCAIT_126_S4',

            'batch': 'BSCAIT-126',

            'program': 'BSCAIT',

            'semester': 'S4',

            'term': None,

            'size': 29,

            'course_units': [

                {'code': 'BIT2222', 'name': 'Python Programming-Theory'},

                {'code': 'BIT2223', 'name': 'Artificial Intelligence'},

                {'code': 'BIT2224', 'name': 'Internet of Things'},

                {'code': 'BIT2225', 'name': 'Virtualization and Cloud Computing'},

                {'code': 'BIT2226', 'name': 'DevOps'},

                {'code': 'BIT2227', 'name': 'Python Programming-Practical'},

                {'code': 'BIT2228', 'name': 'Virtualization and Cloud Computing - Practical'},

            ],

            'academic_year': '2024/2025',

            'is_active': True

        },



        {

            'id': 'SG_BSCAIT_126_S5',

            'batch': 'BSCAIT-126',

            'program': 'BSCAIT',

            'semester': 'S5',

            'term': None,

            'size': 28,

            'course_units': [

                {'code': 'BIT3129', 'name': 'Programming in ASP.Net Core Using C# - Theory'},

                {'code': 'BIT3130', 'name': 'Business Intelligence and Analytics'},

                {'code': 'BIT3131', 'name': 'Mobile Application Development Using Android Technology - Theory'},

                {'code': 'BIT3132', 'name': 'Web and Database Security'},

                {'code': 'BIT3133', 'name': 'Programming in Asp.Net Core Using C# - Practical'},

                {'code': 'BIT3134', 'name': 'Mobile Application Development Using Android Technology - Practical'},

                {'code': 'BIT3135', 'name': 'Research Paper'},

            ],

            'academic_year': '2024/2025',

            'is_active': True

        },



        {

            'id': 'SG_BSCAIT_126_S6',

            'batch': 'BSCAIT-126',

            'program': 'BSCAIT',

            'semester': 'S6',

            'term': None,

            'size': 27,

            'course_units': [

                {'code': 'BIT3236', 'name': 'Green Computing'},

                {'code': 'BIT3237', 'name': 'Technological Entrepreneurship'},

                {'code': 'BIT3238', 'name': 'Digital Marketing'},

                {'code': 'BIT3239', 'name': 'Project'},

            ],

            'academic_year': '2024/2025',

            'is_active': True

        },



        # ===========================================

        # BCS-126 (Bachelor of Computer Science)

        # ===========================================



        {

            'id': 'SG_BCS_126_S1',

            'batch': 'BCS-126',

            'program': 'BCS',

            'semester': 'S1',

            'term': None,

            'size': 40,

            'course_units': [

                {'code': 'BCS1101', 'name': 'Fundamentals of Computer & Office Applications'},

                {'code': 'BCS1102', 'name': 'Computer Organization and Architecture'},

                {'code': 'BCS1103', 'name': 'Programming in C Theory'},

                {'code': 'BCS1104', 'name': 'Programming in C Practical'},

                {'code': 'BCS1105', 'name': 'Soft Skills Development'},

                {'code': 'BCS1106', 'name': 'Foundation of Mathematics & Statistics'},

            ],

            'academic_year': '2024/2025',

            'is_active': True

        },



        {

            'id': 'SG_BCS_126_S2',

            'batch': 'BCS-126',

            'program': 'BCS',

            'semester': 'S2',

            'term': None,

            'size': 39,

            'course_units': [

                {'code': 'BCS1207', 'name': 'Fundamentals of Digital Systems'},

                {'code': 'BCS1208', 'name': 'Object Oriented Programming Using Java - Theory'},

                {'code': 'BCS1209', 'name': 'Object Oriented Programming Using Java - Practical'},

                {'code': 'BCS1210', 'name': 'Data Structures and Algorithms'},

                {'code': 'BCS1211', 'name': 'Operating Systems'},

                {'code': 'BCS1212', 'name': 'Database Management System'},

            ],

            'academic_year': '2024/2025',

            'is_active': True

        },



        {

            'id': 'SG_BCS_126_S3',

            'batch': 'BCS-126',

            'program': 'BCS',

            'semester': 'S3',

            'term': None,

            'size': 38,

            'course_units': [

                {'code': 'BCS2113', 'name': 'Introduction to Cyber Security'},

                {'code': 'BCS2114', 'name': 'Web Technology- Theory'},

                {'code': 'BCS2115', 'name': 'Web Technology- Practical'},

                {'code': 'BCS2116', 'name': 'Artificial Intelligence'},

                {'code': 'BCS2117', 'name': 'Graphics and Multimedia Systems'},

                {'code': 'BCS2118', 'name': 'Software Engineering and Professional Practice'},

            ],

            'academic_year': '2024/2025',

            'is_active': True

        },



        {

            'id': 'SG_BCS_126_S4',

            'batch': 'BCS-126',

            'program': 'BCS',

            'semester': 'S4',

            'term': None,

            'size': 37,

            'course_units': [

                {'code': 'BCS2219', 'name': 'Theories of Computation'},

                {'code': 'BCS2220', 'name': 'Python Programming-Theory'},

                {'code': 'BCS2221', 'name': 'Python Programming-Practical'},

                {'code': 'BCS2222', 'name': 'Data Science Algorithms and Tools'},

                {'code': 'BCS2223', 'name': 'Game Programming'},

                {'code': 'BCS2224', 'name': 'DEVOPS'},

            ],

            'academic_year': '2024/2025',

            'is_active': True

        },



        {

            'id': 'SG_BCS_126_S5',

            'batch': 'BCS-126',

            'program': 'BCS',

            'semester': 'S5',

            'term': None,

            'size': 36,

            'course_units': [

                {'code': 'BCS3125', 'name': 'Programming in ASP.NET Core Using C# - Theory'},

                {'code': 'BCS3126', 'name': 'Programming in ASP.NET Core Using C# - Practical'},

                {'code': 'BCS3127', 'name': 'Compiler Design'},

                {'code': 'BCS3128', 'name': 'Machine Learning'},

                {'code': 'BCS3129', 'name': 'Mobile Application Development Using Android Technology'},

                {'code': 'BCS3130', 'name': 'Research Paper'},

            ],

            'academic_year': '2024/2025',

            'is_active': True

        },



        {

            'id': 'SG_BCS_126_S6',

            'batch': 'BCS-126',

            'program': 'BCS',

            'semester': 'S6',

            'term': None,

            'size': 35,

            'course_units': [

                {'code': 'BCS3231', 'name': 'New Product Development and Innovation'},

                {'code': 'BCS3232', 'name': 'Virtualization and Cloud Computing'},

                {'code': 'BCS3233', 'name': 'Digital Marketing'},

                {'code': 'BCS3234', 'name': 'Project'},

            ],

            'academic_year': '2024/2025',

            'is_active': True

        },



    ]


def seed_student_groups_to_db(db):
    """Seed all student group data to MongoDB database"""
    groups_data = get_all_student_groups()
    
    # Clear existing student groups
    db.student_groups.delete_many({})
    
    # Insert all student groups
    result = db.student_groups.insert_many(groups_data)
    
    print(f"✅ Successfully seeded {len(result.inserted_ids)} student groups")
    print(f"   - BSCAIT-126 Batch: {sum(1 for g in groups_data if g.get('batch') == 'BSCAIT-126')} semesters")
    print(f"   - BCS-126 Batch: {sum(1 for g in groups_data if g.get('batch') == 'BCS-126')} semesters")
    print(f"   - BML-126 Batch: {sum(1 for g in groups_data if g.get('batch') == 'BML-126')} semesters")
    print(f"   - BSCE-126 Batch: {sum(1 for g in groups_data if g.get('batch') == 'BSCE-126')} semesters")
    print(f"   - Total Students: {sum(g.get('size', 0) for g in groups_data)}")
    print(f"\n📚 Course Structure:")
    print(f"   - S1-S5: 5 course units per semester")
    print(f"   - S6: 4 course units (including Final Year Project)")
    print(f"   - Shared courses across programs for efficient timetabling")
    print(f"   - Note: Term splits will be handled by preprocessor")
    
    return result


def get_shared_courses_summary():
    """Get a summary of shared courses across programs"""
    groups_data = get_all_student_groups()
    
    # Track course usage
    course_usage = {}
    
    for group in groups_data:
        # Handle new format where course_units can be dicts with 'code' and 'name'
        for course_item in group['course_units']:
            # Extract course code from dict or use string directly
            if isinstance(course_item, dict):
                course_code = course_item.get('code')
            else:
                course_code = course_item
            
            if course_code and course_code not in course_usage:
                course_usage[course_code] = []
            if course_code:
                course_usage[course_code].append({
                    'program': group['program'],
                    'semester': group['semester'],
                    'batch': group['batch']
                })
    
    # Find shared courses (used by multiple programs)
    shared_courses = {
        course: usage 
        for course, usage in course_usage.items() 
        if len(set(u['program'] for u in usage)) > 1
    }
    
    return shared_courses


def get_student_group_statistics():
    """Get statistics about student groups"""
    groups_data = get_all_student_groups()
    
    stats = {
        'total_groups': len(groups_data),
        'by_batch': {},
        'by_semester': {},
        'total_students': sum(g['size'] for g in groups_data),
        'total_course_enrollments': sum(len(g['course_units']) for g in groups_data),  # Count individual courses
        'avg_group_size': sum(g['size'] for g in groups_data) / len(groups_data)
    }
    
    for group in groups_data:
        batch = group.get('batch')
        semester = group.get('semester')
        
        if batch:
            stats['by_batch'][batch] = stats['by_batch'].get(batch, 0) + 1
        if semester:
            stats['by_semester'][semester] = stats['by_semester'].get(semester, 0) + 1
    
    return stats


if __name__ == '__main__':
    stats = get_student_group_statistics()
    shared = get_shared_courses_summary()
    
    print("\n" + "="*70)
    print("ISBAT UNIVERSITY - STUDENT GROUP DATA (UPDATED WITH REAL COURSES)")
    print("="*70)
    print(f"\n👥 Total Student Groups: {stats['total_groups']} (semester groups)")
    
    print(f"\n📚 By Batch:")
    for batch in sorted(stats['by_batch'].keys()):
        count = stats['by_batch'][batch]
        print(f"   - {batch}: {count} semesters")
    
    print(f"\n📊 By Program:")
    groups_data = get_all_student_groups()
    by_program = {}
    for group in groups_data:
        program = group.get('program')
        if program:
            by_program[program] = by_program.get(program, 0) + 1
    for program in sorted(by_program.keys()):
        print(f"   - {program}: {by_program[program]} groups")
    
    print(f"\n🎓 Student Statistics:")
    print(f"   - Total Students: {stats['total_students']}")
    print(f"   - Average Group Size: {stats['avg_group_size']:.1f}")
    print(f"   - Total Course Enrollments: {stats['total_course_enrollments']}")
    
    print(f"\n🔗 Shared Courses (for efficient timetabling):")
    print(f"   - Total shared courses: {len(shared)}")
    for course_code in sorted(shared.keys())[:10]:  # Show first 10
        programs = set(u['program'] for u in shared[course_code])
        print(f"   - {course_code}: Shared by {', '.join(sorted(programs))}")
    
    print(f"\n📋 Course Structure:")
    print(f"   - Semesters 1-5: 5 course units each")
    print(f"   - Semester 6: 4 course units (including PRJ601 - Final Year Project)")
    print(f"   - All S6 groups include mandatory Final Year Project")
    
    print(f"\n⚙️  Preprocessing:")
    print(f"   - Term splitting: Handled by preprocessor")
    print(f"   - Course distribution: Automatic based on constraints")
    
    print("\n" + "="*70)
    print("✅ Student group data ready for seeding!")
    print("="*70 + "\n")