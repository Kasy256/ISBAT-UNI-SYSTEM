"""Room Specialization model for configurable room specializations."""

from dataclasses import dataclass
from typing import Optional

@dataclass
class RoomSpecialization:
    """Room Specialization model"""
    id: str  # Unique identifier (e.g., "ICT", "Programming", "Theory")
    name: str  # Display name
    description: Optional[str] = None  # Optional description
    
    def to_dict(self):
        """Convert to dictionary for MongoDB"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'RoomSpecialization':
        """Create RoomSpecialization from dictionary"""
        return RoomSpecialization(
            id=data['id'],
            name=data['name'],
            description=data.get('description')
        )
