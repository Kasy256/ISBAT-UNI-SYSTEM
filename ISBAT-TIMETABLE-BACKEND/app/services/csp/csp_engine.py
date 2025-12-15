import time
import math
import random
from typing import List, Dict, Set, Optional, Tuple
from collections import defaultdict
from app.services.csp.domain import SchedulingVariable, Assignment, TimeSlot, DomainManager
from app.services.csp.constraints import ConstraintChecker, ConstraintContext, ConstraintType
from app.models.lecturer import Lecturer
from app.models.room import Room
from app.models.subject import CourseUnit
from app.models.program import Program
from app.config import Config
from app.services.canonical_courses import CANONICAL_COURSE_MAPPING, get_canonical_id

class CSPEngine:
    """CSP-based timetable scheduling engine"""
    
    def __init__(self, resource_booking_manager=None):
        self.domain_manager = DomainManager()
        self.constraint_checker = ConstraintChecker()
        self.constraint_context = None  # Will be initialized with data
        self.variables: List[SchedulingVariable] = []
        self.assignments: List[Assignment] = []
        self.iterations = 0
        self.max_iterations = Config.CSP_MAX_ITERATIONS
        self.start_time = None
        self.timeout = Config.CSP_TIMEOUT_SECONDS
        
        # Resource booking manager for conflict-aware solving
        self.resource_booking_manager = resource_booking_manager
        
        # Progress tracking for early termination
        self.last_progress_iteration = 0
        self.last_progress_count = 0
        self.stall_threshold = 5000  # If no progress for 5000 iterations, terminate
        self.best_assignments: List[Assignment] = []  # Preserve best solution found
        
        # Debugging: Enable detailed debugging logs
        self.debug_mode = True
        
        # Data caches
        self.lecturers: Dict[str, Lecturer] = {}
        self.rooms: Dict[str, Room] = {}
        self.course_units: Dict[str, CourseUnit] = {}
        self.programs: Dict[str, Program] = {}
        
        # Theory/practical pairs: variable_id -> list of paired variable_ids
        self.variable_pairs: Dict[str, List[str]] = {}
        
        # Merged group tracking: merged_group_id -> list of original_group_ids
        self.merged_to_original_groups: Dict[str, List[str]] = {}
        # Reverse mapping: original_group_id -> list of merged_group_ids (for conflict checking)
        self.original_to_merged_groups: Dict[str, List[str]] = {}
        # Original group to variables mapping: original_group_id -> list of variable_ids
        self.original_group_variables: Dict[str, List[str]] = {}
    
    def initialize(self, lecturers: List[Lecturer], rooms: List[Room], 
                   course_units: List[CourseUnit], programs: List[Program],
                   merged_group_details: Optional[Dict] = None, faculty: str = None):
        """Initialize CSP with data"""
        
        # Canonical mappings should already be loaded (reloaded in generate_term_timetable.py with db connection)
        # Don't try to reload here as we may not have Flask app context
        pass
        
        # Build lookup dictionaries
        self.lecturers = {lec.id: lec for lec in lecturers}
        self.rooms = {room.room_number: room for room in rooms}
        self.course_units = {cu.id: cu for cu in course_units}
        self.programs = {sg.id: sg for sg in programs}
        
        self.constraint_context = ConstraintContext(
            variable_pairs={},
            merged_to_original_groups=self.merged_to_original_groups,
            original_to_merged_groups=self.original_to_merged_groups
        )
        
        # CRITICAL: Load existing assignments if resource booking manager provided
        # This makes the CSP solver aware of bookings from other faculties
        if self.resource_booking_manager:
            self.resource_booking_manager.load_existing_assignments_to_context(
                self.constraint_context
            )
            if faculty:
                print(f"   ✅ Loaded existing assignments from other faculties (generating for {faculty})")
            else:
                print(f"   ✅ Loaded existing assignments from other faculties")
        self.constraint_context.lecturers = {
            lec.id: {
                'id': lec.id, 
                'name': lec.name, 
                'role': lec.role,  # CRITICAL: Required for weekly hour limit checking
                'max_weekly_hours': lec.max_weekly_hours,  # CRITICAL: Required for weekly hour limit checking
                'specializations': lec.specializations
            } for lec in lecturers
        }
        self.constraint_context.rooms = {
            room.room_number: {
                'room_number': room.room_number, 
                'capacity': room.capacity, 
                'room_type': room.room_type,
                'specializations': getattr(room, 'specializations', []) or []
            } for room in rooms
        }
        # Store room objects for specialization checking
        self.room_objects = {room.room_number: room for room in rooms}
        self.constraint_context.course_units = {
            cu.id: {
                'id': cu.id, 
                'preferred_room_type': cu.preferred_room_type
            } for cu in course_units
        }
        self.constraint_context.programs = {
            sg.id: {
                'id': sg.id, 
                'size': sg.size
            } for sg in programs
        }
        
        # Build merged group tracking if provided
        if merged_group_details:
            for merged_group_id, details in merged_group_details.items():
                original_group_ids = [g['program'].id for g in details.get('groups', [])]
                self.merged_to_original_groups[merged_group_id] = original_group_ids
                # Build reverse mapping: original_group_id -> list of merged_group_ids
                for orig_group_id in original_group_ids:
                    if orig_group_id not in self.original_to_merged_groups:
                        self.original_to_merged_groups[orig_group_id] = []
                    self.original_to_merged_groups[orig_group_id].append(merged_group_id)
                    # Initialize variable lists for each original group
                    if orig_group_id not in self.original_group_variables:
                        self.original_group_variables[orig_group_id] = []
        
        # Create variables for each session
        self.variables = []
        var_id = 1
        
        course_group_variables: Dict[str, Dict[int, List[SchedulingVariable]]] = defaultdict(lambda: defaultdict(list))
        
        for program in programs:
            course_ids = []
            for cu in program.course_units:
                # Extract course code (handles "CODE - Name" format)
                if isinstance(cu, dict):
                    course_id = cu.get('code') or cu.get('id')
                    if course_id:
                        course_ids.append(course_id.strip())
                elif isinstance(cu, str):
                    # Extract code from "CODE - Name" format
                    if " - " in cu:
                        course_code = cu.split(" - ")[0].strip()
                        course_ids.append(course_code)
                    else:
                        course_ids.append(cu.strip())
            
            for course_unit_id in course_ids:
                course_unit = self.course_units.get(course_unit_id)
                if not course_unit:
                    continue
                
                sessions_needed = course_unit.sessions_required
                
                for session_num in range(1, sessions_needed + 1):
                    variable = SchedulingVariable(
                        id=f"VAR_{var_id}",
                        course_unit_id=course_unit.id,
                        program_id=program.id,
                        term=program.term,
                        session_number=session_num,
                        sessions_required=sessions_needed
                    )
                    
                    self.domain_manager.initialize_variable_domains(
                        variable, lecturers, rooms, course_unit, program
                    )
                    
                    # Use canonical subject mapping as source of truth for pairing
                    # Group variables by canonical ID (canonical subjects are already unified units)
                    canonical_id = get_canonical_id(course_unit.id) or course_unit.id
                    if canonical_id in CANONICAL_COURSE_MAPPING:
                        # This is a canonical subject - group by canonical ID
                        course_group_variables[canonical_id][session_num].append(variable)
                    elif course_unit.course_group:
                        # Fallback to course_group for non-canonical subjects
                        course_group_variables[course_unit.course_group][session_num].append(variable)
                    
                    self.variables.append(variable)
                    
                    # Store variable to program mapping in constraint context
                    self.constraint_context.variable_to_program[variable.id] = program.id
                    
                    # Track which original groups this variable belongs to
                    # If this is a merged group, track variables for all original groups
                    if program.id in self.merged_to_original_groups:
                        original_group_ids = self.merged_to_original_groups[program.id]
                        for orig_group_id in original_group_ids:
                            if orig_group_id not in self.original_group_variables:
                                self.original_group_variables[orig_group_id] = []
                            self.original_group_variables[orig_group_id].append(variable.id)
                    else:
                        # Not a merged group, track directly
                        if program.id not in self.original_group_variables:
                            self.original_group_variables[program.id] = []
                        self.original_group_variables[program.id].append(variable.id)
                    
                    var_id += 1
        
        # Build variable pairs using canonical mapping as source of truth
        self.variable_pairs: Dict[str, List[str]] = {}
        for group_key, session_map in course_group_variables.items():
            for session_num, vars_list in session_map.items():
                if len(vars_list) > 1:
                    var_ids = [var.id for var in vars_list]
                    for var in vars_list:
                        self.variable_pairs[var.id] = [vid for vid in var_ids if vid != var.id]
        if hasattr(self, 'constraint_context') and self.constraint_context:
            self.constraint_context.variable_pairs = self.variable_pairs
        
        if self.variable_pairs:
            pair_count = sum(len(pairs) for pairs in self.variable_pairs.values()) // 2
            print(f"Initialized CSP with {len(self.variables)} variables")
            print(f"   📎 Linked {pair_count} theory/practical pairs")
        else:
            print(f"Initialized CSP with {len(self.variables)} variables")
        
        print("\n📊 Domain Analysis:")
        zero_domain_vars = []
        small_domain_vars = []
        
        def accurate_domain_size(v: SchedulingVariable) -> int:
            """Calculate domain size accounting for lecturer availability"""
            valid_combinations = 0
            for time_slot in v.available_time_slots:
                for lecturer_id in v.available_lecturers:
                    # Check if lecturer is available for this time slot
                    if v.lecturer_time_slots:
                        lecturer_available_slots = v.lecturer_time_slots.get(lecturer_id)
                        if lecturer_available_slots is not None and time_slot not in lecturer_available_slots:
                            continue  # Skip - lecturer not available for this time slot
                    valid_combinations += len(v.available_rooms)
            return valid_combinations
        
        for var in self.variables:
            domain_size = accurate_domain_size(var)
            if domain_size == 0:
                zero_domain_vars.append(var)
            elif domain_size < 10:
                small_domain_vars.append(var)
        
        if zero_domain_vars:
            print(f"   ⚠️  {len(zero_domain_vars)} variables have ZERO valid domain combinations:")
            for var in zero_domain_vars[:5]:
                subject = self.course_units.get(var.course_unit_id)
                group = self.programs.get(var.program_id)
                print(f"      • {var.id}: {subject.code if subject else var.course_unit_id} for {group.display_name if group else var.program_id}")
                print(f"        - Time slots: {len(var.available_time_slots)}")
                print(f"        - Lecturers: {len(var.available_lecturers)}")
                print(f"        - Rooms: {len(var.available_rooms)}")
        
                # Additional diagnostics
                if len(var.available_rooms) == 0:
                    required_type = subject.preferred_room_type if subject else "Unknown"
                    available_rooms_of_type = [r for r in self.rooms.values() if r.room_type == required_type]
                    group_size = group.size if group else 0
                    print(f"        ⚠️  No {required_type} rooms available!")
                    print(f"           - Required room type: {required_type}")
                    print(f"           - Group size: {group_size} students")
                    print(f"           - Total {required_type} rooms in system: {len(available_rooms_of_type)}")
                    if available_rooms_of_type:
                        max_capacity = max(r.capacity for r in available_rooms_of_type)
                        print(f"           - Largest {required_type} room capacity: {max_capacity}")
                        if group_size > max_capacity:
                            print(f"           ❌ Group size ({group_size}) exceeds largest {required_type} room ({max_capacity})")
                        else:
                            print(f"           💡 Rooms exist but may be filtered by other constraints")
                    else:
                        print(f"           ❌ No {required_type} rooms exist in the system!")
        
        if small_domain_vars:
            print(f"   ⚠️  {len(small_domain_vars)} variables have < 10 domain combinations")
        
        course_lecturer_count = {}
        for var in self.variables:
            course_id = var.course_unit_id
            if course_id not in course_lecturer_count:
                course_lecturer_count[course_id] = len(var.available_lecturers)
        
        low_coverage = {cid: count for cid, count in course_lecturer_count.items() if count < 2}
        if low_coverage:
            print(f"\n   ⚠️  {len(low_coverage)} subjects have < 2 available lecturers:")
            for course_id, count in list(low_coverage.items())[:5]:
                subject = self.course_units.get(course_id)
                print(f"      • {subject.code if subject else course_id}: {count} lecturer(s)")
            
            # Show helpful message about missing lecturer assignments
            zero_lecturer_courses = [cid for cid, count in low_coverage.items() if count == 0]
            if zero_lecturer_courses:
                print(f"\n   💡 {len(zero_lecturer_courses)} courses have NO qualified lecturers:")
                print(f"      This means no lecturers have specializations matching these courses.")
                print(f"      Please assign specializations to lecturers in the Lecturers management page.")
                print(f"      Example courses needing lecturers: {', '.join(zero_lecturer_courses[:5])}")
                if len(zero_lecturer_courses) > 5:
                    print(f"      ... and {len(zero_lecturer_courses) - 5} more courses")
        
        print()
    
    def _build_constraint_context(self) -> ConstraintContext:
        """Create a fresh constraint context with resource metadata"""
        context = ConstraintContext(
            variable_pairs=self.variable_pairs,
            merged_to_original_groups=self.merged_to_original_groups
        )
        context.lecturers = {
            lec.id: {
                'id': lec.id,
                'name': lec.name,
                'role': lec.role,
                'max_weekly_hours': lec.max_weekly_hours,
                'specializations': lec.specializations
            } for lec in self.lecturers.values()
        }
        context.rooms = {
            room.id: {
                'id': room.id,
                'capacity': room.capacity,
                'room_type': room.room_type
            } for room in self.rooms.values()
        }
        context.course_units = {
            cu.id: {
                'id': cu.id,
                'preferred_room_type': cu.preferred_room_type
            } for cu in self.course_units.values()
        }
        context.programs = {
            sg.id: {
                'id': sg.id,
                'size': sg.size
            } for sg in self.programs.values()
        }
        return context
    
    def solve(self) -> Optional[List[Assignment]]:
        """Solve CSP using backtracking with heuristics"""
        
        self.start_time = time.time()
        self.iterations = 0
        self.assignments = []
        self.last_progress_iteration = 0
        self.last_progress_count = 0
        self.best_assignments = []  # Reset best solution
        
        # Reset constraint context for fresh solve
        self.constraint_context = self._build_constraint_context()
        
        # First try a deterministic greedy assignment before expensive backtracking
        greedy_success = self._try_greedy_assignment()
        
        if greedy_success:
            print("✅ Greedy assignment produced a complete timetable")
            result = True
        else:
            # Reset context/assignments before attempting full CSP search
            self.assignments = []
            for variable in self.variables:
                variable.assignment = None
            
            self.constraint_context = self._build_constraint_context()
            # Sort variables by MRV (Minimum Remaining Values) heuristic with random tie-breaking
            unassigned = sorted(self.variables, key=lambda v: (v.domain_size(), random.random()))
            result = self._backtrack(unassigned, [])
        
        if result:
            all_valid = True
            violations_found = []
            
            test_context = ConstraintContext(
                variable_pairs=self.variable_pairs,
                merged_to_original_groups=self.merged_to_original_groups
            )
            test_context.lecturers = self.constraint_context.lecturers.copy()
            test_context.rooms = self.constraint_context.rooms.copy()
            test_context.course_units = self.constraint_context.course_units.copy()
            test_context.programs = self.constraint_context.programs.copy()
            
            for assignment in self.assignments:
                is_valid, violations = self.constraint_checker.check_all(assignment, test_context)
                if not is_valid:
                    all_valid = False
                    violations_found.extend(violations)
                test_context.add_assignment(assignment)
            
            critical_violations = [v for v in violations_found if any(
                keyword in v for keyword in ['double-booked', 'capacity', 'room type', 'specialization']
            )]
            limit_violations = [v for v in violations_found if any(
                keyword in v for keyword in ['weekly limit', 'daily limit', 'sessions on']
            )]
            
            if len(critical_violations) == 0:
                if len(limit_violations) > 0:
                    print(f"Solution found in {self.iterations} iterations ({time.time() - self.start_time:.2f}s)")
                    print(f"✅ All {len(self.assignments)} assignments scheduled")
                    print(f"⚠️  Solution has {len(limit_violations)} limit violations")
                    print(f"   GGA will repair these violations during optimization phase")
                    if limit_violations:
                        print(f"   First few violations: {limit_violations[:3]}")
                    return self.assignments
                else:
                    print(f"Solution found in {self.iterations} iterations ({time.time() - self.start_time:.2f}s)")
                    print(f"✅ All {len(self.assignments)} assignments validated - zero constraint violations")
                    return self.assignments
            else:
                print(f"⚠️  Solution found with {len(critical_violations)} CRITICAL violations")
                print(f"   Critical violations: {critical_violations[:3]}")
                return self.assignments
        else:
            print(f"No complete solution found after {self.iterations} iterations")
            print(f"   Progress: {len(self.assignments)}/{len(self.variables)} sessions assigned")
            
            # CRITICAL: Restore best solution if backtracking cleared everything
            if len(self.assignments) == 0 and self.best_assignments:
                self.assignments = self.best_assignments
                print(f"   💡 Restored best solution found ({len(self.assignments)}/{len(self.variables)} sessions)")
            
            if len(self.assignments) > 0:
                print(f"   ⚠️  CSP got stuck - returning partial solution")
                print(f"      • Over-constrained problem (too many strict constraints)")
                print(f"      • Insufficient resources (lecturers, rooms, time slots)")
                print(f"      • Need for better search heuristics")
                
                # Diagnostic: Analyze why remaining variables can't be assigned
                assigned_var_ids = {a.variable_id for a in self.assignments}
                unassigned_vars = [v for v in self.variables if v.id not in assigned_var_ids]
                
                if unassigned_vars:
                    print(f"\n   🔍 Diagnostic: {len(unassigned_vars)} unassigned variables")
                    
                    # Check domain sizes for unassigned variables
                    zero_domain = []
                    small_domain = []
                    for var in unassigned_vars[:10]:  # Check first 10
                        # Calculate accurate domain size
                        domain_size = 0
                        for time_slot in var.available_time_slots:
                            for lecturer_id in var.available_lecturers:
                                if var.lecturer_time_slots:
                                    lecturer_available_slots = var.lecturer_time_slots.get(lecturer_id)
                                    if lecturer_available_slots is not None and time_slot not in lecturer_available_slots:
                                        continue
                                domain_size += len(var.available_rooms)
                        
                        subject = self.course_units.get(var.course_unit_id)
                        if domain_size == 0:
                            zero_domain.append((var, subject))
                        elif domain_size < 10:
                            small_domain.append((var, domain_size, subject))
                    
                    if zero_domain:
                        print(f"      ❌ {len(zero_domain)} variables have ZERO valid combinations:")
                        for var, subject in zero_domain[:5]:
                            group = self.programs.get(var.program_id)
                            print(f"         • {subject.code if subject else var.course_unit_id} for {group.display_name if group else var.program_id}")
                            print(f"           - Lecturers: {len(var.available_lecturers)}")
                            print(f"           - Rooms: {len(var.available_rooms)}")
                            print(f"           - Time slots: {len(var.available_time_slots)}")
                    
                    if small_domain:
                        print(f"      ⚠️  {len(small_domain)} variables have < 10 valid combinations")
                        for var, size, subject in small_domain[:3]:
                            print(f"         • {subject.code if subject else var.course_unit_id}: {size} combinations")
                    
                    # Check lecturer availability and usage
                    lecturer_usage = defaultdict(int)
                    lecturer_daily_usage = defaultdict(lambda: defaultdict(int))
                    for assignment in self.assignments:
                        lecturer_usage[assignment.lecturer_id] += 1
                        day = assignment.time_slot.day
                        lecturer_daily_usage[assignment.lecturer_id][day] += 1
                    
                    # Check which lecturers are needed for unassigned variables
                    unassigned_lecturer_needs = defaultdict(list)
                    for var in unassigned_vars:
                        subject = self.course_units.get(var.course_unit_id)
                        for lecturer_id in var.available_lecturers:
                            unassigned_lecturer_needs[lecturer_id].append((var, subject))
                    
                    # Find lecturers that are at their limits
                    constrained_lecturers = []
                    for lecturer_id, vars_needing in unassigned_lecturer_needs.items():
                        lecturer = self.lecturers.get(lecturer_id)
                        if lecturer:
                            current_sessions = lecturer_usage[lecturer_id]
                            max_weekly = lecturer.max_weekly_hours // 2  # Each session is 2 hours
                            
                            # Check if lecturer is at daily limit on any day
                            at_daily_limit = any(count >= 2 for count in lecturer_daily_usage[lecturer_id].values())
                            
                            if at_daily_limit or (max_weekly < 999 and current_sessions >= max_weekly):
                                constrained_lecturers.append((lecturer_id, current_sessions, max_weekly, at_daily_limit, len(vars_needing)))
                    
                    if constrained_lecturers:
                        print(f"      ⚠️  {len(constrained_lecturers)} lecturer(s) are at their limits:")
                        for lecturer_id, current, max_weekly, at_daily, needed_by in constrained_lecturers[:5]:
                            lecturer = self.lecturers.get(lecturer_id)
                            constraints = []
                            if at_daily:
                                constraints.append("daily limit (2 sessions/day)")
                            if max_weekly < 999 and current >= max_weekly:
                                constraints.append(f"weekly limit ({max_weekly} sessions)")
                            print(f"         • {lecturer.name if lecturer else lecturer_id}: {current}/{max_weekly if max_weekly < 999 else 'unlimited'} sessions, needed by {needed_by} unassigned variable(s)")
                            if constraints:
                                print(f"           Blocked by: {', '.join(constraints)}")
                
                print(f"   💡 Passing partial solution to GGA - it will try to complete and repair violations")
                # Return partial solution - GGA can try to complete it
                return self.assignments
            # If we get here, assignments were cleared but we should have restored best_assignments above
            # If best_assignments is empty, return None
            return None
    
    def _program_has_conflict(self, program_id: str, time_slot: TimeSlot, variable_id: str = None) -> bool:
        """Check if a program already has a session at the given time.
        Allows paired assignments (theory/practical) and canonical merges, but prevents other conflicts.
        
        CRITICAL: For merged groups, checks conflicts for ALL original groups that are part of the merge.
        Also checks if original groups are part of OTHER merged groups that already have assignments.
        This prevents double-booking when canonical subjects are scheduled across different semesters."""
        from app.services.canonical_courses import get_canonical_id
        
        time_key = f"{time_slot.day}_{time_slot.period}"
        
        # Get current variable's subject for canonical merge checking
        current_course_id = None
        if variable_id:
            current_var = next((v for v in self.variables if v.id == variable_id), None)
            if current_var:
                current_course_id = current_var.course_unit_id
        
        # Get all programs to check
        groups_to_check = [program_id]
        
        # If this is a merged group, check all its original groups
        if program_id in self.merged_to_original_groups:
            groups_to_check.extend(self.merged_to_original_groups[program_id])
        
        # CRITICAL: Also check if any of the original groups are part of OTHER merged groups
        # that might already have assignments at this time
        if program_id in self.merged_to_original_groups:
            for orig_group_id in self.merged_to_original_groups[program_id]:
                if orig_group_id in self.original_to_merged_groups:
                    # This original group is part of other merged groups - check those too
                    for other_merged_id in self.original_to_merged_groups[orig_group_id]:
                        if other_merged_id != program_id:  # Don't check the current merged group
                            groups_to_check.append(other_merged_id)
        
        # Check conflicts for all relevant groups
        for group_id in groups_to_check:
            if group_id in self.constraint_context.program_schedule:
                if time_key in self.constraint_context.program_schedule[group_id]:
                    existing = self.constraint_context.program_schedule[group_id][time_key]
                    if len(existing) > 0:
                        # If variable_id is provided, check if ANY existing assignment conflicts
                        if variable_id and current_course_id:
                            # Get paired IDs for current variable (bidirectional check)
                            paired_ids = set(self.variable_pairs.get(variable_id, []))
                            # Also check reverse pairing (if existing vars have current var as pair)
                            for existing_id in existing:
                                if existing_id in self.variable_pairs:
                                    existing_paired = set(self.variable_pairs.get(existing_id, []))
                                    if variable_id in existing_paired:
                                        paired_ids.add(existing_id)
                            
                            # Check if ANY existing assignment is NOT paired AND NOT a canonical merge
                            for existing_id in existing:
                                if existing_id == variable_id:
                                    continue  # Same variable, not a conflict
                                if existing_id in paired_ids:
                                    continue  # Paired variable, allowed
                                
                                # Check if it's a canonical merge
                                existing_assignment = self.constraint_context.assignments.get(existing_id)
                                if existing_assignment:
                                    existing_canonical = get_canonical_id(existing_assignment.course_unit_id) or existing_assignment.course_unit_id
                                    current_canonical = get_canonical_id(current_course_id) or current_course_id
                                    if existing_canonical == current_canonical:
                                        continue  # Canonical merge, allowed
                                
                                # Found an existing assignment that's NOT paired AND NOT a canonical merge - conflict!
                                return True
                        elif variable_id:
                            # Variable ID provided but no subject ID - check for paired only
                            paired_ids = set(self.variable_pairs.get(variable_id, []))
                            for existing_id in existing:
                                if existing_id != variable_id and existing_id not in paired_ids:
                                    return True
                        else:
                            # No variable_id provided - any existing assignment is a conflict
                            return True
        
        return False
    
    def _is_assignment_valid(self, assignment: Assignment) -> bool:
        """Run critical constraint checks for a potential assignment.
        This is the PRIMARY validation - must be strict to prevent invalid assignments."""
        # CRITICAL: Check double-booking FIRST - this is the most important constraint
        if not self.constraint_checker.check_constraint(
            ConstraintType.NO_DOUBLE_BOOKING, assignment, self.constraint_context
        ):
            return False
        
        # Check room capacity
        if not self.constraint_checker.check_constraint(
            ConstraintType.ROOM_CAPACITY, assignment, self.constraint_context
        ):
            return False
        
        # Check room type
        if not self.constraint_checker.check_constraint(
            ConstraintType.ROOM_TYPE, assignment, self.constraint_context
        ):
            return False
        
        # Check same-day repetition (subject can only be scheduled once per day)
        if not self.constraint_checker.check_constraint(
            ConstraintType.NO_SAME_DAY, assignment, self.constraint_context
        ):
            return False
        
        # Check class merging (canonical subjects can share rooms)
        if not self.constraint_checker.check_constraint(
            ConstraintType.CLASS_MERGING, assignment, self.constraint_context
        ):
            return False
        
        # Check class splitting
        if not self.constraint_checker.check_constraint(
            ConstraintType.CLASS_SPLITTING, assignment, self.constraint_context
        ):
            return False
        
        # Check pairing constraint (theory/practical must be at same time)
        if not self.constraint_checker.check_constraint(
            ConstraintType.PAIRING_CONSTRAINT, assignment, self.constraint_context
        ):
            return False
        
        # Check daily limit (max 2 sessions per day, 1 morning + 1 afternoon)
        if not self.constraint_checker.check_constraint(
            ConstraintType.DAILY_LIMIT, assignment, self.constraint_context
        ):
            return False
        
        # Check weekly limit (max hours per week based on role)
        if not self.constraint_checker.check_constraint(
            ConstraintType.WEEKLY_LIMIT, assignment, self.constraint_context
        ):
            return False
        
        return True
    
    def _assign_variable(self, variable: SchedulingVariable, ordered_values: List[Tuple]) -> Optional[Assignment]:
        """Attempt to assign a variable. If part of a pair, assigns its pair at the same time."""
        for value_tuple in ordered_values:
            # Handle tuples: 3-tuple (time_slot, lecturer_id, room_number), 
            # 4-tuple (with room_priority), or 5-tuple (with room_priority and specialization_bonus)
            if len(value_tuple) == 5:
                time_slot, lecturer_id, room_number, _, _ = value_tuple
            elif len(value_tuple) == 4:
                time_slot, lecturer_id, room_number, _ = value_tuple
            else:
                time_slot, lecturer_id, room_number = value_tuple
            # Check for conflicts, allowing paired assignments
            if self._program_has_conflict(variable.program_id, time_slot, variable.id):
                # Conflict exists and it's not a paired assignment - skip this time slot
                continue
            
            assignment = Assignment(
                variable_id=variable.id,
                course_unit_id=variable.course_unit_id,
                program_id=variable.program_id,
                lecturer_id=lecturer_id,
                room_number=room_number,
                time_slot=time_slot,
                term=variable.term,
                session_number=variable.session_number
            )
            
            if not self._is_assignment_valid(assignment):
                continue
            
            # Check if this variable has paired variables (theory/practical pairs)
            paired_var_ids = self.variable_pairs.get(variable.id, [])
            if paired_var_ids:
                # Try to assign all paired variables at the same time slot
                paired_assignments = []
                all_valid = True
                
                for paired_var_id in paired_var_ids:
                    # Find the paired variable
                    paired_var = next((v for v in self.variables if v.id == paired_var_id), None)
                    if not paired_var or paired_var.is_assigned():
                        # Already assigned or not found - skip
                        continue
                    
                    # Find a valid assignment for the paired variable at the same time slot
                    paired_assignment = None
                    course_unit = self.course_units.get(paired_var.course_unit_id)
                    if not course_unit:
                        all_valid = False
                        break
                    
                    # Try to find a valid lecturer and room for the paired variable at this time slot
                    for paired_lecturer_id in paired_var.available_lecturers:
                        # Check lecturer availability for this time slot
                        if paired_var.lecturer_time_slots:
                            lecturer_available_slots = paired_var.lecturer_time_slots.get(paired_lecturer_id)
                            if lecturer_available_slots is not None and time_slot not in lecturer_available_slots:
                                continue
                        
                        for paired_room_id in paired_var.available_rooms:
                            test_assignment = Assignment(
                                variable_id=paired_var.id,
                                course_unit_id=paired_var.course_unit_id,
                                program_id=paired_var.program_id,
                                lecturer_id=paired_lecturer_id,
                                room_number=paired_room_id,
                                time_slot=time_slot,
                                term=paired_var.term,
                                session_number=paired_var.session_number
                            )
                            
                            if self._is_assignment_valid(test_assignment):
                                paired_assignment = test_assignment
                                break
                        
                        if paired_assignment:
                            break
                    
                    if not paired_assignment:
                        all_valid = False
                        break
                    
                    paired_assignments.append((paired_var, paired_assignment))
                
                if not all_valid:
                    continue
                
                variable.assignment = assignment
                self.assignments.append(assignment)
                self.constraint_context.add_assignment(assignment)
                
                for paired_var, paired_assignment in paired_assignments:
                    paired_var.assignment = paired_assignment
                    self.assignments.append(paired_assignment)
                    self.constraint_context.add_assignment(paired_assignment)
                
                return assignment
            else:
                variable.assignment = assignment
                self.assignments.append(assignment)
                self.constraint_context.add_assignment(assignment)
                return assignment
        return None
    
    def _try_greedy_assignment(self) -> bool:
        """Greedy one-pass assignment to quickly find a feasible timetable."""
        self.assignments = []
        assigned_variables = []
        
        def greedy_key(var: SchedulingVariable):
            subject = self.course_units.get(var.course_unit_id)
            group = self.programs.get(var.program_id)
            size = group.size if group else 0
            is_lab = 1 if subject and subject.preferred_room_type == 'Lab' else 0
            # Add random component for variety in each generation
            return (-is_lab, -size, len(var.available_rooms), random.random())
        
        ordered_variables = sorted(self.variables, key=greedy_key)
        
        for variable in ordered_variables:
            if variable.is_assigned():
                assigned_variables.append(variable)
                continue
                
            ordered_values = self._order_domain_values(variable)
            assignment = self._assign_variable(variable, ordered_values)
            if assignment:
                assigned_variables.append(variable)
                paired_var_ids = self.variable_pairs.get(variable.id, [])
                for paired_var_id in paired_var_ids:
                    paired_var = next((v for v in self.variables if v.id == paired_var_id), None)
                    if paired_var and paired_var.is_assigned() and paired_var not in assigned_variables:
                        assigned_variables.append(paired_var)
                continue
            
            # Greedy failed – cleanup and abort
            subject = self.course_units.get(variable.course_unit_id)
            print(f"⚠️  Greedy assignment failed for {subject.code if subject else variable.course_unit_id} (tried {len(ordered_values)} combinations)")
            for assigned_var in assigned_variables:
                if assigned_var.assignment:
                    # Remove paired assignments too
                    paired_var_ids = self.variable_pairs.get(assigned_var.id, [])
                    for paired_var_id in paired_var_ids:
                        paired_var = next((v for v in self.variables if v.id == paired_var_id), None)
                        if paired_var and paired_var.assignment:
                            self.constraint_context.remove_assignment(paired_var.assignment.variable_id)
                            if paired_var.assignment in self.assignments:
                                self.assignments.remove(paired_var.assignment)
                            paired_var.assignment = None
                    
                    self.constraint_context.remove_assignment(assigned_var.assignment.variable_id)
                    if assigned_var.assignment in self.assignments:
                        self.assignments.remove(assigned_var.assignment)
                    assigned_var.assignment = None
            return False
        
        return True
    
    def _backtrack(self, unassigned: List[SchedulingVariable], 
                   assigned: List[SchedulingVariable]) -> bool:
        """Backtracking search with constraint propagation"""
        
        self.iterations += 1
        
        if self.iterations > self.max_iterations:
            print(f"Max iterations ({self.max_iterations}) reached")
            return False
        
        # Check timeout
        if time.time() - self.start_time > self.timeout:
            print("Timeout reached")
            return False
        
        # Progress tracking and early termination if stuck
        # Track MAXIMUM progress ever achieved (not current, since backtracking reduces it)
        current_assigned = len(assigned)
        if current_assigned > self.last_progress_count:
            self.last_progress_count = current_assigned
            self.last_progress_iteration = self.iterations
            # CRITICAL: Preserve best solution assignments (deep copy)
            from copy import deepcopy
            self.best_assignments = deepcopy(self.assignments)
        elif self.iterations - self.last_progress_iteration > self.stall_threshold:
            # Only print once per stall period to avoid spam
            if (self.iterations - self.last_progress_iteration) == self.stall_threshold + 1:
                print(f"⚠️  No progress for {self.stall_threshold} iterations (best: {self.last_progress_count}/{len(self.variables)}, current: {current_assigned}/{len(self.variables)})")
                print(f"   Terminating early to avoid infinite loop")
            return False
        
        if self.iterations % 1000 == 0:
            print(f"Iteration {self.iterations}, assigned: {len(assigned)}/{len(self.variables)}")
        
        # Check if all variables assigned
        if len(unassigned) == 0:
            return True
        
        # Select variable using MRV + Degree heuristic
        # Filter out variables that are already assigned (might be assigned as part of a pair)
        unassigned_filtered = [v for v in unassigned if not v.is_assigned()]
        if not unassigned_filtered:
            # All variables assigned
            return True
        
        variable = self._select_unassigned_variable(unassigned_filtered)
        unassigned.remove(variable)
        
        # Debug: Check if variable has valid domain
        if len(variable.available_time_slots) == 0:
            subject = self.course_units.get(variable.course_unit_id)
            print(f"  ⚠️  Variable {variable.id} ({subject.code if subject else variable.course_unit_id}) has no available time slots")
            unassigned.append(variable)
            return False
        
        if len(variable.available_lecturers) == 0:
            subject = self.course_units.get(variable.course_unit_id)
            print(f"  ⚠️  Variable {variable.id} ({subject.code if subject else variable.course_unit_id}) has no available lecturers")
            print(f"      Subject: {variable.course_unit_id}, Group: {variable.program_id}")
            # Check which lecturers are qualified but unavailable (using canonical matching)
            from app.services.canonical_courses import is_canonical_match
            qualified_lecturers = [lec for lec in self.lecturers.values() 
                                 if is_canonical_match(variable.course_unit_id, lec.specializations)]
            if qualified_lecturers:
                print(f"      Qualified lecturers: {[lec.id for lec in qualified_lecturers]}")
                for lec in qualified_lecturers:
                    if lec.availability:
                        print(f"        {lec.id} ({lec.role}): Available {lec.availability}")
            unassigned.append(variable)
            return False
        
        if len(variable.available_rooms) == 0:
            subject = self.course_units.get(variable.course_unit_id)
            print(f"  ⚠️  Variable {variable.id} ({subject.code if subject else variable.course_unit_id}) has no available rooms")
            unassigned.append(variable)
            return False
        
        # Try values in order of LCV (Least Constraining Value)
        ordered_values = self._order_domain_values(variable)
        
        if len(ordered_values) == 0:
            print(f"  ⚠️  Variable {variable.id} has no valid domain combinations")
            unassigned.append(variable)
            return False
        
        for value_tuple in ordered_values:
            # Handle tuples: 3-tuple (time_slot, lecturer_id, room_number), 
            # 4-tuple (with room_priority), or 5-tuple (with room_priority and specialization_bonus)
            if len(value_tuple) == 5:
                time_slot, lecturer_id, room_number, _, _ = value_tuple
            elif len(value_tuple) == 4:
                time_slot, lecturer_id, room_number, _ = value_tuple
            else:
                time_slot, lecturer_id, room_number = value_tuple
            # Check for conflicts, allowing paired assignments
            if self._program_has_conflict(variable.program_id, time_slot, variable.id):
                # Conflict exists and it's not a paired assignment - skip this time slot
                continue
            
            assignment = Assignment(
                variable_id=variable.id,
                course_unit_id=variable.course_unit_id,
                program_id=variable.program_id,
                lecturer_id=lecturer_id,
                room_number=room_number,
                time_slot=time_slot,
                term=variable.term,
                session_number=variable.session_number
            )
            
            # Check assignment validity
            if not self._is_assignment_valid(assignment):
                continue
            
            # Check if this variable has paired variables
            paired_var_ids = self.variable_pairs.get(variable.id, [])
            paired_vars_assigned = []
            
            if paired_var_ids:
                # Try to assign all paired variables at the same time slot
                all_pairs_valid = True
                for paired_var_id in paired_var_ids:
                    paired_var = next((v for v in self.variables if v.id == paired_var_id), None)
                    if not paired_var or paired_var.is_assigned() or paired_var not in unassigned:
                        continue
                    
                    # Find valid assignment for paired variable at same time slot
                    paired_assignment = None
                    for paired_lecturer_id in paired_var.available_lecturers:
                        if paired_var.lecturer_time_slots:
                            lecturer_available_slots = paired_var.lecturer_time_slots.get(paired_lecturer_id)
                            if lecturer_available_slots is not None and time_slot not in lecturer_available_slots:
                                continue
                        
                        for paired_room_id in paired_var.available_rooms:
                            test_assignment = Assignment(
                                variable_id=paired_var.id,
                                course_unit_id=paired_var.course_unit_id,
                                program_id=paired_var.program_id,
                                lecturer_id=paired_lecturer_id,
                                room_number=paired_room_id,
                                time_slot=time_slot,
                                term=paired_var.term,
                                session_number=paired_var.session_number
                            )
                            
                            if self._is_assignment_valid(test_assignment):
                                paired_assignment = test_assignment
                                break
                        
                        if paired_assignment:
                            break
                    
                    if not paired_assignment:
                        all_pairs_valid = False
                        break
                    
                    paired_vars_assigned.append((paired_var, paired_assignment))
                
                if not all_pairs_valid:
                    # Cannot assign all pairs together - try next value
                    continue
                
                # Assign all pairs
                variable.assignment = assignment
                assigned.append(variable)
                self.assignments.append(assignment)
                self.constraint_context.add_assignment(assignment)
                
                # DEBUG: Log assignment
                for paired_var, paired_assignment in paired_vars_assigned:
                    paired_var.assignment = paired_assignment
                    if paired_var in unassigned:
                        unassigned.remove(paired_var)
                    assigned.append(paired_var)
                    self.assignments.append(paired_assignment)
                    self.constraint_context.add_assignment(paired_assignment)
            else:
                # No pairs - assign normally
                variable.assignment = assignment
                assigned.append(variable)
                self.assignments.append(assignment)
                self.constraint_context.add_assignment(assignment)
                
            # Forward checking - prune domains of unassigned variables
            if self._forward_check(unassigned, assignment):
                # Recurse
                if self._backtrack(unassigned, assigned):
                    return True
            
            # Backtrack - remove assignment and paired assignments
            
            variable.assignment = None
            if assignment in self.assignments:
                self.assignments.remove(assignment)
            self.constraint_context.remove_assignment(assignment.variable_id)
            if variable in assigned:
                assigned.remove(variable)
            
            # Remove paired assignments
            for paired_var, paired_assignment in paired_vars_assigned:
                paired_var.assignment = None
                if paired_assignment in self.assignments:
                    self.assignments.remove(paired_assignment)
                self.constraint_context.remove_assignment(paired_assignment.variable_id)
                if paired_var in assigned:
                    assigned.remove(paired_var)
                if paired_var not in unassigned:
                    unassigned.append(paired_var)
        
        # Failed to assign this variable, backtrack
        unassigned.append(variable)
        return False
    
    def _validate_solution(self, assignments: List[Assignment]) -> bool:
        """
        Comprehensive validation of CSP solution
        
        Returns True if solution is valid, False otherwise
        """
        from collections import defaultdict
        
        # Track usage by program, lecturer, and room
        student_time_slots = defaultdict(set)  # {program_id: {(day, period)}}
        lecturer_time_slots = defaultdict(set)  # {lecturer_id: {(day, period)}}
        room_time_slots = defaultdict(set)      # {room_number: {(day, period)}}
        
        for assignment in assignments:
            day = assignment.time_slot.day
            period = assignment.time_slot.period
            time_key = (day, period)
            
            # Check program double-booking
            if time_key in student_time_slots[assignment.program_id]:
                print(f"  ❌ Validation failed: Program {assignment.program_id} double-booked at {day} {period}")
                return False
            student_time_slots[assignment.program_id].add(time_key)
            
            # Check lecturer double-booking
            if time_key in lecturer_time_slots[assignment.lecturer_id]:
                print(f"  ❌ Validation failed: Lecturer {assignment.lecturer_id} double-booked at {day} {period}")
                return False
            lecturer_time_slots[assignment.lecturer_id].add(time_key)
            
            # Check room double-booking
            if time_key in room_time_slots[assignment.room_number]:
                print(f"  ❌ Validation failed: Room {assignment.room_number} double-booked at {day} {period}")
                return False
            room_time_slots[assignment.room_number].add(time_key)
            
            # Check room capacity
            program = self.programs.get(assignment.program_id)
            room = self.rooms.get(assignment.room_number)
            
            if program and room:
                if program.size > room.capacity:
                    print(f"  ❌ Validation failed: Room {assignment.room_number} capacity {room.capacity} < group size {program.size}")
                    return False
        
        return True
    
    def _select_unassigned_variable(self, unassigned: List[SchedulingVariable]) -> SchedulingVariable:
        """Select variable using MRV + Degree heuristic"""
        
        # Calculate accurate domain sizes (accounting for lecturer_time_slots filtering)
        def accurate_domain_size(v: SchedulingVariable) -> int:
            """Calculate domain size accounting for lecturer availability filtering"""
            valid_combinations = 0
            for time_slot in v.available_time_slots:
                for lecturer_id in v.available_lecturers:
                    # Check if lecturer is available for this time slot
                    if v.lecturer_time_slots:
                        lecturer_available_slots = v.lecturer_time_slots.get(lecturer_id)
                        if lecturer_available_slots is not None and time_slot not in lecturer_available_slots:
                            continue  # Skip - lecturer not available for this time slot
                    valid_combinations += len(v.available_rooms)
            return valid_combinations
        
        # Find minimum domain size using accurate calculation
        domain_sizes = [(v, accurate_domain_size(v)) for v in unassigned]
        min_domain = min(size for _, size in domain_sizes)
        
        # Get all variables with minimum domain
        mrv_candidates = [v for v, size in domain_sizes if size == min_domain]
        
        if len(mrv_candidates) == 1:
            return mrv_candidates[0]
        
        # Break ties with degree heuristic (most constraints on other variables)
        # Count how many other variables share resources (lecturer, room, program, time slot)
        def degree_heuristic(v: SchedulingVariable) -> int:
            degree = 0
            for other in unassigned:
                if other.id == v.id:
                    continue
                # Count constraints: shared program, shared lecturer, shared room
                if other.program_id == v.program_id:
                    degree += 1
                if other.available_lecturers & v.available_lecturers:
                    degree += 1
                if other.available_rooms & v.available_rooms:
                    degree += 1
            return degree
        
        # Select variable with highest degree (most constrained)
        mrv_candidates.sort(key=degree_heuristic, reverse=True)
        
        # Add random tie-breaking for variety in each generation
        # If multiple candidates have the same degree, randomly select one
        max_degree = degree_heuristic(mrv_candidates[0])
        top_candidates = [v for v in mrv_candidates if degree_heuristic(v) == max_degree]
        return random.choice(top_candidates)
    
    def _check_room_specialization_match(self, room, course_unit) -> bool:
        """Check if room specializations match course unit requirements
        
        Returns True if specializations match, False otherwise.
        This is used for prioritization, not filtering (rooms without matches are still allowed).
        """
        if not room or not course_unit:
            return False
        
        room_specializations = getattr(room, 'specializations', []) or []
        
        # If room has no specializations, consider it a match (general-purpose room)
        if not room_specializations:
            return True
        
        # Get course group to determine required specializations
        course_group_id = getattr(course_unit, 'course_group', None)
        if not course_group_id:
            # No course group - use fallback logic
            # Check course name/ID for Linux keyword
            course_name_or_id = (getattr(course_unit, 'name', '') or getattr(course_unit, 'id', '') or '').lower()
            if 'linux' in course_name_or_id:
                # Check if room has LINUX specialization
                if 'LINUX' in room_specializations:
                    return True
                # Also allow Networking & Cyber Security for backward compatibility
                for room_spec in room_specializations:
                    if 'Networking & Cyber Security' in room_spec:
                        return True
            
            required_room_type = getattr(course_unit, 'preferred_room_type', 'Theory')
            if required_room_type == 'Theory':
                return 'Theory' in room_specializations or len(room_specializations) == 0
            else:
                # Lab courses without course group: default to ICT-related specializations
                ict_specs = ['ICT', 'Programming', 'ICT & Programming']
                for spec in ict_specs:
                    if spec in room_specializations:
                        return True
                    for room_spec in room_specializations:
                        if spec in room_spec:
                            return True
                return False
        
        # Get canonical group name
        canonical_group_name = self.domain_manager._get_canonical_group_name(course_group_id)
        if not canonical_group_name:
            # Can't find canonical group - use fallback
            # Check course name/ID for Linux keyword
            course_name_or_id = (getattr(course_unit, 'name', '') or getattr(course_unit, 'id', '') or '').lower()
            if 'linux' in course_name_or_id:
                # Check if room has LINUX specialization
                if 'LINUX' in room_specializations:
                    return True
                # Also allow Networking & Cyber Security for backward compatibility
                for room_spec in room_specializations:
                    if 'Networking & Cyber Security' in room_spec:
                        return True
            
            required_room_type = getattr(course_unit, 'preferred_room_type', 'Theory')
            if required_room_type == 'Theory':
                return 'Theory' in room_specializations or len(room_specializations) == 0
            else:
                ict_specs = ['ICT', 'Programming', 'ICT & Programming']
                for spec in ict_specs:
                    if spec in room_specializations:
                        return True
                    for room_spec in room_specializations:
                        if spec in room_spec:
                            return True
                return False
        
        # Map canonical group name to required specializations
        required_room_type = getattr(course_unit, 'preferred_room_type', 'Theory')
        matching_specializations = self.domain_manager._map_canonical_to_specializations(
            canonical_group_name, required_room_type
        )
        
        # Check if room has any matching specialization
        for spec in matching_specializations:
            if spec in room_specializations:
                return True
            for room_spec in room_specializations:
                if spec in room_spec:
                    return True
        
        # Check Theory fallback
        if required_room_type == 'Theory' and 'Theory' in room_specializations:
            return True
        
        return False
    
    def _order_domain_values(self, variable: SchedulingVariable) -> List[Tuple]:
        """Order domain values using LCV (Least Constraining Value) heuristic"""
        
        values = []
        
        # Generate all combinations, filtering by lecturer availability
        for time_slot in variable.available_time_slots:
            for lecturer_id in variable.available_lecturers:
                # Check if lecturer is available for this time slot
                # For part-time lecturers, this filters to only their available days/hours
                if variable.lecturer_time_slots:
                    lecturer_available_slots = variable.lecturer_time_slots.get(lecturer_id)
                    if lecturer_available_slots is not None and time_slot not in lecturer_available_slots:
                        continue  # Skip - lecturer not available for this time slot
                
                for room_number in variable.available_rooms:
                    # Prioritize Lab rooms for lab subjects and rooms with matching specializations
                    room = self.rooms.get(room_number)
                    course_unit = self.course_units.get(variable.course_unit_id)
                    room_priority = 0
                    if course_unit and course_unit.preferred_room_type == 'Lab' and room:
                        if room.room_type == 'Lab':
                            room_priority = -1000  # Strongly prefer Lab rooms for lab subjects
                        else:
                            room_priority = 1000  # Penalize non-Lab rooms for lab subjects
                    
                    # Add specialization matching bonus (prefer rooms with matching specializations)
                    specialization_bonus = 0
                    if room and course_unit:
                        if self._check_room_specialization_match(room, course_unit):
                            specialization_bonus = -200  # Prefer rooms with matching specializations
                        else:
                            specialization_bonus = 50  # Small penalty for non-matching (but still allowed)
                    
                    values.append((time_slot, lecturer_id, room_number, room_priority, specialization_bonus))
        
        if not values:
            return values
        
        # Count existing assignments per time slot for distribution
        time_slot_usage = defaultdict(int)
        for assignment in self.assignments:
            time_key = f"{assignment.time_slot.day}_{assignment.time_slot.period}"
            time_slot_usage[time_key] += 1
        
        # LCV Heuristic: Order by room type priority + least constraining value + merge preference + time distribution
        # Get group size for capacity-based prioritization
        group_size = self.constraint_context.programs.get(variable.program_id, {}).get('size', 0)
        
        if len(values) > 100:
            def score_value(value_tuple):
                if len(value_tuple) == 5:
                    time_slot, lecturer_id, room_number, room_priority, specialization_bonus = value_tuple
                elif len(value_tuple) == 4:
                    time_slot, lecturer_id, room_number, room_priority = value_tuple
                    specialization_bonus = 0
                else:
                    time_slot, lecturer_id, room_number = value_tuple
                    room_priority = 0
                    specialization_bonus = 0
                score = room_priority + specialization_bonus  # Room type + specialization matching priority
                
                time_key = f"{time_slot.day}_{time_slot.period}"
                room = self.constraint_context.rooms.get(room_number)
                room_capacity = room.get('capacity', 0) if room else 0
                
                # CRITICAL: Prioritize rooms with sufficient capacity for the group
                # This prevents the solver from getting stuck trying small rooms
                if room_capacity < group_size:
                    score += 10000  # Heavily penalize rooms that are too small
                elif room_capacity >= group_size:
                    # Prefer rooms that fit the group but aren't excessively large
                    # This helps with resource utilization
                    excess_capacity = room_capacity - group_size
                    score += excess_capacity * 0.1  # Small penalty for excess capacity
                
                # Time distribution: Prefer less-used time slots
                current_usage = time_slot_usage.get(time_key, 0)
                score += current_usage * 10
                
                if room_number in self.constraint_context.room_schedule:
                    if time_key in self.constraint_context.room_schedule[room_number]:
                        existing_assignments = self.constraint_context.room_schedule[room_number][time_key]
                        
                        total_students = 0
                        current_group_size = self.constraint_context.programs.get(variable.program_id, {}).get('size', 0)
                        
                        for var_id in existing_assignments:
                            existing_assignment = self.constraint_context.assignments.get(var_id)
                            if existing_assignment and existing_assignment.course_unit_id == variable.course_unit_id:
                                existing_group = self.constraint_context.programs.get(existing_assignment.program_id, {})
                                existing_group_size = existing_group.get('size', 0)
                                total_students += existing_group_size
                        
                        total_students += current_group_size
                        
                        if total_students > 0 and total_students <= room_capacity:
                            score -= 1000
                
                conflict_count = 0
                for other_var in self.variables:
                    if other_var.id == variable.id or other_var.is_assigned():
                        continue
                    if lecturer_id in other_var.available_lecturers:
                        conflict_count += 1
                    if room_number in other_var.available_rooms:
                        conflict_count += 1
                    if time_slot in other_var.available_time_slots:
                        conflict_count += 1
                
                score += conflict_count
                return score
            
            # Sort by score (lower is better - merge opportunities first, then least constraining)
            values.sort(key=score_value)
            values = values[:100]  # Limit to 100 values for performance
            
            # Add randomization: shuffle values with the same score for variety
            if len(values) > 1:
                # Group by score and shuffle within groups
                from itertools import groupby
                shuffled = []
                for score, group in groupby(values, key=score_value):
                    group_list = list(group)
                    random.shuffle(group_list)
                    shuffled.extend(group_list)
                values = shuffled
        else:
            def count_remaining_options(value_tuple):
                if len(value_tuple) == 5:
                    time_slot, lecturer_id, room_number, room_priority, specialization_bonus = value_tuple
                elif len(value_tuple) == 4:
                    time_slot, lecturer_id, room_number, room_priority = value_tuple
                    specialization_bonus = 0
                else:
                    time_slot, lecturer_id, room_number = value_tuple
                    room_priority = 0
                    specialization_bonus = 0
                
                score = room_priority + specialization_bonus  # Room type + specialization matching priority
                
                time_key = f"{time_slot.day}_{time_slot.period}"
                room = self.constraint_context.rooms.get(room_number)
                room_capacity = room.get('capacity', 0) if room else 0
                
                # CRITICAL: Prioritize rooms with sufficient capacity for the group
                # This prevents the solver from getting stuck trying small rooms
                if room_capacity < group_size:
                    score += 10000  # Heavily penalize rooms that are too small
                elif room_capacity >= group_size:
                    # Prefer rooms that fit the group but aren't excessively large
                    # This helps with resource utilization
                    excess_capacity = room_capacity - group_size
                    score += excess_capacity * 0.1  # Small penalty for excess capacity
                
                # Time distribution: Prefer less-used time slots
                current_usage = time_slot_usage.get(time_key, 0)
                score += current_usage * 10
                
                if room_number in self.constraint_context.room_schedule:
                    if time_key in self.constraint_context.room_schedule[room_number]:
                        existing_assignments = self.constraint_context.room_schedule[room_number][time_key]
                        
                        total_students = 0
                        current_group_size = self.constraint_context.programs.get(variable.program_id, {}).get('size', 0)
                        
                        for var_id in existing_assignments:
                            existing_assignment = self.constraint_context.assignments.get(var_id)
                            if existing_assignment and existing_assignment.course_unit_id == variable.course_unit_id:
                                existing_group = self.constraint_context.programs.get(existing_assignment.program_id, {})
                                existing_group_size = existing_group.get('size', 0)
                                total_students += existing_group_size
                        
                        total_students += current_group_size
                        
                        if total_students > 0 and total_students <= room_capacity:
                            score -= 1000
                
                # Simplified heuristic: Count how many unassigned variables share resources
                # Values that share resources with fewer variables are less constraining
                conflict_count = 0
                
                # Only check unassigned variables (much faster)
                for other_var in self.variables:
                    if other_var.id == variable.id or other_var.is_assigned():
                        continue
                    
                    # Count shared resources (more shared = more constraining)
                    if lecturer_id in other_var.available_lecturers:
                        conflict_count += 1
                    if room_number in other_var.available_rooms:
                        conflict_count += 1
                    if time_slot in other_var.available_time_slots:
                        conflict_count += 1
                
                score += conflict_count
                # Lower conflict count = less constraining = better
                return score
            
            # Sort by score (lower is better - merge opportunities first, then least constraining)
            values.sort(key=count_remaining_options)
            
            # Add randomization: shuffle values with the same score for variety
            if len(values) > 1:
                # Group by score and shuffle within groups
                from itertools import groupby
                shuffled = []
                for score, group in groupby(values, key=count_remaining_options):
                    group_list = list(group)
                    random.shuffle(group_list)
                    shuffled.extend(group_list)
                values = shuffled
        
        return values
    
    def _forward_check(self, unassigned: List[SchedulingVariable], 
                       assignment: Assignment) -> bool:
        """
        Forward checking - prune inconsistent values from unassigned variables
        
        NOTE: Simplified version - only checks if assignment would cause immediate conflicts
        Full forward checking is computationally expensive and can cause premature backtracking.
        We rely on constraint checking during value assignment instead.
        """
        # Simplified forward check: Only check variables that share resources with this assignment
        # This is much faster and less likely to cause false negatives
        
        time_key = f"{assignment.time_slot.day}_{assignment.time_slot.period}"
        
        # Only check a few critical variables that share resources
        # Check at most 5 variables to avoid performance issues
        checked = 0
        max_check = min(5, len(unassigned))
        
        for var in unassigned:
            if checked >= max_check:
                break
            
            # Only check variables that share resources (likely to conflict)
            shares_resources = (
                var.program_id == assignment.program_id or
                assignment.lecturer_id in var.available_lecturers or
                assignment.room_number in var.available_rooms
            )
            
            if not shares_resources:
                continue
            
            checked += 1
            
            # Quick check: Does this variable still have at least one valid option?
            # Use constraint context to check if assignment would block all options
            has_valid_option = False
            
            # Try a few sample combinations to see if any would work
            # (Full check is too expensive, so we sample)
            sample_size = min(10, len(var.available_time_slots))
            time_slots_sample = list(var.available_time_slots)[:sample_size]
            
            for time_slot in time_slots_sample:
                # Skip if this time slot conflicts with assignment
                if (time_slot.day == assignment.time_slot.day and 
                    time_slot.period == assignment.time_slot.period):
                    # Same time - check if resources conflict
                    if (var.program_id == assignment.program_id or
                        assignment.lecturer_id in var.available_lecturers or
                        assignment.room_number in var.available_rooms):
                        continue  # Conflict at this time slot
                
                # Found a time slot that doesn't conflict - variable still has options
                has_valid_option = True
                break
            
            # If sampled time slots all conflict, variable might be blocked
            # But we don't reject immediately - let constraint checking handle it
            # This prevents false negatives from sampling
            if not has_valid_option and len(var.available_time_slots) <= sample_size:
                # All time slots sampled conflict - likely dead-end
                # But be conservative - only reject if we're very sure
                pass  # Allow it - constraint checking will catch it
        
        return True  # Allow assignment - constraint checking will validate
    
    def get_solution(self) -> Dict:
        """Get formatted solution"""
        
        if not self.assignments:
            return None
        
        # Group by program
        timetable = defaultdict(list)
        
        for assignment in self.assignments:
            course_unit = self.course_units[assignment.course_unit_id]
            lecturer = self.lecturers[assignment.lecturer_id]
            room = self.rooms[assignment.room_number]
            program = self.programs[assignment.program_id]
            
            session = {
                'session_id': assignment.variable_id,
                'course_unit': {
                    'id': course_unit.id,
                    'code': course_unit.code,
                    'name': course_unit.name,
                    'preferred_room_type': course_unit.preferred_room_type
                },
                'lecturer': {
                    'id': lecturer.id,
                    'name': lecturer.name
                },
                'room': {
                    'room_number': room.room_number,
                    'capacity': room.capacity,
                    'type': room.room_type
                },
                'time_slot': assignment.time_slot.to_dict(),
                'term': assignment.term,
                'session_number': assignment.session_number
            }
            
            timetable[program.id].append(session)
        
        return {
            'success': True,
            'timetable': dict(timetable),
            'statistics': {
                'total_sessions': len(self.assignments),
                'iterations': self.iterations,
                'time_elapsed': time.time() - self.start_time if self.start_time else 0,
                'variables': len(self.variables),
                'constraints_checked': self.iterations * 8  # Approximate
            }
        }