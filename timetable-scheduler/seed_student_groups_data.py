"""Seed student group data for ISBAT Timetable System"""

from typing import List, Dict

def get_all_student_groups() -> List[Dict]:
    """
    Get all student group data for Computing Faculty programs
    Programs: BSCAIT, BCS, BML&AI, BSCE
    All semesters S1-S6 for Term 1 testing
    
    Note: No term splits included - the preprocessor will automatically
    split courses into terms based on its intelligence
    
    Returns:
        List of student group dictionaries ready for MongoDB insertion
    """
    student_groups = []
    
    # ========================================
    # BSCAIT-126 Batch (2024/2025 intake)
    # ========================================
    
    # Semester 1
    student_groups.append({
        'id': 'SG_BSCAIT_126_S1',
        'batch': 'BSCAIT-126',
        'program': 'BSCAIT',
        'semester': 'S1',
        'term': None,  # Preprocessor will split into terms
        'size': 50,
        'course_units': ['CS101', 'CS102', 'CS103', 'CS104', 'CS105'],
        'academic_year': '2024/2025',
        'is_active': True
    })
    
    # Semester 2
    student_groups.append({
        'id': 'SG_BSCAIT_126_S2',
        'batch': 'BSCAIT-126',
        'program': 'BSCAIT',
        'semester': 'S2',
        'term': None,
        'size': 45,
        'course_units': ['CS106', 'CS107', 'CS108', 'CS109', 'CS110'],
        'academic_year': '2025/2026',
        'is_active': True
    })
    
    # Semester 3
    student_groups.append({
        'id': 'SG_BSCAIT_126_S3',
        'batch': 'BSCAIT-126',
        'program': 'BSCAIT',
        'semester': 'S3',
        'term': None,
        'size': 40,
        'course_units': ['CS201', 'CS202', 'CS203', 'CS204', 'CS205'],
        'academic_year': '2026/2027',
        'is_active': True
    })
    
    # Semester 4
    student_groups.append({
        'id': 'SG_BSCAIT_126_S4',
        'batch': 'BSCAIT-126',
        'program': 'BSCAIT',
        'semester': 'S4',
        'term': None,
        'size': 35,
        'course_units': ['CS206', 'CS207', 'CS208', 'CS209', 'CS210'],
        'academic_year': '2027/2028',
        'is_active': True
    })
    
    # Semester 5
    student_groups.append({
        'id': 'SG_BSCAIT_126_S5',
        'batch': 'BSCAIT-126',
        'program': 'BSCAIT',
        'semester': 'S5',
        'term': None,
        'size': 20,
        'course_units': ['CS301', 'CS302', 'CS303', 'CS304', 'CS305'],
        'academic_year': '2028/2029',
        'is_active': True
    })
    
    # Semester 6
    student_groups.append({
        'id': 'SG_BSCAIT_126_S6',
        'batch': 'BSCAIT-126',
        'program': 'BSCAIT',
        'semester': 'S6',
        'term': None,
        'size': 20,
        'course_units': ['CS306', 'CS307', 'CS308', 'CS309', 'CS310'],
        'academic_year': '2029/2030',
        'is_active': True
    })
    
    # ========================================
    # BSCAIT-226 Batch (2026/2027 intake)
    # ========================================
    
    # Semester 1
    student_groups.append({
        'id': 'SG_BSCAIT_226_S1',
        'batch': 'BSCAIT-226',
        'program': 'BSCAIT',
        'semester': 'S1',
        'term': None,
        'size': 28,
        'course_units': ['CS101', 'CS102', 'CS103', 'CS104', 'CS105'],
        'academic_year': '2026/2027',
        'is_active': True
    })
    
    # Semester 2
    student_groups.append({
        'id': 'SG_BSCAIT_226_S2',
        'batch': 'BSCAIT-226',
        'program': 'BSCAIT',
        'semester': 'S2',
        'term': None,
        'size': 28,
        'course_units': ['CS106', 'CS107', 'CS108', 'CS109', 'CS110'],
        'academic_year': '2027/2028',
        'is_active': True
    })
    
    # Semester 3
    student_groups.append({
        'id': 'SG_BSCAIT_226_S3',
        'batch': 'BSCAIT-226',
        'program': 'BSCAIT',
        'semester': 'S3',
        'term': None,
        'size': 26,
        'course_units': ['CS201', 'CS202', 'CS203', 'CS204', 'CS205'],
        'academic_year': '2028/2029',
        'is_active': True
    })
    
    # Semester 4
    student_groups.append({
        'id': 'SG_BSCAIT_226_S4',
        'batch': 'BSCAIT-226',
        'program': 'BSCAIT',
        'semester': 'S4',
        'term': None,
        'size': 26,
        'course_units': ['CS206', 'CS207', 'CS208', 'CS209', 'CS210'],
        'academic_year': '2029/2030',
        'is_active': True
    })
    
    # Semester 5
    student_groups.append({
        'id': 'SG_BSCAIT_226_S5',
        'batch': 'BSCAIT-226',
        'program': 'BSCAIT',
        'semester': 'S5',
        'term': None,
        'size': 24,
        'course_units': ['CS301', 'CS302', 'CS303', 'CS304', 'CS305'],
        'academic_year': '2030/2031',
        'is_active': True
    })
    
    # Semester 6
    student_groups.append({
        'id': 'SG_BSCAIT_226_S6',
        'batch': 'BSCAIT-226',
        'program': 'BSCAIT',
        'semester': 'S6',
        'term': None,
        'size': 24,
        'course_units': ['CS306', 'CS307', 'CS308', 'CS309', 'CS310'],
        'academic_year': '2031/2032',
        'is_active': True
    })
    
    # ========================================
    # BCS Program - Batch BCS-126 (2024/2025 intake)
    # ========================================
    
    # Semester 1 - Shares CS102, CS103, CS105 with BSCAIT
    student_groups.append({
        'id': 'SG_BCS_126_S1',
        'batch': 'BCS-126',
        'program': 'BCS',
        'semester': 'S1',
        'term': None,
        'size': 45,
        'course_units': ['BCS101', 'CS102', 'CS103', 'BCS104', 'CS105'],  # Shared: CS102, CS103, CS105
        'academic_year': '2024/2025',
        'is_active': True
    })
    
    # Semester 2 - Shares CS110 with all programs
    student_groups.append({
        'id': 'SG_BCS_126_S2',
        'batch': 'BCS-126',
        'program': 'BCS',
        'semester': 'S2',
        'term': None,
        'size': 40,
        'course_units': ['BCS201', 'BCS202', 'BCS203', 'BCS204', 'CS110'],  # Shared: CS110
        'academic_year': '2025/2026',
        'is_active': True
    })
    
    # Semester 3 - Shares CS203 with BSCAIT
    student_groups.append({
        'id': 'SG_BCS_126_S3',
        'batch': 'BCS-126',
        'program': 'BCS',
        'semester': 'S3',
        'term': None,
        'size': 35,
        'course_units': ['BCS301', 'BCS302', 'CS203', 'BCS303', 'BCS304'],  # Shared: CS203
        'academic_year': '2026/2027',
        'is_active': True
    })
    
    # Semester 4 - Shares CS209 with BSCAIT and BML&AI
    student_groups.append({
        'id': 'SG_BCS_126_S4',
        'batch': 'BCS-126',
        'program': 'BCS',
        'semester': 'S4',
        'term': None,
        'size': 30,
        'course_units': ['BCS401', 'BCS402', 'BCS403', 'BCS404', 'CS209'],  # Shared: CS209
        'academic_year': '2027/2028',
        'is_active': True
    })
    
    # Semester 5
    student_groups.append({
        'id': 'SG_BCS_126_S5',
        'batch': 'BCS-126',
        'program': 'BCS',
        'semester': 'S5',
        'term': None,
        'size': 25,
        'course_units': ['BCS501', 'BCS502', 'BCS503', 'BCS504'],
        'academic_year': '2028/2029',
        'is_active': True
    })
    
    # Semester 6
    student_groups.append({
        'id': 'SG_BCS_126_S6',
        'batch': 'BCS-126',
        'program': 'BCS',
        'semester': 'S6',
        'term': None,
        'size': 22,
        'course_units': ['BCS601', 'BCS602', 'BCS603', 'BCS604'],
        'academic_year': '2029/2030',
        'is_active': True
    })
    
    # ========================================
    # BML&AI Program - Batch BML-126 (2024/2025 intake)
    # ========================================
    
    # Semester 1 - Shares CS105 with all programs
    student_groups.append({
        'id': 'SG_BML_126_S1',
        'batch': 'BML-126',
        'program': 'BML&AI',
        'semester': 'S1',
        'term': None,
        'size': 35,
        'course_units': ['ML101', 'ML102', 'ML103', 'ML104', 'CS105'],  # Shared: CS105
        'academic_year': '2024/2025',
        'is_active': True
    })
    
    # Semester 2 - Shares CS110 with all programs
    student_groups.append({
        'id': 'SG_BML_126_S2',
        'batch': 'BML-126',
        'program': 'BML&AI',
        'semester': 'S2',
        'term': None,
        'size': 32,
        'course_units': ['ML201', 'ML202', 'ML203', 'ML204', 'CS110'],  # Shared: CS110
        'academic_year': '2025/2026',
        'is_active': True
    })
    
    # Semester 3
    student_groups.append({
        'id': 'SG_BML_126_S3',
        'batch': 'BML-126',
        'program': 'BML&AI',
        'semester': 'S3',
        'term': None,
        'size': 28,
        'course_units': ['ML301', 'ML302', 'ML303', 'ML304'],
        'academic_year': '2026/2027',
        'is_active': True
    })
    
    # Semester 4 - Shares CS209 with BSCAIT and BCS
    student_groups.append({
        'id': 'SG_BML_126_S4',
        'batch': 'BML-126',
        'program': 'BML&AI',
        'semester': 'S4',
        'term': None,
        'size': 25,
        'course_units': ['ML401', 'ML402', 'ML403', 'ML404', 'CS209'],  # Shared: CS209
        'academic_year': '2027/2028',
        'is_active': True
    })
    
    # Semester 5
    student_groups.append({
        'id': 'SG_BML_126_S5',
        'batch': 'BML-126',
        'program': 'BML&AI',
        'semester': 'S5',
        'term': None,
        'size': 20,
        'course_units': ['ML501', 'ML502', 'ML503', 'ML504'],
        'academic_year': '2028/2029',
        'is_active': True
    })
    
    # Semester 6
    student_groups.append({
        'id': 'SG_BML_126_S6',
        'batch': 'BML-126',
        'program': 'BML&AI',
        'semester': 'S6',
        'term': None,
        'size': 18,
        'course_units': ['ML601', 'ML602', 'ML603', 'ML604'],
        'academic_year': '2029/2030',
        'is_active': True
    })
    
    # ========================================
    # BSCE Program - Batch BSCE-126 (2024/2025 intake)
    # ========================================
    
    # Semester 1 - Shares CS105 with all programs
    student_groups.append({
        'id': 'SG_BSCE_126_S1',
        'batch': 'BSCE-126',
        'program': 'BSCE',
        'semester': 'S1',
        'term': None,
        'size': 60,  # Larger group to test split rules
        'course_units': ['CE101', 'CE102', 'CE103', 'CE104', 'CS105'],  # Shared: CS105
        'academic_year': '2024/2025',
        'is_active': True
    })
    
    # Semester 2 - Shares CS110 with all programs
    student_groups.append({
        'id': 'SG_BSCE_126_S2',
        'batch': 'BSCE-126',
        'program': 'BSCE',
        'semester': 'S2',
        'term': None,
        'size': 55,  # Larger group to test split rules
        'course_units': ['CE201', 'CE202', 'CE203', 'CE204', 'CS110'],  # Shared: CS110
        'academic_year': '2025/2026',
        'is_active': True
    })
    
    # Semester 3
    student_groups.append({
        'id': 'SG_BSCE_126_S3',
        'batch': 'BSCE-126',
        'program': 'BSCE',
        'semester': 'S3',
        'term': None,
        'size': 50,
        'course_units': ['CE301', 'CE302', 'CE303', 'CE304'],
        'academic_year': '2026/2027',
        'is_active': True
    })
    
    # Semester 4
    student_groups.append({
        'id': 'SG_BSCE_126_S4',
        'batch': 'BSCE-126',
        'program': 'BSCE',
        'semester': 'S4',
        'term': None,
        'size': 45,
        'course_units': ['CE401', 'CE402', 'CE403', 'CE404'],
        'academic_year': '2027/2028',
        'is_active': True
    })
    
    # Semester 5
    student_groups.append({
        'id': 'SG_BSCE_126_S5',
        'batch': 'BSCE-126',
        'program': 'BSCE',
        'semester': 'S5',
        'term': None,
        'size': 40,
        'course_units': ['CE501', 'CE502', 'CE503', 'CE504'],
        'academic_year': '2028/2029',
        'is_active': True
    })
    
    # Semester 6
    student_groups.append({
        'id': 'SG_BSCE_126_S6',
        'batch': 'BSCE-126',
        'program': 'BSCE',
        'semester': 'S6',
        'term': None,
        'size': 35,
        'course_units': ['CE601', 'CE602', 'CE603', 'CE604'],
        'academic_year': '2029/2030',
        'is_active': True
    })
    
    return student_groups


def seed_student_groups_to_db(db):
    """Seed all student group data to MongoDB database"""
    groups_data = get_all_student_groups()
    
    # Clear existing student groups
    db.student_groups.delete_many({})
    
    # Insert all student groups
    result = db.student_groups.insert_many(groups_data)
    
    print(f"✅ Successfully seeded {len(result.inserted_ids)} student groups")
    print(f"   - BSCAIT-126 Batch: {sum(1 for g in groups_data if g['batch'] == 'BSCAIT-126')} semesters")
    print(f"   - BSCAIT-226 Batch: {sum(1 for g in groups_data if g['batch'] == 'BSCAIT-226')} semesters")
    print(f"   - BCS-126 Batch: {sum(1 for g in groups_data if g['batch'] == 'BCS-126')} semesters")
    print(f"   - BML-126 Batch: {sum(1 for g in groups_data if g['batch'] == 'BML-126')} semesters")
    print(f"   - BSCE-126 Batch: {sum(1 for g in groups_data if g['batch'] == 'BSCE-126')} semesters")
    print(f"   - Total Students: {sum(g['size'] for g in groups_data)}")
    print(f"   - Note: Term splits will be handled by preprocessor")
    
    return result


def get_student_group_statistics():
    """Get statistics about student groups"""
    groups_data = get_all_student_groups()
    
    stats = {
        'total_groups': len(groups_data),
        'by_batch': {},
        'by_semester': {},
        'by_term': {},
        'total_students': sum(g['size'] for g in groups_data),
        'total_course_enrollments': sum(len(g['course_units']) for g in groups_data),
        'avg_group_size': sum(g['size'] for g in groups_data) / len(groups_data)
    }
    
    for group in groups_data:
        batch = group['batch']
        semester = group['semester']
        term = group['term']
        
        stats['by_batch'][batch] = stats['by_batch'].get(batch, 0) + 1
        stats['by_semester'][semester] = stats['by_semester'].get(semester, 0) + 1
        stats['by_term'][term] = stats['by_term'].get(term, 0) + 1
    
    return stats


if __name__ == '__main__':
    stats = get_student_group_statistics()
    
    print("\n" + "="*60)
    print("ISBAT STUDENT GROUP STATISTICS")
    print("="*60)
    print(f"\n👥 Total Student Groups: {stats['total_groups']} (semester groups)")
    
    print(f"\n📚 By Batch:")
    for batch in sorted(stats['by_batch'].keys()):
        count = stats['by_batch'][batch]
        print(f"   - {batch}: {count} semesters")
    
    print(f"\n📚 By Program:")
    by_program = {}
    for group in groups_data:
        program = group['program']
        by_program[program] = by_program.get(program, 0) + 1
    for program in sorted(by_program.keys()):
        print(f"   - {program}: {by_program[program]} groups")
    
    print(f"\n📊 By Semester:")
    for sem in sorted(stats['by_semester'].keys()):
        print(f"   - {sem}: {stats['by_semester'][sem]} groups")
    
    print(f"\n🎓 Student Statistics:")
    print(f"   - Total Students: {stats['total_students']}")
    print(f"   - Average Group Size: {stats['avg_group_size']:.1f}")
    print(f"   - Total Course Enrollments: {stats['total_course_enrollments']}")
    
    print(f"\n⚙️  Preprocessing:")
    print(f"   - Term splitting: Handled by preprocessor")
    print(f"   - Course distribution: Automatic based on constraints")
    
    print("\n" + "="*60)
    print("✅ Student group data ready for seeding!")
    print("="*60 + "\n")

