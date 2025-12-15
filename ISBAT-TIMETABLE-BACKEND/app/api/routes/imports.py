"""
Import endpoints for bulk importing data from Excel/CSV files
"""
from flask import Blueprint, request, jsonify
from app import get_db
from app.models.lecturer import Lecturer
from app.models.subject import CourseUnit
from app.models.room import Room
from app.models.program import Program
from app.models.canonical_course_group import CanonicalCourseGroup
from app.middleware.auth import require_auth
import traceback
import json
import re

bp = Blueprint('imports', __name__, url_prefix='/api/import')


def normalize_column_name(name):
    """Normalize column names for case-insensitive matching"""
    # Remove parentheses and their contents, then normalize
    # This handles column names like "Specializations(Subject Groups)" -> "specializations"
    name_cleaned = re.sub(r'\([^)]*\)', '', name).strip()
    # Normalize: lowercase, replace separators with spaces
    normalized = name_cleaned.lower().replace('_', ' ').replace('-', ' ').replace('/', ' ').strip()
    return normalized


@bp.route('/lecturers', methods=['POST'])
@require_auth
def import_lecturers():
    """Import lecturers from Excel/CSV data"""
    try:
        data = request.get_json()
        rows = data.get('data', [])
        
        if not rows:
            return jsonify({'error': 'No data provided'}), 400
        
        db = get_db()
        imported = 0
        errors = []
        skipped = []
        
        required_fields = ['id', 'name', 'role', 'faculty', 'specializations', 'sessions per day', 'max weekly hours']
        
        for index, row in enumerate(rows, start=2):
            try:
                # Normalize column names
                normalized_row = {}
                for key, value in row.items():
                    normalized_key = normalize_column_name(key)
                    normalized_row[normalized_key] = value
                    # Also keep original key for fallback
                    normalized_row[key.lower()] = value
                
                # Map column variations
                lecturer_id = (
                    normalized_row.get('lecturer id') or  # Primary format
                    normalized_row.get('lecturer_id') or
                    normalized_row.get('id')
                )
                name = (
                    normalized_row.get('name') or  # Primary format
                    normalized_row.get('lecturer name') or
                    normalized_row.get('lecturer_name')
                )
                role = (
                    normalized_row.get('role') or  # Primary format
                    normalized_row.get('lecturer role') or
                    normalized_row.get('lecturer_role')
                )
                faculty = normalized_row.get('faculty')  # Primary format
                # Get specializations - normalization now strips parentheses, so "Specializations(Subject Groups)" becomes "specializations"
                specializations_str = (
                    normalized_row.get('specializations') or  # Primary format (handles "Specializations(Subject Groups)" after normalization)
                    normalized_row.get('specialization') or 
                    normalized_row.get('courses') or 
                    normalized_row.get('course units') or
                    normalized_row.get('course_units') or
                    ''
                )
                
                # Validate required fields
                missing_fields = []
                if not lecturer_id:
                    missing_fields.append('Lecturer Id')
                if not name:
                    missing_fields.append('Name')
                if not role:
                    missing_fields.append('Role')
                if not faculty:
                    missing_fields.append('Faculty')
                if not specializations_str or (isinstance(specializations_str, str) and not specializations_str.strip()):
                    missing_fields.append('Specializations(Subject Groups)')
                
                if missing_fields:
                    errors.append(f"Row {index}: Missing required fields: {', '.join(missing_fields)}")
                    continue
                
                # Parse specializations - store exactly as provided (no normalization/conversion)
                # The system accepts: canonical IDs, human-readable names, or subject codes
                # All formats are stored as-is and matched during timetable generation
                if isinstance(specializations_str, str):
                    specializations = [s.strip() for s in specializations_str.split(',') if s.strip()]
                elif isinstance(specializations_str, list):
                    specializations = [str(s).strip() for s in specializations_str if s]
                else:
                    specializations = []
                
                # Validate that specializations are provided
                if not specializations or len(specializations) == 0:
                    errors.append(f"Row {index}: Specializations(Subject Groups) field is required and must contain at least one course group ID or subject code")
                    continue
                
                # Store specializations exactly as provided - no conversion or normalization
                # The matching function will handle all formats (canonical ID, human-readable name, subject code)
                # Specializations are already validated above, so we can proceed
                
                # Parse availability (required)
                # Format: "MON:09:00-11:00,11:00-13:00|TUE:14:00-16:00|WED:09:00-11:00"
                # Uses: | to separate days, : to separate day from slots, , to separate multiple slots
                availability = None
                availability_str = (
                    normalized_row.get('availability') or
                    normalized_row.get('avail')
                )
                
                role_normalized = str(role).strip()
                
                if role_normalized == "Part-Time":
                    # Part-Time: Availability is required
                    if not availability_str:
                        errors.append(f"Row {index}: Missing required field (Availability) for Part-Time lecturer")
                        continue
                    
                    if isinstance(availability_str, dict):
                        # Already a dict, use as is
                        availability = availability_str
                    elif isinstance(availability_str, str) and availability_str.strip():
                        # Try JSON first (for backward compatibility)
                        try:
                            availability = json.loads(availability_str)
                        except:
                            # Parse custom format: "DAY:slot1,slot2|DAY2:slot1"
                            availability = {}
                            # Split by pipe to get days
                            day_entries = availability_str.split('|')
                            for day_entry in day_entries:
                                day_entry = day_entry.strip()
                                if ':' in day_entry:
                                    day, slots_str = day_entry.split(':', 1)
                                    day = day.strip().upper()
                                    # Split slots by comma
                                    slots = [s.strip() for s in slots_str.split(',') if s.strip()]
                                    if day and slots:
                                        availability[day] = slots
                    
                    # Validate that availability has at least one day
                    if not availability or len(availability) == 0:
                        errors.append(f"Row {index}: Availability must contain at least one day with time slots for Part-Time lecturer")
                        continue
                else:
                    # Full-Time and Faculty Dean: Always available (set to None)
                    availability = None
                
                # Parse sessions_per_day (required)
                # Check all possible variations (normalized and original)
                sessions_per_day = None
                sessions_per_day_value = None
                
                # Try normalized keys first
                for key in ['sessions per day', 'sessions_per_day', 'sessions/day']:
                    if key in normalized_row:
                        sessions_per_day_value = normalized_row[key]
                        break
                
                # If not found, try original row keys (case-insensitive)
                if sessions_per_day_value is None:
                    for key in row.keys():
                        if normalize_column_name(key) in ['sessions per day', 'sessions_per_day', 'sessions/day']:
                            sessions_per_day_value = row[key]
                            break
                
                if sessions_per_day_value is not None:
                    try:
                        # Handle both string and numeric values
                        if isinstance(sessions_per_day_value, (int, float)):
                            sessions_per_day = int(sessions_per_day_value)
                        else:
                            sessions_per_day = int(str(sessions_per_day_value).strip())
                        if sessions_per_day < 1:
                            errors.append(f"Row {index}: Sessions/Day must be at least 1")
                            continue
                    except (ValueError, TypeError) as e:
                        errors.append(f"Row {index}: Invalid Sessions/Day value: {sessions_per_day_value} ({str(e)})")
                        continue
                else:
                    errors.append(f"Row {index}: Missing required field (Sessions/Day). Available columns: {', '.join(row.keys())}")
                    continue
                
                # Parse max_weekly_hours (required)
                # Check all possible variations (normalized and original)
                max_weekly_hours = None
                max_weekly_hours_value = None
                
                # Try normalized keys first
                for key in ['max weekly hours', 'max_weekly_hours']:
                    if key in normalized_row:
                        max_weekly_hours_value = normalized_row[key]
                        break
                
                # If not found, try original row keys (case-insensitive)
                if max_weekly_hours_value is None:
                    for key in row.keys():
                        if normalize_column_name(key) in ['max weekly hours', 'max_weekly_hours']:
                            max_weekly_hours_value = row[key]
                            break
                
                if max_weekly_hours_value is not None:
                    try:
                        # Handle both string and numeric values
                        if isinstance(max_weekly_hours_value, (int, float)):
                            max_weekly_hours = int(max_weekly_hours_value)
                        else:
                            max_weekly_hours = int(str(max_weekly_hours_value).strip())
                        if max_weekly_hours < 1:
                            errors.append(f"Row {index}: Max Weekly Hours must be at least 1")
                            continue
                    except (ValueError, TypeError) as e:
                        errors.append(f"Row {index}: Invalid Max Weekly Hours value: {max_weekly_hours_value} ({str(e)})")
                        continue
                else:
                    errors.append(f"Row {index}: Missing required field (Max Weekly Hours). Available columns: {', '.join(row.keys())}")
                    continue
                
                role_normalized = str(role).strip()
                
                lecturer_id = str(lecturer_id).strip()
                
                # Check if exists
                existing = db.lecturers.find_one({'id': lecturer_id})
                if existing:
                    skipped.append(f"Row {index}: Lecturer ID '{lecturer_id}' already exists")
                    continue
                
                # Create lecturer
                lecturer_data = {
                    'id': lecturer_id,
                    'name': str(name).strip(),
                    'role': role_normalized,
                    'faculty': str(faculty).strip(),
                    'specializations': specializations,
                    'availability': availability,
                    'sessions_per_day': sessions_per_day,
                    'max_weekly_hours': max_weekly_hours
                }
                
                lecturer = Lecturer.from_dict(lecturer_data)
                db.lecturers.insert_one(lecturer.to_dict())
                imported += 1
                
            except Exception as e:
                errors.append(f"Row {index}: {str(e)}")
                continue
        
        return jsonify({
            'success': True,
            'imported': imported,
            'skipped': len(skipped),
            'errors': errors[:50],
            'skipped_details': skipped[:20]
        }), 200
        
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@bp.route('/subjects', methods=['POST'])
@require_auth
def import_subjects():
    """Import subjects from Excel/CSV data"""
    try:
        data = request.get_json()
        rows = data.get('data', [])
        
        if not rows:
            return jsonify({'error': 'No data provided'}), 400
        
        db = get_db()
        imported = 0
        errors = []
        skipped = []
        
        for index, row in enumerate(rows, start=2):
            try:
                normalized_row = {}
                for key, value in row.items():
                    normalized_key = normalize_column_name(key)
                    normalized_row[normalized_key] = value
                
                # Map column variations - support both old and new column names
                # Primary format: Subject Code, Subject Name, Program, Semester, Weekly Hours, Room Type, Prefered Term
                course_id = (
                    normalized_row.get('subject code') or  # Primary format
                    normalized_row.get('id') or 
                    normalized_row.get('course id') or
                    normalized_row.get('course_id') or
                    normalized_row.get('code')
                )
                code = (
                    normalized_row.get('subject code') or  # Primary format
                    normalized_row.get('code') or 
                    normalized_row.get('course code') or
                    normalized_row.get('course_code') or
                    course_id
                )
                name = (
                    normalized_row.get('subject name') or  # Primary format
                    normalized_row.get('name') or 
                    normalized_row.get('course name') or
                    normalized_row.get('course_name')
                )
                program = (
                    normalized_row.get('program') or  # Primary format
                    normalized_row.get('program name') or
                    normalized_row.get('program_name')
                )
                semester = normalized_row.get('semester')  # Primary format
                weekly_hours = (
                    normalized_row.get('weekly hours') or  # Primary format
                    normalized_row.get('weekly_hours') or 
                    normalized_row.get('hours')
                )
                credits = normalized_row.get('credits') or normalized_row.get('credit') or 0
                preferred_room_type = (
                    normalized_row.get('room type') or  # Primary format
                    normalized_row.get('preferred room type') or 
                    normalized_row.get('preferred_room_type') or
                    normalized_row.get('room_type') or
                    normalized_row.get('type')
                )
                preferred_term = (
                    normalized_row.get('prefered term') or  # Primary format (note: "Prefered" spelling)
                    normalized_row.get('preferred term') or  # Alternative spelling
                    normalized_row.get('preferred_term') or
                    normalized_row.get('prefered_term') or
                    normalized_row.get('term')
                )
                
                if not course_id or not code or not name:
                    errors.append(f"Row {index}: Missing required fields (Subject Code, Subject Name)")
                    continue
                
                if not weekly_hours or str(weekly_hours).strip() == '':
                    errors.append(f"Row {index}: Missing required field (Weekly Hours)")
                    continue
                
                if not preferred_room_type or str(preferred_room_type).strip() == '':
                    errors.append(f"Row {index}: Missing required field (Room Type)")
                    continue
                
                # Parse numeric fields
                try:
                    weekly_hours = int(weekly_hours)
                    if weekly_hours <= 0:
                        errors.append(f"Row {index}: Weekly Hours must be greater than 0")
                        continue
                except (ValueError, TypeError):
                    errors.append(f"Row {index}: Invalid Weekly Hours value: {weekly_hours}")
                    continue
                
                try:
                    credits = int(credits) if credits else 0
                except:
                    credits = 0  # Credits is optional, default to 0
                
                # Validate room type
                if preferred_room_type:
                    preferred_room_type = str(preferred_room_type).strip().capitalize()
                    if preferred_room_type not in ['Theory', 'Lab']:
                        preferred_room_type = 'Theory'  # Default
                else:
                    preferred_room_type = 'Theory'
                
                code = str(code).strip()
                course_id = code  # Use code as the primary key (id)
                
                # Check if exists
                existing = db.course_units.find_one({'id': course_id})
                if existing:
                    skipped.append(f"Row {index}: Subject with code '{code}' already exists")
                    continue
                
                # Create subject - use code as id
                # Only include new required fields (removed: difficulty, is_foundational, prerequisites)
                course_data = {
                    'id': course_id,  # id = code
                    'code': code,
                    'name': str(name).strip(),
                    'weekly_hours': weekly_hours,
                    'credits': credits,
                    'preferred_room_type': preferred_room_type,
                    'semester': str(semester).strip() if semester else None,
                    'program': str(program).strip() if program else None,
                    'preferred_term': str(preferred_term).strip() if preferred_term else None
                }
                
                # Add course_group if provided
                course_group = normalized_row.get('course group') or normalized_row.get('course_group')
                if course_group:
                    course_data['course_group'] = str(course_group).strip()
                
                subject = CourseUnit.from_dict(course_data)
                db.course_units.insert_one(subject.to_dict())
                imported += 1
                
            except Exception as e:
                errors.append(f"Row {index}: {str(e)}")
                continue
        
        return jsonify({
            'success': True,
            'imported': imported,
            'skipped': len(skipped),
            'errors': errors[:50],
            'skipped_details': skipped[:20]
        }), 200
        
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@bp.route('/rooms', methods=['POST'])
@require_auth
def import_rooms():
    """Import rooms from Excel/CSV data"""
    try:
        data = request.get_json()
        rows = data.get('data', [])
        
        if not rows:
            return jsonify({'error': 'No data provided'}), 400
        
        db = get_db()
        imported = 0
        errors = []
        skipped = []
        
        for index, row in enumerate(rows, start=2):
            try:
                normalized_row = {}
                for key, value in row.items():
                    normalized_key = normalize_column_name(key)
                    normalized_row[normalized_key] = value
                
                # Parse required fields - check both normalized and original column names
                room_number = None
                for key in ['room number', 'room_number', 'number', 'id']:
                    if key in normalized_row:
                        room_number = normalized_row[key]
                        break
                    # Also check original row keys
                    for orig_key in row.keys():
                        if normalize_column_name(orig_key) == key:
                            room_number = row[orig_key]
                            break
                    if room_number:
                        break
                
                capacity = None
                for key in ['capacity']:
                    if key in normalized_row:
                        capacity = normalized_row[key]
                        break
                    # Also check original row keys
                    for orig_key in row.keys():
                        if normalize_column_name(orig_key) == key:
                            capacity = row[orig_key]
                            break
                
                room_type = None
                for key in ['room type', 'room_type', 'type']:
                    if key in normalized_row:
                        room_type = normalized_row[key]
                        break
                    # Also check original row keys
                    for orig_key in row.keys():
                        if normalize_column_name(orig_key) == key:
                            room_type = row[orig_key]
                            break
                    if room_type:
                        break
                
                specializations_str = (
                    normalized_row.get('specialization') or
                    normalized_row.get('specializations') or
                    ''
                )
                
                # Validate required fields
                missing_fields = []
                if not room_number:
                    missing_fields.append('room_number')
                if capacity is None or str(capacity).strip() == '':
                    missing_fields.append('capacity')
                if not room_type or str(room_type).strip() == '':
                    missing_fields.append('room_type')
                if not specializations_str or str(specializations_str).strip() == '':
                    missing_fields.append('specialization')
                
                if missing_fields:
                    errors.append(f"Row {index}: Missing required fields ({', '.join(missing_fields)})")
                    continue
                
                # Parse capacity
                try:
                    capacity = int(capacity) if capacity else 0
                except:
                    capacity = 0
                
                # Validate room type
                if room_type:
                    room_type = str(room_type).strip().capitalize()
                    if room_type not in ['Theory', 'Lab']:
                        room_type = 'Theory'  # Default
                else:
                    room_type = 'Theory'
                
                # Parse specializations (comma-separated) - required field
                specializations = []
                if specializations_str:
                    specializations = [
                        s.strip() 
                        for s in str(specializations_str).split(',') 
                        if s.strip()
                    ]
                
                # Validate that at least one specialization was provided
                if not specializations:
                    errors.append(f"Row {index}: Specialization field is required and must contain at least one specialization")
                    continue
                
                room_number = str(room_number).strip()
                
                # Check if exists
                existing = db.rooms.find_one({'room_number': room_number})
                if existing:
                    skipped.append(f"Row {index}: Room number '{room_number}' already exists")
                    continue
                
                # Create room - explicitly exclude 'id' field
                room_data = {
                    'room_number': room_number,
                    'capacity': capacity,
                    'room_type': room_type,
                    'specializations': specializations,
                    'is_available': True
                }
                
                # Ensure 'id' is not in the data (rooms use room_number as primary key)
                room_data.pop('id', None)
                
                room = Room.from_dict(room_data)
                room_dict = room.to_dict()
                # Double-check: remove 'id' if it somehow got in there
                room_dict.pop('id', None)
                
                db.rooms.insert_one(room_dict)
                imported += 1
                
            except Exception as e:
                errors.append(f"Row {index}: {str(e)}")
                continue
        
        return jsonify({
            'success': True,
            'imported': imported,
            'skipped': len(skipped),
            'errors': errors[:50],
            'skipped_details': skipped[:20]
        }), 200
        
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@bp.route('/programs', methods=['POST'])
@require_auth
def import_programs():
    """
    Import programs from Excel/CSV data
    
    Expected columns:
    - Program Code (required): Program identifier (e.g., BSCAIT, BSCCS, BBA)
    - Program Name (required): Full program name
    - Faculty (required): Faculty name (e.g., "ICT", "Business & Commerce")
    - Batch (required): Batch identifier
    - Semester (required): Semester (e.g., S1, S2, S3, S4, S5, S6)
    - Student Size (required): Number of students
    - Subjects (required): Comma-separated list of subject codes
    
    Optional columns:
    - Term: Term identifier (Term1, Term2)
    
    Faculty normalization:
    - "Business", "Business and Commerce" -> "Business & Commerce"
    - "ICT", "Information Technology", "Computer Science", "IT" -> "ICT"
    
    If Faculty is missing, system will try to infer from Program Code:
    - BSCAIT, BSCCS, BCS, BIT -> "ICT"
    - BBA, BAF, BSC.AF -> "Business & Commerce"
    """
    try:
        data = request.get_json()
        rows = data.get('data', [])
        
        if not rows:
            return jsonify({'error': 'No data provided'}), 400
        
        db = get_db()
        imported = 0
        errors = []
        skipped = []
        
        for index, row in enumerate(rows, start=2):
            try:
                normalized_row = {}
                for key, value in row.items():
                    normalized_key = normalize_column_name(key)
                    normalized_row[normalized_key] = value
                
                # Map column variations - Primary format: Program Code, Program Name, Faculty, Batch, Semester, Student Size, Subjects
                program_id = (
                    normalized_row.get('program code') or  # Primary format
                    normalized_row.get('id') or 
                    normalized_row.get('program id') or
                    normalized_row.get('program_id') or
                    normalized_row.get('code')
                )
                batch = normalized_row.get('batch')  # Primary format
                program = (
                    normalized_row.get('program name') or  # Primary format
                    normalized_row.get('program') or 
                    normalized_row.get('program_name') or
                    normalized_row.get('name')
                )
                faculty = (
                    normalized_row.get('faculty') or  # Primary format
                    normalized_row.get('faculty name') or
                    normalized_row.get('faculty_name')
                )
                semester = normalized_row.get('semester')  # Primary format
                term = normalized_row.get('term')  # Optional - not in primary format but may be needed
                size = (
                    normalized_row.get('student size') or  # Primary format
                    normalized_row.get('size') or 
                    normalized_row.get('student_size')
                )
                subjects_str = (
                    normalized_row.get('subjects') or  # Primary format
                    normalized_row.get('course units') or 
                    normalized_row.get('course_units') or
                    normalized_row.get('courses')
                )
                
                # Required fields: Program Code, Program Name, Faculty, Batch, Semester, Student Size, Subjects
                missing_fields = []
                if not program_id:
                    missing_fields.append('Program Code')
                if not program:
                    missing_fields.append('Program Name')
                if not faculty:
                    missing_fields.append('Faculty')
                if not batch:
                    missing_fields.append('Batch')
                if not semester:
                    missing_fields.append('Semester')
                if not size:
                    missing_fields.append('Student Size')
                
                if missing_fields:
                    errors.append(f"Row {index}: Missing required fields: {', '.join(missing_fields)}")
                    continue
                
                # Normalize faculty name (clean up common variations)
                if faculty:
                    faculty = str(faculty).strip()
                    # Normalize common variations
                    faculty_normalizations = {
                        'Business & Commerce': 'Business & Commerce',
                        'Business': 'Business & Commerce',
                        'Business and Commerce': 'Business & Commerce',
                        'ICT': 'ICT',
                        'Information Technology': 'ICT',
                        'Computer Science': 'ICT',
                        'IT': 'ICT'
                    }
                    faculty = faculty_normalizations.get(faculty, faculty)
                
                # Subjects is required
                if not subjects_str:
                    errors.append(f"Row {index}: Missing required field (Subjects)")
                    continue
                
                # Parse Student Size
                try:
                    size = int(size) if size else 0
                    if size < 0:
                        errors.append(f"Row {index}: Student Size must be a positive number")
                        continue
                except (ValueError, TypeError):
                    errors.append(f"Row {index}: Invalid Student Size value: {size}")
                    continue
                
                # Parse Subjects (multi-unit field - comma-separated, REQUIRED)
                subjects = []
                if isinstance(subjects_str, str):
                    # Split by comma and clean up each subject code
                    subjects = [c.strip() for c in subjects_str.split(',') if c.strip()]
                elif isinstance(subjects_str, list):
                    subjects = [str(c).strip() for c in subjects_str if c]
                
                # Validate that at least one subject is provided
                if not subjects or len(subjects) == 0:
                    errors.append(f"Row {index}: Subjects field must contain at least one subject code")
                    continue
                
                # Validate that subject codes exist in database (optional check - warn but don't fail)
                existing_subjects = db.course_units.find({'code': {'$in': subjects}})
                existing_codes = {s['code'] for s in existing_subjects}
                missing_codes = set(subjects) - existing_codes
                if missing_codes:
                    # Warn but don't fail - subjects might be imported later
                    pass  # Could add warning here if needed
                
                # Normalize program_id
                program_id = str(program_id).strip()
                
                # If program_id doesn't look like a full ID (e.g., just "BSCAIT"), construct it
                # Expected format: SG_BSCAIT_S126_S1_T1 or similar
                # If it's just a code, we'll construct: {code}_{batch}_{semester}
                if not '_' in program_id and batch and semester:
                    # Construct ID from components
                    semester_normalized_for_id = str(semester).strip().upper()
                    if semester_normalized_for_id and not semester_normalized_for_id.startswith('S'):
                        if semester_normalized_for_id.isdigit():
                            semester_normalized_for_id = f"S{semester_normalized_for_id}"
                    program_id = f"{program_id}_{batch}_{semester_normalized_for_id}"
                
                # Check if exists
                existing = db.programs.find_one({'id': program_id})
                if existing:
                    skipped.append(f"Row {index}: Program ID '{program_id}' already exists")
                    continue
                
                # Create program
                # Note: term is optional - if not provided, set to empty string
                # Normalize semester to ensure proper format
                semester_normalized = str(semester).strip().upper()
                if semester_normalized and not semester_normalized.startswith('S'):
                    # If just a number, add S prefix
                    if semester_normalized.isdigit():
                        semester_normalized = f"S{semester_normalized}"
                
                program_data = {
                    'id': str(program_id).strip(),
                    'batch': str(batch).strip(),
                    'program': str(program).strip(),
                    'semester': semester_normalized,
                    'term': str(term).strip() if term else "",  # Optional field - not in primary format
                    'size': size,
                    'course_units': subjects,  # Multi-unit field (list of subject codes)
                    'is_active': True,
                    'faculty': faculty if faculty else None  # Faculty field (required for scalable generation)
                }
                
                program = Program.from_dict(program_data)
                db.programs.insert_one(program.to_dict())
                imported += 1
                
            except Exception as e:
                errors.append(f"Row {index}: {str(e)}")
                continue
        
        return jsonify({
            'success': True,
            'imported': imported,
            'skipped': len(skipped),
            'errors': errors[:50],
            'skipped_details': skipped[:20]
        }), 200
        
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@bp.route('/canonical-groups', methods=['POST'])
@require_auth
def import_canonical_groups():
    """Import canonical subject groups from Excel/CSV data"""
    try:
        data = request.get_json()
        rows = data.get('data', [])
        
        if not rows:
            return jsonify({'error': 'No data provided'}), 400
        
        db = get_db()
        imported = 0
        skipped = []
        errors = []
        
        for index, row in enumerate(rows, start=2):  # Start at 2 (row 1 is header)
            try:
                # Normalize column names
                normalized_row = {}
                for key, value in row.items():
                    normalized_key = normalize_column_name(key)
                    normalized_row[normalized_key] = value
                
                # Map field names (case-insensitive)
                # Required: Group Id, Subject Name, Subject Codes
                canonical_id = (
                    normalized_row.get('group id') or
                    normalized_row.get('group_id') or
                    normalized_row.get('canonical id') or
                    normalized_row.get('canonical_id')
                )
                
                name = (
                    normalized_row.get('subject name') or
                    normalized_row.get('subject_name') or
                    normalized_row.get('name')
                )
                
                subject_codes_str = (
                    normalized_row.get('subject codes') or
                    normalized_row.get('subject_codes') or
                    normalized_row.get('course codes') or
                    normalized_row.get('course_codes')
                )
                
                description = (
                    normalized_row.get('description') or
                    normalized_row.get('desc')
                )
                
                # Validate required fields
                if not canonical_id:
                    errors.append(f"Row {index}: Missing required field (Group Id)")
                    continue
                
                if not name:
                    errors.append(f"Row {index}: Missing required field (Subject Name)")
                    continue
                
                if not subject_codes_str:
                    errors.append(f"Row {index}: Missing required field (Subject Codes)")
                    continue
                
                if not description:
                    errors.append(f"Row {index}: Missing required field (Description)")
                    continue
                
                # Parse Subject Codes (multi-input field - comma-separated, REQUIRED)
                subject_codes = []
                if isinstance(subject_codes_str, str):
                    # Split by comma and clean up each subject code
                    subject_codes = [c.strip() for c in subject_codes_str.split(',') if c.strip()]
                elif isinstance(subject_codes_str, list):
                    subject_codes = [str(c).strip() for c in subject_codes_str if c]
                
                # Validate that at least one subject code is provided
                if not subject_codes or len(subject_codes) == 0:
                    errors.append(f"Row {index}: Subject Codes field must contain at least one subject code")
                    continue
                
                # Check if canonical group already exists
                existing = db.canonical_course_groups.find_one({'canonical_id': canonical_id})
                if existing:
                    skipped.append(f"Row {index}: Group Id '{canonical_id}' already exists")
                    continue
                
                # Validate that subject codes exist in database (optional check - warn but don't fail)
                existing_subjects = db.course_units.find({'code': {'$in': subject_codes}})
                existing_codes = {s['code'] for s in existing_subjects}
                missing_codes = set(subject_codes) - existing_codes
                if missing_codes:
                    # Warn but don't fail - subjects might be imported later
                    pass  # Could add warning here if needed
                
                # Create canonical group
                group_data = {
                    'canonical_id': str(canonical_id).strip(),
                    'name': str(name).strip(),
                    'course_codes': subject_codes,
                    'description': str(description).strip()
                }
                
                canonical_group = CanonicalCourseGroup.from_dict(group_data)
                db.canonical_course_groups.insert_one(canonical_group.to_dict())
                imported += 1
                
            except Exception as e:
                errors.append(f"Row {index}: {str(e)}")
                continue
        
        return jsonify({
            'success': True,
            'imported': imported,
            'skipped': len(skipped),
            'errors': errors[:50],
            'skipped_details': skipped[:20]
        }), 200
        
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

