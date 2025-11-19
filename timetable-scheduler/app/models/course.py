"""Course Unit model."""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class DifficultyLevel(Enum):
    """Course difficulty levels"""
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


class PreferredTerm(Enum):
    """Preferred term for course"""
    TERM_1 = "Term 1"
    TERM_2 = "Term 2"
    EITHER = "Either"


@dataclass
class CourseUnit:
    """Course Unit model"""
    id: str
    code: str
    name: str
    weekly_hours: int
    credits: int
    is_lab: bool
    difficulty: str = DifficultyLevel.MEDIUM.value
    is_foundational: bool = False
    prerequisites: List[str] = field(default_factory=list)
    corequisites: List[str] = field(default_factory=list)
    preferred_term: Optional[str] = None
    semester: Optional[str] = None
    program: Optional[str] = None
    
    def to_dict(self):
        """Convert to dictionary for MongoDB"""
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'weekly_hours': self.weekly_hours,
            'credits': self.credits,
            'is_lab': self.is_lab,
            'difficulty': self.difficulty,
            'is_foundational': self.is_foundational,
            'prerequisites': self.prerequisites,
            'corequisites': self.corequisites,
            'preferred_term': self.preferred_term,
            'semester': self.semester,
            'program': self.program
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'CourseUnit':
        """Create CourseUnit from dictionary"""
        return CourseUnit(
            id=data['id'],
            code=data['code'],
            name=data['name'],
            weekly_hours=data['weekly_hours'],
            credits=data['credits'],
            is_lab=data['is_lab'],
            difficulty=data.get('difficulty', DifficultyLevel.MEDIUM.value),
            is_foundational=data.get('is_foundational', False),
            prerequisites=data.get('prerequisites', []),
            corequisites=data.get('corequisites', []),
            preferred_term=data.get('preferred_term'),
            semester=data.get('semester'),
            program=data.get('program')
        )
    
    @property
    def required_room_type(self) -> str:
        """Get required room type"""
        return "Lab" if self.is_lab else "Classroom"
    
    @property
    def sessions_required(self) -> int:
        """Calculate number of sessions required per week"""
        # Each session is 2 hours
        return (self.weekly_hours + 1) // 2
    
    def has_prerequisite(self, course_id: str) -> bool:
        """Check if course has a specific prerequisite"""
        return course_id in self.prerequisites
    
    def has_corequisite(self, course_id: str) -> bool:
        """Check if course has a specific corequisite"""
        return course_id in self.corequisites
