"""Room model."""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class RoomType(Enum):
    """Room types - only Theory and Lab"""
    THEORY = "Theory"
    LAB = "Lab"


@dataclass
class Room:
    """Room model"""
    id: str
    room_number: str
    capacity: int
    room_type: str
    building: Optional[str] = None
    floor: Optional[int] = None
    facilities: List[str] = field(default_factory=list)
    specializations: List[str] = field(default_factory=list)
    is_available: bool = True
    
    def to_dict(self):
        """Convert to dictionary for MongoDB"""
        return {
            'id': self.id,
            'room_number': self.room_number,
            'capacity': self.capacity,
            'room_type': self.room_type,
            'building': self.building,
            'floor': self.floor,
            'facilities': self.facilities,
            'specializations': self.specializations,
            'is_available': self.is_available
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Room':
        """Create Room from dictionary"""
        return Room(
            id=data['id'],
            room_number=data['room_number'],
            capacity=data['capacity'],
            room_type=data['room_type'],
            building=data.get('building'),
            floor=data.get('floor'),
            facilities=data.get('facilities', []),
            specializations=data.get('specializations', []),
            is_available=data.get('is_available', True)
        )
    
    def can_accommodate(self, student_count: int) -> bool:
        """Check if room can accommodate given number of students"""
        return self.capacity >= student_count
    
    def is_type(self, room_type: str) -> bool:
        """Check if room is of given type"""
        return self.room_type == room_type
    
    def is_lab(self) -> bool:
        """Check if room is a lab"""
        return self.room_type == RoomType.LAB.value
    
    def is_theory(self) -> bool:
        """Check if room is a theory room"""
        return self.room_type == RoomType.THEORY.value
    
    def has_facility(self, facility: str) -> bool:
        """Check if room has specific facility"""
        return facility in self.facilities
    
    def has_specialization(self, spec: str) -> bool:
        """Check if room has specific specialization"""
        return spec in self.specializations
