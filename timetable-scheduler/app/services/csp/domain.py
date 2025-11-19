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
    
    # Current assignment
    assignment: Optional[Assignment] = None
    
    def is_assigned(self) -> bool:
        return self.assignment is not None
    
    def domain_size(self) -> int:
        """Calculate total domain size"""
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
        # All time slots initially available
        variable.available_time_slots = self.all_time_slots.copy()
        
        # Find qualified lecturers
        variable.available_lecturers = set(
            lec.id for lec in lecturers 
            if course_unit.id in lec.specializations
        )
        
        # Find suitable rooms (with capacity check)
        variable.available_rooms = set(
            room.id for room in rooms
            if self._is_room_suitable(room, course_unit, student_group)
        )
        
        return variable
    
    def _is_room_suitable(self, room, course_unit, student_group=None) -> bool:
        """Check if room is suitable for course unit"""
        # Check room type
        if course_unit.is_lab and room.room_type != "Lab":
            return False
        
        # Check room capacity (CRITICAL: filter out rooms that are too small)
        if student_group and hasattr(student_group, 'size'):
            if room.capacity < student_group.size:
                return False
        
        return True
    
    def filter_domain(self, variable: SchedulingVariable, 
                     constraint_type: str, 
                     conflict_data: Dict) -> SchedulingVariable:
        """Filter domain based on constraint"""
        
        if constraint_type == "TIME_SLOT":
            # Remove conflicting time slots
            variable.available_time_slots.discard(conflict_data['time_slot'])
        
        elif constraint_type == "LECTURER":
            # Remove unavailable lecturer
            variable.available_lecturers.discard(conflict_data['lecturer_id'])
        
        elif constraint_type == "ROOM":
            # Remove unavailable room
            variable.available_rooms.discard(conflict_data['room_id'])
        
        return variable