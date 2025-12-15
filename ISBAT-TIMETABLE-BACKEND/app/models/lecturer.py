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
        """Set max weekly hours based on role (only if not explicitly set)"""
        # Only set defaults if max_weekly_hours is still at the default value (22)
        # This allows explicit values from imports/forms to be preserved
        # Note: Role-based defaults are now handled in from_dict() to preserve imported values
        pass
    
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
        # Get max_weekly_hours, preserving explicit values
        max_hours = data.get('max_weekly_hours')
        if max_hours is None:
            # No value provided, use default
            max_hours = 22
        
        lecturer = Lecturer(
            id=data['id'],
            name=data['name'],
            role=data['role'],
            faculty=data['faculty'],
            specializations=data['specializations'],
            availability=data.get('availability'),
            sessions_per_day=data.get('sessions_per_day', 2),
            max_weekly_hours=max_hours
        )
        
        # Only apply role-based defaults if max_weekly_hours is still at default (22)
        # This preserves explicitly set values from imports/forms
        if lecturer.max_weekly_hours == 22:
            if lecturer.role == LecturerRole.FACULTY_DEAN.value:
                lecturer.max_weekly_hours = 15
            elif lecturer.role == LecturerRole.PART_TIME.value:
                lecturer.max_weekly_hours = 2  # Default for Part-Time
        
        return lecturer
    
    def is_available(self, day: str, time_slot: str) -> bool:
        """Check if lecturer is available at given time"""
        if not self.availability:
            return True  # No restrictions
        
        day_availability = self.availability.get(day, [])
        return time_slot in day_availability or len(day_availability) == 0
    
    def is_qualified_for(self, course_unit_id: str) -> bool:
        """
        Check if lecturer is qualified to teach subject.
        Specializations are now stored as canonical IDs (subject groups).
        Uses canonical matching to check if the subject belongs to any of the lecturer's specializations.
        """
        from app.services.canonical_courses import is_canonical_match
        return is_canonical_match(course_unit_id, self.specializations)