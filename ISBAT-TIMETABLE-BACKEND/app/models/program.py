"""Program model."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Program:
    """Academic program cohort representation."""
    id: str  # Program ID
    batch: str  # Batch identifier
    program: str  # Human-readable program name/code
    semester: str
    term: str
    size: int  # Student size
    course_units: List[str] = field(default_factory=list)
    is_active: bool = True
    faculty: str = None  # Faculty name (e.g., "ICT", "Business", "Engineering")

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
            'is_active': self.is_active,
            'faculty': self.faculty
        }

    @staticmethod
    def from_dict(data: dict) -> 'Program':
        """Create Program from dictionary"""
        return Program(
            id=data['id'],
            batch=data['batch'],
            program=data['program'],
            semester=data['semester'],
            term=data['term'],
            size=data['size'],
            course_units=data.get('course_units', []),
            is_active=data.get('is_active', True),
            faculty=data.get('faculty', None)
        )

    def has_course(self, course_unit_id: str) -> bool:
        """Check if program has specific subject"""
        return course_unit_id in self.course_units

    def add_course(self, course_unit_id: str):
        """Add subject to program"""
        if course_unit_id not in self.course_units:
            self.course_units.append(course_unit_id)

    def remove_course(self, course_unit_id: str):
        """Remove subject from program"""
        if course_unit_id in self.course_units:
            self.course_units.remove(course_unit_id)

    @property
    def display_name(self) -> str:
        """Get display name for program"""
        return f"{self.program}_{self.batch}_{self.semester}_{self.term}"

    @property
    def total_courses(self) -> int:
        """Get total number of subjects"""
        return len(self.course_units)

