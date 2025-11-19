"""Seed lecturer data for ISBAT Timetable System"""

from typing import List, Dict

def get_all_lecturers() -> List[Dict]:
    """
    Get all lecturer data for ISBAT
    
    Returns:
        List of lecturer dictionaries ready for MongoDB insertion
    """
    lecturers = []
    
    # Sample lecturers provided by user - Realistic specialization distribution
    # Distribution: Some with 1 specialization (experts), some with 2-3 (moderate), 
    # a few with 4 (versatile), and 1-2 with 5 (senior professors)
    lecturers.extend([
        {
            'id': 'L001',
            'name': 'Dr. Jane Achieng',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['CS101', 'CS205'],  # Java Programming, C Programming (2 specializations)
            'availability': None,  # Full-time: Available all day (9am-6pm)
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L002',
            'name': 'Dr. Peter Ouma',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['CS102', 'CS206'],  # Data Structures, Advanced Python (2 specializations)
            'availability': None,  # Full-time: Available all day (9am-6pm)
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L003',
            'name': 'Ms. Alice Nakitende',
            'role': 'Part-Time',
            'faculty': 'Computing',
            'specializations': ['CS103', 'CS207'],  # Database Systems, Web Development II (2 specializations)
            # Part-time: Available 3 days/week, can teach 2-4 hours per day
            'availability': {
                'MON': ['09:00-11:00', '14:00-16:00'],  # Monday: 4 hours (2 sessions) - morning + afternoon
                'WED': ['09:00-11:00', '14:00-16:00'],  # Wednesday: 4 hours (2 sessions) - morning + afternoon
                'FRI': ['14:00-16:00']  # Friday: 2 hours (1 session) - afternoon
            },
            'sessions_per_day': 2,  # Can teach up to 2 sessions (4 hours) on available days
            'max_weekly_hours': None  # Part-time: No strict weekly limit - teach when available
        },
        {
            'id': 'L004',
            'name': 'Dr. Samuel Kato',
            'role': 'Faculty Dean',
            'faculty': 'Computing',
            'specializations': ['CS104', 'CS208'],  # Networking, Cybersecurity (2 specializations)
            'availability': None,  # Faculty Dean: Available all day (9am-6pm)
            'sessions_per_day': 2,
            'max_weekly_hours': 15
        },
        
        # Additional lecturers to cover all courses
        {
            'id': 'L005',
            'name': 'Dr. Mary Ssemakula',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['CS105', 'CS106', 'CS107'],  # IT Fundamentals, OS, Software Eng (3 specializations)
            'availability': None,  # Available all times
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L006',
            'name': 'Mr. David Mukasa',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['CS108', 'CS109', 'CS110'],  # Web Dev, Cybersecurity, Python (3 specializations)
            'availability': None,
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L007',
            'name': 'Dr. Grace Nalwoga',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['CS201', 'CS202', 'CS203', 'CS301'],  # Mobile App, Networking II, Data Analytics, Machine Learning (4 specializations - expanded for coverage)
            'availability': None,
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L008',
            'name': 'Prof. John Walusimbi',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['CS203', 'CS204', 'CS209', 'CS210'],  # Data Analytics, Cloud Computing, AI Basics, Project Mgmt (4 specializations - senior professor)
            'availability': None,
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L009',
            'name': 'Dr. Sarah Namugga',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['CS301', 'CS302', 'CS307', 'CS306', 'CS303'],  # Machine Learning, Big Data, AI Applications, Capstone, DevOps (5 specializations - expanded for coverage)
            'availability': None,
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L010',
            'name': 'Mr. Patrick Okello',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['CS303', 'CS304', 'CS305', 'CS302'],  # DevOps, Blockchain, Enterprise Systems, Big Data (4 specializations - expanded for coverage)
            'availability': None,
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L011',
            'name': 'Dr. Rebecca Namutebi',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['CS306', 'CS308', 'CS309', 'CS307'],  # Capstone, Advanced Networking, Testing, AI Applications (4 specializations - expanded for coverage)
            'availability': None,
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L012',
            'name': 'Ms. Florence Nantongo',
            'role': 'Part-Time',
            'faculty': 'Computing',
            'specializations': ['CS310', 'CS105', 'CS106'],  # IT Governance, IT Fundamentals, OS (3 specializations)
            # Part-time: Available 2 days/week, can teach 2-4 hours
            'availability': {
                'THU': ['09:00-11:00', '11:00-13:00', '14:00-16:00'],  # Thursday: 6 hours (3 sessions) - all slots
                'TUE': ['09:00-11:00']  # Tuesday: 2 hours (1 session) - morning
            },
            'sessions_per_day': 3,  # Can teach up to 3 sessions (6 hours) on available days
            'max_weekly_hours': None  # Part-time: No strict weekly limit - teach when available
        },
        
        # Additional backup lecturers for coverage
        {
            'id': 'L013',
            'name': 'Dr. James Mugisha',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['CS101', 'CS102', 'CS103', 'CS107', 'CS205', 'CS304', 'CS305'],  # Java, Data Structures, Database, Software Eng, C Programming, Blockchain, Enterprise Systems (7 specializations - intro courses backup, expanded)
            'availability': None,
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L014',
            'name': 'Ms. Christine Atuhaire',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['CS104', 'CS108', 'CS109', 'CS110', 'CS206', 'CS207', 'CS204', 'CS209', 'CS210', 'CS208', 'CS308', 'CS309', 'CS310'],  # Networking, Web Dev, Cybersecurity, Python, Advanced Python, Web Dev II, Cloud Computing, AI Basics, Project Mgmt, Cybersecurity, Advanced Networking, Testing, IT Governance (13 specializations - versatile backup lecturer)
            'availability': None,
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L015',
            'name': 'Dr. Moses Kibirige',
            'role': 'Part-Time',
            'faculty': 'Computing',
            'specializations': ['CS201', 'CS202'],  # Mobile App Development, Networking II (2 specializations - realistic for part-time)
            # Part-time: Available 3 days/week, can teach 2-4 hours per day
            'availability': {
                'TUE': ['09:00-11:00', '14:00-16:00'],  # Tuesday: 4 hours (2 sessions) - morning + afternoon
                'THU': ['14:00-16:00'],  # Thursday: 2 hours (1 session) - afternoon
                'FRI': ['09:00-11:00', '14:00-16:00']  # Friday: 4 hours (2 sessions) - morning + afternoon
            },
            'sessions_per_day': 2,  # Can teach up to 2 sessions (4 hours) on available days
            'max_weekly_hours': None  # Part-time: No strict weekly limit - teach when available
        },
        
        # Additional lecturers for BCS program
        {
            'id': 'L016',
            'name': 'Dr. Andrew Kasumba',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['BCS101', 'BCS201', 'BCS301', 'BCS302'],  # C++, System Programming, Advanced Algorithms, Compiler Design
            'availability': None,
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L032',
            'name': 'Dr. Paul Ssenyonga',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['BCS101', 'BCS201', 'BCS301', 'BCS302'],  # C++, System Programming, Advanced Algorithms, Compiler Design (backup for L016)
            'availability': None,
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L017',
            'name': 'Ms. Susan Nakalembe',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['BCS202', 'BCS203', 'BCS204', 'BCS303', 'BCS304'],  # Software Design Patterns, Web Technologies, Network Programming, Distributed Systems, Quality Assurance
            'availability': None,
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L033',
            'name': 'Dr. Rose Nakamya',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['BCS202', 'BCS203', 'BCS204', 'BCS303', 'BCS304'],  # Software Design Patterns, Web Technologies, Network Programming, Distributed Systems, Quality Assurance (backup for L017)
            'availability': None,
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L018',
            'name': 'Dr. Robert Ssebaggala',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['BCS401', 'BCS402', 'BCS403', 'BCS501', 'BCS502'],  # OS Design, Computer Graphics, Parallel Computing, Information Security, Mobile Computing
            'availability': None,
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L019',
            'name': 'Prof. Elizabeth Nakibuuka',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['BCS503', 'BCS504', 'BCS601', 'BCS602', 'BCS603'],  # Cloud Computing Systems, Database Admin, Capstone, Advanced System Design, Enterprise Architecture
            'availability': None,
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        
        # Additional lecturers for BML&AI program
        {
            'id': 'L020',
            'name': 'Dr. Francis Katamba',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['ML101', 'ML102', 'ML103', 'ML104'],  # Intro to AI, Programming for AI, Mathematics for AI, Statistics for Data Science
            'availability': None,
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L039',
            'name': 'Dr. Andrew Kiggundu',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['ML101', 'ML102', 'ML103', 'ML104'],  # Intro to AI, Programming for AI, Mathematics for AI, Statistics for Data Science (backup for L020)
            'availability': None,
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L021',
            'name': 'Dr. Patricia Mukasa',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['ML201', 'ML202', 'ML203', 'ML204'],  # Linear Algebra for ML, Data Science Fundamentals, Data Visualization, Probability for ML
            'availability': None,
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L040',
            'name': 'Dr. Jennifer Nakazi',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['ML201', 'ML202', 'ML203', 'ML204'],  # Linear Algebra for ML, Data Science Fundamentals, Data Visualization, Probability for ML (backup for L021)
            'availability': None,
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L022',
            'name': 'Prof. Michael Kigozi',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['ML301', 'ML302', 'ML303', 'ML304', 'ML401'],  # ML Basics, Deep Learning Fundamentals, NLP, Computer Vision, Advanced ML
            'availability': None,
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L041',
            'name': 'Dr. Ronald Ssali',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['ML301', 'ML302', 'ML303', 'ML304', 'ML401'],  # ML Basics, Deep Learning Fundamentals, NLP, Computer Vision, Advanced ML (backup for L022)
            'availability': None,
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L023',
            'name': 'Dr. Catherine Naluwooza',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['ML402', 'ML403', 'ML404', 'ML501', 'ML502'],  # Reinforcement Learning, Advanced NLP, Advanced Computer Vision, Deep Learning Applications, Neural Networks
            'availability': None,
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L042',
            'name': 'Dr. Grace Namubiru',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['ML402', 'ML403', 'ML404', 'ML501', 'ML502'],  # Reinforcement Learning, Advanced NLP, Advanced Computer Vision, Deep Learning Applications, Neural Networks (backup for L023)
            'availability': None,
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L024',
            'name': 'Dr. Joseph Bbosa',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['ML503', 'ML504', 'ML601', 'ML602', 'ML603'],  # Big Data Analytics, AI Ethics, AI Capstone, Advanced AI Systems, AI Deployment
            'availability': None,
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L043',
            'name': 'Dr. Peter Kasaija',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['ML503', 'ML504', 'ML601', 'ML602', 'ML603'],  # Big Data Analytics, AI Ethics, AI Capstone, Advanced AI Systems, AI Deployment (backup for L024)
            'availability': None,
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        
        # Additional lecturers for BSCE program (some computing courses)
        {
            'id': 'L025',
            'name': 'Dr. Agnes Nakayima',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['CE101', 'CE102', 'CE202'],  # Programming Fundamentals, CAD Systems, Engineering Software Applications
            'availability': None,
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L030',
            'name': 'Dr. Sarah Nakibuuka',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['CE103', 'CE201', 'CE301'],  # Engineering Mathematics I, Structural Analysis Basics, Concrete Technology
            'availability': None,
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L031',
            'name': 'Dr. Martin Ssemwogerere',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['CE103', 'CE201', 'CE302'],  # Engineering Mathematics I, Structural Analysis Basics, Geotechnical Engineering
            'availability': None,
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L034',
            'name': 'Dr. Patrick Kato',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['CE401', 'CE402', 'CE501'],  # Highway Engineering, Water Resources Engineering, Structural Engineering
            'availability': None,
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L035',
            'name': 'Dr. Margaret Nakamya',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['CE401', 'CE402', 'CE501', 'CE502', 'CE601', 'CE602'],  # Highway Engineering, Water Resources Engineering, Structural Engineering, Environmental Engineering, Capstone Design Project, Advanced Structural Design
            'availability': None,
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L038',
            'name': 'Dr. Stephen Kiwanuka',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['CE402', 'CE501', 'CE502', 'CE602'],  # Water Resources Engineering, Structural Engineering, Environmental Engineering, Advanced Structural Design (backup for CE courses)
            'availability': None,
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L036',
            'name': 'Dr. David Ssempijja',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['BCS401', 'BCS402', 'BCS501', 'BCS502'],  # OS Design, Computer Graphics, Information Security, Mobile Computing (backup for L018)
            'availability': None,
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L037',
            'name': 'Dr. Betty Nalubega',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['BCS601', 'BCS602', 'BCS603'],  # Capstone, Advanced System Design, Enterprise Architecture (backup for L019)
            'availability': None,
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        
        # Additional part-time lecturers for flexibility
        {
            'id': 'L026',
            'name': 'Mr. Samuel Nsubuga',
            'role': 'Part-Time',
            'faculty': 'Computing',
            'specializations': ['BCS104', 'BCS204', 'BCS304'],  # Computer Architecture, Network Programming, Software Quality Assurance
            'availability': {
                'MON': ['09:00-11:00', '14:00-16:00'],
                'WED': ['14:00-16:00'],
                'FRI': ['09:00-11:00', '14:00-16:00']
            },
            'sessions_per_day': 2,
            'max_weekly_hours': None
        },
        {
            'id': 'L027',
            'name': 'Ms. Dorothy Nakato',
            'role': 'Part-Time',
            'faculty': 'Computing',
            'specializations': ['ML203', 'ML303', 'ML403'],  # Data Visualization, NLP, Advanced NLP
            'availability': {
                'TUE': ['09:00-11:00', '14:00-16:00'],
                'THU': ['14:00-16:00'],
                'FRI': ['09:00-11:00']
            },
            'sessions_per_day': 2,
            'max_weekly_hours': None
        },
        
        # Backup lecturers for shared courses (to handle increased demand)
        {
            'id': 'L028',
            'name': 'Dr. Emmanuel Kigozi',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['CS105', 'CS110', 'CS102', 'CS103'],  # IT Fundamentals, Python, Data Structures, Database Systems (shared courses backup)
            'availability': None,
            'sessions_per_day': 2,
            'max_weekly_hours': 22
        },
        {
            'id': 'L029',
            'name': 'Dr. Winnie Namukasa',
            'role': 'Full-Time',
            'faculty': 'Computing',
            'specializations': ['CS203', 'CS209', 'ML202'],  # Data Analytics, AI Basics, Data Science Fundamentals (shared courses backup)
            'availability': None,
            'sessions_per_day': 2,
            'max_weekly_hours': 22
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

