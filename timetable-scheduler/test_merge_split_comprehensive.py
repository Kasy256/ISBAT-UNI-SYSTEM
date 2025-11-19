"""
Comprehensive Merge/Split Rules Testing Script
Tests merge rules (shared courses) and split rules (large groups) 
and all constraints in detail
"""

import sys
import io
sys.path.insert(0, '.')

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import csv
from collections import defaultdict
from pymongo import MongoClient
from app.models.course import CourseUnit

def load_timetable(csv_file):
    """Load timetable from CSV"""
    sessions = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sessions.append(row)
    return sessions

def load_database_info():
    """Load course and student group info from database"""
    client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
    db = client['timetable_scheduler']
    
    courses_data = list(db.course_units.find())
    courses = {CourseUnit.from_dict(c).id: CourseUnit.from_dict(c) for c in courses_data}
    
    groups_data = list(db.student_groups.find({'is_active': True}))
    groups = {g['id']: g for g in groups_data}
    
    client.close()
    return courses, groups

def test_merge_rules(sessions, courses, groups):
    """Test merge rules - shared courses should be merged when possible"""
    print("\n" + "="*70)
    print("          MERGE RULES TEST - SHARED COURSES")
    print("="*70)
    
    # Find shared courses (courses taken by multiple groups)
    course_groups = defaultdict(set)
    for session in sessions:
        course_code = session['Course_Code']
        group = session['Student_Group']
        semester = session['Semester']
        # Key by course + semester (same course in same semester can be merged)
        key = (course_code, semester)
        course_groups[key].add(group)
    
    shared_courses = {k: v for k, v in course_groups.items() if len(v) > 1}
    
    print(f"\n📊 Found {len(shared_courses)} shared courses across multiple groups:")
    for (course, semester), group_set in sorted(shared_courses.items()):
        print(f"   • {course} ({semester}): {len(group_set)} groups")
        for group in sorted(group_set):
            print(f"      - {group}")
    
    print(f"\n🔍 Testing merge rules:")
    print("   Rule: Multiple groups sharing the same course can be merged")
    print("   Condition: Total students ≤ Room Capacity")
    print("   Expected: Shared courses should be scheduled together when room capacity allows\n")
    
    # Check actual merging
    room_time_course_groups = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))
    for session in sessions:
        room = session['Room_Number']
        day = session['Day']
        time_slot = session['Time_Slot']
        course = session['Course_Code']
        semester = session['Semester']
        group = session['Student_Group']
        key = (day, time_slot)
        course_key = (course, semester)
        
        room_time_course_groups[room][key][course_key].add(group)
    
    merged_sessions = 0
    merge_opportunities_missed = 0
    merge_violations = 0
    
    print("📋 Merge Analysis:")
    for room, time_slots in room_time_course_groups.items():
        for time_key, course_groups_dict in time_slots.items():
            for (course, semester), groups_in_room in course_groups_dict.items():
                if len(groups_in_room) > 1:
                    # Multiple groups are merged for this course
                    merged_sessions += 1
                    total_students = sum(int(s['Group_Size']) for s in sessions 
                                       if s['Room_Number'] == room and 
                                       s['Day'] == time_key[0] and 
                                       s['Time_Slot'] == time_key[1] and
                                       s['Course_Code'] == course and
                                       s['Student_Group'] in groups_in_room)
                    room_capacity = int(next(s['Room_Capacity'] for s in sessions 
                                            if s['Room_Number'] == room and
                                            s['Day'] == time_key[0] and
                                            s['Time_Slot'] == time_key[1]), 0)
                    
                    if total_students > room_capacity:
                        merge_violations += 1
                        print(f"   ❌ VIOLATION: {course} ({semester}) - Room {room} capacity exceeded")
                        print(f"      Room: {room} (capacity: {room_capacity})")
                        print(f"      Time: {time_key[0]} {time_key[1]}")
                        print(f"      Groups: {', '.join(sorted(groups_in_room))}")
                        print(f"      Total students: {total_students} > {room_capacity}")
                    else:
                        print(f"   ✅ MERGED: {course} ({semester})")
                        print(f"      Room: {room} (capacity: {room_capacity})")
                        print(f"      Time: {time_key[0]} {time_key[1]}")
                        print(f"      Groups: {', '.join(sorted(groups_in_room))}")
                        print(f"      Total students: {total_students} ≤ {room_capacity}")
    
    # Check for missed merge opportunities
    print(f"\n🔍 Checking for missed merge opportunities...")
    for (course, semester), groups in shared_courses.items():
        # Check if these groups are scheduled separately when they could be merged
        course_sessions = [s for s in sessions if s['Course_Code'] == course and s['Semester'] == semester]
        group_times = defaultdict(set)
        for session in course_sessions:
            group = session['Student_Group']
            time_key = (session['Day'], session['Time_Slot'])
            group_times[group].add(time_key)
        
        # Check if groups have different time slots (not merged)
        all_times = set()
        for times in group_times.values():
            all_times.update(times)
        
        # If groups are scheduled at different times, check if they could be merged
        if len(all_times) > 1:
            # Groups are scheduled separately - check if merging is possible
            group_sizes = {}
            for session in course_sessions:
                group = session['Student_Group']
                if group not in group_sizes:
                    group_sizes[group] = int(session['Group_Size'])
            
            total_size = sum(group_sizes.values())
            # Find suitable room for merging
            suitable_rooms = [s for s in course_sessions if int(s['Room_Capacity']) >= total_size]
            if suitable_rooms:
                merge_opportunities_missed += len(all_times) - 1
                print(f"   ℹ️  OPPORTUNITY: {course} ({semester}) - {len(groups)} groups scheduled separately")
                print(f"      Total students: {total_size}")
                print(f"      Groups: {', '.join(sorted(groups))}")
                print(f"      Scheduled at {len(all_times)} different time slots: {sorted(all_times)}")
                print(f"      Could potentially be merged (suitable rooms available)")
    
    print(f"\n📊 Merge Summary:")
    print(f"   • Merged sessions: {merged_sessions}")
    print(f"   • Merge violations: {merge_violations}")
    print(f"   • Missed merge opportunities: {merge_opportunities_missed}")
    
    if merge_violations == 0:
        print(f"\n   ✅ PASSED: All merged sessions fit within room capacity")
    else:
        print(f"\n   ❌ FAILED: {merge_violations} merge violations")
    
    return {
        'merged_sessions': merged_sessions,
        'merge_violations': merge_violations,
        'merge_opportunities_missed': merge_opportunities_missed
    }

def test_split_rules(sessions):
    """Test split rules - large groups must be split"""
    print("\n" + "="*70)
    print("          SPLIT RULES TEST - LARGE GROUPS")
    print("="*70)
    
    print(f"\n🔍 Testing split rules:")
    print("   Rule: Groups exceeding room capacity must be split")
    print("   Condition: If group_size > room_capacity, group must have _SPLIT_ suffix")
    print("   Expected: All groups fit in assigned rooms or are properly split\n")
    
    splitting_violations = 0
    split_groups = []
    oversized_groups = []
    
    print("📋 Split Analysis:")
    for session in sessions:
        student_group = session['Student_Group']
        group_size = int(session['Group_Size'])
        room_capacity = int(session['Room_Capacity'])
        course = session['Course_Code']
        room = session['Room_Number']
        
        if group_size > room_capacity:
            is_split_group = '_SPLIT_' in student_group or 'SPLIT' in student_group.upper()
            
            if is_split_group:
                split_groups.append({
                    'group': student_group,
                    'size': group_size,
                    'room': room,
                    'capacity': room_capacity,
                    'course': course
                })
                print(f"   ✅ SPLIT: {student_group}")
                print(f"      Size: {group_size}, Room: {room} (capacity: {room_capacity})")
                print(f"      Course: {course}")
            else:
                splitting_violations += 1
                oversized_groups.append({
                    'group': student_group,
                    'size': group_size,
                    'room': room,
                    'capacity': room_capacity,
                    'course': course
                })
                print(f"   ❌ VIOLATION: {student_group} NOT split")
                print(f"      Size: {group_size} > Room capacity: {room_capacity}")
                print(f"      Room: {room}, Course: {course}")
    
    print(f"\n📊 Split Summary:")
    print(f"   • Split groups found: {len(split_groups)}")
    print(f"   • Oversized groups (should be split): {len(oversized_groups)}")
    print(f"   • Split violations: {splitting_violations}")
    
    if splitting_violations == 0:
        if len(oversized_groups) == 0:
            print(f"\n   ✅ PASSED: No groups exceed room capacity (no splitting needed)")
        else:
            print(f"\n   ✅ PASSED: All oversized groups are properly split")
    else:
        print(f"\n   ❌ FAILED: {splitting_violations} groups exceed room capacity without splitting")
        print(f"\n   Violations:")
        for v in oversized_groups:
            print(f"      • {v['group']}: {v['size']} students in room {v['room']} (capacity: {v['capacity']})")
    
    return {
        'split_groups': len(split_groups),
        'oversized_groups': len(oversized_groups),
        'splitting_violations': splitting_violations
    }

def test_all_constraints_detailed(sessions):
    """Test all constraints with detailed output"""
    print("\n" + "="*70)
    print("          DETAILED CONSTRAINT TESTING")
    print("="*70)
    
    violations = []
    
    # 1. No Double-Booking
    print("\n1️⃣  NO DOUBLE-BOOKING")
    print("-"*70)
    student_time_slots = defaultdict(set)
    lecturer_time_slots = defaultdict(set)
    room_time_slots = defaultdict(set)
    
    student_conflicts = []
    lecturer_conflicts = []
    room_conflicts = []
    
    for session in sessions:
        group = session['Student_Group']
        lecturer = session['Lecturer_ID']
        room = session['Room_Number']
        day = session['Day']
        time_slot = session['Time_Slot']
        key = (day, time_slot)
        
        # Check student conflicts
        if key in student_time_slots[group]:
            student_conflicts.append({
                'group': group,
                'day': day,
                'time': time_slot,
                'course': session['Course_Code']
            })
        student_time_slots[group].add(key)
        
        # Check lecturer conflicts
        if key in lecturer_time_slots[lecturer]:
            lecturer_conflicts.append({
                'lecturer': session['Lecturer_Name'],
                'lecturer_id': lecturer,
                'day': day,
                'time': time_slot,
                'course': session['Course_Code']
            })
        lecturer_time_slots[lecturer].add(key)
        
        # Check room conflicts
        if key in room_time_slots[room]:
            room_conflicts.append({
                'room': room,
                'day': day,
                'time': time_slot,
                'course': session['Course_Code']
            })
        room_time_slots[room].add(key)
    
    if student_conflicts:
        print(f"   ❌ FAILED: {len(student_conflicts)} student double-booking violations")
        for c in student_conflicts[:5]:
            print(f"      • {c['group']} double-booked on {c['day']} at {c['time']}")
    else:
        print(f"   ✅ PASSED: No student double-booking")
    
    if lecturer_conflicts:
        print(f"   ❌ FAILED: {len(lecturer_conflicts)} lecturer double-booking violations")
        for c in lecturer_conflicts[:5]:
            print(f"      • {c['lecturer']} ({c['lecturer_id']}) double-booked on {c['day']} at {c['time']}")
    else:
        print(f"   ✅ PASSED: No lecturer double-booking")
    
    if room_conflicts:
        print(f"   ❌ FAILED: {len(room_conflicts)} room double-booking violations")
        for c in room_conflicts[:5]:
            print(f"      • Room {c['room']} double-booked on {c['day']} at {c['time']}")
    else:
        print(f"   ✅ PASSED: No room double-booking")
    
    # 2. Room Capacity
    print("\n2️⃣  ROOM CAPACITY")
    print("-"*70)
    capacity_violations = []
    for session in sessions:
        room_capacity = int(session['Room_Capacity'])
        group_size = int(session['Group_Size'])
        if group_size > room_capacity:
            capacity_violations.append({
                'room': session['Room_Number'],
                'capacity': room_capacity,
                'group': session['Student_Group'],
                'size': group_size,
                'course': session['Course_Code']
            })
    
    if capacity_violations:
        print(f"   ❌ FAILED: {len(capacity_violations)} capacity violations")
        for v in capacity_violations[:5]:
            print(f"      • Room {v['room']}: {v['size']} students > {v['capacity']} capacity")
            print(f"        Group: {v['group']}, Course: {v['course']}")
    else:
        print(f"   ✅ PASSED: All rooms have sufficient capacity")
    
    # 3. Room Type Matching
    print("\n3️⃣  ROOM TYPE MATCHING")
    print("-"*70)
    room_type_violations = []
    for session in sessions:
        course_type = session['Course_Type']
        room_type = session['Room_Type']
        if course_type == 'Lab' and room_type != 'Lab':
            room_type_violations.append({
                'course': session['Course_Code'],
                'course_type': course_type,
                'room': session['Room_Number'],
                'room_type': room_type
            })
        elif course_type == 'Theory' and room_type not in ['Classroom', 'Lecture Hall', 'Seminar Room']:
            room_type_violations.append({
                'course': session['Course_Code'],
                'course_type': course_type,
                'room': session['Room_Number'],
                'room_type': room_type
            })
    
    if room_type_violations:
        print(f"   ❌ FAILED: {len(room_type_violations)} room type violations")
        for v in room_type_violations[:5]:
            print(f"      • {v['course']} ({v['course_type']}) in {v['room']} ({v['room_type']})")
    else:
        print(f"   ✅ PASSED: All room types correctly matched")
    
    # 4. Weekly Hour Limits
    print("\n4️⃣  WEEKLY HOUR LIMITS (LECTURERS)")
    print("-"*70)
    lecturer_hours = defaultdict(int)
    lecturer_roles = {}
    for session in sessions:
        lecturer_id = session['Lecturer_ID']
        lecturer_hours[lecturer_id] += 2  # Each session is 2 hours
        lecturer_roles[lecturer_id] = session['Lecturer_Role']
    
    role_limits = {
        'Faculty Dean': 15,
        'Full-Time': 22,
        'Part-Time': 999  # No strict limit for part-time
    }
    
    weekly_violations = []
    for lecturer_id, hours in lecturer_hours.items():
        role = lecturer_roles.get(lecturer_id, 'Full-Time')
        max_hours = role_limits.get(role, 22)
        if role != 'Part-Time' and hours > max_hours:
            lecturer_name = next((s['Lecturer_Name'] for s in sessions if s['Lecturer_ID'] == lecturer_id), 'Unknown')
            weekly_violations.append({
                'lecturer': lecturer_name,
                'lecturer_id': lecturer_id,
                'role': role,
                'hours': hours,
                'max_hours': max_hours
            })
    
    if weekly_violations:
        print(f"   ❌ FAILED: {len(weekly_violations)} weekly limit violations")
        for v in weekly_violations[:5]:
            print(f"      • {v['lecturer']} ({v['role']}): {v['hours']} hours > {v['max_hours']} max")
    else:
        print(f"   ✅ PASSED: All lecturers within weekly hour limits")
        print(f"      Total lecturers: {len(lecturer_hours)}")
        print(f"      Average hours: {sum(lecturer_hours.values()) / len(lecturer_hours):.1f}")
    
    # 5. Daily Session Limits
    print("\n5️⃣  DAILY SESSION LIMITS (LECTURERS)")
    print("-"*70)
    lecturer_daily = defaultdict(lambda: defaultdict(list))
    for session in sessions:
        lecturer_id = session['Lecturer_ID']
        day = session['Day']
        start_time = session.get('Start_Time', '')
        is_afternoon = False
        if start_time:
            hour = int(start_time.split(':')[0])
            is_afternoon = hour >= 14
        
        lecturer_daily[lecturer_id][day].append({
            'is_afternoon': is_afternoon,
            'course': session['Course_Code'],
            'time': session['Time_Slot']
        })
    
    daily_violations = []
    for lecturer_id, days in lecturer_daily.items():
        for day, sessions_list in days.items():
            if len(sessions_list) > 2:
                lecturer_name = next((s['Lecturer_Name'] for s in sessions if s['Lecturer_ID'] == lecturer_id), 'Unknown')
                daily_violations.append({
                    'lecturer': lecturer_name,
                    'lecturer_id': lecturer_id,
                    'day': day,
                    'sessions': len(sessions_list),
                    'courses': [s['course'] for s in sessions_list]
                })
            else:
                morning_count = sum(1 for s in sessions_list if not s['is_afternoon'])
                afternoon_count = sum(1 for s in sessions_list if s['is_afternoon'])
                if morning_count > 1 or afternoon_count > 1:
                    lecturer_name = next((s['Lecturer_Name'] for s in sessions if s['Lecturer_ID'] == lecturer_id), 'Unknown')
                    daily_violations.append({
                        'lecturer': lecturer_name,
                        'lecturer_id': lecturer_id,
                        'day': day,
                        'issue': f'Morning: {morning_count}, Afternoon: {afternoon_count}',
                        'courses': [s['course'] for s in sessions_list]
                    })
    
    if daily_violations:
        print(f"   ❌ FAILED: {len(daily_violations)} daily limit violations")
        for v in daily_violations[:5]:
            print(f"      • {v['lecturer']} on {v['day']}: {v.get('sessions', 'unknown')} sessions")
            if 'issue' in v:
                print(f"        Issue: {v['issue']}")
    else:
        print(f"   ✅ PASSED: All lecturers within daily session limits")
    
    # 6. Standard Teaching Blocks
    print("\n6️⃣  STANDARD TEACHING BLOCKS")
    print("-"*70)
    standard_blocks = {'09:00-11:00', '11:00-13:00', '14:00-16:00', '16:00-18:00'}
    block_violations = []
    for session in sessions:
        time_slot = session['Time_Slot']
        if time_slot not in standard_blocks:
            block_violations.append({
                'session_id': session['Session_ID'],
                'time_slot': time_slot,
                'course': session['Course_Code']
            })
    
    if block_violations:
        print(f"   ❌ FAILED: {len(block_violations)} non-standard time block violations")
        for v in block_violations[:5]:
            print(f"      • {v['session_id']}: {v['time_slot']} ({v['course']})")
    else:
        print(f"   ✅ PASSED: All sessions use standard teaching blocks")
    
    # 7. No Same-Day Unit Repetition
    print("\n7️⃣  NO SAME-DAY UNIT REPETITION")
    print("-"*70)
    course_sessions_by_day = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for session in sessions:
        group = session['Student_Group']
        course = session['Course_Code']
        day = session['Day']
        time_slot = session['Time_Slot']
        course_type = session['Course_Type']
        
        course_sessions_by_day[group][day][course].append({
            'time_slot': time_slot,
            'course_type': course_type
        })
    
    time_slot_to_period = {
        '09:00-11:00': 0,
        '11:00-13:00': 1,
        '14:00-16:00': 2,
        '16:00-18:00': 3
    }
    
    repetition_violations = []
    for group, days in course_sessions_by_day.items():
        for day, courses in days.items():
            for course, session_list in courses.items():
                if len(session_list) > 1:
                    # Multiple sessions of same course on same day
                    session_list.sort(key=lambda x: time_slot_to_period.get(x['time_slot'], 999))
                    
                    is_consecutive = False
                    if len(session_list) == 2:
                        periods = [time_slot_to_period.get(s['time_slot']) for s in session_list]
                        if None not in periods and abs(periods[1] - periods[0]) == 1:
                            is_consecutive = True
                    
                    course_type = session_list[0]['course_type']
                    if not is_consecutive or course_type != 'Lab':
                        repetition_violations.append({
                            'group': group,
                            'course': course,
                            'day': day,
                            'sessions': len(session_list),
                            'times': [s['time_slot'] for s in session_list],
                            'is_consecutive': is_consecutive,
                            'course_type': course_type
                        })
    
    if repetition_violations:
        print(f"   ❌ FAILED: {len(repetition_violations)} same-day repetition violations")
        for v in repetition_violations[:5]:
            print(f"      • {v['group']}: {v['course']} ({v['course_type']}) on {v['day']}")
            print(f"        {v['sessions']} sessions at {', '.join(v['times'])}")
            print(f"        Consecutive: {v['is_consecutive']}")
    else:
        print(f"   ✅ PASSED: No same-day unit repetition")
    
    return {
        'student_conflicts': len(student_conflicts),
        'lecturer_conflicts': len(lecturer_conflicts),
        'room_conflicts': len(room_conflicts),
        'capacity_violations': len(capacity_violations),
        'room_type_violations': len(room_type_violations),
        'weekly_violations': len(weekly_violations),
        'daily_violations': len(daily_violations),
        'block_violations': len(block_violations),
        'repetition_violations': len(repetition_violations)
    }

def main():
    """Main test function"""
    import sys
    
    csv_file = sys.argv[1] if len(sys.argv) > 1 else 'TIMETABLE_TERM1_COMPLETE.csv'
    
    print("\n" + "="*70)
    print("          COMPREHENSIVE MERGE/SPLIT & CONSTRAINT TESTING")
    print("="*70)
    print(f"\n📁 Analyzing: {csv_file}\n")
    
    try:
        sessions = load_timetable(csv_file)
        print(f"✅ Loaded {len(sessions)} sessions\n")
        
        # Load database info for context
        courses, groups = load_database_info()
        print(f"✅ Loaded {len(courses)} courses and {len(groups)} student groups from database\n")
        
        # Test merge rules
        merge_results = test_merge_rules(sessions, courses, groups)
        
        # Test split rules
        split_results = test_split_rules(sessions)
        
        # Test all constraints in detail
        constraint_results = test_all_constraints_detailed(sessions)
        
        # Final summary
        print("\n" + "="*70)
        print("          TEST SUMMARY")
        print("="*70)
        
        total_violations = (
            merge_results['merge_violations'] +
            split_results['splitting_violations'] +
            constraint_results['student_conflicts'] +
            constraint_results['lecturer_conflicts'] +
            constraint_results['room_conflicts'] +
            constraint_results['capacity_violations'] +
            constraint_results['room_type_violations'] +
            constraint_results['weekly_violations'] +
            constraint_results['daily_violations'] +
            constraint_results['block_violations'] +
            constraint_results['repetition_violations']
        )
        
        print(f"\n📊 Overall Results:")
        print(f"   • Total violations: {total_violations}")
        print(f"\n   Merge/Split:")
        print(f"      - Merge violations: {merge_results['merge_violations']}")
        print(f"      - Split violations: {split_results['splitting_violations']}")
        print(f"      - Merged sessions: {merge_results['merged_sessions']}")
        print(f"      - Split groups: {split_results['split_groups']}")
        print(f"\n   Constraints:")
        print(f"      - Double-booking: {constraint_results['student_conflicts'] + constraint_results['lecturer_conflicts'] + constraint_results['room_conflicts']}")
        print(f"      - Capacity: {constraint_results['capacity_violations']}")
        print(f"      - Room type: {constraint_results['room_type_violations']}")
        print(f"      - Weekly limits: {constraint_results['weekly_violations']}")
        print(f"      - Daily limits: {constraint_results['daily_violations']}")
        print(f"      - Teaching blocks: {constraint_results['block_violations']}")
        print(f"      - Same-day repetition: {constraint_results['repetition_violations']}")
        
        if total_violations == 0:
            print(f"\n   ✅ ALL TESTS PASSED: No violations found!")
        else:
            print(f"\n   ⚠️  SOME VIOLATIONS FOUND: Please review above details")
        
        print("\n" + "="*70 + "\n")
        
    except FileNotFoundError:
        print(f"❌ Error: File '{csv_file}' not found!")
        print("\nUsage: python test_merge_split_comprehensive.py [CSV_FILE]")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

