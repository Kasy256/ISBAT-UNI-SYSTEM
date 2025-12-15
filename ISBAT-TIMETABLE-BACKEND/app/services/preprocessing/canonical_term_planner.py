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


def build_canonical_term_alignment(programs, subjects: Dict[str, Any]) -> Tuple[Dict[str, int], Dict[str, Dict[str, Any]]]:
    """
    Build a global canonical term alignment so equivalent subjects land in the same term.
    
    This function performs an initial term split to see where subject groups (Theory+Practical pairs)
    actually get assigned, then aligns canonical subjects accordingly. This ensures that when
    one program has a subject group (e.g., BIT1212 Theory + BIT1214 Practical) assigned to a term,
    the equivalent subject in another program (e.g., BCS1212 Theory) is also assigned to that term.

    Returns:
        alignment (dict): canonical_id -> term_number (1 or 2)
        decisions (dict): canonical_id -> metadata about the decision
    """
    splitter = TermSplitter()
    canonical_occurrences = defaultdict(list)
    
    # First pass: Collect all canonical subjects with their metadata
    for group in programs:
        for cu in group.course_units:
            # Extract course code (handles "CODE - Name" format)
            if isinstance(cu, dict):
                course_id = (cu.get('code') or cu.get('id', '')).strip()
            elif isinstance(cu, str):
                # Extract code from "CODE - Name" format
                if " - " in cu:
                    course_id = cu.split(" - ")[0].strip()
                else:
                    course_id = cu.strip()
            else:
                continue
            subject = subjects.get(course_id)
            if not subject:
                continue
            canonical_id = subject.canonical_id
            if not canonical_id:
                continue

            canonical_occurrences[canonical_id].append({
                'subject': subject,
                'course_id': subject.id,
                'group_id': group.id,
                'group_name': group.display_name,
                'program': group.program,  # Store program identifier (string), not the Program object
                'semester': subject.semester or group.semester,
                'preferred_term': _normalize_term_value(subject.preferred_term),
                'course_group': subject.course_group
            })

    canonical_term_from_course_groups = {}
    
    # Group by semester to do term splits
    groups_by_semester = defaultdict(list)
    for group in programs:
        semester = group.semester
        groups_by_semester[semester].append(group)
    
    # For each semester, do initial term split to see where subject groups land
    for semester, groups in groups_by_semester.items():
        for group in groups:
            # Get all subjects for this group
            group_courses = []
            for cu in group.course_units:
                # Extract course code (handles "CODE - Name" format)
                if isinstance(cu, dict):
                    course_id = (cu.get('code') or cu.get('id', '')).strip()
                elif isinstance(cu, str):
                    # Extract code from "CODE - Name" format
                    if " - " in cu:
                        course_id = cu.split(" - ")[0].strip()
                    else:
                        course_id = cu.strip()
                else:
                    continue
                subject = subjects.get(course_id)
                if subject and (subject.semester or group.semester) == semester:
                    group_courses.append(subject)
            
            if group_courses:
                try:
                    # Do initial split (without canonical alignment) to see where subject groups land
                    # Pass program identifier for alternating ratios
                    program = getattr(group, 'program', None)
                    term1_plan, term2_plan = splitter.split_semester(semester, group_courses, program=program)
                    
                    # Track ALL canonical_ids from subjects in course_groups that were assigned to each term
                    # This ensures that when a course_group (like DATABASE_MGMT_SYSTEM_GROUP) is assigned to a term,
                    # ALL subjects with that canonical_id are tracked (e.g., BIT1212, BCS1212, BIT1214 all map to DATABASE_MGMT_SYSTEM)
                    for subject in term1_plan.assigned_units:
                        if subject.course_group and subject.canonical_id:
                            # If already set to Term 2, don't override (shouldn't happen, but be safe)
                            if canonical_term_from_course_groups.get(subject.canonical_id) != 2:
                                canonical_term_from_course_groups[subject.canonical_id] = 1
                    for subject in term2_plan.assigned_units:
                        if subject.course_group and subject.canonical_id:
                            # If already set to Term 1, don't override (shouldn't happen, but be safe)
                            if canonical_term_from_course_groups.get(subject.canonical_id) != 1:
                                canonical_term_from_course_groups[subject.canonical_id] = 2
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
        # If so, force all subjects with this canonical_id to that term
        assigned_term_from_group = canonical_term_from_course_groups.get(canonical_id)
        
        votes = Counter(o['preferred_term'] for o in occurrences if o['preferred_term'])
        assigned_term = None
        reason = ""
        conflicts = []

        # Priority 1: If a course_group with this canonical_id is assigned to a term, use that
        # This ensures that when BIT has Theory+Practical as 1 unit (course_group) and it's assigned
        # to a term, BCS's equivalent Theory-only subject is also assigned to that term
        # Example: BIT1212+BIT1214 (course_group) -> Term 1, then BCS1212 (Theory) -> Term 1
        if assigned_term_from_group is not None:
            assigned_term = assigned_term_from_group
            courses_with_group = [o for o in occurrences if o['course_group']]
            # Extract program identifier - handle both string and Program object cases
            programs_with_group = {
                o['program'].program if hasattr(o['program'], 'program') else o['program']
                for o in courses_with_group
            }
            if courses_with_group:
                group_name = courses_with_group[0]['course_group']
                if len(programs_with_group) > 1:
                    reason = f"Aligned with subject group {group_name} across programs (Term {assigned_term})"
                else:
                    reason = f"Aligned with subject group {group_name} (Term {assigned_term})"
            else:
                # This subject doesn't have a course_group, but another program's equivalent does
                reason = f"Aligned with equivalent subject group in another program (Term {assigned_term})"
        # Priority 2: Use preferred_term votes
        elif votes:
            assigned_term, count = votes.most_common(1)[0]
            reason = f"Majority preferred Term {assigned_term} ({count} vote{'s' if count != 1 else ''})"
            if len(votes) > 1:
                conflicts.append(f"Conflicting preferences: Term 1 = {votes.get(1, 0)}, Term 2 = {votes.get(2, 0)}")
        # Priority 3: Use heuristics (fallback - should rarely be needed)
        else:
            # is_foundational is no longer used - default to Term 1 if no preference
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
