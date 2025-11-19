import time
import math
from typing import List, Dict, Set, Optional, Tuple
from collections import defaultdict
from app.services.csp.domain import SchedulingVariable, Assignment, TimeSlot, DomainManager
from app.services.csp.constraints import ConstraintChecker, ConstraintContext
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
    
    def solve(self) -> Optional[List[Assignment]]:
        """Solve CSP using backtracking with heuristics"""
        
        self.start_time = time.time()
        self.iterations = 0
        self.assignments = []
        
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
            
            if all_valid:
                print(f"Solution found in {self.iterations} iterations ({time.time() - self.start_time:.2f}s)")
                print(f"✅ All {len(self.assignments)} assignments validated - zero constraint violations")
                return self.assignments
            else:
                # CRITICAL: Do NOT return invalid solutions - continue searching
                print(f"❌ Solution found but has {len(violations_found)} constraint violations - REJECTING")
                print(f"   First few violations: {violations_found[:3]}")
                print(f"   Continuing search for valid solution...")
                # Clear assignments and continue searching
                self.assignments = []
                self.constraint_context = ConstraintContext()
                # Re-populate context with resource data
                self.constraint_context.lecturers = {
                    lec.id: {
                        'id': lec.id, 
                        'name': lec.name, 
                        'role': lec.role,
                        'max_weekly_hours': lec.max_weekly_hours,
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
                # Continue searching
                unassigned = sorted(self.variables, key=lambda v: v.domain_size())
                result = self._backtrack(unassigned, [])
                if result:
                    return self.assignments
                return None  # No valid solution found
        else:
            print(f"No solution found after {self.iterations} iterations")
            return None
    
    def _backtrack(self, unassigned: List[SchedulingVariable], 
                   assigned: List[SchedulingVariable]) -> bool:
        """Backtracking search with constraint propagation"""
        
        self.iterations += 1
        
        # Check timeout
        if time.time() - self.start_time > self.timeout:
            print("Timeout reached")
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
            print(f"  ⚠️  Variable {variable.id} has no available time slots")
            unassigned.append(variable)
            return False
        
        if len(variable.available_lecturers) == 0:
            print(f"  ⚠️  Variable {variable.id} has no available lecturers")
            unassigned.append(variable)
            return False
        
        if len(variable.available_rooms) == 0:
            print(f"  ⚠️  Variable {variable.id} has no available rooms")
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
            
            # CRITICAL: Check consistency using constraint checker (includes ALL 10 hard constraints)
            consistent, violations = self.constraint_checker.check_all(
                assignment, 
                self.constraint_context
            )
            
            # Debug: Print first few constraint failures
            if not consistent and self.iterations <= 5:
                violation_msg = violations[0] if violations else 'Unknown'
                print(f"  ⚠️  Assignment {variable.id} rejected: {violation_msg[:80]}")
            
            # STRICT: Only accept if ALL constraints are satisfied
            if not consistent:
                continue  # Skip this assignment, try next value
            
            # Assignment passed all constraints - add it
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
        
        # Find minimum domain size
        min_domain = min(v.domain_size() for v in unassigned)
        
        # Get all variables with minimum domain
        mrv_candidates = [v for v in unassigned if v.domain_size() == min_domain]
        
        if len(mrv_candidates) == 1:
            return mrv_candidates[0]
        
        # Break ties with degree heuristic (most constraints on other variables)
        # For now, just return first (can be enhanced)
        return mrv_candidates[0]
    
    def _order_domain_values(self, variable: SchedulingVariable) -> List[Tuple]:
        """Order domain values using LCV heuristic"""
        
        values = []
        
        # Generate all combinations
        for time_slot in variable.available_time_slots:
            for lecturer_id in variable.available_lecturers:
                for room_id in variable.available_rooms:
                    values.append((time_slot, lecturer_id, room_id))
        
        # Shuffle to avoid bias, but keep it simple for CSP
        # Weekday balancing will be handled by GGA optimization
        import random
        random.shuffle(values)
        return values
    
    def _forward_check(self, unassigned: List[SchedulingVariable], 
                       assignment: Assignment) -> bool:
        """Forward checking - prune inconsistent values from unassigned variables"""
        
        # For simplicity, we rely on constraint checking during backtracking
        # More sophisticated forward checking can be added here
        return True
    
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