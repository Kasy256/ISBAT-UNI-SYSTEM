from dataclasses import dataclass, field
from typing import List, Set, Optional, Dict
from app.config import Config

@dataclass
class TimeSlot:
    """Time slot representation"""
    day: str
    period: str
    start: str
    end: str
    is_afternoon: bool
    
    def __hash__(self):
        return hash((self.day, self.period))
    
    def __eq__(self, other):
        if not isinstance(other, TimeSlot):
            return False
        return self.day == other.day and self.period == other.period
    
    def copy(self):
        """Create a copy of this timeslot"""
        return TimeSlot(
            day=self.day,
            period=self.period,
            start=self.start,
            end=self.end,
            is_afternoon=self.is_afternoon
        )
    
    def to_dict(self):
        return {
            'day': self.day,
            'period': self.period,
            'start': self.start,
            'end': self.end,
            'is_afternoon': self.is_afternoon
        }

@dataclass
class Assignment:
    """Session assignment"""
    variable_id: str
    course_unit_id: str
    program_id: str
    lecturer_id: str
    room_number: str
    time_slot: TimeSlot
    term: str
    session_number: int
    
    def to_dict(self):
        return {
            'variable_id': self.variable_id,
            'course_unit_id': self.course_unit_id,
            'program_id': self.program_id,
            'lecturer_id': self.lecturer_id,
            'room_number': self.room_number,
            'time_slot': self.time_slot.to_dict(),
            'term': self.term,
            'session_number': self.session_number
        }

@dataclass
class SchedulingVariable:
    """Variable representing a session to be scheduled"""
    id: str
    course_unit_id: str
    program_id: str
    term: str
    session_number: int
    sessions_required: int
    
    # Domain values
    available_time_slots: Set[TimeSlot] = field(default_factory=set)
    available_lecturers: Set[str] = field(default_factory=set)
    available_rooms: Set[str] = field(default_factory=set)
    lecturer_time_slots: Dict[str, Set[TimeSlot]] = field(default_factory=dict)  # lecturer_id -> available time slots
    
    # Current assignment
    assignment: Optional[Assignment] = None
    
    def is_assigned(self) -> bool:
        return self.assignment is not None
    
    def domain_size(self) -> int:
        """Calculate total domain size (approximate - doesn't account for lecturer_time_slots filtering)"""
        # Note: This is an approximation. For accurate size, use the calculation in CSPEngine._select_unassigned_variable
        # that accounts for lecturer_time_slots filtering
        return len(self.available_time_slots) * len(self.available_lecturers) * len(self.available_rooms)

class DomainManager:
    """Manages domains for CSP variables"""
    
    def __init__(self):
        self.all_time_slots = self._generate_all_time_slots()
    
    def _generate_all_time_slots(self) -> Set[TimeSlot]:
        """Generate all possible time slots from database or config"""
        from app.services.config_loader import get_time_slots_for_config
        slots = set()
        
        try:
            time_slots_config = get_time_slots_for_config()
        except Exception as e:
            raise ValueError(
                f"Failed to load time slots from database: {str(e)}. "
                "Please ensure time slots are seeded in the database."
            )
        
        if not time_slots_config:
            # Try to get more details about why time slots are empty
            try:
                from app.services.config_loader import get_time_slots
                raw_slots = get_time_slots()
                if not raw_slots:
                    raise ValueError(
                        "No time slots found in database. "
                        "Please seed time slots using: python seed_config_data.py "
                        "or use the Time Slots management page in the UI."
                    )
                else:
                    raise ValueError(
                        f"Time slots found in database ({len(raw_slots)} slots) but failed to format them. "
                        "Please check time slot data format."
                    )
            except ValueError:
                raise
            except Exception as e:
                raise ValueError(
                    f"Error checking time slots: {str(e)}. "
                    "Please ensure time slots are properly configured in the database."
                )
        
        for day in Config.DAYS:
            for slot_config in time_slots_config:
                slots.add(TimeSlot(
                    day=day,
                    period=slot_config['period'],
                    start=slot_config['start'],
                    end=slot_config['end'],
                    is_afternoon=slot_config['is_afternoon']
                ))
        return slots
    
    def initialize_variable_domains(self, variable: SchedulingVariable, 
                                    lecturers: List, rooms: List, 
                                    course_unit, program=None) -> SchedulingVariable:
        """Initialize domains for a variable"""
        self.rooms = {room.room_number: room for room in rooms}
        # All time slots initially available
        variable.available_time_slots = self.all_time_slots.copy()
        
        # Find qualified lecturers (by specialization using canonical matching)
        from app.services.canonical_courses import is_canonical_match
        
        qualified_lecturers = [
            lec for lec in lecturers 
            if is_canonical_match(course_unit.id, lec.specializations)
        ]
        
        # Build lecturer-to-time-slot mapping based on availability
        # For part-time lecturers, filter time slots to only their available days/hours
        lecturer_time_slots = {}  # lecturer_id -> set of available time slots
        
        for lec in qualified_lecturers:
            if lec.availability:
                # Part-time lecturer with availability restrictions
                # Only available on days specified in availability dict
                available_slots = set()
                for time_slot in self.all_time_slots:
                    # Check if lecturer is available on this day
                    if time_slot.day not in lec.availability:
                        # Day not in availability dict - lecturer not available on this day
                        continue
                    
                    day_availability = lec.availability[time_slot.day]
                    
                    # If empty list, lecturer available all day (unlikely for part-time, but handle it)
                    if len(day_availability) == 0:
                        available_slots.add(time_slot)
                    else:
                        # Check if time slot overlaps with any available time range
                        # Time slot format: "09:00-11:00", availability format: "09:00-11:00" or "10:00-12:00"
                        time_slot_str = f"{time_slot.start}-{time_slot.end}"
                        if time_slot_str in day_availability:
                            # Exact match
                            available_slots.add(time_slot)
                        else:
                            # Check for overlap: time slot overlaps if it starts or ends within an available range
                            slot_start = self._time_to_minutes(time_slot.start)
                            slot_end = self._time_to_minutes(time_slot.end)
                            
                            for avail_range in day_availability:
                                if '-' in avail_range:
                                    avail_start_str, avail_end_str = avail_range.split('-')
                                    avail_start = self._time_to_minutes(avail_start_str.strip())
                                    avail_end = self._time_to_minutes(avail_end_str.strip())
                                    
                                    # Check if time slot overlaps with available range
                                    # Overlap if: slot starts before range ends AND slot ends after range starts
                                    if slot_start < avail_end and slot_end > avail_start:
                                        available_slots.add(time_slot)
                                        break
                
                lecturer_time_slots[lec.id] = available_slots
            else:
                # Full-time lecturer - available all time slots
                lecturer_time_slots[lec.id] = self.all_time_slots.copy()
        
        # Only include lecturers who have at least one available time slot
        # This filters out part-time lecturers whose availability doesn't match any time slots
        available_lecturer_ids = set()
        for lec_id, slots in lecturer_time_slots.items():
            if len(slots) > 0:  # Lecturer has at least one available time slot
                available_lecturer_ids.add(lec_id)
        
        variable.available_lecturers = available_lecturer_ids
        variable.lecturer_time_slots = lecturer_time_slots  # Store for later filtering
        
        # Find suitable rooms (with capacity check)
        variable.available_rooms = set(
            room.room_number for room in rooms
            if self._is_room_suitable(room, course_unit, program)
        )
        
        return variable
    
    def _time_to_minutes(self, time_str: str) -> int:
        """Convert time string (HH:MM) to minutes since midnight"""
        try:
            parts = time_str.strip().split(':')
            return int(parts[0]) * 60 + int(parts[1])
        except:
            return 0
    
    def _is_room_suitable(self, room, course_unit, program=None) -> bool:
        """Check if room is suitable for course unit
        
        Checks room TYPE, capacity, and specialization matching.
        This prevents the solver from wasting time trying rooms that can never work.
        """
        # Get required room type directly from preferred_room_type
        required_room_type = getattr(course_unit, 'preferred_room_type', 'Theory')
        
        # STRICT: Room type must match subject type
        # Lab subjects MUST use Lab rooms, Theory subjects MUST use Theory rooms
        if room.room_type != required_room_type:
            return False
        
        # CRITICAL: Also check capacity at domain level to prevent trying rooms that are too small
        # This is more efficient than failing during assignment
        if program and hasattr(program, 'size'):
            if room.capacity < program.size:
                return False  # Room is too small for this group
        
        # Check room specialization matching
        room_specializations = getattr(room, 'specializations', []) or []
        
        # If room has no specializations, it can be used for any subject (backward compatibility)
        if not room_specializations:
            return True
        
        # Get subject's course group to determine specialization
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
            
            if required_room_type == 'Theory':
                # Theory subjects: check for Theory specialization or no specialization requirement
                return 'Theory' in room_specializations or len(room_specializations) == 0
            else:
                # Lab courses without course group: default to ICT-related specializations
                # Check if room has ICT, Programming, or ICT & Programming
                ict_specs = ['ICT', 'Programming', 'ICT & Programming']
                for spec in ict_specs:
                    if spec in room_specializations:
                        return True
                    # Also check substring match for compound specializations
                    for room_spec in room_specializations:
                        if spec in room_spec:
                            return True
                # FALLBACK: Allow room anyway if no specialization match (backward compatibility)
                return True
        
        # Get canonical group name from course_group_id
        canonical_group_name = self._get_canonical_group_name(course_group_id)
        if not canonical_group_name:
            # Can't find canonical group - use fallback logic
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
            
            if required_room_type == 'Theory':
                # Theory courses: check for Theory specialization or no specialization requirement
                return 'Theory' in room_specializations or len(room_specializations) == 0
            else:
                # Lab courses without canonical group: default to ICT-related specializations
                # Check if room has ICT, Programming, or ICT & Programming
                ict_specs = ['ICT', 'Programming', 'ICT & Programming']
                for spec in ict_specs:
                    if spec in room_specializations:
                        return True
                    # Also check substring match for compound specializations
                    for room_spec in room_specializations:
                        if spec in room_spec:
                            return True
                # FALLBACK: Allow room anyway if no specialization match (backward compatibility)
                return True
        
        # Map canonical group name to room specializations
        # Pass required_room_type so we can add ICT fallback for Lab courses
        matching_specializations = self._map_canonical_to_specializations(canonical_group_name, required_room_type)
        
        # Check if room has any matching specialization
        # Handle both exact matches and compound specializations
        # Cases handled:
        # 1. Room has ["ICT"] and we're looking for "ICT" -> exact match
        # 2. Room has ["ICT & Programming"] and we're looking for "ICT" or "Programming" -> substring match
        # 3. Room has ["ICT", "Programming"] and we're looking for "ICT" or "Programming" -> exact match
        # 4. Room has ["ICT", "Programming"] and we're looking for "ICT & Programming" -> handled by mapping both separately
        for spec in matching_specializations:
            # Exact match (handles case 1 and 3)
            if spec in room_specializations:
                return True
            # Substring match (handles case 2: compound room specs)
            # e.g., "ICT" in "ICT & Programming" will match
            for room_spec in room_specializations:
                if spec in room_spec:
                    return True
        
        # If no match found, check if it's a theory subject and room has "Theory" specialization
        if required_room_type == 'Theory' and 'Theory' in room_specializations:
            return True
        
        # FALLBACK: If no specialization match found, allow the room anyway (backward compatibility)
        # The old system didn't check specializations - it only checked room type and capacity
        # This makes specialization matching a "preference" rather than a "requirement"
        # This allows the system to work even if specializations don't match perfectly
        return True
    
    def _get_canonical_group_name(self, canonical_id: str) -> Optional[str]:
        """Get canonical group name from canonical ID"""
        try:
            from app import get_db
            db = get_db()
            group = db.canonical_course_groups.find_one({'canonical_id': canonical_id})
            if group:
                return group.get('name')
        except:
            pass
        return None
    
    def _map_canonical_to_specializations(self, canonical_group_name: str, required_room_type: str = 'Theory') -> List[str]:
        """Map canonical group name to room specializations
        
        This maps course group names to room specializations for matching.
        Examples:
        - "Programming in C" -> ["Programming", "ICT"]
        - "Networking" -> ["Networking & Cyber Security"]
        - "Multimedia" -> ["Multimedia"]
        - Unknown Lab course -> ["ICT", "Programming", "ICT & Programming"] (fallback)
        
        Args:
            canonical_group_name: Name of the canonical course group
            required_room_type: "Lab" or "Theory" - used for fallback logic
        """
        name_lower = canonical_group_name.lower()
        specializations = []
        matched_specific = False  # Track if we matched any specific category
        
        # Programming-related
        if any(keyword in name_lower for keyword in ['programming', 'prog', 'code', 'software', 'java', 'python', 'c++', 'c#', 'web', 'asp', 'mobile']):
            specializations.append('Programming')
            specializations.append('ICT')
            specializations.append('ICT & Programming')  # Also include compound specialization for rooms that have it
            matched_specific = True
        
        # LINUX (specific specialization for Linux-related courses)
        if any(keyword in name_lower for keyword in ['linux']):
            specializations.append('LINUX')
            matched_specific = True
        
        # Networking & Cyber Security
        if any(keyword in name_lower for keyword in ['network', 'cyber', 'security', 'admin', 'iot']):
            specializations.append('Networking & Cyber Security')
            matched_specific = True
        
        # Multimedia
        if any(keyword in name_lower for keyword in ['multimedia', 'graphics', 'design', 'animation']):
            specializations.append('Multimedia')
            matched_specific = True
        
        # AI & ML
        if any(keyword in name_lower for keyword in ['artificial intelligence', 'machine learning', 'ai', 'ml', 'data science', 'deep learning']):
            specializations.append('AI & ML')
            matched_specific = True
        
        # Statistics
        if any(keyword in name_lower for keyword in ['statistics', 'stat', 'math', 'mathematics']):
            specializations.append('Statistics')
            matched_specific = True
        
        # Management
        if any(keyword in name_lower for keyword in ['management', 'business', 'entrepreneurship', 'marketing']):
            specializations.append('Management Lab')
            matched_specific = True
        
        # Physics
        if any(keyword in name_lower for keyword in ['physics', 'physical']):
            specializations.append('Physics Lab')
            matched_specific = True
        
        # Electronics
        if any(keyword in name_lower for keyword in ['electronics', 'digital', 'hardware', 'circuit']):
            specializations.append('Electronics Lab')
            matched_specific = True
        
        # BHM (Business Hospitality Management)
        if any(keyword in name_lower for keyword in ['bhm', 'hospitality', 'tourism']):
            specializations.append('BHM')
            matched_specific = True
        
        # Fallback for Lab courses that don't match any specific category
        # If it's a Lab course and we didn't match any specific specialization, default to ICT
        if required_room_type == 'Lab' and not matched_specific:
            specializations.append('ICT')
            specializations.append('Programming')
            specializations.append('ICT & Programming')
        
        # Theory (default for theory subjects)
        specializations.append('Theory')
        
        return list(set(specializations))  # Remove duplicates
    
    def filter_domain(self, variable: SchedulingVariable, 
                     constraint_type: str, 
                     conflict_data: Dict) -> SchedulingVariable:
        """Filter domain based on constraint"""
        
        if constraint_type == "TIME_SLOT":
            variable.available_time_slots.discard(conflict_data['time_slot'])
        
        elif constraint_type == "LECTURER":
            variable.available_lecturers.discard(conflict_data['lecturer_id'])
        
        elif constraint_type == "ROOM":
            # Remove unavailable room
            variable.available_rooms.discard(conflict_data['room_id'])
        
        return variable