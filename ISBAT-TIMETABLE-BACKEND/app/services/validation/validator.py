from typing import Dict, List, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
from app.services.csp.constraints import ConstraintChecker
from app.models.lecturer import Lecturer
from app.models.room import Room
from app.models.subject import CourseUnit
from app.models.program import Program

@dataclass
class ValidationError:
    """Validation error details"""
    code: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    category: str
    message: str
    affected_entities: List[str] = field(default_factory=list)
    suggestion: str = ""

@dataclass
class ValidationResult:
    """Complete validation result"""
    is_valid: bool
    phase: str
    critical_errors: List[ValidationError] = field(default_factory=list)
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    info: List[str] = field(default_factory=list)
    
    total_checks: int = 0
    passed_checks: int = 0
    
    def to_dict(self):
        return {
            'is_valid': self.is_valid,
            'phase': self.phase,
            'summary': {
                'critical_errors': len(self.critical_errors),
                'errors': len(self.errors),
                'warnings': len(self.warnings),
                'total_checks': self.total_checks,
                'passed_checks': self.passed_checks,
                'pass_rate': (self.passed_checks / self.total_checks * 100) if self.total_checks > 0 else 0
            },
            'critical_errors': [self._error_to_dict(e) for e in self.critical_errors],
            'errors': [self._error_to_dict(e) for e in self.errors],
            'warnings': [self._error_to_dict(e) for e in self.warnings],
            'info': self.info
        }
    
    def _error_to_dict(self, error: ValidationError):
        return {
            'code': error.code,
            'severity': error.severity,
            'category': error.category,
            'message': error.message,
            'affected_entities': error.affected_entities,
            'suggestion': error.suggestion
        }

class TimetableValidator:
    """Comprehensive timetable validation"""
    
    def __init__(self):
        self.constraint_checker = ConstraintChecker()
    
    def validate_input_data(self, lecturers: List[Lecturer], rooms: List[Room],
                           course_units: List[CourseUnit], 
                           programs: List[Program]) -> ValidationResult:
        """Validate input data before scheduling"""
        
        result = ValidationResult(is_valid=True, phase="INPUT_VALIDATION")
        
        # Validate lecturers
        lecturer_checks = self._validate_lecturers(lecturers)
        result.critical_errors.extend(lecturer_checks['critical'])
        result.errors.extend(lecturer_checks['errors'])
        result.warnings.extend(lecturer_checks['warnings'])
        result.total_checks += lecturer_checks['total']
        result.passed_checks += lecturer_checks['passed']
        
        # Validate rooms
        room_checks = self._validate_rooms(rooms)
        result.critical_errors.extend(room_checks['critical'])
        result.errors.extend(room_checks['errors'])
        result.warnings.extend(room_checks['warnings'])
        result.total_checks += room_checks['total']
        result.passed_checks += room_checks['passed']
        
        # Validate course units
        course_checks = self._validate_course_units(course_units)
        result.critical_errors.extend(course_checks['critical'])
        result.errors.extend(course_checks['errors'])
        result.warnings.extend(course_checks['warnings'])
        result.total_checks += course_checks['total']
        result.passed_checks += course_checks['passed']
        
        # Validate programs
        student_checks = self._validate_programs(programs, course_units)
        result.critical_errors.extend(student_checks['critical'])
        result.errors.extend(student_checks['errors'])
        result.warnings.extend(student_checks['warnings'])
        result.total_checks += student_checks['total']
        result.passed_checks += student_checks['passed']
        
        # Cross-reference validation
        cross_checks = self._validate_cross_references(
            lecturers, rooms, course_units, programs
        )
        result.critical_errors.extend(cross_checks['critical'])
        result.errors.extend(cross_checks['errors'])
        result.warnings.extend(cross_checks['warnings'])
        result.total_checks += cross_checks['total']
        result.passed_checks += cross_checks['passed']
        
        # Feasibility checks
        feasibility_checks = self._validate_feasibility(
            lecturers, rooms, course_units, programs
        )
        result.critical_errors.extend(feasibility_checks['critical'])
        result.errors.extend(feasibility_checks['errors'])
        result.total_checks += feasibility_checks['total']
        result.passed_checks += feasibility_checks['passed']
        
        result.is_valid = len(result.critical_errors) == 0 and len(result.errors) == 0
        
        return result
    
    def _validate_lecturers(self, lecturers: List[Lecturer]) -> Dict:
        """Validate lecturer data"""
        critical = []
        errors = []
        warnings = []
        total = 0
        passed = 0
        
        for lecturer in lecturers:
            # Check ID
            total += 1
            if not lecturer.id or len(lecturer.id.strip()) == 0:
                critical.append(ValidationError(
                    code="LECTURER_MISSING_ID",
                    severity="CRITICAL",
                    category="DATA_INTEGRITY",
                    message=f"Lecturer missing ID",
                    affected_entities=[lecturer.name]
                ))
            else:
                passed += 1
            
            # Check name
            total += 1
            if not lecturer.name or len(lecturer.name.strip()) == 0:
                critical.append(ValidationError(
                    code="LECTURER_MISSING_NAME",
                    severity="CRITICAL",
                    category="DATA_INTEGRITY",
                    message=f"Lecturer {lecturer.id} missing name",
                    affected_entities=[lecturer.id]
                ))
            else:
                passed += 1
            
            # Check specializations
            total += 1
            if not lecturer.specializations or len(lecturer.specializations) == 0:
                errors.append(ValidationError(
                    code="LECTURER_NO_SPECIALIZATIONS",
                    severity="HIGH",
                    category="DATA_INTEGRITY",
                    message=f"Lecturer {lecturer.name} has no specializations",
                    affected_entities=[lecturer.id],
                    suggestion="Add at least one course unit specialization"
                ))
            else:
                passed += 1
            
            # Check role and workload limits
            total += 1
            valid_roles = ["Faculty Dean", "Full-Time", "Part-Time"]
            if lecturer.role not in valid_roles:
                errors.append(ValidationError(
                    code="LECTURER_INVALID_ROLE",
                    severity="HIGH",
                    category="DATA_INTEGRITY",
                    message=f"Lecturer {lecturer.name} has invalid role: {lecturer.role}",
                    affected_entities=[lecturer.id],
                    suggestion=f"Role must be one of: {valid_roles}"
                ))
            else:
                passed += 1
        
        return {
            'critical': critical,
            'errors': errors,
            'warnings': warnings,
            'total': total,
            'passed': passed
        }
    
    def _validate_rooms(self, rooms: List[Room]) -> Dict:
        """Validate room data"""
        critical = []
        errors = []
        warnings = []
        total = 0
        passed = 0
        
        for room in rooms:
            # Check capacity
            total += 1
            if room.capacity <= 0:
                critical.append(ValidationError(
                    code="ROOM_INVALID_CAPACITY",
                    severity="CRITICAL",
                    category="DATA_INTEGRITY",
                    message=f"Room {room.room_number} has invalid capacity: {room.capacity}",
                    affected_entities=[room.id]
                ))
            else:
                passed += 1
            
            # Check capacity range
            total += 1
            if room.capacity > 200:
                warnings.append(ValidationError(
                    code="ROOM_LARGE_CAPACITY",
                    severity="LOW",
                    category="DATA_QUALITY",
                    message=f"Room {room.room_number} has unusually large capacity: {room.capacity}",
                    affected_entities=[room.id],
                    suggestion="Verify capacity is correct"
                ))
            else:
                passed += 1
            
            # Check room type
            total += 1
            valid_types = ["Theory", "Lab"]
            if room.room_type not in valid_types:
                critical.append(ValidationError(
                    code="ROOM_INVALID_TYPE",
                    severity="CRITICAL",
                    category="DATA_INTEGRITY",
                    message=f"Room {room.room_number} has invalid type: {room.room_type}",
                    affected_entities=[room.id],
                    suggestion=f"Type must be one of: {valid_types}"
                ))
            else:
                passed += 1
        
        return {
            'critical': critical,
            'errors': errors,
            'warnings': warnings,
            'total': total,
            'passed': passed
        }
    
    def _validate_course_units(self, course_units: List[CourseUnit]) -> Dict:
        """Validate course unit data"""
        critical = []
        errors = []
        warnings = []
        total = 0
        passed = 0
        
        # Prerequisites are no longer used - removed prerequisite graph building
        
        for course_unit in course_units:
            # Check weekly hours
            total += 1
            if course_unit.weekly_hours <= 0 or course_unit.weekly_hours > 8:
                errors.append(ValidationError(
                    code="COURSE_INVALID_HOURS",
                    severity="HIGH",
                    category="DATA_INTEGRITY",
                    message=f"Subject {course_unit.code} has invalid weekly hours: {course_unit.weekly_hours}",
                    affected_entities=[course_unit.id],
                    suggestion="Weekly hours should be between 1 and 8"
                ))
            else:
                passed += 1
            
            # Check credits
            total += 1
            if course_unit.credits <= 0:
                errors.append(ValidationError(
                    code="COURSE_INVALID_CREDITS",
                    severity="MEDIUM",
                    category="DATA_INTEGRITY",
                    message=f"Subject {course_unit.code} has invalid credits: {course_unit.credits}",
                    affected_entities=[course_unit.id]
                ))
            else:
                passed += 1
            
            # Prerequisites validation removed - system now uses preferred_term directly
            # No prerequisite checking needed
        
        if len(cycles) == 0:
            total += 1
            passed += 1
        
        return {
            'critical': critical,
            'errors': errors,
            'warnings': warnings,
            'total': total,
            'passed': passed
        }
    
    def _validate_programs(self, programs: List[Program], 
                                 course_units: List[CourseUnit]) -> Dict:
        """Validate program data"""
        critical = []
        errors = []
        warnings = []
        total = 0
        passed = 0
        
        for group in programs:
            # Check size
            total += 1
            if group.size <= 0:
                critical.append(ValidationError(
                    code="GROUP_INVALID_SIZE",
                    severity="CRITICAL",
                    category="DATA_INTEGRITY",
                    message=f"Program {group.id} has invalid size: {group.size}",
                    affected_entities=[group.id]
                ))
            else:
                passed += 1
            
            # Check course units exist
            for cu_id in group.course_units:
                total += 1
                if not any(cu.id == cu_id for cu in course_units):
                    errors.append(ValidationError(
                        code="GROUP_MISSING_COURSE",
                        severity="HIGH",
                        category="DATA_INTEGRITY",
                        message=f"Program {group.id} references non-existent subject: {cu_id}",
                        affected_entities=[group.id, cu_id]
                    ))
                else:
                    passed += 1
        
        return {
            'critical': critical,
            'errors': errors,
            'warnings': warnings,
            'total': total,
            'passed': passed
        }
    
    def _validate_cross_references(self, lecturers: List[Lecturer], rooms: List[Room],
                                   course_units: List[CourseUnit], 
                                   programs: List[Program]) -> Dict:
        """Validate cross-references between entities"""
        critical = []
        errors = []
        warnings = []
        total = 0
        passed = 0
        
        # Check lecturer specializations reference valid canonical groups (subject groups)
        from app.services.canonical_courses import get_course_groupings
        canonical_groups = get_course_groupings()
        canonical_ids = set(canonical_groups.keys())
        
        # Also get all subject codes for backward compatibility check
        course_ids = set(cu.id for cu in course_units)
        course_codes = set(cu.code for cu in course_units if cu.code)
        
        for lecturer in lecturers:
            for spec in lecturer.specializations:
                total += 1
                # Check if it's a canonical ID (preferred) or a subject code (backward compatibility)
                if spec not in canonical_ids and spec not in course_ids and spec not in course_codes:
                    warnings.append(ValidationError(
                        code="LECTURER_UNKNOWN_SPECIALIZATION",
                        severity="MEDIUM",
                        category="CROSS_REFERENCE",
                        message=f"Lecturer {lecturer.name} has specialization for unknown subject group or subject: {spec}",
                        affected_entities=[lecturer.id, spec]
                    ))
                else:
                    passed += 1
        
        # Check all subjects have at least one qualified lecturer (using canonical matching)
        from app.services.canonical_courses import is_canonical_match
        for subject in course_units:
            total += 1
            qualified = [l for l in lecturers if is_canonical_match(subject.id, l.specializations)]
            if len(qualified) == 0:
                critical.append(ValidationError(
                    code="COURSE_NO_QUALIFIED_LECTURER",
                    severity="CRITICAL",
                    category="RESOURCE_CONFLICT",
                    message=f"No lecturer qualified to teach {subject.code}",
                    affected_entities=[subject.id],
                    suggestion="Add qualification to at least one lecturer"
                ))
            else:
                passed += 1
        
        return {
            'critical': critical,
            'errors': errors,
            'warnings': warnings,
            'total': total,
            'passed': passed
        }
    
    def _validate_feasibility(self, lecturers: List[Lecturer], rooms: List[Room],
                             course_units: List[CourseUnit], 
                             programs: List[Program]) -> Dict:
        """Validate scheduling feasibility"""
        critical = []
        errors = []
        total = 0
        passed = 0
        
        # Calculate total required hours
        total_required_hours = 0
        for group in programs:
            for cu_id in group.course_units:
                subject = next((cu for cu in course_units if cu.id == cu_id), None)
                if subject:
                    total_required_hours += subject.weekly_hours
        
        # Calculate total lecturer capacity
        total_lecturer_capacity = sum(l.max_weekly_hours for l in lecturers)
        
        total += 1
        if total_required_hours > total_lecturer_capacity:
            critical.append(ValidationError(
                code="INSUFFICIENT_LECTURER_CAPACITY",
                severity="CRITICAL",
                category="FEASIBILITY",
                message=f"Required teaching hours ({total_required_hours}) exceed total lecturer capacity ({total_lecturer_capacity})",
                affected_entities=[],
                suggestion="Hire more lecturers or reduce subject offerings"
            ))
        else:
            passed += 1
        
        # Check room capacity feasibility
        largest_group = max((g.size for g in programs), default=0)
        largest_room = max((r.capacity for r in rooms), default=0)
        
        total += 1
        if largest_group > largest_room:
            critical.append(ValidationError(
                code="INSUFFICIENT_ROOM_CAPACITY",
                severity="CRITICAL",
                category="FEASIBILITY",
                message=f"Largest program ({largest_group}) exceeds largest room capacity ({largest_room})",
                affected_entities=[],
                suggestion="Add larger rooms or split large groups"
            ))
        else:
            passed += 1
        
        # Check lab availability
        lab_courses = [cu for cu in course_units if cu.preferred_room_type == "Lab"]
        lab_rooms = [r for r in rooms if r.room_type == "Lab"]
        
        total += 1
        if len(lab_courses) > 0 and len(lab_rooms) == 0:
            critical.append(ValidationError(
                code="NO_LAB_ROOMS",
                severity="CRITICAL",
                category="FEASIBILITY",
                message=f"{len(lab_courses)} lab subjects but no lab rooms available",
                affected_entities=[],
                suggestion="Add lab rooms"
            ))
        else:
            passed += 1
        
        return {
            'critical': critical,
            'errors': errors,
            'total': total,
            'passed': passed
        }
    
    def _detect_prerequisite_cycles(self, graph: Dict[str, List[str]]) -> List[List[str]]:
        """Legacy method - prerequisites are no longer used, always returns empty list"""
        return []