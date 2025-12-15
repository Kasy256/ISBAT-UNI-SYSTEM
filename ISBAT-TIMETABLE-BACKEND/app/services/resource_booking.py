"""
Resource Booking Manager
Manages global resource bookings across all faculties to prevent conflicts
"""

from typing import List, Dict, Optional, Set
from datetime import datetime
from collections import defaultdict
from app.services.csp.domain import Assignment, TimeSlot
from app.services.csp.constraints import ConstraintContext


class ResourceBookingManager:
    """Manages global resource bookings across all faculties"""
    
    def __init__(self, db, term: str, academic_year: str = None):
        """
        Initialize Resource Booking Manager
        
        Args:
            db: MongoDB database instance
            term: Term identifier (e.g., "Term1", "Term2")
            academic_year: Academic year (e.g., "2024-2025"). If None, uses current year
        """
        self.db = db
        self.term = term
        self.academic_year = academic_year or self._get_current_academic_year()
        self._cache = {}  # In-memory cache for performance
        self._cache_valid = True
    
    def _get_current_academic_year(self) -> str:
        """Get current academic year based on current date"""
        now = datetime.now()
        if now.month >= 8:  # August onwards = new academic year
            return f"{now.year}-{now.year + 1}"
        else:
            return f"{now.year - 1}-{now.year}"
    
    def invalidate_cache(self):
        """Invalidate the cache (call after making changes)"""
        self._cache = {}
        self._cache_valid = False
    
    def is_room_available(self, room_number: str, day: str, 
                         period: str, start_time: str = None, 
                         end_time: str = None) -> bool:
        """
        Check if room is available at given time
        
        Args:
            room_number: Room identifier
            day: Day of week (MON, TUE, etc.)
            period: Period identifier
            start_time: Start time (optional, for future use)
            end_time: End time (optional, for future use)
        
        Returns:
            True if room is available, False otherwise
        """
        # Check cache first
        key = f"room:{room_number}:{day}:{period}"
        if key in self._cache:
            return not self._cache[key]
        
        # Query database
        booking = self.db.resource_bookings.find_one({
            'resource_type': 'room',
            'resource_id': room_number,
            'term': self.term,
            'academic_year': self.academic_year,
            'day': day,
            'period': period,
            'is_booked': True
        })
        
        is_available = booking is None
        self._cache[key] = not is_available
        return is_available
    
    def is_lecturer_available(self, lecturer_id: str, day: str,
                             period: str, start_time: str = None, 
                             end_time: str = None) -> bool:
        """
        Check if lecturer is available at given time
        
        Args:
            lecturer_id: Lecturer identifier
            day: Day of week (MON, TUE, etc.)
            period: Period identifier
            start_time: Start time (optional, for future use)
            end_time: End time (optional, for future use)
        
        Returns:
            True if lecturer is available, False otherwise
        """
        key = f"lecturer:{lecturer_id}:{day}:{period}"
        if key in self._cache:
            return not self._cache[key]
        
        booking = self.db.resource_bookings.find_one({
            'resource_type': 'lecturer',
            'resource_id': lecturer_id,
            'term': self.term,
            'academic_year': self.academic_year,
            'day': day,
            'period': period,
            'is_booked': True
        })
        
        is_available = booking is None
        self._cache[key] = not is_available
        return is_available
    
    def book_resource(self, assignment: Assignment, faculty: str = None, 
                     generation_id: str = None):
        """
        Book a resource (room, lecturer, time slot)
        
        Args:
            assignment: Assignment object from CSP
            faculty: Faculty name (optional)
            generation_id: Generation identifier (optional)
        """
        if generation_id is None:
            generation_id = f"gen_{self.term.lower()}_{faculty.lower() if faculty else 'unknown'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        time_slot = assignment.time_slot
        if isinstance(time_slot, dict):
            day = time_slot.get('day')
            period = time_slot.get('period')
            start_time = time_slot.get('start')
            end_time = time_slot.get('end')
        else:
            day = time_slot.day
            period = time_slot.period
            start_time = time_slot.start
            end_time = time_slot.end
        
        # Book room
        room_booking = {
            'resource_type': 'room',
            'resource_id': assignment.room_number,
            'term': self.term,
            'academic_year': self.academic_year,
            'day': day,
            'period': period,
            'start_time': start_time,
            'end_time': end_time,
            'is_booked': True,
            'assignment_id': assignment.variable_id,
            'faculty': faculty,
            'generation_id': generation_id,
            'booked_at': datetime.now()
        }
        self.db.resource_bookings.insert_one(room_booking)
        
        # Book lecturer
        lecturer_booking = {
            'resource_type': 'lecturer',
            'resource_id': assignment.lecturer_id,
            'term': self.term,
            'academic_year': self.academic_year,
            'day': day,
            'period': period,
            'start_time': start_time,
            'end_time': end_time,
            'is_booked': True,
            'assignment_id': assignment.variable_id,
            'faculty': faculty,
            'generation_id': generation_id,
            'booked_at': datetime.now()
        }
        self.db.resource_bookings.insert_one(lecturer_booking)
        
        # Invalidate cache for this specific resource
        room_key = f"room:{assignment.room_number}:{day}:{period}"
        lecturer_key = f"lecturer:{assignment.lecturer_id}:{day}:{period}"
        self._cache[room_key] = True
        self._cache[lecturer_key] = True
    
    def get_existing_assignments(self, faculty: str = None) -> List[Dict]:
        """
        Get all existing assignments for conflict awareness
        
        Args:
            faculty: Optional faculty filter
        
        Returns:
            List of assignment dictionaries
        """
        query = {
            'term': self.term,
            'academic_year': self.academic_year,
            'status': 'confirmed'
        }
        if faculty:
            query['faculty'] = faculty
        
        return list(self.db.timetable_assignments.find(query))
    
    def load_existing_assignments_to_context(self, constraint_context: ConstraintContext):
        """
        Load existing assignments into CSP constraint context
        
        This allows the CSP solver to be aware of existing bookings
        and avoid conflicts automatically.
        
        Args:
            constraint_context: CSP ConstraintContext to populate
        """
        existing = self.get_existing_assignments()
        
        print(f"   📋 Loading {len(existing)} existing assignments into constraint context...")
        
        for assignment in existing:
            time_key = f"{assignment['day']}_{assignment['period']}"
            
            # Mark room as booked
            if assignment['room_number'] not in constraint_context.room_schedule:
                constraint_context.room_schedule[assignment['room_number']] = {}
            if time_key not in constraint_context.room_schedule[assignment['room_number']]:
                constraint_context.room_schedule[assignment['room_number']][time_key] = set()
            constraint_context.room_schedule[assignment['room_number']][time_key].add(
                assignment['session_id']
            )
            
            # Mark lecturer as booked
            if assignment['lecturer_id'] not in constraint_context.lecturer_schedule:
                constraint_context.lecturer_schedule[assignment['lecturer_id']] = {}
            if time_key not in constraint_context.lecturer_schedule[assignment['lecturer_id']]:
                constraint_context.lecturer_schedule[assignment['lecturer_id']][time_key] = set()
            constraint_context.lecturer_schedule[assignment['lecturer_id']][time_key].add(
                assignment['session_id']
            )
            
            # Track program schedule (for student group conflicts)
            if assignment['program_id'] not in constraint_context.program_schedule:
                constraint_context.program_schedule[assignment['program_id']] = {}
            if time_key not in constraint_context.program_schedule[assignment['program_id']]:
                constraint_context.program_schedule[assignment['program_id']][time_key] = set()
            constraint_context.program_schedule[assignment['program_id']][time_key].add(
                assignment['session_id']
            )
        
        print(f"   ✅ Loaded existing assignments into constraint context")
    
    def save_assignment(self, assignment: Assignment, faculty: str = None,
                       generation_id: str = None) -> Dict:
        """
        Save an assignment to the timetable_assignments collection
        
        Args:
            assignment: Assignment object from CSP
            faculty: Faculty name (optional)
            generation_id: Generation identifier (optional)
        
        Returns:
            Saved assignment document
        """
        if generation_id is None:
            generation_id = f"gen_{self.term.lower()}_{faculty.lower() if faculty else 'unknown'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        time_slot = assignment.time_slot
        if isinstance(time_slot, dict):
            day = time_slot.get('day')
            period = time_slot.get('period')
            start_time = time_slot.get('start')
            end_time = time_slot.get('end')
        else:
            day = time_slot.day
            period = time_slot.period
            start_time = time_slot.start
            end_time = time_slot.end
        
        assignment_doc = {
            'session_id': assignment.variable_id,
            'term': self.term,
            'academic_year': self.academic_year,
            'faculty': faculty,
            'program_id': assignment.program_id,
            'course_id': assignment.course_unit_id,
            'lecturer_id': assignment.lecturer_id,
            'room_number': assignment.room_number,
            'day': day,
            'period': period,
            'start_time': start_time,
            'end_time': end_time,
            'session_number': getattr(assignment, 'session_number', 1),
            'status': 'confirmed',
            'created_at': datetime.now(),
            'generation_id': generation_id
        }
        
        result = self.db.timetable_assignments.insert_one(assignment_doc)
        assignment_doc['_id'] = result.inserted_id
        
        return assignment_doc
    
    def delete_faculty_assignments(self, faculty: str):
        """
        Delete all assignments and bookings for a specific faculty
        
        Used when regenerating a faculty's timetable
        
        Args:
            faculty: Faculty name
        """
        # Delete timetable assignments
        assignments_deleted = self.db.timetable_assignments.delete_many({
            'term': self.term,
            'academic_year': self.academic_year,
            'faculty': faculty
        })
        
        # Delete resource bookings
        bookings_deleted = self.db.resource_bookings.delete_many({
            'term': self.term,
            'academic_year': self.academic_year,
            'faculty': faculty
        })
        
        # Invalidate cache
        self.invalidate_cache()
        
        return {
            'assignments_deleted': assignments_deleted.deleted_count,
            'bookings_deleted': bookings_deleted.deleted_count
        }
    
    def get_resource_availability(self, resource_type: str, resource_id: str) -> Dict:
        """
        Get availability information for a specific resource
        
        Args:
            resource_type: 'room' or 'lecturer'
            resource_id: Resource identifier
        
        Returns:
            Dictionary with availability information
        """
        bookings = list(self.db.resource_bookings.find({
            'resource_type': resource_type,
            'resource_id': resource_id,
            'term': self.term,
            'academic_year': self.academic_year,
            'is_booked': True
        }))
        
        booked_slots = {}
        for booking in bookings:
            day = booking['day']
            period = booking['period']
            if day not in booked_slots:
                booked_slots[day] = []
            booked_slots[day].append({
                'period': period,
                'start_time': booking.get('start_time'),
                'end_time': booking.get('end_time'),
                'faculty': booking.get('faculty')
            })
        
        return {
            'resource_type': resource_type,
            'resource_id': resource_id,
            'term': self.term,
            'academic_year': self.academic_year,
            'booked_slots': booked_slots,
            'total_bookings': len(bookings)
        }
