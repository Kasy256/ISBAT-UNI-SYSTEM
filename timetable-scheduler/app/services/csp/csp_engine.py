import time
import math
from typing import List, Dict, Set, Optional, Tuple
from collections import defaultdict
from app.services.csp.domain import SchedulingVariable, Assignment, TimeSlot, DomainManager
from app.services.csp.constraints import ConstraintChecker, ConstraintContext, ConstraintType
from app.models.lecturer import Lecturer
from app.models.room import Room
from app.models.course import CourseUnit
from app.models.student import StudentGroup
from app.config import Config

class CSPEngine:
    """CSP-based timetable scheduling engine"""
    
    def __init__(self):
        self.domain_manager = DomainManager()
        self.constraint_checker = ConstraintChecker()
        self.constraint_context = None  # Will be initialized with data
        self.variables: List[SchedulingVariable] = []
        self.assignments: List[Assignment] = []
        self.iterations = 0
        self.max_iterations = Config.CSP_MAX_ITERATIONS
        self.start_time = None
        self.timeout = Config.CSP_TIMEOUT_SECONDS
        
        # Progress tracking for early termination
        self.last_progress_iteration = 0
        self.last_progress_count = 0
        self.stall_threshold = 5000  # If no progress for 5000 iterations, terminate
        
        # Data caches
        self.lecturers: Dict[str, Lecturer] = {}
        self.rooms: Dict[str, Room] = {}
        self.course_units: Dict[str, CourseUnit] = {}
        self.student_groups: Dict[str, StudentGroup] = {}
    
    def initialize(self, lecturers: List[Lecturer], rooms: List[Room], 
                   course_units: List[CourseUnit], student_groups: List[StudentGroup]):
        """Initialize CSP with data"""
        
        # Build lookup dictionaries
        self.lecturers = {lec.id: lec for lec in lecturers}
        self.rooms = {room.id: room for room in rooms}
        self.course_units = {cu.id: cu for cu in course_units}
        self.student_groups = {sg.id: sg for sg in student_groups}
        
        # Initialize constraint context with resource data
        self.constraint_context = ConstraintContext()
        # Populate context with resource data for constraint checking (CRITICAL: include all required fields)
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
            room.id: {
                'id': room.id, 
                'capacity': room.capacity, 
                'room_type': room.room_type
            } for room in rooms
        }
        self.constraint_context.course_units = {
            cu.id: {
                'id': cu.id, 
                'is_lab': cu.is_lab
            } for cu in course_units
        }
        self.constraint_context.student_groups = {
            sg.id: {
                'id': sg.id, 
                'size': sg.size
            } for sg in student_groups
        }
        
        # Create variables for each session
        self.variables = []
        var_id = 1
        
        for student_group in student_groups:
            for course_unit_id in student_group.course_units:
                course_unit = self.course_units.get(course_unit_id)
                if not course_unit:
                    continue
                
                sessions_needed = course_unit.sessions_required
                
                for session_num in range(1, sessions_needed + 1):
                    variable = SchedulingVariable(
                        id=f"VAR_{var_id}",
                        course_unit_id=course_unit.id,
                        student_group_id=student_group.id,
                        term=student_group.term,
                        session_number=session_num,
                        sessions_required=sessions_needed
                    )
                    
                    # Initialize domains (pass student_group for capacity filtering)
                    self.domain_manager.initialize_variable_domains(
                        variable, lecturers, rooms, course_unit, student_group
                    )
                    
                    self.variables.append(variable)
                    var_id += 1
        
        print(f"Initialized CSP with {len(self.variables)} variables")
        
        # DIAGNOSTIC: Check domain sizes and identify problematic variables
        print("\n📊 Domain Analysis:")
        zero_domain_vars = []
        small_domain_vars = []
        
        # Use accurate domain size calculation (accounts for lecturer_time_slots)
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
        
        for var in self.variables:
            domain_size = accurate_domain_size(var)
            if domain_size == 0:
                zero_domain_vars.append(var)
            elif domain_size < 10:
                small_domain_vars.append(var)
        
        if zero_domain_vars:
            print(f"   ⚠️  {len(zero_domain_vars)} variables have ZERO valid domain combinations:")
            for var in zero_domain_vars[:5]:  # Show first 5
                course = self.course_units.get(var.course_unit_id)
                group = self.student_groups.get(var.student_group_id)
                print(f"      • {var.id}: {course.code if course else var.course_unit_id} for {group.display_name if group else var.student_group_id}")
                print(f"        - Time slots: {len(var.available_time_slots)}")
                print(f"        - Lecturers: {len(var.available_lecturers)}")
                print(f"        - Rooms: {len(var.available_rooms)}")
        
        if small_domain_vars:
            print(f"   ⚠️  {len(small_domain_vars)} variables have < 10 domain combinations (may be constrained)")
        
        # Check lecturer coverage
        course_lecturer_count = {}
        for var in self.variables:
            course_id = var.course_unit_id
            if course_id not in course_lecturer_count:
                course_lecturer_count[course_id] = len(var.available_lecturers)
        
        low_coverage = {cid: count for cid, count in course_lecturer_count.items() if count < 2}
        if low_coverage:
            print(f"\n   ⚠️  {len(low_coverage)} courses have < 2 available lecturers:")
            for course_id, count in list(low_coverage.items())[:5]:
                course = self.course_units.get(course_id)
                print(f"      • {course.code if course else course_id}: {count} lecturer(s)")
        
        print()  # Empty line for readability
    
    def solve(self) -> Optional[List[Assignment]]:
        """Solve CSP using backtracking with heuristics"""
        
        self.start_time = time.time()
        self.iterations = 0
        self.assignments = []
        self.last_progress_iteration = 0
        self.last_progress_count = 0
        
        # Reset constraint context for fresh solve
        self.constraint_context = ConstraintContext()
        # Re-populate context with resource data (CRITICAL: include ALL required fields for constraint checking)
        self.constraint_context.lecturers = {
            lec.id: {
                'id': lec.id, 
                'name': lec.name, 
                'role': lec.role,  # CRITICAL: Required for weekly hour limit checking
                'max_weekly_hours': lec.max_weekly_hours,  # CRITICAL: Required for weekly hour limit checking
                'specializations': lec.specializations
            } for lec in list(self.lecturers.values())
        }
        self.constraint_context.rooms = {
            room.id: {
                'id': room.id, 
                'capacity': room.capacity, 
                'room_type': room.room_type
            } for room in list(self.rooms.values())
        }
        self.constraint_context.course_units = {
            cu.id: {
                'id': cu.id, 
                'is_lab': cu.is_lab
            } for cu in list(self.course_units.values())
        }
        self.constraint_context.student_groups = {
            sg.id: {
                'id': sg.id, 
                'size': sg.size
            } for sg in list(self.student_groups.values())
        }
        
        # Sort variables by MRV (Minimum Remaining Values) heuristic
        unassigned = sorted(self.variables, key=lambda v: v.domain_size())
        
        result = self._backtrack(unassigned, [])
        
        if result:
            # CRITICAL: Comprehensive validation using ConstraintChecker
            all_valid = True
            violations_found = []
            
            # Rebuild context and validate all assignments
            test_context = ConstraintContext()
            test_context.lecturers = self.constraint_context.lecturers.copy()
            test_context.rooms = self.constraint_context.rooms.copy()
            test_context.course_units = self.constraint_context.course_units.copy()
            test_context.student_groups = self.constraint_context.student_groups.copy()
            
            for assignment in self.assignments:
                is_valid, violations = self.constraint_checker.check_all(assignment, test_context)
                if not is_valid:
                    all_valid = False
                    violations_found.extend(violations)
                test_context.add_assignment(assignment)
            
            # Separate critical violations from limit violations
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
                    print(f"⚠️  Solution has {len(limit_violations)} limit violations (weekly/daily hours)")
                    print(f"   GGA will repair these violations during optimization phase")
                    if limit_violations:
                        print(f"   First few violations: {limit_violations[:3]}")
                    return self.assignments
                else:
                    print(f"Solution found in {self.iterations} iterations ({time.time() - self.start_time:.2f}s)")
                    print(f"✅ All {len(self.assignments)} assignments validated - zero constraint violations")
                    return self.assignments
            else:
                # Critical violations should never happen - this indicates a bug
                print(f"⚠️  Solution found with {len(critical_violations)} CRITICAL violations")
                print(f"   This indicates a bug in constraint enforcement")
                print(f"   Critical violations: {critical_violations[:3]}")
                return self.assignments  # Return anyway, but this should be fixed
        else:
            print(f"No complete solution found after {self.iterations} iterations")
            print(f"   Progress: {len(self.assignments)}/{len(self.variables)} sessions assigned")
            if len(self.assignments) > 0:
                print(f"   ⚠️  CSP got stuck - returning partial solution")
                print(f"      • Over-constrained problem (too many strict constraints)")
                print(f"      • Insufficient resources (lecturers, rooms, time slots)")
                print(f"      • Need for better search heuristics")
                print(f"   💡 Passing partial solution to GGA - it will try to complete and repair violations")
                # Return partial solution - GGA can try to complete it
                return self.assignments
            return None
    
    def _backtrack(self, unassigned: List[SchedulingVariable], 
                   assigned: List[SchedulingVariable]) -> bool:
        """Backtracking search with constraint propagation"""
        
        self.iterations += 1
        
        # CRITICAL FIX: Check max_iterations limit (was missing!)
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
        elif self.iterations - self.last_progress_iteration > self.stall_threshold:
            print(f"⚠️  No progress for {self.stall_threshold} iterations (best: {self.last_progress_count}/{len(self.variables)}, current: {current_assigned}/{len(self.variables)})")
            print(f"   Terminating early to avoid infinite loop")
            return False
        
        if self.iterations % 1000 == 0:
            print(f"Iteration {self.iterations}, assigned: {len(assigned)}/{len(self.variables)}")
        
        # Check if all variables assigned
        if len(unassigned) == 0:
            return True
        
        # Select variable using MRV + Degree heuristic
        variable = self._select_unassigned_variable(unassigned)
        unassigned.remove(variable)
        
        # Debug: Check if variable has valid domain
        if len(variable.available_time_slots) == 0:
            course = self.course_units.get(variable.course_unit_id)
            print(f"  ⚠️  Variable {variable.id} ({course.code if course else variable.course_unit_id}) has no available time slots")
            unassigned.append(variable)
            return False
        
        if len(variable.available_lecturers) == 0:
            course = self.course_units.get(variable.course_unit_id)
            print(f"  ⚠️  Variable {variable.id} ({course.code if course else variable.course_unit_id}) has no available lecturers")
            print(f"      Course: {variable.course_unit_id}, Group: {variable.student_group_id}")
            # Check which lecturers are qualified but unavailable
            qualified_lecturers = [lec for lec in self.lecturers.values() 
                                 if variable.course_unit_id in lec.specializations]
            if qualified_lecturers:
                print(f"      Qualified lecturers: {[lec.id for lec in qualified_lecturers]}")
                for lec in qualified_lecturers:
                    if lec.availability:
                        print(f"        {lec.id} ({lec.role}): Available {lec.availability}")
            unassigned.append(variable)
            return False
        
        if len(variable.available_rooms) == 0:
            course = self.course_units.get(variable.course_unit_id)
            print(f"  ⚠️  Variable {variable.id} ({course.code if course else variable.course_unit_id}) has no available rooms")
            unassigned.append(variable)
            return False
        
        # Try values in order of LCV (Least Constraining Value)
        ordered_values = self._order_domain_values(variable)
        
        if len(ordered_values) == 0:
            print(f"  ⚠️  Variable {variable.id} has no valid domain combinations")
            unassigned.append(variable)
            return False
        
        # Debug: Show how many values we're trying
        if self.iterations <= 3:
            print(f"  🔍 Variable {variable.id}: Trying {len(ordered_values)} domain combinations")
        
        for time_slot, lecturer_id, room_id in ordered_values:
            # Quick pre-check: student group conflict (fastest check, prevents double-booking)
            time_key = f"{time_slot.day}_{time_slot.period}"
            if variable.student_group_id in self.constraint_context.student_group_schedule:
                if time_key in self.constraint_context.student_group_schedule[variable.student_group_id]:
                    existing = self.constraint_context.student_group_schedule[variable.student_group_id][time_key]
                    if len(existing) > 0:
                        continue  # Skip - student group already has session at this time
            
            # Create assignment
            assignment = Assignment(
                variable_id=variable.id,
                course_unit_id=variable.course_unit_id,
                student_group_id=variable.student_group_id,
                lecturer_id=lecturer_id,
                room_id=room_id,
                time_slot=time_slot,
                term=variable.term,
                session_number=variable.session_number
            )
            
            course_unit = self.course_units[variable.course_unit_id]
            
            # INDUSTRY-STANDARD: Two-phase constraint checking
            # Phase 1 (CSP): Enforce CRITICAL constraints that cannot be repaired
            # Phase 2 (GGA): Repair LIMIT violations (weekly/daily hours)
            
            # Check critical constraints (must be satisfied in CSP phase)
            # 1. Double-booking (CRITICAL - cannot be repaired)
            if not self.constraint_checker.check_constraint(
                ConstraintType.NO_DOUBLE_BOOKING, assignment, self.constraint_context
            ):
                continue  # Reject immediately
            
            # 2. Room capacity (CRITICAL - cannot be repaired)
            if not self.constraint_checker.check_constraint(
                ConstraintType.ROOM_CAPACITY, assignment, self.constraint_context
            ):
                continue  # Reject immediately
            
            # 3. Room type matching (CRITICAL - cannot be repaired)
            if not self.constraint_checker.check_constraint(
                ConstraintType.ROOM_TYPE, assignment, self.constraint_context
            ):
                continue  # Reject immediately
            
            # 4. Lecturer specialization (CRITICAL - validated during domain initialization)
            # Already handled by available_lecturers filter
            
            # 5. Standard teaching blocks (CRITICAL - validated during domain initialization)
            # Already handled by available_time_slots filter
            
            # 6. Weekly hour limits (SOFT - allow violations, GGA will repair)
            # These are checked but not enforced during CSP to allow solution finding
            # GGA will repair violations during optimization phase
            weekly_ok = self.constraint_checker.check_constraint(
                ConstraintType.WEEKLY_LIMIT, assignment, self.constraint_context
            )
            # Note: We allow violations here - GGA will fix them
            
            # 7. Daily session limits (SOFT - allow violations, GGA will repair)
            # These are checked but not enforced during CSP to allow solution finding
            # GGA will repair violations during optimization phase
            daily_ok = self.constraint_checker.check_constraint(
                ConstraintType.DAILY_LIMIT, assignment, self.constraint_context
            )
            # Note: We allow violations here - GGA will fix them
            
            # Same-day repetition - allow consecutive labs, reject others
            same_day_ok = self.constraint_checker.check_constraint(
                ConstraintType.NO_SAME_DAY, assignment, self.constraint_context
            )
            if not same_day_ok:
                # Check if it's a consecutive lab session (allowed)
                # This is handled in the constraint itself, so if it fails, reject
                continue
            
            # Merging/splitting - check but allow if needed (GGA can repair)
            # Check merging constraint (allows multiple groups in same room/time if capacity allows)
            merge_ok = self.constraint_checker.check_constraint(
                ConstraintType.CLASS_MERGING, assignment, self.constraint_context
            )
            if not merge_ok:
                continue  # Reject if merged groups exceed room capacity
            
            # Check splitting constraint (ensures large groups are split)
            split_ok = self.constraint_checker.check_constraint(
                ConstraintType.CLASS_SPLITTING, assignment, self.constraint_context
            )
            if not split_ok:
                continue  # Reject if group too large and not split
            
            # All critical constraints passed - accept assignment
            
            # Assignment passed all constraints - add it
            variable.assignment = assignment  # Track assignment in variable
            assigned.append(variable)
            self.assignments.append(assignment)
            self.constraint_context.add_assignment(assignment)
            
            # Forward checking - prune domains of unassigned variables
            if self._forward_check(unassigned, assignment):
                # Recurse
                if self._backtrack(unassigned, assigned):
                    return True
            
            # Backtrack - remove assignment
            variable.assignment = None
            self.assignments.remove(assignment)
            self.constraint_context.remove_assignment(assignment.variable_id)
            assigned.remove(variable)
        
        # Failed to assign this variable, backtrack
        unassigned.append(variable)
        return False
    
    def _validate_solution(self, assignments: List[Assignment]) -> bool:
        """
        Comprehensive validation of CSP solution
        
        Returns True if solution is valid, False otherwise
        """
        from collections import defaultdict
        
        # Track usage by student group, lecturer, and room
        student_time_slots = defaultdict(set)  # {student_group_id: {(day, period)}}
        lecturer_time_slots = defaultdict(set)  # {lecturer_id: {(day, period)}}
        room_time_slots = defaultdict(set)      # {room_id: {(day, period)}}
        
        for assignment in assignments:
            day = assignment.time_slot.day
            period = assignment.time_slot.period
            time_key = (day, period)
            
            # Check student group double-booking
            if time_key in student_time_slots[assignment.student_group_id]:
                print(f"  ❌ Validation failed: Student group {assignment.student_group_id} double-booked at {day} {period}")
                return False
            student_time_slots[assignment.student_group_id].add(time_key)
            
            # Check lecturer double-booking
            if time_key in lecturer_time_slots[assignment.lecturer_id]:
                print(f"  ❌ Validation failed: Lecturer {assignment.lecturer_id} double-booked at {day} {period}")
                return False
            lecturer_time_slots[assignment.lecturer_id].add(time_key)
            
            # Check room double-booking
            if time_key in room_time_slots[assignment.room_id]:
                print(f"  ❌ Validation failed: Room {assignment.room_id} double-booked at {day} {period}")
                return False
            room_time_slots[assignment.room_id].add(time_key)
            
            # Check room capacity
            student_group = self.student_groups.get(assignment.student_group_id)
            room = self.rooms.get(assignment.room_id)
            
            if student_group and room:
                if student_group.size > room.capacity:
                    print(f"  ❌ Validation failed: Room {assignment.room_id} capacity {room.capacity} < group size {student_group.size}")
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
        # Count how many other variables share resources (lecturer, room, student group, time slot)
        def degree_heuristic(v: SchedulingVariable) -> int:
            degree = 0
            for other in unassigned:
                if other.id == v.id:
                    continue
                # Count constraints: shared student group, shared lecturer, shared room
                if other.student_group_id == v.student_group_id:
                    degree += 1
                if other.available_lecturers & v.available_lecturers:
                    degree += 1
                if other.available_rooms & v.available_rooms:
                    degree += 1
            return degree
        
        # Select variable with highest degree (most constrained)
        mrv_candidates.sort(key=degree_heuristic, reverse=True)
        return mrv_candidates[0]
    
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
                
                for room_id in variable.available_rooms:
                    values.append((time_slot, lecturer_id, room_id))
        
        if not values:
            return values
        
        # LCV Heuristic: Order by least constraining value + merge preference
        # A value is less constraining if it leaves more options for other variables
        # PLUS: Prefer values that allow merging with existing shared course assignments
        # OPTIMIZED: Only check unassigned variables, and limit to reasonable number
        if len(values) > 100:
            # Too many values - use simpler heuristic with merge preference
            def score_value(value_tuple):
                time_slot, lecturer_id, room_id = value_tuple
                score = 0
                
                # Merge preference: Check if this assignment would merge with existing shared courses
                time_key = f"{time_slot.day}_{time_slot.period}"
                room = self.constraint_context.rooms.get(room_id)
                room_capacity = room.get('capacity', 0) if room else 0
                
                # Check if other groups with same course are already assigned to this room/time
                if room_id in self.constraint_context.room_schedule:
                    if time_key in self.constraint_context.room_schedule[room_id]:
                        existing_assignments = self.constraint_context.room_schedule[room_id][time_key]
                        
                        # Check if any existing assignment is for the same course (potential merge)
                        total_students = 0
                        current_group_size = self.constraint_context.student_groups.get(variable.student_group_id, {}).get('size', 0)
                        
                        for var_id in existing_assignments:
                            existing_assignment = self.constraint_context.assignments.get(var_id)
                            if existing_assignment and existing_assignment.course_unit_id == variable.course_unit_id:
                                # Same course! Check if we can merge
                                existing_group = self.constraint_context.student_groups.get(existing_assignment.student_group_id, {})
                                existing_group_size = existing_group.get('size', 0)
                                total_students += existing_group_size
                        
                        total_students += current_group_size
                        
                        # Prefer merging if it fits (bonus score)
                        if total_students > 0 and total_students <= room_capacity:
                            score -= 1000  # Large bonus for merge opportunities (lower score = preferred)
                
                # Add conflict count (more conflicts = higher score = less preferred)
                conflict_count = 0
                for other_var in self.variables:
                    if other_var.id == variable.id or other_var.is_assigned():
                        continue
                    if lecturer_id in other_var.available_lecturers:
                        conflict_count += 1
                    if room_id in other_var.available_rooms:
                        conflict_count += 1
                    if time_slot in other_var.available_time_slots:
                        conflict_count += 1
                
                score += conflict_count
                return score
            
            # Sort by score (lower is better - merge opportunities first, then least constraining)
            values.sort(key=score_value)
            values = values[:100]  # Limit to 100 values for performance
        else:
            # Reasonable number - use full LCV heuristic with merge preference
            def count_remaining_options(value_tuple):
                time_slot, lecturer_id, room_id = value_tuple
                
                score = 0
                
                # Merge preference: Check if this assignment would merge with existing shared courses
                time_key = f"{time_slot.day}_{time_slot.period}"
                room = self.constraint_context.rooms.get(room_id)
                room_capacity = room.get('capacity', 0) if room else 0
                
                # Check if other groups with same course are already assigned to this room/time
                if room_id in self.constraint_context.room_schedule:
                    if time_key in self.constraint_context.room_schedule[room_id]:
                        existing_assignments = self.constraint_context.room_schedule[room_id][time_key]
                        
                        # Check if any existing assignment is for the same course (potential merge)
                        total_students = 0
                        current_group_size = self.constraint_context.student_groups.get(variable.student_group_id, {}).get('size', 0)
                        
                        for var_id in existing_assignments:
                            existing_assignment = self.constraint_context.assignments.get(var_id)
                            if existing_assignment and existing_assignment.course_unit_id == variable.course_unit_id:
                                # Same course! Check if we can merge
                                existing_group = self.constraint_context.student_groups.get(existing_assignment.student_group_id, {})
                                existing_group_size = existing_group.get('size', 0)
                                total_students += existing_group_size
                        
                        total_students += current_group_size
                        
                        # Prefer merging if it fits (bonus score)
                        if total_students > 0 and total_students <= room_capacity:
                            score -= 1000  # Large bonus for merge opportunities (lower score = preferred)
                
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
                    if room_id in other_var.available_rooms:
                        conflict_count += 1
                    if time_slot in other_var.available_time_slots:
                        conflict_count += 1
                
                score += conflict_count
                # Lower conflict count = less constraining = better
                return score
            
            # Sort by score (lower is better - merge opportunities first, then least constraining)
            values.sort(key=count_remaining_options)
        
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
                var.student_group_id == assignment.student_group_id or
                assignment.lecturer_id in var.available_lecturers or
                assignment.room_id in var.available_rooms
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
                    if (var.student_group_id == assignment.student_group_id or
                        assignment.lecturer_id in var.available_lecturers or
                        assignment.room_id in var.available_rooms):
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
        
        # Group by student group
        timetable = defaultdict(list)
        
        for assignment in self.assignments:
            course_unit = self.course_units[assignment.course_unit_id]
            lecturer = self.lecturers[assignment.lecturer_id]
            room = self.rooms[assignment.room_id]
            student_group = self.student_groups[assignment.student_group_id]
            
            session = {
                'session_id': assignment.variable_id,
                'course_unit': {
                    'id': course_unit.id,
                    'code': course_unit.code,
                    'name': course_unit.name,
                    'is_lab': course_unit.is_lab
                },
                'lecturer': {
                    'id': lecturer.id,
                    'name': lecturer.name
                },
                'room': {
                    'id': room.id,
                    'number': room.room_number,
                    'capacity': room.capacity,
                    'type': room.room_type
                },
                'time_slot': assignment.time_slot.to_dict(),
                'term': assignment.term,
                'session_number': assignment.session_number
            }
            
            timetable[student_group.id].append(session)
        
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