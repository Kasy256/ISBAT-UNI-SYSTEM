"""Subject model."""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class DifficultyLevel(Enum):
    """Subject difficulty levels"""
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


class PreferredTerm(Enum):
    """Preferred term for subject"""
    TERM_1 = "Term 1"
    TERM_2 = "Term 2"
    EITHER = "Either"


@dataclass
class CourseUnit:
    """Subject model (CourseUnit kept for backward compatibility)"""
    id: str
    code: str
    name: str
    weekly_hours: int
    credits: int
    preferred_room_type: str  # REQUIRED: "Lab" or "Theory" - primary field for room type assignment
    preferred_term: Optional[str] = None
    semester: Optional[str] = None
    program: Optional[str] = None
    course_group: Optional[str] = None  # Links Theory/Practical pairs (e.g., 'BIT1101_GROUP')
    # Legacy fields (kept for backward compatibility when reading old data, but not saved)
    difficulty: Optional[str] = None
    is_foundational: Optional[bool] = None
    prerequisites: Optional[List[str]] = None
    
    def to_dict(self):
        """Convert to dictionary for MongoDB - only saves new required fields"""
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'weekly_hours': self.weekly_hours,
            'credits': self.credits,
            'preferred_room_type': self.preferred_room_type,
            'preferred_term': self.preferred_term,
            'semester': self.semester,
            'program': self.program,
            'course_group': self.course_group
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'CourseUnit':
        """Create Subject from dictionary"""
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
            credits=data.get('credits', 0),  # Default to 0 if not provided
            preferred_room_type=preferred_room_type,
            preferred_term=data.get('preferred_term'),
            semester=data.get('semester'),
            program=data.get('program'),
            course_group=data.get('course_group'),
            # Legacy fields (for backward compatibility when reading old data)
            difficulty=data.get('difficulty'),
            is_foundational=data.get('is_foundational'),
            prerequisites=data.get('prerequisites')
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
        """Check if subject has a specific prerequisite (legacy method, always returns False)"""
        # Prerequisites are no longer used in the system
        return False
    
    @property
    def canonical_id(self) -> Optional[str]:
        """Get canonical subject ID for this subject"""
        from app.services.canonical_courses import get_canonical_id
        return get_canonical_id(self.id)
