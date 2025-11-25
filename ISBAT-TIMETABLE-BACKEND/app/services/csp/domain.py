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
    student_group_id: str
    lecturer_id: str
    room_id: str
    time_slot: TimeSlot
    term: str
    session_number: int
    
    def to_dict(self):
        return {
            'variable_id': self.variable_id,
            'course_unit_id': self.course_unit_id,
            'student_group_id': self.student_group_id,
            'lecturer_id': self.lecturer_id,
            'room_id': self.room_id,
            'time_slot': self.time_slot.to_dict(),
            'term': self.term,
            'session_number': self.session_number
        }

@dataclass
class SchedulingVariable:
    """Variable representing a session to be scheduled"""
    id: str
    course_unit_id: str
    student_group_id: str
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
        """Generate all possible time slots"""
        slots = set()
        for day in Config.DAYS:
            for slot_config in Config.TIME_SLOTS:
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
                                    course_unit, student_group=None) -> SchedulingVariable:
        """Initialize domains for a variable"""
        self.rooms = {room.id: room for room in rooms}
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
            room.id for room in rooms
            if self._is_room_suitable(room, course_unit, student_group)
        )
        
        return variable
    
    def _time_to_minutes(self, time_str: str) -> int:
        """Convert time string (HH:MM) to minutes since midnight"""
        try:
            parts = time_str.strip().split(':')
            return int(parts[0]) * 60 + int(parts[1])
        except:
            return 0
    
    def _is_room_suitable(self, room, course_unit, student_group=None) -> bool:
        """Check if room is suitable for course unit
        
        Checks both room TYPE and capacity to avoid including rooms that can never work.
        This prevents the solver from wasting time trying rooms that are too small.
        """
        # Get required room type directly from preferred_room_type
        required_room_type = getattr(course_unit, 'preferred_room_type', 'Theory')
        
        # STRICT: Room type must match course type
        # Lab courses MUST use Lab rooms, Theory courses MUST use Theory rooms
        if room.room_type != required_room_type:
            return False
        
        # CRITICAL: Also check capacity at domain level to prevent trying rooms that are too small
        # This is more efficient than failing during assignment
        if student_group and hasattr(student_group, 'size'):
            if room.capacity < student_group.size:
                return False  # Room is too small for this group
        
        return True
    
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