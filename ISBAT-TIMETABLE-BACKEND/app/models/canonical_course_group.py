"""Canonical Subject Group model for database-driven subject grouping."""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class CanonicalCourseGroup:
    """Canonical Subject Group model for grouping equivalent subjects"""
    canonical_id: str  # Unique identifier (e.g., 'PROG_C')
    name: str  # Display name (e.g., 'Programming in C')
    course_codes: List[str]  # List of subject codes in this group (e.g., ['BIT1103', 'BCS1103'])
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    
    def to_dict(self):
        """Convert to dictionary for MongoDB"""
        return {
            'canonical_id': self.canonical_id,
            'name': self.name,
            'course_codes': self.course_codes,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'CanonicalCourseGroup':
        """Create CanonicalCourseGroup from dictionary"""
        created_at = None
        updated_at = None
        if data.get('created_at'):
            if isinstance(data['created_at'], str):
                created_at = datetime.fromisoformat(data['created_at'])
            else:
                created_at = data['created_at']
        if data.get('updated_at'):
            if isinstance(data['updated_at'], str):
                updated_at = datetime.fromisoformat(data['updated_at'])
            else:
                updated_at = data['updated_at']
        
        return CanonicalCourseGroup(
            canonical_id=data['canonical_id'],
            name=data['name'],
            course_codes=data.get('course_codes', []),
            description=data.get('description'),
            created_at=created_at,
            updated_at=updated_at,
            created_by=data.get('created_by')
        )

