from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum

class LecturerRole(Enum):
    FACULTY_DEAN = "Faculty Dean"
    FULL_TIME = "Full-Time"
    PART_TIME = "Part-Time"

@dataclass
class Lecturer:
    """Lecturer model"""
    id: str
    name: str
    role: str
    faculty: str
    specializations: List[str]
    availability: Optional[Dict[str, List[str]]] = None
    sessions_per_day: int = 2
    max_weekly_hours: int = 22
    
    def __post_init__(self):
        """Set max weekly hours based on role"""
        if self.role == LecturerRole.FACULTY_DEAN.value:
            self.max_weekly_hours = 15
        elif self.role == LecturerRole.FULL_TIME.value:
            self.max_weekly_hours = 22
        elif self.role == LecturerRole.PART_TIME.value:
            self.max_weekly_hours = 3
    
    def to_dict(self):
        """Convert to dictionary for MongoDB"""
        return {
            'id': self.id,
            'name': self.name,
            'role': self.role,
            'faculty': self.faculty,
            'specializations': self.specializations,
            'availability': self.availability,
            'sessions_per_day': self.sessions_per_day,
            'max_weekly_hours': self.max_weekly_hours
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Lecturer':
        """Create Lecturer from dictionary"""
        return Lecturer(
            id=data['id'],
            name=data['name'],
            role=data['role'],
            faculty=data['faculty'],
            specializations=data['specializations'],
            availability=data.get('availability'),
            sessions_per_day=data.get('sessions_per_day', 2),
            max_weekly_hours=data.get('max_weekly_hours', 22)
        )
    
    def is_available(self, day: str, time_slot: str) -> bool:
        """Check if lecturer is available at given time"""
        if not self.availability:
            return True  # No restrictions
        
        day_availability = self.availability.get(day, [])
        return time_slot in day_availability or len(day_availability) == 0
    
    def is_qualified_for(self, course_unit_id: str) -> bool:
        """Check if lecturer is qualified to teach course"""
        return course_unit_id in self.specializations