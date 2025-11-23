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
    preferred_room_type: str  # REQUIRED: "Lab" or "Theory" - primary field for room type assignment
    difficulty: str = DifficultyLevel.MEDIUM.value
    is_foundational: bool = False
    prerequisites: List[str] = field(default_factory=list)
    corequisites: List[str] = field(default_factory=list)
    preferred_term: Optional[str] = None
    semester: Optional[str] = None
    program: Optional[str] = None
    course_group: Optional[str] = None  # Links Theory/Practical pairs (e.g., 'BIT1101_GROUP')
    
    def to_dict(self):
        """Convert to dictionary for MongoDB"""
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'weekly_hours': self.weekly_hours,
            'credits': self.credits,
            'preferred_room_type': self.preferred_room_type,
            'difficulty': self.difficulty,
            'is_foundational': self.is_foundational,
            'prerequisites': self.prerequisites,
            'corequisites': self.corequisites,
            'preferred_term': self.preferred_term,
            'semester': self.semester,
            'program': self.program,
            'course_group': self.course_group
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'CourseUnit':
        """Create CourseUnit from dictionary"""
        # preferred_room_type is required, but derive from is_lab for backward compatibility
        preferred_room_type = data.get('preferred_room_type')
        if not preferred_room_type:
            # Backward compatibility: derive from is_lab if available
            is_lab = data.get('is_lab', False)
            preferred_room_type = "Lab" if is_lab else "Theory"
        
        return CourseUnit(
            id=data['id'],
            code=data['code'],
            name=data['name'],
            weekly_hours=data['weekly_hours'],
            credits=data['credits'],
            preferred_room_type=preferred_room_type,
            difficulty=data.get('difficulty', DifficultyLevel.MEDIUM.value),
            is_foundational=data.get('is_foundational', False),
            prerequisites=data.get('prerequisites', []),
            corequisites=data.get('corequisites', []),
            preferred_term=data.get('preferred_term'),
            semester=data.get('semester'),
            program=data.get('program'),
            course_group=data.get('course_group')
        )
    
    @property
    def required_room_type(self) -> str:
        """Get required room type - directly from preferred_room_type"""
        return self.preferred_room_type
    
    @property
    def sessions_required(self) -> int:
        """Calculate number of sessions required per week"""
        if hasattr(self, '_sessions_required'):
            return self._sessions_required
        return (self.weekly_hours + 1) // 2
    
    def has_prerequisite(self, course_id: str) -> bool:
        """Check if course has a specific prerequisite"""
        return course_id in self.prerequisites
    
    def has_corequisite(self, course_id: str) -> bool:
        """Check if course has a specific corequisite"""
        return course_id in self.corequisites
    
    @property
    def canonical_id(self) -> Optional[str]:
        """Get canonical course ID for this course"""
        from app.services.canonical_courses import get_canonical_id
        return get_canonical_id(self.id)
