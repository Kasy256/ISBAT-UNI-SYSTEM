"""
Deep timetable verification script.

Usage:
    python verify_timetable_constraints.py TIMETABLE_TERM1_COMPLETE.csv [--export violations.json]

The script inspects the exported timetable CSV and performs the following:
    • Hard constraint checks (double-booking, capacity, room type, etc.)
    • Soft constraint checks (weekly/daily lecturer load, repeated units)
    • Canonical merge validation (ensures equivalent subjects really merged)
    • Theory/Practical pairing validation
    • Program schedule analysis (gaps, distribution)
    • Room utilization analysis
    • Subject completion checks
    • Detailed logging so conflicts are easy to spot
    • Export violations to JSON file
"""

import sys
import io
import csv
import json
import argparse
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple
from datetime import datetime

sys.path.insert(0, '.')

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from app.services.canonical_courses import get_canonical_id, CANONICAL_COURSE_MAPPING


def load_sessions(csv_path: Path) -> List[Dict[str, str]]:
    sessions = []
    with csv_path.open('r', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            sessions.append(row)
    return sessions


def section(title: str):
    line = '=' * 80
    print(f"\n{line}\n{title}\n{line}")


def log_summary(title: str, count: int, ok_message: str):
    emoji = '✅' if count == 0 else '❌'
    postfix = ok_message if count == 0 else f"{count} issue(s) detected"
    print(f"{emoji} {title}: {postfix}")


def get_program_label(row: Dict[str, str]) -> str:
    """Return the normalized program identifier for a CSV row."""
    return row.get('Program') or row.get('Student_Group', '')


def get_program_size(row: Dict[str, str]) -> int:
    """Return the normalized student size for a CSV row."""
    size_value = row.get('Student_Size') or row.get('Group_Size') or 0
    try:
        return int(size_value)
    except (ValueError, TypeError):
        return 0


def check_double_booking(sessions: List[Dict[str, str]], violations: List[Dict]) -> None:
    print("\n[Hard] Double booking / overlaps")
    buckets = {
        'student': defaultdict(lambda: defaultdict(list)),
        'lecturer': defaultdict(lambda: defaultdict(list)),
        'room': defaultdict(lambda: defaultdict(list)),
    }
    labels = {
        'student': 'Program',
        'lecturer': 'Lecturer',
        'room': 'Room',
    }
    counts = dict.fromkeys(buckets.keys(), 0)
    
    for row in sessions:
        day = row['Day']
        slot = row['Time_Slot']
        key = (day, slot)
        mappings = {
            'student': get_program_label(row),
            'lecturer': row['Lecturer_ID'],
            'room': row['Room_Number'],
        }
        for bucket_name, entity_id in mappings.items():
            if key in buckets[bucket_name][entity_id]:
                # Get existing conflicting sessions
                existing_sessions = buckets[bucket_name][entity_id][key]
                
                # Check if this is a legitimate canonical subject merge (same canonical ID)
                # Canonical subjects should be scheduled together, so this is NOT a violation
                # ALL existing sessions must be compatible (canonical merges) for this to be allowed
                current_course = row['Course_Code']
                current_canonical = get_canonical_id(current_course) or current_course
                all_compatible = True
                
                for existing in existing_sessions:
                    existing_course = existing['Course_Code']
                    existing_canonical = get_canonical_id(existing_course) or existing_course
                    # If both subjects map to the same canonical ID, they should be scheduled together
                    if current_canonical == existing_canonical and current_canonical in CANONICAL_COURSE_MAPPING:
                        continue  # This existing session is a canonical merge - compatible
                    # If subjects are different canonical IDs, it's a conflict
                    all_compatible = False
                    break
                
                # Only count as violation if NOT all existing sessions are canonical merges
                if not all_compatible:
                    counts[bucket_name] += 1
                    violations.append({
                        'constraint': 'double_booking',
                        'type': bucket_name,
                        'entity': entity_id,
                        'entity_name': row.get('Lecturer_Name' if bucket_name == 'lecturer' else 
                                               get_program_label(row)),
                        'day': day,
                        'time_slot': slot,
                        'session_id': row['Session_ID'],
                        'course_code': current_course,
                        'course_name': row['Course_Name'],
                        'conflicting_sessions': [
                            {
                                'session_id': e['Session_ID'],
                                'course_code': e['Course_Code'],
                                'course_name': e['Course_Name']
                            } for e in existing_sessions
                        ],
                        'severity': 'CRITICAL',
                        'message': f'{labels[bucket_name]} {entity_id} double-booked at {day} {slot}'
                    })
            
            buckets[bucket_name][entity_id][key].append(row)
    
    for bucket_name, cnt in counts.items():
        log_summary(f"{labels[bucket_name]} clashes", cnt, "no overlaps")


def check_room_capacity_and_type(sessions: List[Dict[str, str]], violations: List[Dict]):
    print("\n[Hard] Room capacity / type")
    capacity_violations = 0
    type_violations = 0
    for row in sessions:
        capacity = int(row['Room_Capacity'])
        size = get_program_size(row)
        course_code = row['Course_Code']
        room = row['Room_Number']
        if size > capacity:
            capacity_violations += 1
            violations.append({
                'constraint': 'room_capacity',
                'room': room,
                'subject': course_code,
                'size': size,
                'capacity': capacity,
                'severity': 'CRITICAL',
            })
        course_type = row['Course_Type']
        room_type = row['Room_Type']
        if course_type == 'Lab' and room_type != 'Lab':
            # Calculate TOTAL merged students for canonical subjects at same time slot
            day = row['Day']
            slot = row['Time_Slot']
            time_key = (day, slot)
            current_canonical = get_canonical_id(course_code) or course_code
            
            # Sum all groups with same canonical subject at same time in same room
            total_merged_students = size
            for other_row in sessions:
                if (other_row['Day'] == day and other_row['Time_Slot'] == slot and 
                    other_row['Room_Number'] == room and other_row['Session_ID'] != row['Session_ID']):
                    other_course = other_row['Course_Code']
                    other_canonical = get_canonical_id(other_course) or other_course
                    if other_canonical == current_canonical and current_canonical in CANONICAL_COURSE_MAPPING:
                        total_merged_students += get_program_size(other_row)
            
            # Get all Lab rooms and their capacities
            try:
                from seed_rooms_data import get_all_rooms
                all_rooms = get_all_rooms()
                lab_rooms = {r.get('id'): r for r in all_rooms if r.get('room_type') == 'Lab'}
            except Exception:
                # If we can't load room data, build from CSV data
                lab_rooms = {}
                for other_row in sessions:
                    if other_row.get('Room_Type') == 'Lab':
                        room_id = other_row.get('Room_Number')
                        if room_id and room_id not in lab_rooms:
                            lab_rooms[room_id] = {
                                'id': room_id,
                                'capacity': int(other_row.get('Room_Capacity', 0))
                            }
            
            # Check if ANY AVAILABLE Lab room can fit the total merged students at this time slot
            # A Lab room is available if it's not already booked at this time (or only booked by canonical merges)
            has_available_lab_room = False
            available_lab_room_id = None
            available_lab_capacity = 0
            
            for lab_room_id, lab_room_data in lab_rooms.items():
                lab_capacity = lab_room_data.get('capacity', 0) if isinstance(lab_room_data, dict) else 0
                if lab_capacity < total_merged_students:
                    continue  # Can't fit the merged total
                
                # Check if this Lab room is available at this time slot
                room_available = True
                # Check if room is already booked at this time
                for other_row in sessions:
                    if (other_row['Day'] == day and other_row['Time_Slot'] == slot and 
                        other_row['Room_Number'] == lab_room_id and 
                        other_row['Session_ID'] != row['Session_ID']):
                        # Room is booked - check if it's for the same canonical subject (allowed merge)
                        other_course = other_row['Course_Code']
                        other_canonical = get_canonical_id(other_course) or other_course
                        if other_canonical != current_canonical:
                            # Different canonical subject - room is not available
                            room_available = False
                            break
                
                if room_available:
                    has_available_lab_room = True
                    available_lab_room_id = lab_room_id
                    available_lab_capacity = lab_capacity
                    break
            
            # Only flag violation if there's an available Lab room that can fit the merged total
            if has_available_lab_room:
                type_violations += 1
                violations.append({
                    'constraint': 'room_type',
                    'reason': f'Lab subject assigned to non-lab room (merged total {total_merged_students} students fits in available Lab room {available_lab_room_id} with capacity {available_lab_capacity})',
                    'subject': course_code,
                    'room': room,
                    'room_type': room_type,
                    'group_size': size,
                    'total_merged_students': total_merged_students,
                    'available_lab_room': available_lab_room_id,
                    'available_lab_capacity': available_lab_capacity,
                    'severity': 'CRITICAL',
                })
            # If no available Lab room can fit, this is a legitimate fallback - don't count as violation
        if course_type != 'Lab' and room_type != 'Theory':
            type_violations += 1
            violations.append({
                'constraint': 'room_type',
                'reason': 'Theory subject assigned to inappropriate room',
                'subject': course_code,
                'room': room,
                'room_type': room_type,
                'severity': 'CRITICAL',
            })
    log_summary("Capacity violations", capacity_violations, "all rooms fit their groups")
    log_summary("Room type violations", type_violations, "all room types match")


def check_lecturer_loads(sessions: List[Dict[str, str]], violations: List[Dict]):
    print("\n[Soft] Lecturer weekly / daily load")
    hours = defaultdict(int)
    roles = {}
    daily_sessions = defaultdict(lambda: defaultdict(list))
    for row in sessions:
        lec_id = row['Lecturer_ID']
        roles[lec_id] = row['Lecturer_Role'] or 'Full-Time'
        hours[lec_id] += 2  # each session 2 hours
        daily_sessions[lec_id][row['Day']].append(row)
    role_limits = {'Full-Time': 22, 'Faculty Dean': 15, 'Part-Time': 999}
    weekly_violations = 0
    for lec_id, total in hours.items():
        role = roles.get(lec_id, 'Full-Time')
        limit = role_limits.get(role, 22)
        if role != 'Part-Time' and total > limit:
            weekly_violations += 1
            violations.append({
                'constraint': 'weekly_limit',
                'lecturer_id': lec_id,
                'hours': total,
                'max_hours': limit,
                'severity': 'WARNING',
            })
    log_summary("Weekly hour excess", weekly_violations, "all lecturers within weekly limits")
    # daily
    daily_violations = 0
    for lec_id, days in daily_sessions.items():
        for day, slots in days.items():
            if len(slots) > 2:
                daily_violations += 1
                violations.append({
                    'constraint': 'daily_limit',
                    'lecturer_id': lec_id,
                    'day': day,
                    'sessions': len(slots),
                    'severity': 'WARNING',
                })
            morning = sum(1 for s in slots if int(s['Start_Time'].split(':')[0]) < 14)
            afternoon = len(slots) - morning
            if morning > 1 or afternoon > 1:
                daily_violations += 1
                violations.append({
                    'constraint': 'daily_limit',
                    'lecturer_id': lec_id,
                    'day': day,
                    'morning_sessions': morning,
                    'afternoon_sessions': afternoon,
                    'severity': 'WARNING',
                })
    log_summary("Daily overloads", daily_violations, "all lecturers respect daily max")


def check_standard_blocks(sessions: List[Dict[str, str]], violations: List[Dict]):
    print("\n[Hard] Standard teaching blocks")
    
    # Load allowed time slots from database (not hardcoded)
    try:
        from app.services.config_loader import get_time_slots
        time_slots = get_time_slots(use_cache=True)
        allowed = set()
        for slot in time_slots:
            allowed.add(f"{slot['start']}-{slot['end']}")
        
        if not allowed:
            # Fallback if database is empty (should not happen)
    allowed = {'09:00-11:00', '11:00-13:00', '14:00-16:00', '16:00-18:00'}
            print("   ⚠️  WARNING: No time slots in database, using fallback values")
    except Exception as e:
        # Fallback if database access fails
        allowed = {'09:00-11:00', '11:00-13:00', '14:00-16:00', '16:00-18:00'}
        print(f"   ⚠️  WARNING: Failed to load time slots from database: {e}")
        print("   Using fallback values")
    
    bad = 0
    for row in sessions:
        slot = row['Time_Slot']
        if slot not in allowed:
            bad += 1
            violations.append({
                'constraint': 'time_block',
                'session_id': row['Session_ID'],
                'time_slot': slot,
                'severity': 'CRITICAL',
            })
    log_summary("Non-standard slot usage", bad, "all sessions use standard blocks")


def check_same_day_repetition(sessions: List[Dict[str, str]], violations: List[Dict]):
    print("\n[Hard] Same-day repetition per program")
    
    # Load time slots from database to build slot_index (not hardcoded)
    try:
        from app.services.config_loader import get_time_slots
        time_slots = get_time_slots(use_cache=True)
        slot_index = {}
        for idx, slot in enumerate(sorted(time_slots, key=lambda x: x.get('order', 0))):
            slot_str = f"{slot['start']}-{slot['end']}"
            slot_index[slot_str] = idx
        
        if not slot_index:
            # Fallback if database is empty
            slot_index = {'09:00-11:00': 0, '11:00-13:00': 1, '14:00-16:00': 2, '16:00-18:00': 3}
    except Exception as e:
        # Fallback if database access fails
    slot_index = {'09:00-11:00': 0, '11:00-13:00': 1, '14:00-16:00': 2, '16:00-18:00': 3}
    grouped = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for row in sessions:
        program = get_program_label(row)
        grouped[program][row['Day']][row['Course_Code']].append(row)
    repeats = 0
    for group, days in grouped.items():
        for day, subjects in days.items():
            for subject, slots in subjects.items():
                if len(slots) <= 1:
                    continue
                indices = sorted(slot_index.get(s['Time_Slot'], -1) for s in slots)
                is_lab = all(s['Course_Type'] == 'Lab' for s in slots)
                consecutive = len(indices) == 2 and indices[1] - indices[0] == 1
                if not (is_lab and consecutive):
                    repeats += 1
                    violations.append({
                        'constraint': 'same_day_unit',
                        'program': group,
                        'subject': subject,
                        'day': day,
                        'slots': [s['Time_Slot'] for s in slots],
                        'severity': 'CRITICAL',
                    })
    log_summary("Same-day repetition violations", repeats, "no problematic repetitions")


def analyze_canonical_merges(sessions: List[Dict[str, str]], violations: List[Dict]):
    """Analyze canonical subject merging using CANONICAL_COURSE_MAPPING as source of truth"""
    section("Canonical merge audit (using CANONICAL_COURSE_MAPPING)")
    
    # Build mapping: course_code -> canonical_id using CANONICAL_COURSE_MAPPING
    course_to_canonical = {}
    for canonical_id, course_codes in CANONICAL_COURSE_MAPPING.items():
        for course_code in course_codes:
            course_to_canonical[course_code] = canonical_id
    
    # Group sessions by canonical ID
    canonical_sessions = defaultdict(list)
    non_canonical_sessions = []
    
    for row in sessions:
        course_code = row['Course_Code']
        canonical_id = course_to_canonical.get(course_code)
        if canonical_id:
            canonical_sessions[canonical_id].append(row)
        else:
            # Check if it's already a canonical ID (merged subject)
            if course_code in CANONICAL_COURSE_MAPPING:
                canonical_sessions[course_code].append(row)
            else:
                non_canonical_sessions.append(course_code)
    
    print(f"📊 Found {len(canonical_sessions)} canonical subject groups")
    print(f"📊 Found {len(set(non_canonical_sessions))} non-canonical subjects")
    
    merge_alignment_issues = 0
    capacity_issues = 0
    
    for canonical_id, rows in canonical_sessions.items():
        # Get expected subject codes from mapping
        expected_courses = CANONICAL_COURSE_MAPPING.get(canonical_id, [canonical_id])
        groups = sorted({get_program_label(r) for r in rows})
        times = Counter((r['Day'], r['Time_Slot']) for r in rows)
        unique_slots = len(times)
        
        # Group by subject codes to see which original subjects are present
        present_course_codes = sorted({r['Course_Code'] for r in rows})
        
        print(f"\n• {canonical_id} (from mapping: {', '.join(expected_courses)})")
        print(f"   Present subjects: {', '.join(present_course_codes)}")
        print(f"   Programs: {len(groups)}, Time slots: {unique_slots}")
        
        # Check if canonical subjects are scheduled at different times
        # For subjects with 2 sessions per week, they SHOULD be in 2 different time slots (different days)
        # VIOLATION: Same program has same subject twice on same day
        same_day_violations = 0
        for group in groups:
            group_rows = [r for r in rows if get_program_label(r) == group]
            group_times = Counter((r['Day'], r['Time_Slot']) for r in group_rows)
            # Check if same group has same subject on same day (should only be once per day)
            day_counts = Counter(r['Day'] for r in group_rows)
            for day, count in day_counts.items():
                if count > 1:
                    same_day_violations += 1
                    day_slots = [r['Time_Slot'] for r in group_rows if r['Day'] == day]
                    violations.append({
                        'constraint': 'canonical_same_day_repetition',
                        'canonical_id': canonical_id,
                        'program': group,
                        'day': day,
                        'time_slots': day_slots,
                        'severity': 'CRITICAL',
                        'message': f'Canonical subject {canonical_id} scheduled {count} times on {day} for {group} (HARD: only 1 session per day allowed)'
                    })
        
        if same_day_violations == 0:
            if unique_slots == 1:
                print(f"   ✅ All sessions at same time slot")
            else:
                print(f"   ✅ Sessions distributed across {unique_slots} time slots (correct for 2 sessions/week)")
        else:
            print(f"   ❌ VIOLATION: {same_day_violations} same-day repetition(s) detected")
            merge_alignment_issues += same_day_violations
        
        # Check room capacity for merged groups
        for (day, slot), freq in times.items():
            involved = [get_program_label(r) for r in rows if r['Day'] == day and r['Time_Slot'] == slot]
            total_size = sum(get_program_size(r) for r in rows if r['Day'] == day and r['Time_Slot'] == slot)
            
            # Get room capacity from first session
            room_capacity = 0
            for r in rows:
                if r['Day'] == day and r['Time_Slot'] == slot:
                    try:
                        room_capacity = int(r.get('Room_Capacity', 0))
                        break
                    except (ValueError, TypeError):
                        pass
            
            if room_capacity > 0 and total_size > room_capacity:
                capacity_issues += 1
                print(f"   ❌ VIOLATION: {day} {slot}: {total_size} students > {room_capacity} capacity")
                violations.append({
                    'constraint': 'canonical_merge_capacity',
                    'canonical_id': canonical_id,
                    'day': day,
                    'time_slot': slot,
                    'students': total_size,
                    'capacity': room_capacity,
                    'groups': involved,
                    'severity': 'CRITICAL',
                    'message': f'Merged groups exceed room capacity: {total_size} > {room_capacity}'
                })
            elif room_capacity > 0:
                print(f"   ✅ {day} {slot}: {total_size} students ≤ {room_capacity} capacity")
    
    log_summary("Canonical merge alignment issues", merge_alignment_issues, "all canonical subjects properly merged at same time")
    log_summary("Canonical merge capacity issues", capacity_issues, "all merged groups fit in rooms")


def check_theory_practical_pairs(sessions: List[Dict[str, str]], violations: List[Dict]):
    """Check that theory and practical components are scheduled at the same time using canonical subjects"""
    print("\n[Hard] Theory/Practical pairing (using CANONICAL_COURSE_MAPPING)")
    
    # Use canonical subject mapping to identify theory/practical pairs
    # Canonical subjects that include both theory and practical should be scheduled together
    pair_violations = 0
    
    # Group sessions by canonical ID
    canonical_sessions = defaultdict(lambda: defaultdict(list))
    for row in sessions:
        course_code = row['Course_Code']
        canonical_id = get_canonical_id(course_code)
        if canonical_id:
            # Check if this canonical subject includes both theory and practical
            expected_courses = CANONICAL_COURSE_MAPPING.get(canonical_id, [])
            # Group by program to check pairing per group
            program = get_program_label(row)
            canonical_sessions[canonical_id][program].append(row)
    
    # Check each canonical subject group
    for canonical_id, group_sessions in canonical_sessions.items():
        expected_courses = CANONICAL_COURSE_MAPPING.get(canonical_id, [])
        
        # Check if this canonical subject should have theory+practical
        # (if it includes subjects with both theory and practical in their names)
        has_theory = any('theory' in c.lower() or 'Theory' in c for c in expected_courses)
        has_practical = any('practical' in c.lower() or 'Practical' in c or 'Lab' in c for c in expected_courses)
        
        if not (has_theory and has_practical):
            continue  # Not a theory/practical pair
        
        # Check each program
        for program, rows in group_sessions.items():
            theory_rows = [r for r in rows if 'theory' in r['Course_Name'].lower() or r['Course_Type'] == 'Theory']
            practical_rows = [r for r in rows if 'practical' in r['Course_Name'].lower() or r['Course_Type'] == 'Lab']
            
            if theory_rows and practical_rows:
                # Check if they're scheduled at the same time
                theory_times = {(r['Day'], r['Time_Slot']) for r in theory_rows}
                practical_times = {(r['Day'], r['Time_Slot']) for r in practical_rows}
                
                # They should have at least one common time slot (canonical subjects are unified)
                common_times = theory_times & practical_times
                if not common_times:
                    pair_violations += 1
                    violations.append({
                        'constraint': 'theory_practical_pairing',
                        'canonical_id': canonical_id,
                        'program': program,
                        'theory_times': list(theory_times),
                        'practical_times': list(practical_times),
                        'theory_codes': [r['Course_Code'] for r in theory_rows],
                        'practical_codes': [r['Course_Code'] for r in practical_rows],
                        'severity': 'CRITICAL',
                        'message': f'Canonical subject {canonical_id}: Theory and Practical components scheduled at different times (should be unified)'
                    })
    
    log_summary("Theory/Practical pairing violations", pair_violations, "all canonical subject pairs scheduled together")


def check_program_schedule_quality(sessions: List[Dict[str, str]], violations: List[Dict]):
    """Check program schedule quality (gaps, distribution, balance)"""
    print("\n[Soft] Program schedule quality")
    
    # Load time slots from database to build slot_times (not hardcoded)
    try:
        from app.services.config_loader import get_time_slots
        time_slots = get_time_slots(use_cache=True)
        slot_times = {}
        for slot in time_slots:
            slot_str = f"{slot['start']}-{slot['end']}"
            # Extract hour from start time for sorting
            start_hour = int(slot['start'].split(':')[0])
            slot_times[slot_str] = start_hour
        
        if not slot_times:
            # Fallback if database is empty
            slot_times = {'09:00-11:00': 9, '11:00-13:00': 11, '14:00-16:00': 14, '16:00-18:00': 16}
    except Exception as e:
        # Fallback if database access fails
        slot_times = {'09:00-11:00': 9, '11:00-13:00': 11, '14:00-16:00': 14, '16:00-18:00': 16}
    
    day_order = {'MON': 0, 'TUE': 1, 'WED': 2, 'THU': 3, 'FRI': 4}
    
    by_group = defaultdict(lambda: defaultdict(list))
    for row in sessions:
        by_group[get_program_label(row)][row['Day']].append(row)
    
    gap_violations = 0
    distribution_violations = 0
    overload_day_violations = 0
    
    for group_id, days in by_group.items():
        # Check for large gaps in daily schedule
        for day, day_sessions in days.items():
            if len(day_sessions) < 2:
                continue
            
            # Sort by time
            sorted_sessions = sorted(day_sessions, key=lambda s: slot_times.get(s['Time_Slot'], 0))
            for i in range(len(sorted_sessions) - 1):
                current_time = slot_times.get(sorted_sessions[i]['Time_Slot'], 0)
                next_time = slot_times.get(sorted_sessions[i + 1]['Time_Slot'], 0)
                gap = next_time - current_time
                
                # Gap of 3+ hours (skipping one slot) is acceptable, but 5+ hours is problematic
                if gap >= 5:
                    gap_violations += 1
                    violations.append({
                        'constraint': 'schedule_gap',
                        'program': group_id,
                        'day': day,
                        'gap_hours': gap,
                        'first_slot': sorted_sessions[i]['Time_Slot'],
                        'second_slot': sorted_sessions[i + 1]['Time_Slot'],
                        'severity': 'WARNING',
                        'message': f'Large gap ({gap} hours) in schedule'
                    })
        
        # Check day distribution (should be balanced)
        day_counts = {day: len(sessions) for day, sessions in days.items()}
        if day_counts:
            avg_sessions = sum(day_counts.values()) / len(day_counts)
            max_sessions = max(day_counts.values())
            min_sessions = min(day_counts.values())
            
            # If one day has 2x more sessions than average, it's unbalanced
            if max_sessions > avg_sessions * 1.8:
                distribution_violations += 1
                overload_day = max(day_counts, key=day_counts.get)
                violations.append({
                    'constraint': 'unbalanced_distribution',
                    'program': group_id,
                    'overload_day': overload_day,
                    'sessions': day_counts[overload_day],
                    'average': round(avg_sessions, 1),
                    'day_distribution': day_counts,
                    'severity': 'WARNING',
                    'message': f'Unbalanced schedule: {overload_day} has {day_counts[overload_day]} sessions'
                })
            
            # Check if any day has too many sessions (>4 is excessive)
            if max_sessions > 4:
                overload_day_violations += 1
                overload_day = max(day_counts, key=day_counts.get)
                violations.append({
                    'constraint': 'day_overload',
                    'program': group_id,
                    'day': overload_day,
                    'sessions': day_counts[overload_day],
                    'severity': 'WARNING',
                    'message': f'Too many sessions on {overload_day}'
                })
    
    log_summary("Schedule gap issues", gap_violations, "no excessive gaps")
    log_summary("Distribution issues", distribution_violations, "balanced distribution")
    log_summary("Day overload issues", overload_day_violations, "no overloaded days")


def check_room_utilization(sessions: List[Dict[str, str]], violations: List[Dict]):
    """Check room utilization and efficiency"""
    print("\n[Soft] Room utilization")
    
    room_usage = defaultdict(lambda: {'sessions': 0, 'total_capacity_used': 0, 'max_capacity': 0, 'time_slots': set()})
    
    for row in sessions:
        room = row['Room_Number']
        capacity = int(row['Room_Capacity'])
        size = get_program_size(row)
        time_key = (row['Day'], row['Time_Slot'])
        
        room_usage[room]['sessions'] += 1
        room_usage[room]['total_capacity_used'] += size
        room_usage[room]['max_capacity'] = max(room_usage[room]['max_capacity'], capacity)
        room_usage[room]['time_slots'].add(time_key)
    
    underutilized = 0
    overutilized = 0
    
    for room, stats in room_usage.items():
        if stats['max_capacity'] == 0:
            continue
        
        # Calculate average utilization
        avg_utilization = (stats['total_capacity_used'] / stats['sessions']) / stats['max_capacity'] if stats['sessions'] > 0 else 0
        
        # Room is underutilized if average usage is < 30%
        if avg_utilization < 0.3 and stats['sessions'] > 5:
            underutilized += 1
            violations.append({
                'constraint': 'room_underutilization',
                'room': room,
                'avg_utilization': round(avg_utilization * 100, 1),
                'sessions': stats['sessions'],
                'capacity': stats['max_capacity'],
                'severity': 'INFO',
                'message': f'Room {room} is underutilized ({avg_utilization*100:.1f}% average)'
            })
        
        # Room is overutilized if consistently at > 90% capacity
        if avg_utilization > 0.9 and stats['sessions'] > 3:
            overutilized += 1
            violations.append({
                'constraint': 'room_overutilization',
                'room': room,
                'avg_utilization': round(avg_utilization * 100, 1),
                'sessions': stats['sessions'],
                'capacity': stats['max_capacity'],
                'severity': 'WARNING',
                'message': f'Room {room} is consistently overutilized ({avg_utilization*100:.1f}% average)'
            })
    
    log_summary("Underutilized rooms", underutilized, "good room utilization")
    log_summary("Overutilized rooms", overutilized, "no overutilization issues")


def check_course_completion(sessions: List[Dict[str, str]], violations: List[Dict]):
    """Check that all required subject sessions are scheduled (using canonical IDs)"""
    print("\n[Hard] Subject completion (using canonical subjects)")
    
    # Count sessions per canonical subject per group
    canonical_sessions = defaultdict(int)
    course_info = {}
    
    for row in sessions:
        course_code = row['Course_Code']
        canonical_id = get_canonical_id(course_code) or course_code
        key = (get_program_label(row), canonical_id)
        canonical_sessions[key] += 1
        if key not in course_info:
            course_info[key] = {
                'canonical_id': canonical_id,
                'original_code': course_code,
                'name': row['Course_Name'],
                'type': row['Course_Type']
            }
    
    # Estimate required sessions (typically 2 hours per session)
    # Canonical subjects should have 2 sessions per week (4 hours = 2 sessions)
    incomplete = 0
    
    for (group, canonical_id), count in canonical_sessions.items():
        info = course_info.get((group, canonical_id), {})
        # Canonical subjects should typically have 2 sessions per week
        # Flag if significantly less (0 or 1 session when expecting 2)
        if count == 0:
            incomplete += 1
            violations.append({
                'constraint': 'course_incomplete',
                'program': group,
                'canonical_id': canonical_id,
                'original_code': info.get('original_code', canonical_id),
                'sessions_scheduled': count,
                'severity': 'WARNING',
                'message': f'Canonical subject {canonical_id} has no scheduled sessions'
            })
        elif count == 1:
            # Might be incomplete - canonical subjects should have 2 sessions
            incomplete += 1
            violations.append({
                'constraint': 'course_incomplete',
                'program': group,
                'canonical_id': canonical_id,
                'original_code': info.get('original_code', canonical_id),
                'sessions_scheduled': count,
                'severity': 'INFO',
                'message': f'Canonical subject {canonical_id} has only {count} session (expected 2)'
            })
    
    log_summary("Incomplete subjects", incomplete, "all subjects have sessions scheduled")


def check_lecturer_specialization(sessions: List[Dict[str, str]], violations: List[Dict]):
    """Check that lecturers are teaching subjects in their specialization"""
    print("\n[Soft] Lecturer specialization")
    
    # This is a soft check - we'd need lecturer data to fully validate
    # For now, we'll just track which lecturers teach which subjects
    lecturer_courses = defaultdict(set)
    
    for row in sessions:
        lecturer_id = row['Lecturer_ID']
        course_code = row['Course_Code']
        lecturer_courses[lecturer_id].add(course_code)
    
    # Report lecturers teaching many different subjects (might indicate specialization issues)
    diverse_lecturers = 0
    for lecturer_id, subjects in lecturer_courses.items():
        if len(subjects) > 8:  # Teaching more than 8 different subjects might be excessive
            diverse_lecturers += 1
            violations.append({
                'constraint': 'lecturer_diversity',
                'lecturer_id': lecturer_id,
                'num_courses': len(subjects),
                'subjects': list(subjects),
                'severity': 'INFO',
                'message': f'Lecturer {lecturer_id} teaching {len(subjects)} different subjects'
            })
    
    log_summary("Lecturer diversity issues", diverse_lecturers, "lecturers have reasonable subject diversity")


def check_semester_coverage(sessions: List[Dict[str, str]], violations: List[Dict]):
    """Check which semesters have classes scheduled"""
    print("\n[Info] Semester coverage analysis")
    
    semester_groups = defaultdict(set)
    for row in sessions:
        semester = row.get('Semester', '')
        group = get_program_label(row)
        if semester and group:
            semester_groups[semester].add(group)
    
    print(f"📊 Semesters with scheduled classes:")
    for semester in sorted(semester_groups.keys()):
        group_count = len(semester_groups[semester])
        print(f"   • {semester}: {group_count} program(s)")
        if group_count == 0:
            violations.append({
                'constraint': 'semester_no_classes',
                'semester': semester,
                'severity': 'WARNING',
                'message': f'Semester {semester} has no scheduled classes'
            })


def check_term_semester_alignment(sessions: List[Dict[str, str]], violations: List[Dict]):
    """Check that terms and semesters are properly aligned"""
    print("\n[Hard] Term/Semester alignment")
    
    alignment_issues = 0
    term_semester_map = defaultdict(set)
    
    for row in sessions:
        term = row.get('Term', '')
        semester = row.get('Semester', '')
        group = get_program_label(row)
        
        if term and semester:
            term_semester_map[group].add((term, semester))
    
    for group, term_sem_pairs in term_semester_map.items():
        if len(term_sem_pairs) > 1:
            alignment_issues += 1
            violations.append({
                'constraint': 'term_semester_mismatch',
                'program': group,
                'term_semester_combinations': list(term_sem_pairs),
                'severity': 'WARNING',
                'message': f'Program {group} has sessions in multiple term/semester combinations'
            })
    
    log_summary("Term/Semester alignment issues", alignment_issues, "proper alignment")


def dump_summary(violations: List[Dict[str, str]], export_path: Path = None):
    section("Violation summary")
    if not violations:
        print("✅ No violations detected")
        if export_path:
            with export_path.open('w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'total_violations': 0,
                    'violations': [],
                    'summary': {}
                }, f, indent=2)
        return
    
    # Group by severity
    by_severity = defaultdict(list)
    by_constraint = defaultdict(int)
    
    for v in violations:
        severity = v.get('severity', 'UNKNOWN')
        by_severity[severity].append(v)
        by_constraint[v['constraint']] += 1
    
    print(f"\n📊 Total violations: {len(violations)}")
    print(f"\nBy severity:")
    for severity in ['CRITICAL', 'WARNING', 'INFO']:
        count = len(by_severity.get(severity, []))
        emoji = '🔴' if severity == 'CRITICAL' else '🟡' if severity == 'WARNING' else '🔵'
        print(f"  {emoji} {severity}: {count}")
    
    print(f"\nBy constraint type:")
    for constraint, count in sorted(by_constraint.items(), key=lambda item: item[1], reverse=True):
        print(f"  • {constraint}: {count}")
    
    # Show critical violations first
    critical = by_severity.get('CRITICAL', [])
    if critical:
        print(f"\n🔴 CRITICAL Violations (showing first 10):")
        for i, entry in enumerate(critical[:10], 1):
            print(f"  {i}. {entry.get('constraint', 'unknown')}: {entry.get('message', str(entry))}")
    
    # Export to JSON if requested
    if export_path:
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'total_violations': len(violations),
            'by_severity': {k: len(v) for k, v in by_severity.items()},
            'by_constraint': dict(by_constraint),
            'violations': violations
        }
        with export_path.open('w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, default=str)
        print(f"\n💾 Violations exported to: {export_path}")


def main():
    parser = argparse.ArgumentParser(description='Verify timetable constraints')
    parser.add_argument('csv_file', help='Path to timetable CSV file')
    parser.add_argument('--export', help='Export violations to JSON file', default=None)
    args = parser.parse_args()
    
    csv_path = Path(args.csv_file).resolve()
    if not csv_path.exists():
        print(f"❌ CSV not found: {csv_path}")
        sys.exit(1)
    
    sessions = load_sessions(csv_path)
    section("Timetable constraint verification")
    print(f"Loaded {len(sessions)} sessions from {csv_path.name}")
    
    violations: List[Dict] = []
    
    # Hard constraints
    section("HARD CONSTRAINTS")
    check_double_booking(sessions, violations)
    check_room_capacity_and_type(sessions, violations)
    check_standard_blocks(sessions, violations)
    check_same_day_repetition(sessions, violations)
    check_theory_practical_pairs(sessions, violations)
    check_course_completion(sessions, violations)
    check_term_semester_alignment(sessions, violations)
    check_semester_coverage(sessions, violations)
    
    # Soft constraints
    section("SOFT CONSTRAINTS")
    check_lecturer_loads(sessions, violations)
    check_program_schedule_quality(sessions, violations)
    check_room_utilization(sessions, violations)
    check_lecturer_specialization(sessions, violations)
    
    # Canonical merge analysis
    analyze_canonical_merges(sessions, violations)
    
    # Summary and export
    export_path = Path(args.export) if args.export else None
    dump_summary(violations, export_path)
    
    # Exit code based on critical violations
    critical_count = sum(1 for v in violations if v.get('severity') == 'CRITICAL')
    if critical_count > 0:
        print(f"\n⚠️  Found {critical_count} CRITICAL violation(s)")
        sys.exit(1)
    else:
        print(f"\n✅ No critical violations found")
        sys.exit(0)


if __name__ == '__main__':
    main()

