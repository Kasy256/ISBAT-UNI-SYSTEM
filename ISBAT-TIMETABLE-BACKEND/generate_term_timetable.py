"""
Generate Term-Based University Timetable
Generates timetables for a SPECIFIC TERM (Term1 or Term2) across ALL semesters
All programs share the same academic terms
"""

import sys
import io
sys.path.insert(0, '.')

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from pymongo import MongoClient
from datetime import datetime
import csv
from collections import defaultdict
import argparse

from app.models.lecturer import Lecturer
from app.models.course import CourseUnit
from app.models.room import Room
from app.models.student import StudentGroup
from app.services.preprocessing.term_splitter import TermSplitter
from app.services.preprocessing.canonical_term_planner import build_canonical_term_alignment
from app.services.csp.csp_engine import CSPEngine
from app.services.gga.gga_engine import GGAEngine
from app.config import Config
from app.services.canonical_courses import get_canonical_id, CANONICAL_COURSE_MAPPING

def setup_database():
    """Connect to MongoDB"""
    mongo_uri = Config.MONGO_URI
    db_name = Config.MONGO_DB_NAME
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    db = client[db_name]
    return client, db

def fetch_all_data(db):
    """Fetch all data from database"""
    print("\n📥 Loading university data...")
    
    # Load student groups (batch is stored but not used for filtering)
    query = {'is_active': True}
    student_groups_data = list(db.student_groups.find(query))
    student_groups = [StudentGroup.from_dict(sg) for sg in student_groups_data]
    
    # Load all courses
    courses_data = list(db.course_units.find())
    courses = {CourseUnit.from_dict(c).id: CourseUnit.from_dict(c) for c in courses_data}
    
    # Load all lecturers
    lecturers_data = list(db.lecturers.find())
    lecturers = {Lecturer.from_dict(l).id: Lecturer.from_dict(l) for l in lecturers_data}
    
    # Load all rooms
    rooms_data = list(db.rooms.find())
    rooms = {Room.from_dict(r).id: Room.from_dict(r) for r in rooms_data}
    
    print(f"   ✅ {len(student_groups)} student groups")
    print(f"   ✅ {len(courses)} courses")
    print(f"   ✅ {len(lecturers)} lecturers")
    print(f"   ✅ {len(rooms)} rooms")
    
    return student_groups, courses, lecturers, rooms

def get_term_courses_for_group(student_group, courses, term_number, canonical_alignment=None):
    """Get courses for a specific term for a student group"""
    course_ids = []
    for cu in student_group.course_units:
        if isinstance(cu, dict):
            course_id = cu.get('code')
            if course_id:
                course_ids.append(course_id)
        elif isinstance(cu, str):
            course_ids.append(cu)
    
    group_courses = [courses[cu_id] for cu_id in course_ids if cu_id in courses]
    
    if not group_courses:
        return []
    
    term_splitter = TermSplitter()
    
    try:
        term1_plan, term2_plan = term_splitter.split_semester(
            student_group.semester,
            group_courses,
            canonical_alignment=canonical_alignment,
            program=student_group.program
        )
        
        if term_number == 1:
            return term1_plan.assigned_units
        elif term_number == 2:
            return term2_plan.assigned_units
        else:
            raise ValueError(f"Invalid term number: {term_number}. Must be 1 or 2.")
            
    except ValueError as e:
        print(f"   ⚠️  Warning for {student_group.display_name}: {str(e)}")
        
        course_groups = {}
        standalone_courses = []
        for course in group_courses:
            if course.course_group:
                if course.course_group not in course_groups:
                    course_groups[course.course_group] = []
                course_groups[course.course_group].append(course)
            else:
                standalone_courses.append(course)
        
        effective_units = list(course_groups.values()) + [[c] for c in standalone_courses]
        effective_unit_count = len(effective_units)
        
        ratio = term_splitter.split_ratios.get(student_group.semester)
        if not ratio:
            term1_unit_count = effective_unit_count // 2
        else:
            total_expected = ratio.term1_units + ratio.term2_units
            if total_expected == 0:
                term1_unit_count = effective_unit_count // 2
            else:
                term1_ratio = ratio.term1_units / total_expected
                term1_unit_count = max(1, int(effective_unit_count * term1_ratio))
                term1_unit_count = min(term1_unit_count, effective_unit_count - 1)
        
        preferred_term1_units = []
        preferred_term2_units = []
        flexible_units = []
        
        for unit_group in effective_units:
            forced_term = None
            if canonical_alignment:
                for course in unit_group:
                    canonical_id = course.canonical_id
                    if canonical_id and canonical_id in canonical_alignment:
                        forced_term = canonical_alignment[canonical_id]
                        break

            has_term1_pref = forced_term == 1 or any(
                (c.preferred_term in ["Term 1", "Term1", "1"]) for c in unit_group
            )
            has_term2_pref = forced_term == 2 or any(
                (c.preferred_term in ["Term 2", "Term2", "2"]) for c in unit_group
            )
            
            if has_term1_pref:
                preferred_term1_units.append(unit_group)
            elif has_term2_pref:
                preferred_term2_units.append(unit_group)
            else:
                flexible_units.append(unit_group)
        
        term1_courses = [c for unit_group in preferred_term1_units for c in unit_group]
        term2_courses = [c for unit_group in preferred_term2_units for c in unit_group]
        
        remaining_term1_slots = max(0, term1_unit_count - len(preferred_term1_units))
        remaining_term2_slots = max(0, effective_unit_count - term1_unit_count - len(preferred_term2_units))
        
        flexible_sorted = sorted(flexible_units, key=lambda unit_group: (
            not any(c.is_foundational for c in unit_group),
            any(c.difficulty == "Hard" for c in unit_group)
        ))
        
        assigned_term1_count = len(preferred_term1_units)
        for unit_group in flexible_sorted:
            if assigned_term1_count < term1_unit_count and remaining_term1_slots > 0:
                term1_courses.extend(unit_group)
                remaining_term1_slots -= 1
                assigned_term1_count += 1
            else:
                term2_courses.extend(unit_group)
                remaining_term2_slots -= 1
        
        if term_number == 1:
            return term1_courses
        else:
            return term2_courses


def clean_course_name(name: str) -> str:
    """
    Remove 'Theory' and 'Practical' suffixes from course names.
    For canonical courses that combine theory and practical, display clean name.
    
    Examples:
        'Programming in C - Theory' -> 'Programming in C'
        'Programming in C - Practical' -> 'Programming in C'
        'Object Oriented Programming Using JAVA - Theory' -> 'Object Oriented Programming Using JAVA'
    """
    if not name:
        return name
    
    # Remove common suffixes
    name = name.replace(' - Theory', '').replace(' - Practical', '')
    name = name.replace(' Theory', '').replace(' Practical', '')
    name = name.replace('-Theory', '').replace('-Practical', '')
    name = name.replace('--Theory', '').replace('--Practical', '')
    
    # Clean up any double spaces or trailing dashes
    name = name.replace('  ', ' ').strip()
    if name.endswith(' -'):
        name = name[:-2].strip()
    if name.endswith('-'):
        name = name[:-1].strip()
    
    return name


def _create_merged_course(canonical_id, canonical_courses, data, courses_dict, groups, 
                          merged_course_units, canonical_course_codes):
    """Helper function to create a merged course unit."""
    prototype = data['prototype']
    
    # If no courses found in mapping, fall back to collected courses
    if not canonical_courses:
        canonical_courses = [prototype]
        seen_course_ids = {prototype.id}
        for group_info in groups:
            course_id = group_info['course_id']
            if course_id not in seen_course_ids and course_id in courses_dict:
                canonical_courses.append(courses_dict[course_id])
                seen_course_ids.add(course_id)
    
    # Since canonical mapping already combines theory+practical as ONE unified unit,
    # all courses in the mapping represent components of the same course
    # Use the maximum hours from any component (they're all part of one course)
    if canonical_courses:
        total_weekly_hours = max(c.weekly_hours for c in canonical_courses)
    else:
        total_weekly_hours = prototype.weekly_hours
    
    # Use canonical courses for other properties too
    courses_for_props = canonical_courses if canonical_courses else [prototype]
    total_credits = max(c.credits for c in courses_for_props)
    # CRITICAL: If any component has a lab (practical), the merged course is a Lab course
    has_lab = any(c.preferred_room_type == 'Lab' for c in courses_for_props)
    preferred_room_type = 'Lab' if has_lab else 'Theory'
    preserved_course_group = f"{canonical_id}_GROUP"
    total_sessions_required = (total_weekly_hours + 1) // 2
    
    # Clean the course name - remove "Theory" and "Practical" suffixes
    # Use the cleanest name from all canonical courses
    clean_names = [clean_course_name(c.name) for c in courses_for_props]
    # Prefer the longest clean name (most descriptive)
    clean_name = max(clean_names, key=len) if clean_names else clean_course_name(prototype.name)
    
    merged_course = CourseUnit(
        id=canonical_id,
        code=prototype.code,
        name=clean_name,  # Use cleaned name without Theory/Practical suffix
        weekly_hours=total_weekly_hours,
        credits=total_credits,
        preferred_room_type=preferred_room_type,  # Lab if any component is a lab
        difficulty=prototype.difficulty,
        is_foundational=prototype.is_foundational,
        prerequisites=prototype.prerequisites,
        corequisites=prototype.corequisites,
        preferred_term=prototype.preferred_term,
        semester=prototype.semester,
        program=prototype.program,
        course_group=preserved_course_group
    )
    merged_course._sessions_required = total_sessions_required
    merged_course_units.append(merged_course)
    courses_dict[canonical_id] = merged_course


def merge_equivalent_courses(group_entries, term_number, courses_dict, rooms_list=None):
    """Merge equivalent courses across student groups using canonical IDs."""
    canonical_map = {}
    merged_student_groups = []
    merged_course_units = []
    merged_group_details = {}

    for entry in group_entries:
        original_group = entry['original_group']
        term_courses = entry['term_courses']

        for course in term_courses:
            canonical_id = get_canonical_id(course.id) or course.id
            data = canonical_map.setdefault(canonical_id, {
                'prototype': course,
                'groups': []
            })
            data['groups'].append({
                'student_group': original_group,
                'course_id': course.id
            })

    for canonical_id, data in canonical_map.items():
        groups = data['groups']
        
        # CRITICAL FIX: Deduplicate by student_group.id before summing
        # Multiple course units (e.g., BIT1101, BIT1106) can map to the same canonical_id,
        # but they're taken by the SAME student group, so we should only count each group once
        unique_student_groups = {}
        course_units_per_group = {}  # Track which course units each group has
        for g in groups:
            student_group = g['student_group']
            course_id = g['course_id']
            # Use student_group.id as key to ensure we only count each group once
            if student_group.id not in unique_student_groups:
                unique_student_groups[student_group.id] = student_group
                course_units_per_group[student_group.id] = []
            course_units_per_group[student_group.id].append(course_id)
        
        # Sum sizes of unique student groups only
        total_size = sum(sg.size for sg in unique_student_groups.values())
        
        # Debug output: Show deduplication if multiple course units per group
        if len(groups) > len(unique_student_groups):
            print(f"   📊 {canonical_id}: {len(groups)} course entries → {len(unique_student_groups)} unique groups (total: {total_size} students)")
            for group_id, course_ids in course_units_per_group.items():
                if len(course_ids) > 1:
                    group = unique_student_groups[group_id]
                    print(f"      • {group.display_name} ({group.size} students): {', '.join(course_ids)}")
        
        # Get canonical course codes and courses (needed for course creation)
        canonical_course_codes = CANONICAL_COURSE_MAPPING.get(canonical_id, [])
        canonical_courses = []
        for course_code in canonical_course_codes:
            if course_code in courses_dict:
                canonical_courses.append(courses_dict[course_code])
        
        # Merge all groups into one
        merged_group_id = f"MERGED_{canonical_id}_T{term_number}"

        merged_student_group = StudentGroup.from_dict({
            'id': merged_group_id,
            'batch': 'MERGED',
            'program': 'MERGED',
            'semester': f"S*_T{term_number}",
            'term': f"Term{term_number}",
            'size': total_size,
            'course_units': [canonical_id],
            'is_active': True
        })
        merged_student_groups.append(merged_student_group)

        # Create merged course using helper function
        _create_merged_course(
            canonical_id, canonical_courses, data, courses_dict, groups,
            merged_course_units, canonical_course_codes
        )

        merged_group_details[merged_group_id] = {
            'canonical_id': canonical_id,
            'groups': groups
        }

    return merged_student_groups, merged_course_units, merged_group_details


def try_reschedule_conflict(assignment, group_time_slots, courses, lecturers, rooms, all_assignments):
    """
    Try to reschedule a conflicting assignment to a different time slot.
    Prioritizes slots with at least 1 free day gap from existing sessions.
    
    Returns:
        Rescheduled assignment dict if successful, None otherwise
    """
    from app.services.csp.domain import TimeSlot
    
    course = courses.get(assignment['course_id'])
    lecturer = lecturers.get(assignment['lecturer_id'])
    original_room = rooms.get(assignment['room_id'])
    group_id = assignment['student_group_id']
    group_size = assignment.get('group_size', 0)
    
    if not course or not lecturer:
        return None
    
    # Get all rooms of the correct type
    available_rooms = [r for r in rooms.values() 
                      if r.room_type == course.preferred_room_type 
                      and r.capacity >= group_size]
    
    if not available_rooms:
        return None
    
    # Get all time slots for this course
    DAYS = ['MON', 'TUE', 'WED', 'THU', 'FRI']
    PERIODS = {
        'SLOT_1': {'start': '09:00', 'end': '11:00'},
        'SLOT_2': {'start': '11:00', 'end': '13:00'},
        'SLOT_3': {'start': '14:00', 'end': '16:00'},
        'SLOT_4': {'start': '16:00', 'end': '18:00'}
    }
    
    # Find existing assignments for this course and group
    existing_sessions = []
    for a in all_assignments:
        if a['student_group_id'] == group_id and a['course_id'] == assignment['course_id']:
            existing_sessions.append(a)
    
    # Collect all candidate slots, prioritizing those with better day gaps
    candidates = []  # List of (day, period, times, room, day_gap_score)
    
    for day in DAYS:
        for period, times in PERIODS.items():
            time_slot_str = f"{times['start']}-{times['end']}"
            key = (group_id, day, time_slot_str)
            
            # Skip if this time slot is already occupied
            if key in group_time_slots:
                continue
            
            # Calculate day gap score (higher is better - prefer at least 1 day gap)
            day_gap_score = 0
            if existing_sessions:
                existing_days = {a['day'] for a in existing_sessions}
                day_index = DAYS.index(day)
                min_gap = 10  # Large number
                for existing_day in existing_days:
                    existing_index = DAYS.index(existing_day)
                    gap = abs(day_index - existing_index)
                    min_gap = min(min_gap, gap)
                
                # Score: 0 if same/adjacent day, 1 if 1 day gap, 2 if 2+ day gap
                if min_gap >= 2:
                    day_gap_score = 2
                elif min_gap == 1:
                    day_gap_score = 1
                else:
                    day_gap_score = 0  # Same or adjacent day - not ideal but acceptable if no other option
            else:
                day_gap_score = 2  # No existing sessions, so any day is fine
            
            # Check lecturer availability
            lecturer_busy = False
            for a in all_assignments:
                if (a['lecturer_id'] == lecturer.id and 
                    a['day'] == day and 
                    a['time_slot']['start'] == times['start']):
                    lecturer_busy = True
                    break
            if lecturer_busy:
                continue
            
            # Try each available room
            for room in available_rooms:
                # Check room availability
                room_busy = False
                for a in all_assignments:
                    if (a['room_id'] == room.id and 
                        a['day'] == day and 
                        a['time_slot']['start'] == times['start']):
                        room_busy = True
                        break
                if room_busy:
                    continue
                
                # Valid candidate found
                candidates.append((day, period, times, room, day_gap_score))
    
    # Sort candidates by day gap score (best first), then by day
    candidates.sort(key=lambda x: (-x[4], x[0]))  # Negative score for descending order
    
    # Try candidates in order of preference
    for day, period, times, room, day_gap_score in candidates:
        # Create rescheduled assignment
        rescheduled = assignment.copy()
        rescheduled['day'] = day
        rescheduled['room_id'] = room.id
        rescheduled['time_slot'] = {
            'day': day,
            'period': period,
            'start': times['start'],
            'end': times['end'],
            'is_afternoon': times['start'] >= '14:00'
        }
        return rescheduled
    
    return None


def expand_assignment_dicts(gene, merged_group_details, original_groups_dict, courses, term_number):
    """
    Expand merged assignments into per-group assignments for export.
    Creates ONE row per student group, using the canonical course ID.
    """
    expanded = []
    details = merged_group_details.get(gene.student_group_id)

    if not details:
        original_group = original_groups_dict.get(gene.student_group_id)
        course = courses.get(gene.course_unit_id)
        if not original_group or not course:
            return expanded
        expanded.append({
            'session_id': gene.session_id,
            'student_group_id': original_group.id,
            'student_group_name': original_group.display_name,
            'semester': original_group.semester,
            'term': f'Term{term_number}',
            'group_size': original_group.size,
            'course_id': gene.course_unit_id,
            'lecturer_id': gene.lecturer_id,
            'room_id': gene.room_id,
            'day': gene.time_slot.day,
            'time_slot': gene.time_slot.to_dict(),
            'session_number': gene.session_number
        })
        return expanded

    canonical_id = details['canonical_id']
    seen_groups = set()
    
    for idx, group_info in enumerate(details['groups'], start=1):
        original_group = group_info['student_group']
        
        if original_group.id in seen_groups:
            continue
        
        seen_groups.add(original_group.id)
        expanded.append({
            'session_id': f"{gene.session_id}_{original_group.id}",
            'student_group_id': original_group.id,
            'student_group_name': original_group.display_name,
            'semester': original_group.semester,
            'term': f'Term{term_number}',
            'group_size': original_group.size,
            'course_id': canonical_id,
            'lecturer_id': gene.lecturer_id,
            'room_id': gene.room_id,
            'day': gene.time_slot.day,
            'time_slot': gene.time_slot.to_dict(),
            'session_number': gene.session_number
        })

    return expanded

def generate_term_timetable(term_number):
    """
    Generate timetable for a specific term across ALL semesters
    
    Args:
        term_number: 1 for Term1, 2 for Term2
    """
    start_time = datetime.now()
    
    print("\n" + "="*70)
    print(f"          TERM {term_number} TIMETABLE GENERATION")
    print("="*70)
    print(f"\n🎯 Generating timetable for: TERM {term_number}")
    print(f"   Scope: ALL semesters (S1-S6)")
    print(f"   All programs share the same academic terms\n")
    
    try:
        # Setup
        client, db = setup_database()
        
        # Load all data
        student_groups, courses, lecturers, rooms = fetch_all_data(db)
        
        if not student_groups:
            print("❌ No student groups found!")
            return
        
        canonical_alignment, canonical_decisions = build_canonical_term_alignment(student_groups, courses)
        if canonical_alignment:
            print("\n🔗 Canonical course alignment:")
            print(f"   • {len(canonical_alignment)} canonical families forced into shared terms")
            sample_items = list(canonical_decisions.items())[:5]
            for canonical_id, data in sample_items:
                print(f"     - {canonical_id}: Term {data['assigned_term']} ({data['reason']})")
            if len(canonical_decisions) > 5:
                print(f"     ... and {len(canonical_decisions) - 5} more canonical groups")
            conflicts = [cid for cid, data in canonical_decisions.items() if data['conflicts']]
            if conflicts:
                print(f"   ⚠️ Conflicts detected for: {', '.join(conflicts)}")
        else:
            print("\n🔗 Canonical course alignment:")
            print("   • No cross-program canonical courses detected for this dataset")

        # Collect all term-specific courses and student groups
        term_student_groups = []
        term_courses_by_group = {}
        
        print(f"\n📋 Processing student groups for Term {term_number}...")
        print("─"*70)
        
        group_term_entries = []

        for student_group in student_groups:
            term_courses = get_term_courses_for_group(
                student_group,
                courses,
                term_number,
                canonical_alignment=canonical_alignment
            )
            
            if term_courses:
                # Create term-specific student group
                term_student_group = StudentGroup.from_dict({
                    **student_group.to_dict(),
                    'term': f'Term{term_number}',
                    'course_units': [c.id for c in term_courses]
                })
                
                term_student_groups.append(term_student_group)
                term_courses_by_group[term_student_group.id] = term_courses
                group_term_entries.append({
                    'original_group': student_group,
                    'term_group': term_student_group,
                    'term_courses': term_courses
                })
                
                # Track all unique courses
                for course in term_courses:
                    pass
                
                print(f"   ✅ {student_group.display_name}: {len(term_courses)} courses")
            else:
                print(f"   ⚠️  {student_group.display_name}: No courses for Term {term_number}")
        
        if not term_student_groups:
            print(f"\n❌ No student groups have courses for Term {term_number}!")
            client.close()
            return

        original_student_groups_dict = {sg.id: sg for sg in student_groups}
        merged_student_groups, merged_course_units, merged_group_details = merge_equivalent_courses(
            group_term_entries,
            term_number,
            courses
        )
        
        term_student_groups = merged_student_groups
        term_student_groups_dict = {sg.id: sg for sg in term_student_groups}
        all_term_courses_list = merged_course_units
        
        print(f"\n📊 Summary:")
        total_sessions_to_schedule = sum(course.sessions_required for course in merged_course_units)
        print(f"   • Student Groups: {len(term_student_groups)} (merged)")
        print(f"   • Unique Courses: {len(merged_course_units)}")
        print(f"   • Total Sessions to Schedule: {total_sessions_to_schedule}")
        
        # Step 1: CSP - Generate initial timetable for ALL groups together
        print(f"\n{'='*70}")
        print("🧩 Step 1: CSP Engine - Satisfying Hard Constraints")
        print("="*70)
        print(f"   Scheduling ALL semesters together for Term {term_number}...")
        
        csp_engine = CSPEngine()
        csp_engine.initialize(
            lecturers=list(lecturers.values()),
            rooms=list(rooms.values()),
            course_units=all_term_courses_list,
            student_groups=term_student_groups,
            merged_group_details=merged_group_details
        )
        
        print("   Running CSP solver...")
        csp_solution = csp_engine.solve()
        
        if not csp_solution:
            print("   ❌ CSP failed to find any assignments!")
            print("   This may indicate resource constraints (rooms, lecturers, time slots)")
            client.close()
            return
        
        total_sessions = len(csp_engine.variables)
        if len(csp_solution) < total_sessions:
            print(f"   ⚠️  CSP Partial Solution: {len(csp_solution)}/{total_sessions} sessions scheduled")
            print(f"   💡 GGA will attempt to complete the remaining {total_sessions - len(csp_solution)} sessions")
        else:
            print(f"   ✅ CSP Complete Solution: {len(csp_solution)} sessions scheduled")
        
        # Step 2: Convert CSP solution to Chromosome for GGA
        from app.services.gga.chromosome import Chromosome, Gene
        
        genes = []
        for assignment in csp_solution:
            gene = Gene(
                session_id=assignment.variable_id,
                course_unit_id=assignment.course_unit_id,
                student_group_id=assignment.student_group_id,
                lecturer_id=assignment.lecturer_id,
                room_id=assignment.room_id,
                time_slot=assignment.time_slot,
                term=assignment.term,
                session_number=assignment.session_number
            )
            genes.append(gene)
        
        csp_chromosome = Chromosome(id=f'CSP_Term{term_number}_Initial', genes=genes)
        
        # Extract variable pairs and canonical course groups for GGA
        # Use canonical course mapping as source of truth
        variable_pairs = csp_engine.variable_pairs
        canonical_course_groups = {}  # Canonical courses that should be scheduled together
        
        # Build canonical course groups using CANONICAL_COURSE_MAPPING directly
        # Group genes by canonical ID (from the mapping)
        from collections import defaultdict
        canonical_genes_map = defaultdict(lambda: defaultdict(list))
        
        for g in genes:
            # Get canonical ID for this course
            canonical_id = get_canonical_id(g.course_unit_id) or g.course_unit_id
            # Only include if it's in the canonical mapping (shared/merged courses)
            if canonical_id in CANONICAL_COURSE_MAPPING:
                canonical_genes_map[canonical_id][g.session_number].append(g.session_id)
        
        # Convert to the format GGA expects
        for canonical_id, session_map in canonical_genes_map.items():
            # Only include if there are multiple sessions (need to keep them together)
            if any(len(gene_ids) > 1 for gene_ids in session_map.values()):
                canonical_course_groups[canonical_id] = dict(session_map)
        
        # Step 3: GGA - Optimize for soft constraints
        print(f"\n{'='*70}")
        print("🧬 Step 2: GGA Engine - Optimizing Soft Constraints")
        print("="*70)
        
        # Prepare resource dictionaries for GGA
        course_units_dict = {c.id: c for c in all_term_courses_list}
        student_groups_dict = {sg.id: sg for sg in term_student_groups}
        
        gga_engine = GGAEngine(
            course_units=course_units_dict,
            student_groups=student_groups_dict,
            lecturers=lecturers,
            rooms=rooms,
            variable_pairs=variable_pairs,  # Pass theory/practical pairs
            canonical_course_groups=canonical_course_groups  # Pass canonical course groups
        )
        
        # Use more generations for comprehensive optimization (especially weekday balance)
        gga_engine.max_generations = 200  # Increased from 100
        gga_engine.population_size = 200  # Increased from 150
        
        print("   Running GGA optimization...")
        optimized_chromosome = gga_engine.optimize(csp_chromosome)
        
        print(f"   ✅ Optimized Solution: {len(optimized_chromosome.genes)} sessions")
        if optimized_chromosome.fitness:
            print(f"   ✅ Fitness Score: {optimized_chromosome.fitness.overall_fitness:.4f}")
        
        # Step 4: Export to CSV
        print(f"\n{'='*70}")
        print("📊 Step 3: Exporting Timetable")
        print("="*70)
        
        # Convert to assignment dicts
        assignment_dicts = []
        # Track conflicts to prevent double-booking when expanding merged groups
        group_time_slots = {}  # {(student_group_id, day, time_slot): [assignment_dicts]}
        conflicts_found = 0
        conflicts_rescheduled = 0
        conflicts_failed = 0
        pending_conflicts = []  # Store conflicts that need rescheduling
        
        # First pass: collect all assignments and detect conflicts
        for gene in optimized_chromosome.genes:
            expanded = expand_assignment_dicts(
                gene,
                merged_group_details,
                original_student_groups_dict,
                courses,
                term_number
            )
            
            # Check for conflicts before adding
            for assignment in expanded:
                group_id = assignment['student_group_id']
                day = assignment['day']
                time_slot_str = f"{assignment['time_slot']['start']}-{assignment['time_slot']['end']}"
                key = (group_id, day, time_slot_str)
                
                if key in group_time_slots:
                    # Conflict detected - try to reschedule instead of skipping
                    conflicting = group_time_slots[key]
                    conflicts_found += 1
                    print(f"   ⚠️  CONFLICT DETECTED: {group_id} has multiple courses at {day} {time_slot_str}")
                    print(f"      Existing: {conflicting[0].get('course_id', 'unknown')}")
                    print(f"      New: {assignment.get('course_id', 'unknown')}")
                    # Store for rescheduling attempt
                    pending_conflicts.append(assignment)
                    continue
                
                assignment_dicts.append(assignment)
                if key not in group_time_slots:
                    group_time_slots[key] = []
                group_time_slots[key].append(assignment)
        
        # Second pass: Try to reschedule conflicts
        if pending_conflicts:
            print(f"   🔄 Attempting to reschedule {len(pending_conflicts)} conflicting assignments...")
            for conflict_assignment in pending_conflicts:
                rescheduled = try_reschedule_conflict(
                    conflict_assignment, 
                    group_time_slots, 
                    courses, 
                    lecturers, 
                    rooms, 
                    assignment_dicts
                )
                
                if rescheduled:
                    # Successfully rescheduled
                    group_id = rescheduled['student_group_id']
                    day = rescheduled['day']
                    time_slot_str = f"{rescheduled['time_slot']['start']}-{rescheduled['time_slot']['end']}"
                    key = (group_id, day, time_slot_str)
                    
                    assignment_dicts.append(rescheduled)
                    if key not in group_time_slots:
                        group_time_slots[key] = []
                    group_time_slots[key].append(rescheduled)
                    conflicts_rescheduled += 1
                    print(f"      ✅ Rescheduled {rescheduled['course_id']} for {group_id} to {day} {time_slot_str}")
                else:
                    # Failed to reschedule
                    conflicts_failed += 1
                    print(f"      ❌ Failed to reschedule {conflict_assignment['course_id']} for {conflict_assignment['student_group_id']}")
        
        # Validate before export
        if conflicts_found > 0:
            print(f"   📊 Conflict Resolution Summary:")
            print(f"      • Total conflicts: {conflicts_found}")
            print(f"      • Successfully rescheduled: {conflicts_rescheduled}")
            print(f"      • Failed to reschedule: {conflicts_failed}")
            if conflicts_failed > 0:
                print(f"      ⚠️  {conflicts_failed} assignments could not be rescheduled and were removed")
        
        # Validate course completion: Check if all courses have required sessions
        course_session_counts = defaultdict(lambda: defaultdict(int))  # {course_id: {group_id: count}}
        for assignment in assignment_dicts:
            course_id = assignment['course_id']
            group_id = assignment['student_group_id']
            course_session_counts[course_id][group_id] += 1
        
        incomplete_courses = []
        for course_id, group_counts in course_session_counts.items():
            course = courses.get(course_id)
            if not course:
                continue
            required_sessions = course.sessions_required
            for group_id, count in group_counts.items():
                if count < required_sessions:
                    incomplete_courses.append({
                        'course_id': course_id,
                        'course_code': course.code if course else course_id,
                        'group_id': group_id,
                        'required': required_sessions,
                        'actual': count
                    })
        
        if incomplete_courses:
            print(f"   ⚠️  Found {len(incomplete_courses)} incomplete course assignments:")
            for inc in incomplete_courses[:10]:  # Show first 10
                print(f"      • {inc['course_code']} for {inc['group_id']}: {inc['actual']}/{inc['required']} sessions")
            if len(incomplete_courses) > 10:
                print(f"      ... and {len(incomplete_courses) - 10} more")
        else:
            print(f"   ✅ All courses have required number of sessions")
        
        # Additional validation: Check for room type violations
        room_type_violations = []
        for assignment in assignment_dicts:
            course = courses.get(assignment['course_id'])
            room = rooms.get(assignment['room_id'])
            if course and room:
                if course.preferred_room_type == 'Lab' and room.room_type != 'Lab':
                    room_type_violations.append({
                        'course': course.code,
                        'room': room.room_number,
                        'expected': 'Lab',
                        'actual': room.room_type
                    })
                elif course.preferred_room_type == 'Theory' and room.room_type != 'Theory':
                    room_type_violations.append({
                        'course': course.code,
                        'room': room.room_number,
                        'expected': 'Theory',
                        'actual': room.room_type
                    })
        
        if room_type_violations:
            print(f"   ⚠️  Found {len(room_type_violations)} room type violations in exported assignments")
            for v in room_type_violations[:5]:  # Show first 5
                print(f"      - {v['course']} (needs {v['expected']}) assigned to room {v['room']} ({v['actual']})")
            if len(room_type_violations) > 5:
                print(f"      ... and {len(room_type_violations) - 5} more")
        
        # Export
        filename = f'TIMETABLE_TERM{term_number}_COMPLETE.csv'
        export_to_csv(assignment_dicts, courses, lecturers, rooms, filename, term_number)
        
        # Generate statistics
        generate_statistics(assignment_dicts, courses, lecturers, rooms, filename, term_number)
        
        # Close connection
        client.close()
        
        # Final summary
        elapsed = (datetime.now() - start_time).total_seconds()
        
        print(f"\n{'='*70}")
        print("                    ✅ GENERATION COMPLETE!")
        print("="*70)
        print(f"\n📊 Statistics:")
        print(f"   • Term: Term {term_number}")
        print(f"   • Total Sessions: {len(assignment_dicts)}")
        print(f"   • Student Groups: {len(term_student_groups)}")
        print(f"   • Unique Courses: {len(merged_course_units)}")
        print(f"   • Time Elapsed: {elapsed:.2f} seconds")
        print(f"\n📁 Output Files:")
        print(f"   • {filename}")
        print(f"   • {filename.replace('.csv', '_SUMMARY.txt')}")
        print(f"\n🎉 Term {term_number} timetable successfully generated!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

def export_to_csv(assignments, courses, lecturers, rooms, filename, term_number):
    """Export timetable to CSV"""
    
    headers = [
        "Session_ID", "Day", "Time_Slot", "Start_Time", "End_Time",
        "Course_Code", "Course_Name", "Course_Type", "Credits",
        "Lecturer_ID", "Lecturer_Name", "Lecturer_Role",
        "Room_Number", "Room_Type", "Room_Capacity", "Room_Building", "Room_Campus",
        "Student_Group", "Semester", "Term", "Group_Size"
    ]
    
    # Handle file permission errors (file might be open in Excel)
    import os
    from datetime import datetime
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            
            for assignment in assignments:
                course = courses.get(assignment['course_id'], None)
                lecturer = lecturers.get(assignment['lecturer_id'], None)
                room = rooms.get(assignment['room_id'], None)
                
                if not course or not lecturer or not room:
                    continue
                
                ts = assignment['time_slot']
                
                row = {
                    "Session_ID": assignment['session_id'],
                    "Day": assignment['day'],
                    "Time_Slot": f"{ts['start']}-{ts['end']}",
                    "Start_Time": ts['start'],
                    "End_Time": ts['end'],
                    "Course_Code": course.code,
                    "Course_Name": clean_course_name(course.name),  # Clean name without Theory/Practical
                    "Course_Type": course.preferred_room_type,
                    "Credits": course.credits,
                    "Lecturer_ID": lecturer.id,
                    "Lecturer_Name": lecturer.name,
                    "Lecturer_Role": lecturer.role,
                    "Room_Number": room.room_number,
                    "Room_Type": room.room_type,
                    "Room_Capacity": room.capacity,
                    "Room_Building": room.building,
                    "Room_Campus": getattr(room, 'campus', 'N/A'),
                    "Student_Group": assignment['student_group_name'],
                    "Semester": assignment['semester'],
                    "Term": f"Term{term_number}",
                    "Group_Size": assignment['group_size']
                }
                writer.writerow(row)
        
        print(f"   ✅ Exported {len(assignments)} sessions to {filename}")
    except PermissionError:
        # File is likely open in Excel, try with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = filename.replace('.csv', '')
        fallback_filename = f"{base_name}_{timestamp}.csv"
        try:
            with open(fallback_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                
                for assignment in assignments:
                    course = courses.get(assignment['course_id'], None)
                    lecturer = lecturers.get(assignment['lecturer_id'], None)
                    room = rooms.get(assignment['room_id'], None)
                    
                    row = {
                        "Session_ID": assignment['session_id'],
                        "Day": assignment['day'],
                        "Time_Slot": assignment['time_slot'],
                        "Start_Time": assignment['start_time'],
                        "End_Time": assignment['end_time'],
                        "Course_Code": course.code if course else "N/A",
                        "Course_Name": clean_course_name(course.name) if course else "N/A",  # Clean name
                        "Course_Type": course.preferred_room_type if course else "Theory",
                        "Credits": course.credits if course else 0,
                        "Lecturer_ID": lecturer.id if lecturer else "N/A",
                        "Lecturer_Name": lecturer.name if lecturer else "N/A",
                        "Lecturer_Role": lecturer.role if lecturer else "N/A",
                        "Room_Number": room.room_number if room else "N/A",
                        "Room_Type": room.room_type if room else "N/A",
                        "Room_Capacity": room.capacity if room else 0,
                        "Room_Building": room.building if room else "N/A",
                        "Room_Campus": getattr(room, 'campus', 'N/A') if room else "N/A",
                        "Student_Group": assignment['student_group_name'],
                        "Semester": assignment['semester'],
                        "Term": f"Term{term_number}",
                        "Group_Size": assignment['group_size']
                    }
                    writer.writerow(row)
            
            print(f"   ⚠️  Original file locked, exported to: {fallback_filename}")
        except Exception as e2:
            print(f"   ❌ Failed to export CSV: {e2}")
            print(f"   💡 Please close any open CSV files and try again")

def generate_statistics(assignments, courses, lecturers, rooms, csv_filename, term_number):
    """Generate comprehensive statistics"""
    
    # Group by various dimensions
    by_semester = defaultdict(int)
    by_day = defaultdict(int)
    by_course = defaultdict(int)
    by_lecturer = defaultdict(int)
    by_room = defaultdict(int)
    
    for assignment in assignments:
        by_semester[assignment['semester']] += 1
        by_day[assignment['day']] += 1
        by_course[assignment['course_id']] += 1
        by_lecturer[assignment['lecturer_id']] += 1
        by_room[assignment['room_id']] += 1
    
    # Create summary file
    summary_filename = csv_filename.replace('.csv', '_SUMMARY.txt')
    
    with open(summary_filename, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write(f"          TERM {term_number} TIMETABLE - COMPREHENSIVE SUMMARY\n")
        f.write("="*70 + "\n\n")
        
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Term: Term {term_number}\n")
        f.write(f"Total Sessions: {len(assignments)}\n\n")
        
        f.write("="*70 + "\n")
        f.write("SESSIONS BY SEMESTER\n")
        f.write("="*70 + "\n")
        for sem, count in sorted(by_semester.items()):
            f.write(f"  {sem}: {count} sessions\n")
        
        f.write("\n" + "="*70 + "\n")
        f.write("SESSIONS BY DAY\n")
        f.write("="*70 + "\n")
        for day in ['MON', 'TUE', 'WED', 'THU', 'FRI']:
            count = by_day.get(day, 0)
            f.write(f"  {day}: {count} sessions\n")
        
        f.write("\n" + "="*70 + "\n")
        f.write("TOP 10 COURSES (by sessions)\n")
        f.write("="*70 + "\n")
        top_courses = sorted(by_course.items(), key=lambda x: x[1], reverse=True)[:10]
        for course_id, count in top_courses:
            course = courses.get(course_id)
            if course:
                f.write(f"  {course.code} - {course.name}: {count} sessions\n")
        
        f.write("\n" + "="*70 + "\n")
        f.write("TOP 10 LECTURERS (by sessions)\n")
        f.write("="*70 + "\n")
        top_lecturers = sorted(by_lecturer.items(), key=lambda x: x[1], reverse=True)[:10]
        for lec_id, count in top_lecturers:
            lecturer = lecturers.get(lec_id)
            if lecturer:
                f.write(f"  {lecturer.name}: {count} sessions\n")
        
        f.write("\n" + "="*70 + "\n")
        f.write("TOP 10 ROOMS (by usage)\n")
        f.write("="*70 + "\n")
        top_rooms = sorted(by_room.items(), key=lambda x: x[1], reverse=True)[:10]
        for room_id, count in top_rooms:
            room = rooms.get(room_id)
            if room:
                f.write(f"  {room.room_number} ({room.room_type}): {count} sessions\n")
        
        f.write("\n" + "="*70 + "\n")
    
    print(f"   ✅ Summary: {summary_filename}")

def main():
    """Main execution with command-line interface"""
    parser = argparse.ArgumentParser(
        description='Generate term-based university timetable',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate Term1 timetable
  python generate_term_timetable.py --term 1
  
  # Generate Term2 timetable
  python generate_term_timetable.py --term 2
  
  # Generate Term1 timetable (interactive)
  python generate_term_timetable.py
        """
    )
    
    parser.add_argument(
        '--term',
        type=int,
        choices=[1, 2],
        help='Term number (1 or 2)'
    )
    
    args = parser.parse_args()
    
    # If term not provided, prompt user
    if args.term is None:
        print("\n" + "="*70)
        print("          TERM-BASED TIMETABLE GENERATION")
        print("="*70)
        print("\nSelect term to generate:")
        print("  1. Term 1")
        print("  2. Term 2")
        
        while True:
            try:
                term_input = input("\nEnter term number (1 or 2): ").strip()
                term_number = int(term_input)
                if term_number in [1, 2]:
                    break
                else:
                    print("❌ Please enter 1 or 2")
            except ValueError:
                print("❌ Please enter a valid number (1 or 2)")
            except KeyboardInterrupt:
                print("\n\n❌ Cancelled by user")
                return
    else:
        term_number = args.term
    
    # Generate timetable
    generate_term_timetable(term_number)

if __name__ == '__main__':
    main()

