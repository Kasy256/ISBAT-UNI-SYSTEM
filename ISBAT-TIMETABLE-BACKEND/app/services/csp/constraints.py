"""CSP Constraint definitions for timetable scheduling."""

from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass
from enum import Enum


class ConstraintType(Enum):
    """Types of constraints"""
    NO_DOUBLE_BOOKING = "no_double_booking"
    ROOM_CAPACITY = "room_capacity"
    ROOM_TYPE = "room_type"
    LECTURER_SPECIALIZATION = "lecturer_specialization"
    WEEKLY_LIMIT = "weekly_limit"
    DAILY_LIMIT = "daily_limit"
    TIME_BLOCKS = "time_blocks"
    NO_SAME_DAY = "no_same_day_repetition"
    CLASS_MERGING = "class_merging"
    CLASS_SPLITTING = "class_splitting"
    PAIRING_CONSTRAINT = "pairing_constraint"  # Theory/practical must be scheduled together


@dataclass
class Assignment:
    """Represents an assignment of a session"""
    variable_id: str
    course_unit_id: str
    student_group_id: str
    lecturer_id: str
    room_id: str
    time_slot: Dict[str, Any]  # {day, period, start, end, is_afternoon}
    term: str


class Constraint:
    """Base constraint class"""
    
    def __init__(self, constraint_type: ConstraintType, scope: List[str]):
        self.type = constraint_type
        self.scope = scope  # Variable IDs this constraint affects
    
    def is_satisfied(self, assignment: Assignment, context: 'ConstraintContext') -> bool:
        """Check if constraint is satisfied by assignment"""
        raise NotImplementedError
    
    def get_violations(self, assignment: Assignment, context: 'ConstraintContext') -> List[str]:
        """Get list of constraint violations"""
        raise NotImplementedError


class ConstraintContext:
    """Context containing all scheduling information for constraint checking"""
    
    def __init__(self, variable_pairs: Optional[Dict[str, List[str]]] = None,
                 merged_to_original_groups: Optional[Dict[str, List[str]]] = None,
                 original_to_merged_groups: Optional[Dict[str, List[str]]] = None):
        self.lecturer_schedule: Dict[str, Dict[str, Set[str]]] = {}
        self.room_schedule: Dict[str, Dict[str, Set[str]]] = {}
        self.student_group_schedule: Dict[str, Dict[str, Set[str]]] = {}
        self.lecturer_daily_count: Dict[str, Dict[str, int]] = {}
        self.lecturer_morning_used: Dict[str, Dict[str, bool]] = {}
        self.lecturer_afternoon_used: Dict[str, Dict[str, bool]] = {}
        self.lecturer_weekly_hours: Dict[str, float] = {}
        self.unit_daily_schedule: Dict[tuple, Dict[str, bool]] = {}
        self.assignments: Dict[str, Assignment] = {}
        self.lecturers: Dict[str, Any] = {}
        self.rooms: Dict[str, Any] = {}
        self.course_units: Dict[str, Any] = {}
        self.student_groups: Dict[str, Any] = {}
        self.variable_pairs: Dict[str, List[str]] = variable_pairs or {}
        self.merged_to_original_groups: Dict[str, List[str]] = merged_to_original_groups or {}
        self.original_to_merged_groups: Dict[str, List[str]] = original_to_merged_groups or {}
        self.variable_to_student_group: Dict[str, str] = {}  # variable_id -> student_group_id
    
    def add_assignment(self, assignment: Assignment):
        """Add assignment and update indices"""
        self.assignments[assignment.variable_id] = assignment
        
        # Update schedules
        time_key = f"{assignment.time_slot.day}_{assignment.time_slot.period}"
        
        if assignment.lecturer_id not in self.lecturer_schedule:
            self.lecturer_schedule[assignment.lecturer_id] = {}
        if time_key not in self.lecturer_schedule[assignment.lecturer_id]:
            self.lecturer_schedule[assignment.lecturer_id][time_key] = set()
        self.lecturer_schedule[assignment.lecturer_id][time_key].add(assignment.variable_id)
        
        if assignment.room_id not in self.room_schedule:
            self.room_schedule[assignment.room_id] = {}
        if time_key not in self.room_schedule[assignment.room_id]:
            self.room_schedule[assignment.room_id][time_key] = set()
        self.room_schedule[assignment.room_id][time_key].add(assignment.variable_id)
        
        # Track assignment for the student group
        if assignment.student_group_id not in self.student_group_schedule:
            self.student_group_schedule[assignment.student_group_id] = {}
        if time_key not in self.student_group_schedule[assignment.student_group_id]:
            self.student_group_schedule[assignment.student_group_id][time_key] = set()
        self.student_group_schedule[assignment.student_group_id][time_key].add(assignment.variable_id)
        
        # CRITICAL: If this is a merged group, also track the assignment for all original groups
        # This ensures conflict checking works correctly for canonical courses across semesters
        if assignment.student_group_id in self.merged_to_original_groups:
            original_group_ids = self.merged_to_original_groups[assignment.student_group_id]
            for orig_group_id in original_group_ids:
                if orig_group_id not in self.student_group_schedule:
                    self.student_group_schedule[orig_group_id] = {}
                if time_key not in self.student_group_schedule[orig_group_id]:
                    self.student_group_schedule[orig_group_id][time_key] = set()
                self.student_group_schedule[orig_group_id][time_key].add(assignment.variable_id)
        
        day = assignment.time_slot.day
        if assignment.lecturer_id not in self.lecturer_daily_count:
            self.lecturer_daily_count[assignment.lecturer_id] = {}
        self.lecturer_daily_count[assignment.lecturer_id][day] = \
            self.lecturer_daily_count[assignment.lecturer_id].get(day, 0) + 1
        
        if assignment.lecturer_id not in self.lecturer_morning_used:
            self.lecturer_morning_used[assignment.lecturer_id] = {}
            self.lecturer_afternoon_used[assignment.lecturer_id] = {}
        
        if assignment.time_slot.is_afternoon:
            self.lecturer_afternoon_used[assignment.lecturer_id][day] = True
        else:
            self.lecturer_morning_used[assignment.lecturer_id][day] = True
        
        course_unit = self.course_units.get(assignment.course_unit_id)
        if course_unit:
            hours = 2
            self.lecturer_weekly_hours[assignment.lecturer_id] = \
                self.lecturer_weekly_hours.get(assignment.lecturer_id, 0) + hours
        
        unit_key = (assignment.student_group_id, assignment.course_unit_id)
        if unit_key not in self.unit_daily_schedule:
            self.unit_daily_schedule[unit_key] = {}
        self.unit_daily_schedule[unit_key][day] = True
    
    def remove_assignment(self, variable_id: str):
        """Remove assignment and update indices"""
        if variable_id not in self.assignments:
            return
        
        assignment = self.assignments[variable_id]
        time_key = f"{assignment.time_slot.day}_{assignment.time_slot.period}"
        
        if assignment.lecturer_id in self.lecturer_schedule:
            if time_key in self.lecturer_schedule[assignment.lecturer_id]:
                self.lecturer_schedule[assignment.lecturer_id][time_key].discard(variable_id)
        
        if assignment.room_id in self.room_schedule:
            if time_key in self.room_schedule[assignment.room_id]:
                self.room_schedule[assignment.room_id][time_key].discard(variable_id)
        
        # Remove from student group schedule
        if assignment.student_group_id in self.student_group_schedule:
            if time_key in self.student_group_schedule[assignment.student_group_id]:
                self.student_group_schedule[assignment.student_group_id][time_key].discard(variable_id)
        
        # CRITICAL: Also remove from original groups' schedules if this is a merged group
        if assignment.student_group_id in self.merged_to_original_groups:
            original_group_ids = self.merged_to_original_groups[assignment.student_group_id]
            for orig_group_id in original_group_ids:
                if orig_group_id in self.student_group_schedule:
                    if time_key in self.student_group_schedule[orig_group_id]:
                        self.student_group_schedule[orig_group_id][time_key].discard(variable_id)
        
        day = assignment.time_slot.day
        if assignment.lecturer_id in self.lecturer_daily_count:
            if day in self.lecturer_daily_count[assignment.lecturer_id]:
                self.lecturer_daily_count[assignment.lecturer_id][day] -= 1
                if self.lecturer_daily_count[assignment.lecturer_id][day] <= 0:
                    del self.lecturer_daily_count[assignment.lecturer_id][day]
        
        remaining_sessions = 0
        morning_sessions = 0
        afternoon_sessions = 0
        
        for var_id, other_assignment in self.assignments.items():
            if (var_id != variable_id and 
                other_assignment.lecturer_id == assignment.lecturer_id and
                other_assignment.time_slot.day == day):
                remaining_sessions += 1
                if other_assignment.time_slot.is_afternoon:
                    afternoon_sessions += 1
                else:
                    morning_sessions += 1
        
        if assignment.lecturer_id in self.lecturer_morning_used:
            if day in self.lecturer_morning_used[assignment.lecturer_id]:
                self.lecturer_morning_used[assignment.lecturer_id][day] = (morning_sessions > 0)
        
        if assignment.lecturer_id in self.lecturer_afternoon_used:
            if day in self.lecturer_afternoon_used[assignment.lecturer_id]:
                self.lecturer_afternoon_used[assignment.lecturer_id][day] = (afternoon_sessions > 0)
        
        hours = 2
        if assignment.lecturer_id in self.lecturer_weekly_hours:
            self.lecturer_weekly_hours[assignment.lecturer_id] -= hours
            if self.lecturer_weekly_hours[assignment.lecturer_id] <= 0:
                del self.lecturer_weekly_hours[assignment.lecturer_id]
        
        unit_key = (assignment.student_group_id, assignment.course_unit_id)
        if unit_key in self.unit_daily_schedule:
            if day in self.unit_daily_schedule[unit_key]:
                del self.unit_daily_schedule[unit_key][day]
        
        del self.assignments[variable_id]


class NoDoubleBookingConstraint(Constraint):
    """Ensures no lecturer, room, or student group is double-booked"""
    
    def __init__(self):
        super().__init__(ConstraintType.NO_DOUBLE_BOOKING, [])
        # Import canonical course utilities
        from app.services.canonical_courses import get_canonical_id, CANONICAL_COURSE_MAPPING
        self.get_canonical_id = get_canonical_id
        self.CANONICAL_COURSE_MAPPING = CANONICAL_COURSE_MAPPING
    
    def is_satisfied(self, assignment: Assignment, context: ConstraintContext) -> bool:
        """Check for double-booking conflicts"""
        time_key = f"{assignment.time_slot.day}_{assignment.time_slot.period}"
        
        def are_paired(var_id1: str, var_id2: str) -> bool:
            """Check if two variables are paired (bidirectional check)"""
            if not context.variable_pairs:
                return False
            pairs1 = context.variable_pairs.get(var_id1, [])
            pairs2 = context.variable_pairs.get(var_id2, [])
            # Check both directions: var_id2 in pairs1 OR var_id1 in pairs2
            return var_id2 in pairs1 or var_id1 in pairs2
        
        def are_canonical_merge(course_id1: str, course_id2: str) -> bool:
            """Check if two courses are canonical merges (same canonical ID)"""
            canonical1 = self.get_canonical_id(course_id1)
            canonical2 = self.get_canonical_id(course_id2)
            # If both have the same canonical ID (and it's not None), they should be merged
            if canonical1 and canonical2:
                return canonical1 == canonical2
            # If one or both don't have canonical IDs, they're not canonical merges
            return False
        
        if assignment.lecturer_id in context.lecturer_schedule:
            if time_key in context.lecturer_schedule[assignment.lecturer_id]:
                existing = context.lecturer_schedule[assignment.lecturer_id][time_key]
                if len(existing) > 0:
                    if assignment.variable_id not in existing:
                        # Check if all existing assignments are either paired OR canonical merges
                        all_compatible = True
                        for existing_id in existing:
                            if are_paired(assignment.variable_id, existing_id):
                                continue
                            existing_assignment = context.assignments.get(existing_id)
                            if existing_assignment:
                                if are_canonical_merge(assignment.course_unit_id, existing_assignment.course_unit_id):
                                    continue
                            # Not paired and not canonical merge - conflict!
                            all_compatible = False
                            break
                        if not all_compatible:
                            return False
        
        if assignment.room_id in context.room_schedule:
            if time_key in context.room_schedule[assignment.room_id]:
                existing = context.room_schedule[assignment.room_id][time_key]
                if len(existing) > 0:
                    if assignment.variable_id not in existing:
                        # Check if all existing assignments are either paired OR canonical merges
                        all_compatible = True
                        for existing_id in existing:
                            if are_paired(assignment.variable_id, existing_id):
                                continue
                            existing_assignment = context.assignments.get(existing_id)
                            if existing_assignment:
                                if are_canonical_merge(assignment.course_unit_id, existing_assignment.course_unit_id):
                                    continue
                            # Not paired and not canonical merge - conflict!
                            all_compatible = False
                            break
                        if not all_compatible:
                            return False
        
        # CRITICAL: Check student group double-booking
        # For merged groups, check conflicts for ALL original groups that are part of the merge
        # Also check if original groups are part of OTHER merged groups that already have assignments
        groups_to_check = [assignment.student_group_id]
        if assignment.student_group_id in context.merged_to_original_groups:
            # This is a merged group - check conflicts for all original groups
            groups_to_check.extend(context.merged_to_original_groups[assignment.student_group_id])
            # Also check if any of the original groups are part of OTHER merged groups
            if hasattr(context, 'original_to_merged_groups') and context.original_to_merged_groups:
                for orig_group_id in context.merged_to_original_groups[assignment.student_group_id]:
                    if orig_group_id in context.original_to_merged_groups:
                        for other_merged_id in context.original_to_merged_groups[orig_group_id]:
                            if other_merged_id != assignment.student_group_id:
                                groups_to_check.append(other_merged_id)
        
        for group_id in groups_to_check:
            if group_id in context.student_group_schedule:
                if time_key in context.student_group_schedule[group_id]:
                    existing = context.student_group_schedule[group_id][time_key]
                    if len(existing) > 0:
                        # If this variable is already in the schedule, it's not a conflict (re-checking same assignment)
                        if assignment.variable_id not in existing:
                            # Check if ALL existing assignments are either paired OR canonical merges
                            # If ANY existing assignment is NOT paired AND NOT a canonical merge, it's a conflict
                            all_compatible = True
                            for existing_id in existing:
                                if are_paired(assignment.variable_id, existing_id):
                                    continue
                                existing_assignment = context.assignments.get(existing_id)
                                if existing_assignment:
                                    if are_canonical_merge(assignment.course_unit_id, existing_assignment.course_unit_id):
                                        continue
                                # Not paired and not canonical merge - conflict!
                                all_compatible = False
                                break
                            if not all_compatible:
                                # Found at least one existing assignment that's not compatible - conflict!
                                return False
        
        return True
    
    def get_violations(self, assignment: Assignment, context: ConstraintContext) -> List[str]:
        """Get specific double-booking violations"""
        violations = []
        time_key = f"{assignment.time_slot.day}_{assignment.time_slot.period}"
        
        if assignment.lecturer_id in context.lecturer_schedule:
            if time_key in context.lecturer_schedule[assignment.lecturer_id]:
                if context.lecturer_schedule[assignment.lecturer_id][time_key]:
                    violations.append(f"Lecturer {assignment.lecturer_id} already scheduled")
        
        if assignment.room_id in context.room_schedule:
            if time_key in context.room_schedule[assignment.room_id]:
                if context.room_schedule[assignment.room_id][time_key]:
                    violations.append(f"Room {assignment.room_id} already booked")
        
        if assignment.student_group_id in context.student_group_schedule:
            if time_key in context.student_group_schedule[assignment.student_group_id]:
                if context.student_group_schedule[assignment.student_group_id][time_key]:
                    violations.append(f"Student group {assignment.student_group_id} already has class")
        
        return violations


class RoomCapacityConstraint(Constraint):
    """Ensures room capacity is sufficient for student group"""
    
    def __init__(self):
        super().__init__(ConstraintType.ROOM_CAPACITY, [])
    
    def is_satisfied(self, assignment: Assignment, context: ConstraintContext) -> bool:
        """Check if room can accommodate student group
        
        IMPORTANT: For merged groups, the student_group.size already represents
        the total merged size (e.g., 72 students from multiple original groups).
        This check ensures the room capacity (e.g., 88) is >= merged group size (72).
        """
        room = context.rooms.get(assignment.room_id)
        student_group = context.student_groups.get(assignment.student_group_id)
        
        if not room or not student_group:
            return False
        
        room_capacity = room.get('capacity', 0)
        group_size = student_group.get('size', 0)
        
        # Room capacity must be >= group size
        # For merged groups, group_size is already the total merged size
        return room_capacity >= group_size
    
    def get_violations(self, assignment: Assignment, context: ConstraintContext) -> List[str]:
        """Get capacity violations"""
        violations = []
        room = context.rooms.get(assignment.room_id)
        student_group = context.student_groups.get(assignment.student_group_id)
        
        if room and student_group:
            if room.get('capacity', 0) < student_group.get('size', 0):
                violations.append(
                    f"Room {assignment.room_id} capacity {room['capacity']} "
                    f"< group size {student_group['size']}"
                )
        
        return violations


class RoomTypeConstraint(Constraint):
    """Ensures room type matches course requirements (Lab courses → Lab rooms, Theory courses → Theory rooms)"""
    
    def __init__(self):
        super().__init__(ConstraintType.ROOM_TYPE, [])
    
    def is_satisfied(self, assignment: Assignment, context: ConstraintContext) -> bool:
        """Check if room type matches course requirements
        
        DIRECT LOGIC:
        1. Check course type (Lab/Practical → Lab room, Theory → Theory room)
        2. For merged canonical courses: Calculate SUM of all merged groups
        3. Check if Lab room can fit the total merged students
        """
        room = context.rooms.get(assignment.room_id)
        course_unit = context.course_units.get(assignment.course_unit_id)
        student_group = context.student_groups.get(assignment.student_group_id)
        
        if not room or not course_unit:
            return False
        
        preferred_room_type = course_unit.get('preferred_room_type', 'Theory')  # Required field
        room_type = room.get('room_type', '')
        
        # Use preferred_room_type directly
        required_room_type = preferred_room_type
        
        # STRICT: Course MUST use the required room type
        if room_type != required_room_type:
            # HARD CONSTRAINT: Room type must match course type
            # Lab courses MUST use Lab rooms, Theory courses MUST use Theory rooms
            return False
        else:
            # Room type matches - always valid
            return True
    
    def get_violations(self, assignment: Assignment, context: ConstraintContext) -> List[str]:
        """Get room type violations"""
        violations = []
        room = context.rooms.get(assignment.room_id)
        course_unit = context.course_units.get(assignment.course_unit_id)
        
        if room and course_unit:
            preferred_room_type = course_unit.get('preferred_room_type', 'Theory')
            room_type = room.get('room_type', '')
            
            if preferred_room_type == 'Lab' and room_type != 'Lab':
                violations.append(f"Lab course {assignment.course_unit_id} requires Lab room")
            elif preferred_room_type == 'Theory' and room_type == 'Lab':
                violations.append(f"Theory course {assignment.course_unit_id} assigned to Lab room")
        
        return violations


class LecturerSpecializationConstraint(Constraint):
    """Ensures lecturer is qualified to teach the course"""
    
    def __init__(self):
        super().__init__(ConstraintType.LECTURER_SPECIALIZATION, [])
    
    def is_satisfied(self, assignment: Assignment, context: ConstraintContext) -> bool:
        """Check if lecturer is qualified using canonical matching"""
        lecturer = context.lecturers.get(assignment.lecturer_id)
        
        if not lecturer:
            return False
        
        specializations = lecturer.get('specializations', [])
        
        # Use canonical matching
        from app.services.canonical_courses import is_canonical_match
        return is_canonical_match(assignment.course_unit_id, specializations)
    
    def get_violations(self, assignment: Assignment, context: ConstraintContext) -> List[str]:
        """Get qualification violations"""
        violations = []
        lecturer = context.lecturers.get(assignment.lecturer_id)
        
        if lecturer:
            specializations = lecturer.get('specializations', [])
            # Use canonical matching
            from app.services.canonical_courses import is_canonical_match
            if not is_canonical_match(assignment.course_unit_id, specializations):
                violations.append(
                    f"Lecturer {assignment.lecturer_id} not qualified for "
                    f"course {assignment.course_unit_id}"
                )
        
        return violations


class DailyLimitConstraint(Constraint):
    """Ensures lecturer doesn't exceed 2 sessions per day (max 1 morning + 1 afternoon)"""
    
    def __init__(self):
        super().__init__(ConstraintType.DAILY_LIMIT, [])
    
    def is_satisfied(self, assignment: Assignment, context: ConstraintContext) -> bool:
        """Check daily session limit"""
        day = assignment.time_slot.day
        lecturer_id = assignment.lecturer_id
        
        # Get current daily count
        current_count = context.lecturer_daily_count.get(lecturer_id, {}).get(day, 0)
        
        # Maximum 2 sessions per day
        if current_count >= 2:
            return False
        
        # Check morning/afternoon rule: max 1 morning + 1 afternoon
        is_afternoon = assignment.time_slot.is_afternoon
        morning_used = context.lecturer_morning_used.get(lecturer_id, {}).get(day, False)
        afternoon_used = context.lecturer_afternoon_used.get(lecturer_id, {}).get(day, False)
        
        if is_afternoon and afternoon_used:
            return False
        
        if not is_afternoon and morning_used:
            return False
        
        return True
    
    def get_violations(self, assignment: Assignment, context: ConstraintContext) -> List[str]:
        """Get daily limit violations"""
        violations = []
        day = assignment.time_slot.day
        lecturer_id = assignment.lecturer_id
        
        current_count = context.lecturer_daily_count.get(lecturer_id, {}).get(day, 0)
        
        if current_count >= 2:
            violations.append(
                f"Lecturer {lecturer_id} already has 2 sessions on {day}"
            )
        
        # Check morning/afternoon rule: max 1 morning + 1 afternoon
        is_afternoon = assignment.time_slot.is_afternoon
        morning_used = context.lecturer_morning_used.get(lecturer_id, {}).get(day, False)
        afternoon_used = context.lecturer_afternoon_used.get(lecturer_id, {}).get(day, False)
        
        if is_afternoon and afternoon_used:
            violations.append(
                f"Lecturer {lecturer_id} already has an afternoon session on {day}"
            )
        
        if not is_afternoon and morning_used:
            violations.append(
                f"Lecturer {lecturer_id} already has a morning session on {day}"
            )
        
        return violations


class WeeklyLimitConstraint(Constraint):
    """Ensures lecturer doesn't exceed weekly hour limits based on role"""
    
    def __init__(self):
        super().__init__(ConstraintType.WEEKLY_LIMIT, [])
    
    def is_satisfied(self, assignment: Assignment, context: ConstraintContext) -> bool:
        """Check weekly hour limit"""
        lecturer = context.lecturers.get(assignment.lecturer_id)
        
        if not lecturer:
            return False
        
        max_weekly_hours = lecturer.get('max_weekly_hours', 22)
        
        # Part-time lecturers: No strict weekly limit (availability-based)
        # If max_weekly_hours is very high (999), skip weekly limit check
        if max_weekly_hours >= 999:
            return True  # Part-time: controlled by availability, not weekly hours
        
        current_hours = context.lecturer_weekly_hours.get(assignment.lecturer_id, 0)
        session_hours = 2  # Each session is 2 hours
        
        return (current_hours + session_hours) <= max_weekly_hours
    
    def get_violations(self, assignment: Assignment, context: ConstraintContext) -> List[str]:
        """Get weekly limit violations"""
        violations = []
        lecturer = context.lecturers.get(assignment.lecturer_id)
        
        if lecturer:
            max_weekly_hours = lecturer.get('max_weekly_hours', 22)
            
            # Part-time lecturers: No strict weekly limit (availability-based)
            if max_weekly_hours >= 999:
                return violations  # Skip check for part-time
            
            current_hours = context.lecturer_weekly_hours.get(assignment.lecturer_id, 0)
            session_hours = 2
            
            if (current_hours + session_hours) > max_weekly_hours:
                violations.append(
                    f"Lecturer {assignment.lecturer_id} would exceed weekly limit: "
                    f"{current_hours + session_hours} > {max_weekly_hours} hours"
                )
        
        return violations


class NoSameDayRepetitionConstraint(Constraint):
    """
    HARD CONSTRAINT: Ensures same course unit is only taught once per day to same group
    A course unit can only have 1 session per day - no exceptions
    """
    
    def __init__(self):
        super().__init__(ConstraintType.NO_SAME_DAY, [])
    
    def is_satisfied(self, assignment: Assignment, context: ConstraintContext) -> bool:
        """Check for same-day repetition - HARD: no course unit twice on same day"""
        day = assignment.time_slot.day
        unit_key = (assignment.student_group_id, assignment.course_unit_id)
        
        # HARD CONSTRAINT: If course already scheduled on this day, reject
        if context.unit_daily_schedule.get(unit_key, {}).get(day, False):
            return False
        
        return True
    
    def get_violations(self, assignment: Assignment, context: ConstraintContext) -> List[str]:
        """Get same-day repetition violations"""
        violations = []
        day = assignment.time_slot.day
        unit_key = (assignment.student_group_id, assignment.course_unit_id)
        
        # HARD CONSTRAINT: Course unit can only be scheduled once per day
        if context.unit_daily_schedule.get(unit_key, {}).get(day, False):
            violations.append(
                f"Course {assignment.course_unit_id} already scheduled for "
                f"group {assignment.student_group_id} on {day} (HARD: only 1 session per day allowed)"
            )
        
        return violations


class StandardTeachingBlocksConstraint(Constraint):
    """Ensures sessions are only scheduled in standard time blocks"""
    
    VALID_TIME_BLOCKS = {
        'SLOT_1': {'start': '09:00', 'end': '11:00'},  # 9-11 AM
        'SLOT_2': {'start': '11:00', 'end': '13:00'},  # 11-1 PM
        'SLOT_3': {'start': '14:00', 'end': '16:00'},  # 2-4 PM
        'SLOT_4': {'start': '16:00', 'end': '18:00'}   # 4-6 PM
    }
    
    def __init__(self):
        super().__init__(ConstraintType.TIME_BLOCKS, [])
    
    def is_satisfied(self, assignment: Assignment, context: ConstraintContext) -> bool:
        """Check if session is in a valid time block"""
        period = assignment.time_slot.period
        start = assignment.time_slot.start
        end = assignment.time_slot.end
        
        # Check if period is valid
        if period not in self.VALID_TIME_BLOCKS:
            return False
        
        # Check if times match the standard block
        expected = self.VALID_TIME_BLOCKS[period]
        return start == expected['start'] and end == expected['end']
    
    def get_violations(self, assignment: Assignment, context: ConstraintContext) -> List[str]:
        """Get time block violations"""
        violations = []
        period = assignment.time_slot.period
        start = assignment.time_slot.start
        end = assignment.time_slot.end
        
        if period not in self.VALID_TIME_BLOCKS:
            violations.append(
                f"Invalid time period '{period}'. Must be SLOT_1, SLOT_2, SLOT_3, or SLOT_4"
            )
        else:
            expected = self.VALID_TIME_BLOCKS[period]
            if start != expected['start'] or end != expected['end']:
                violations.append(
                    f"Time {start}-{end} doesn't match standard block for {period}: "
                    f"{expected['start']}-{expected['end']}"
                )
        
        return violations


class ClassMergingConstraint(Constraint):
    """Ensures merged classes don't exceed room capacity"""
    
    def __init__(self):
        super().__init__(ConstraintType.CLASS_MERGING, [])
    
    def is_satisfied(self, assignment: Assignment, context: ConstraintContext) -> bool:
        """
        Check if merged groups can fit in room
        
        This allows multiple student groups to be merged for the same session
        as long as combined count <= room capacity
        """
        room = context.rooms.get(assignment.room_id)
        
        if not room:
            return False
        
        room_capacity = room.get('capacity', 0)
        time_key = f"{assignment.time_slot.day}_{assignment.time_slot.period}"
        
        # Get all assignments for this room at this time
        if assignment.room_id in context.room_schedule:
            if time_key in context.room_schedule[assignment.room_id]:
                existing_assignments = context.room_schedule[assignment.room_id][time_key]
                
                # Calculate total student count including this assignment
                total_students = 0
                for var_id in existing_assignments:
                    existing_assignment = context.assignments.get(var_id)
                    if existing_assignment:
                        student_group = context.student_groups.get(
                            existing_assignment.student_group_id
                        )
                        if student_group:
                            total_students += student_group.get('size', 0)
                
                # Add current group size
                current_group = context.student_groups.get(assignment.student_group_id)
                if current_group:
                    total_students += current_group.get('size', 0)
                
                # Check if merged count exceeds capacity
                return total_students <= room_capacity
        
        # No existing assignments, just check current group
        current_group = context.student_groups.get(assignment.student_group_id)
        if current_group:
            return current_group.get('size', 0) <= room_capacity
        
        return True
    
    def get_violations(self, assignment: Assignment, context: ConstraintContext) -> List[str]:
        """Get class merging violations"""
        violations = []
        room = context.rooms.get(assignment.room_id)
        
        if not room:
            return violations
        
        room_capacity = room.get('capacity', 0)
        time_key = f"{assignment.time_slot.day}_{assignment.time_slot.period}"
        
        if assignment.room_id in context.room_schedule:
            if time_key in context.room_schedule[assignment.room_id]:
                existing_assignments = context.room_schedule[assignment.room_id][time_key]
                
                if existing_assignments:
                    total_students = 0
                    group_ids = []
                    
                    for var_id in existing_assignments:
                        existing_assignment = context.assignments.get(var_id)
                        if existing_assignment:
                            student_group = context.student_groups.get(
                                existing_assignment.student_group_id
                            )
                            if student_group:
                                total_students += student_group.get('size', 0)
                                group_ids.append(existing_assignment.student_group_id)
                    
                    current_group = context.student_groups.get(assignment.student_group_id)
                    if current_group:
                        current_size = current_group.get('size', 0)
                        total_students += current_size
                        group_ids.append(assignment.student_group_id)
                    
                    if total_students > room_capacity:
                        violations.append(
                            f"Merged groups {', '.join(group_ids)} total {total_students} students "
                            f"exceeds room {assignment.room_id} capacity {room_capacity}"
                        )
        
        return violations


class ClassSplittingConstraint(Constraint):
    """Ensures large groups are properly split when exceeding room capacity"""
    
    def __init__(self):
        super().__init__(ConstraintType.CLASS_SPLITTING, [])
    
    def is_satisfied(self, assignment: Assignment, context: ConstraintContext) -> bool:
        """
        Check if class splitting is properly handled
        
        If a group is too large for any single room, it must be split.
        This constraint validates that split groups are properly managed.
        """
        room = context.rooms.get(assignment.room_id)
        student_group = context.student_groups.get(assignment.student_group_id)
        
        if not room or not student_group:
            return False
        
        group_size = student_group.get('size', 0)
        room_capacity = room.get('capacity', 0)
        
        # If group fits in room, no splitting needed
        if group_size <= room_capacity:
            return True
        
        # If group is too large, check if it's marked for splitting
        # This would typically be handled by the preprocessing phase
        # For now, we enforce that oversized groups cannot be assigned
        # The scheduler should split them before assignment
        
        # Check if this is a split group (would have suffix like _SPLIT_1, _SPLIT_2)
        is_split_group = '_SPLIT_' in assignment.student_group_id
        
        if is_split_group:
            # Split groups should fit in the room
            return group_size <= room_capacity
        else:
            # Non-split groups that are too large should be rejected
            # They need to be split first
            return False
    
    def get_violations(self, assignment: Assignment, context: ConstraintContext) -> List[str]:
        """Get class splitting violations"""
        violations = []
        room = context.rooms.get(assignment.room_id)
        student_group = context.student_groups.get(assignment.student_group_id)
        
        if room and student_group:
            group_size = student_group.get('size', 0)
            room_capacity = room.get('capacity', 0)
            
            if group_size > room_capacity:
                is_split_group = '_SPLIT_' in assignment.student_group_id
                
                if not is_split_group:
                    violations.append(
                        f"Group {assignment.student_group_id} with {group_size} students "
                        f"exceeds room {assignment.room_id} capacity {room_capacity}. "
                        f"Group must be split before assignment."
                    )
                else:
                    violations.append(
                        f"Split group {assignment.student_group_id} with {group_size} students "
                        f"still exceeds room {assignment.room_id} capacity {room_capacity}"
                    )
        
        return violations


class PairingConstraint(Constraint):
    """Ensures theory/practical pairs are scheduled at the same time"""
    
    def __init__(self):
        super().__init__(ConstraintType.PAIRING_CONSTRAINT, [])
    
    def is_satisfied(self, assignment: Assignment, context: ConstraintContext) -> bool:
        """Check if paired variables are scheduled at the same time"""
        # Get paired variable IDs for this assignment
        paired_var_ids = context.variable_pairs.get(assignment.variable_id, [])
        if not paired_var_ids:
            return True  # No pairs, constraint satisfied
        
        # Check if all paired variables are scheduled at the same time
        time_key = f"{assignment.time_slot.day}_{assignment.time_slot.period}"
        
        for paired_var_id in paired_var_ids:
            if paired_var_id in context.assignments:
                paired_assignment = context.assignments[paired_var_id]
                paired_time_key = f"{paired_assignment.time_slot.day}_{paired_assignment.time_slot.period}"
                if paired_time_key != time_key:
                    return False  # Pair broken - not at same time
        
        return True
    
    def get_violations(self, assignment: Assignment, context: ConstraintContext) -> List[str]:
        """Get pairing violations"""
        violations = []
        paired_var_ids = context.variable_pairs.get(assignment.variable_id, [])
        
        if paired_var_ids:
            time_key = f"{assignment.time_slot.day}_{assignment.time_slot.period}"
            for paired_var_id in paired_var_ids:
                if paired_var_id in context.assignments:
                    paired_assignment = context.assignments[paired_var_id]
                    paired_time_key = f"{paired_assignment.time_slot.day}_{paired_assignment.time_slot.period}"
                    if paired_time_key != time_key:
                        violations.append(
                            f"Paired variable {paired_var_id} scheduled at different time "
                            f"({paired_time_key} vs {time_key})"
                        )
        
        return violations


class ConstraintChecker:
    """Manages and checks all constraints"""
    
    def __init__(self):
        self.constraints: List[Constraint] = [
            NoDoubleBookingConstraint(),
            RoomCapacityConstraint(),
            RoomTypeConstraint(),
            LecturerSpecializationConstraint(),
            PairingConstraint(),  # Add pairing as hard constraint
            DailyLimitConstraint(),
            WeeklyLimitConstraint(),
            NoSameDayRepetitionConstraint(),
            StandardTeachingBlocksConstraint(),
            ClassMergingConstraint(),
            ClassSplittingConstraint()
        ]
    
    def check_all(self, assignment: Assignment, context: ConstraintContext) -> tuple[bool, List[str]]:
        """Check all constraints for assignment"""
        violations = []
        
        for constraint in self.constraints:
            if not constraint.is_satisfied(assignment, context):
                violations.extend(constraint.get_violations(assignment, context))
        
        return len(violations) == 0, violations
    
    def check_constraint(self, constraint_type: ConstraintType, 
                        assignment: Assignment, context: ConstraintContext) -> bool:
        """Check specific constraint type"""
        for constraint in self.constraints:
            if constraint.type == constraint_type:
                return constraint.is_satisfied(assignment, context)
        return True
