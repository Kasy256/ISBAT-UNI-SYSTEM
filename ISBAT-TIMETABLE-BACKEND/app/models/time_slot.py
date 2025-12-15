"""Time Slot model for configurable timetable time slots."""

from dataclasses import dataclass
from typing import Optional

@dataclass
class TimeSlot:
    """Time Slot model"""
    period: str  # Unique identifier (e.g., "SLOT_1", "SLOT_2")
    start: str  # Start time (e.g., "09:00")
    end: str  # End time (e.g., "11:00")
    is_afternoon: bool = False  # Whether this is an afternoon slot
    display_name: Optional[str] = None  # Optional display name (e.g., "09:00 AM - 11:00 AM")
    order: int = 0  # Order for sorting
    
    def to_dict(self):
        """Convert to dictionary for MongoDB"""
        return {
            'period': self.period,
            'start': self.start,
            'end': self.end,
            'is_afternoon': self.is_afternoon,
            'display_name': self.display_name,
            'order': self.order
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'TimeSlot':
        """Create TimeSlot from dictionary"""
        return TimeSlot(
            period=data['period'],
            start=data['start'],
            end=data['end'],
            is_afternoon=data.get('is_afternoon', False),
            display_name=data.get('display_name'),
            order=data.get('order', 0)
        )
