from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any

from app.services.preprocessing.term_splitter import TermSplitter
from app.services.canonical_courses import get_canonical_id


def _normalize_term_value(value) -> int:
    if value is None:
        return None
    text = str(value).strip().lower()
    if text in {'term1', 'term 1', '1'}:
        return 1
    if text in {'term2', 'term 2', '2'}:
        return 2
    return None


def build_canonical_term_alignment(student_groups, courses: Dict[str, Any]) -> Tuple[Dict[str, int], Dict[str, Dict[str, Any]]]:
    """
    Build a global canonical term alignment so equivalent courses land in the same term.
    
    This function performs an initial term split to see where course groups (Theory+Practical pairs)
    actually get assigned, then aligns canonical courses accordingly. This ensures that when
    one program has a course group (e.g., BIT1212 Theory + BIT1214 Practical) assigned to a term,
    the equivalent course in another program (e.g., BCS1212 Theory) is also assigned to that term.

    Returns:
        alignment (dict): canonical_id -> term_number (1 or 2)
        decisions (dict): canonical_id -> metadata about the decision
    """
    splitter = TermSplitter()
    canonical_occurrences = defaultdict(list)
    
    # First pass: Collect all canonical courses with their metadata
    for group in student_groups:
        for cu in group.course_units:
            course_id = cu.get('code') if isinstance(cu, dict) else cu
            course = courses.get(course_id)
            if not course:
                continue
            canonical_id = course.canonical_id
            if not canonical_id:
                continue

            canonical_occurrences[canonical_id].append({
                'course': course,
                'course_id': course.id,
                'group_id': group.id,
                'group_name': group.display_name,
                'program': group.program,
                'semester': course.semester or group.semester,
                'preferred_term': _normalize_term_value(course.preferred_term),
                'course_group': course.course_group,
                'student_group': group
            })

    canonical_term_from_course_groups = {}
    
    # Group by semester to do term splits
    groups_by_semester = defaultdict(list)
    for group in student_groups:
        semester = group.semester
        groups_by_semester[semester].append(group)
    
    # For each semester, do initial term split to see where course groups land
    for semester, groups in groups_by_semester.items():
        for group in groups:
            # Get all courses for this group
            group_courses = []
            for cu in group.course_units:
                course_id = cu.get('code') if isinstance(cu, dict) else cu
                course = courses.get(course_id)
                if course and (course.semester or group.semester) == semester:
                    group_courses.append(course)
            
            if group_courses:
                try:
                    # Do initial split (without canonical alignment) to see where course groups land
                    # Pass program identifier for alternating ratios
                    program = getattr(group, 'program', None)
                    term1_plan, term2_plan = splitter.split_semester(semester, group_courses, program=program)
                    
                    # Track ALL canonical_ids from courses in course_groups that were assigned to each term
                    # This ensures that when a course_group (like DATABASE_MGMT_SYSTEM_GROUP) is assigned to a term,
                    # ALL courses with that canonical_id are tracked (e.g., BIT1212, BCS1212, BIT1214 all map to DATABASE_MGMT_SYSTEM)
                    for course in term1_plan.assigned_units:
                        if course.course_group and course.canonical_id:
                            # If already set to Term 2, don't override (shouldn't happen, but be safe)
                            if canonical_term_from_course_groups.get(course.canonical_id) != 2:
                                canonical_term_from_course_groups[course.canonical_id] = 1
                    for course in term2_plan.assigned_units:
                        if course.course_group and course.canonical_id:
                            # If already set to Term 1, don't override (shouldn't happen, but be safe)
                            if canonical_term_from_course_groups.get(course.canonical_id) != 1:
                                canonical_term_from_course_groups[course.canonical_id] = 2
                except Exception:
                    pass  # Skip if split fails

    alignment = {}
    decisions = {}

    for canonical_id, occurrences in canonical_occurrences.items():
        unique_courses = {o['course_id'] for o in occurrences}
        if len(unique_courses) <= 1:
            # No cross-program duplication, skip
            continue

        # Check if a course_group with this canonical_id has already been assigned to a term
        # If so, force all courses with this canonical_id to that term
        assigned_term_from_group = canonical_term_from_course_groups.get(canonical_id)
        
        votes = Counter(o['preferred_term'] for o in occurrences if o['preferred_term'])
        assigned_term = None
        reason = ""
        conflicts = []

        # Priority 1: If a course_group with this canonical_id is assigned to a term, use that
        # This ensures that when BIT has Theory+Practical as 1 unit (course_group) and it's assigned
        # to a term, BCS's equivalent Theory-only course is also assigned to that term
        # Example: BIT1212+BIT1214 (course_group) -> Term 1, then BCS1212 (Theory) -> Term 1
        if assigned_term_from_group is not None:
            assigned_term = assigned_term_from_group
            courses_with_group = [o for o in occurrences if o['course_group']]
            programs_with_group = {o['program'] for o in courses_with_group}
            if courses_with_group:
                group_name = courses_with_group[0]['course_group']
                if len(programs_with_group) > 1:
                    reason = f"Aligned with course group {group_name} across programs (Term {assigned_term})"
                else:
                    reason = f"Aligned with course group {group_name} (Term {assigned_term})"
            else:
                # This course doesn't have a course_group, but another program's equivalent does
                reason = f"Aligned with equivalent course group in another program (Term {assigned_term})"
        # Priority 2: Use preferred_term votes
        elif votes:
            assigned_term, count = votes.most_common(1)[0]
            reason = f"Majority preferred Term {assigned_term} ({count} vote{'s' if count != 1 else ''})"
            if len(votes) > 1:
                conflicts.append(f"Conflicting preferences: Term 1 = {votes.get(1, 0)}, Term 2 = {votes.get(2, 0)}")
        # Priority 3: Use heuristics
        else:
            is_foundational = any(o['course'].is_foundational for o in occurrences)
            if is_foundational:
                assigned_term = 1
                reason = "Defaulted to Term 1 (foundational course)"
            else:
                sample_semester = next((o['semester'] for o in occurrences if o['semester']), None)
                ratio = splitter.split_ratios.get(sample_semester) if sample_semester else None
                if ratio and ratio.term1_units != ratio.term2_units:
                    assigned_term = 1 if ratio.term1_units >= ratio.term2_units else 2
                    reason = f"Followed semester {sample_semester} ratio bias (Term {assigned_term})"
                else:
                    assigned_term = 1
                    reason = "Defaulted to Term 1 (no preferences)"

        alignment[canonical_id] = assigned_term
        decisions[canonical_id] = {
            'canonical_id': canonical_id,
            'assigned_term': assigned_term,
            'reason': reason,
            'votes': dict(votes),
            'conflicts': conflicts,
            'occurrences': [{
                'course_id': o['course_id'],
                'group_id': o['group_id'],
                'group_name': o['group_name'],
                'program': o['program'],
                'semester': o['semester'],
                'preferred_term': o['preferred_term'],
                'course_group': o['course_group']
            } for o in occurrences]
        }

    return alignment, decisions
