"""Student Group model."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class StudentGroup:
    """Student Group model"""
    id: str
    batch: str
    program: str
    semester: str
    term: str
    size: int
    course_units: List[str] = field(default_factory=list)
    academic_year: Optional[str] = None
    is_active: bool = True
    
    def to_dict(self):
        """Convert to dictionary for MongoDB"""
        return {
            'id': self.id,
            'batch': self.batch,
            'program': self.program,
            'semester': self.semester,
            'term': self.term,
            'size': self.size,
            'course_units': self.course_units,
            'academic_year': self.academic_year,
            'is_active': self.is_active
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'StudentGroup':
        """Create StudentGroup from dictionary"""
        return StudentGroup(
            id=data['id'],
            batch=data['batch'],
            program=data['program'],
            semester=data['semester'],
            term=data['term'],
            size=data['size'],
            course_units=data.get('course_units', []),
            academic_year=data.get('academic_year'),
            is_active=data.get('is_active', True)
        )
    
    def has_course(self, course_unit_id: str) -> bool:
        """Check if group has specific course"""
        return course_unit_id in self.course_units
    
    def add_course(self, course_unit_id: str):
        """Add course to group"""
        if course_unit_id not in self.course_units:
            self.course_units.append(course_unit_id)
    
    def remove_course(self, course_unit_id: str):
        """Remove course from group"""
        if course_unit_id in self.course_units:
            self.course_units.remove(course_unit_id)
    
    @property
    def display_name(self) -> str:
        """Get display name for group"""
        return f"{self.program}_{self.batch}_{self.semester}_{self.term}"
    
    @property
    def total_courses(self) -> int:
        """Get total number of courses"""
        return len(self.course_units)
