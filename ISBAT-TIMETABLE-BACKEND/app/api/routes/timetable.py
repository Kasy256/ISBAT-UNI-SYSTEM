from flask import Blueprint, request, jsonify
from app import get_db
from app.middleware.auth import require_auth, require_role
from bson import ObjectId
import traceback
import subprocess
import os
import json
from pathlib import Path
from datetime import datetime

bp = Blueprint('timetable', __name__, url_prefix='/api/timetable')

PROGRESS_FILE_TEMPLATE = 'timetable_generation_progress_term{}.json'


def get_program_identifier(row):
    """Extract program identifier from CSV row."""
    return row.get('Program') or row.get('Student_Group', '')


def get_program_size(row):
    """Extract student size from CSV row."""
    size_value = row.get('Student_Size') or row.get('Group_Size') or 0
    try:
        return int(size_value)
    except (ValueError, TypeError):
        return 0


@bp.route('/generate', methods=['POST'])
@require_auth
@require_role('scheduler')
def generate_timetable():
    """
    Generate timetable for a specific term (Term 1 or Term 2)
    Calls generate_term_timetable.py --term X and then verifies constraints
    
    Request body:
    {
        "term": 1  or 2
    }
    """
    try:
        data = request.get_json()
        term = data.get('term')
        
        if term not in [1, 2]:
            return jsonify({'error': 'Term must be 1 or 2'}), 400
        
        # Validate that time slots exist in database and have correct format
        db = get_db()
        time_slots_count = db.time_slots.count_documents({})
        if time_slots_count == 0:
            # Auto-seed time slots if they don't exist
            from seed_config_data import seed_time_slots_to_db
            print("⚠️  No time slots found in database. Auto-seeding default time slots...")
            try:
                seed_time_slots_to_db(db)
                print("✅ Time slots seeded successfully")
                # Invalidate cache after seeding
                from app.services.config_loader import invalidate_config_cache
                invalidate_config_cache()
            except Exception as seed_error:
                return jsonify({
                    'error': 'No time slots configured. Please seed time slots first.',
                    'details': 'Run: python seed_config_data.py or use the Time Slots management page'
                }), 500
        else:
            # Validate time slot format
            from app.services.config_loader import get_time_slots_for_config
            try:
                time_slots_config = get_time_slots_for_config(use_cache=True)
                if not time_slots_config:
                    return jsonify({
                        'error': 'Time slots found but failed to load. Please check time slot format.',
                        'details': 'Ensure all time slots have: period, start, end, is_afternoon fields'
                    }), 500
                
                # Validate required fields
                required_fields = ['period', 'start', 'end', 'is_afternoon']
                invalid_slots = []
                for slot in time_slots_config:
                    missing_fields = [field for field in required_fields if field not in slot]
                    if missing_fields:
                        invalid_slots.append(f"{slot.get('period', 'UNKNOWN')}: missing {', '.join(missing_fields)}")
                
                if invalid_slots:
                    return jsonify({
                        'error': f'{len(invalid_slots)} time slot(s) have invalid format',
                        'details': invalid_slots[:5],  # Show first 5 errors
                        'message': 'Please fix time slot format in the Time Slots management page'
                    }), 500
            except Exception as e:
                return jsonify({
                    'error': 'Failed to validate time slots',
                    'details': str(e)
                }), 500
        
        # Validate that room specializations exist
        room_specs_count = db.room_specializations.count_documents({})
        if room_specs_count == 0:
            # Auto-seed room specializations if they don't exist
            from seed_config_data import seed_room_specializations_to_db
            print("⚠️  No room specializations found in database. Auto-seeding default specializations...")
            try:
                seed_room_specializations_to_db(db)
                print("✅ Room specializations seeded successfully")
                # Invalidate cache after seeding
                from app.services.config_loader import invalidate_config_cache
                invalidate_config_cache()
            except Exception as seed_error:
                return jsonify({
                    'error': 'No room specializations configured. Please seed room specializations first.',
                    'details': 'Run: python seed_config_data.py or use the Room Specializations management page'
                }), 500
        
        # Get the backend directory path
        # __file__ is at: app/api/routes/timetable.py
        # So we need to go up 3 levels: routes -> api -> app -> backend root
        current_file = Path(__file__).resolve()
        backend_dir = current_file.parent.parent.parent.parent
        
        # Debug: Print path information
        print(f"Current file: {current_file}")
        print(f"Calculated backend_dir: {backend_dir}")
        print(f"Backend dir exists: {backend_dir.exists()}")
        
        # Alternative: Try to find the script in common locations
        if not (backend_dir / 'generate_term_timetable.py').exists():
            # Try current directory
            backend_dir = Path.cwd()
            if not (backend_dir / 'generate_term_timetable.py').exists():
                # Try one level up
                backend_dir = Path.cwd().parent
                if not (backend_dir / 'generate_term_timetable.py').exists():
                    return jsonify({
                        'error': 'Timetable generation script not found',
                        'searched_paths': [
                            str(current_file.parent.parent.parent.parent),
                            str(Path.cwd()),
                            str(Path.cwd().parent)
                        ]
                    }), 500
        
        # Clear any existing progress file
        progress_file = backend_dir / PROGRESS_FILE_TEMPLATE.format(term)
        if progress_file.exists():
            try:
                progress_file.unlink()
            except Exception:
                pass  # Ignore if file can't be deleted
        
        # Step 1: Generate timetable by calling Python script
        print(f"\n{'='*70}")
        print(f"Generating Term {term} Timetable")
        print(f"Backend directory: {backend_dir}")
        print(f"{'='*70}\n")
        
        generate_script = backend_dir / 'generate_term_timetable.py'
        if not generate_script.exists():
            return jsonify({
                'error': f'Timetable generation script not found at {generate_script}',
                'backend_dir': str(backend_dir)
            }), 500
        
        # Determine Python executable (handle Windows)
        import sys
        python_exe = sys.executable  # Use the same Python that's running Flask
        
        # Run generation script in background
        try:
            print(f"Starting background generation: {python_exe} {generate_script} --term {term}")
            
            # Start process in background
            process = subprocess.Popen(
                [python_exe, str(generate_script), '--term', str(term)],
                cwd=str(backend_dir),
                stdout=subprocess.DEVNULL, # Don't block waiting for output
                stderr=subprocess.DEVNULL,
                start_new_session=True # Detach from parent process
            )
            
            return jsonify({
                'success': True,
                'message': f'Timetable generation started in background for Term {term}',
                'term': term,
                'status': 'started',
                'process_id': process.pid
            }), 202
            
        except Exception as e:
            error_msg = f'Failed to start generation script: {str(e)}'
            print(f"ERROR: {error_msg}")
            return jsonify({
                'error': error_msg,
                'traceback': traceback.format_exc()
            }), 500
        
    except ConnectionError as e:
        return jsonify({"error": "Database Connection Error", "message": str(e)}), 503
    except Exception as e:
        error_msg = f"Error generating timetable: {str(e)}"
        error_traceback = traceback.format_exc()
        print(f"\n{'='*70}")
        print("ERROR IN TIMETABLE GENERATION")
        print(f"{'='*70}")
        print(error_msg)
        print(f"\nFull traceback:")
        print(error_traceback)
        print(f"{'='*70}\n")
        return jsonify({
            'error': "Internal Server Error",
            'message': str(e),
            'traceback': error_traceback
        }), 500

@bp.route('/progress/<int:term>', methods=['GET'])
def get_generation_progress(term):
    """Get progress of timetable generation for a specific term"""
    try:
        # Try to find progress file in common locations
        current_file = Path(__file__).resolve()
        backend_dir = current_file.parent.parent.parent.parent
        
        # Try multiple locations
        possible_paths = [
            backend_dir / PROGRESS_FILE_TEMPLATE.format(term),
            Path.cwd() / PROGRESS_FILE_TEMPLATE.format(term),
            Path.cwd().parent / PROGRESS_FILE_TEMPLATE.format(term),
        ]
        
        progress_file = None
        for path in possible_paths:
            if path.exists():
                progress_file = path
                break
        
        if not progress_file or not progress_file.exists():
            return jsonify({
                'status': 'not_started',
                'percentage': 0,
                'stage': 'Waiting',
                'message': 'Generation not started'
            }), 200
        
        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                progress_data = json.load(f)
            
            # Check if generation is complete (100%) or failed (-1)
            if progress_data.get('percentage', 0) >= 100:
                return jsonify({
                    'status': 'completed',
                    **progress_data
                }), 200
            elif progress_data.get('percentage', 0) < 0:
                return jsonify({
                    'status': 'error',
                    **progress_data
                }), 200
            else:
                return jsonify({
                    'status': 'in_progress',
                    **progress_data
                }), 200
        except json.JSONDecodeError:
            return jsonify({
                'status': 'error',
                'percentage': -1,
                'stage': 'Error',
                'message': 'Invalid progress file format'
            }), 200
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@bp.route('/<timetable_id>', methods=['GET'])
def get_timetable(timetable_id):
    """Get specific timetable by ID"""
    try:
        db = get_db()
        timetable = db.timetables.find_one({'_id': ObjectId(timetable_id)})
        
        if not timetable:
            return jsonify({'error': 'Timetable not found'}), 404
        
        # Enrich lecturer data with faculty information
        timetable_data = timetable.get('timetable', {})
        if timetable_data:
            # Pre-fetch all lecturers to get faculty information
            lecturers_cache = {}
            lecturers_data = db.lecturers.find({})
            for lecturer in lecturers_data:
                lecturers_cache[lecturer.get('id')] = {
                    'faculty': lecturer.get('faculty', ''),
                    'name': lecturer.get('name', ''),
                    'role': lecturer.get('role', '')
                }
            
            # Enrich sessions with lecturer faculty
            for program_key, sessions in timetable_data.items():
                if isinstance(sessions, list):
                    for session in sessions:
                        if 'lecturer' in session and isinstance(session['lecturer'], dict):
                            lecturer_id = session['lecturer'].get('id', '')
                            if lecturer_id and lecturer_id in lecturers_cache:
                                # Add faculty if not already present
                                if 'faculty' not in session['lecturer']:
                                    session['lecturer']['faculty'] = lecturers_cache[lecturer_id].get('faculty', '')
        
        timetable['_id'] = str(timetable['_id'])
        return jsonify(timetable), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/list', methods=['GET'])
def list_timetables():
    """List all timetables"""
    try:
        db = get_db()
        timetables = list(db.timetables.find().sort('created_at', -1).limit(50))
        
        for tt in timetables:
            tt['_id'] = str(tt['_id'])
        
        return jsonify({'timetables': timetables}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<timetable_id>', methods=['DELETE'])
def delete_timetable(timetable_id):
    """Delete a timetable"""
    try:
        db = get_db()
        result = db.timetables.delete_one({'_id': ObjectId(timetable_id)})
        
        if result.deleted_count == 0:
            return jsonify({'error': 'Timetable not found'}), 404
        
        return jsonify({'message': 'Timetable deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/generate/faculty', methods=['POST'])
@require_auth
@require_role('scheduler')
def generate_faculty_timetable():
    """
    Generate timetable for a specific faculty and term
    
    Request body:
    {
        "term": 1,
        "faculty": "ICT",  # or "Business", "Engineering", etc.
        "academic_year": "2024-2025",  # Optional, defaults to current
        "regenerate": false  # If true, deletes existing assignments first
    }
    """
    try:
        data = request.get_json()
        term = data.get('term')
        faculty = data.get('faculty')
        academic_year = data.get('academic_year')
        regenerate = data.get('regenerate', False)
        
        if term not in [1, 2]:
            return jsonify({'error': 'Term must be 1 or 2'}), 400
        
        if not faculty:
            return jsonify({'error': 'Faculty is required'}), 400
        
        # Validate time slots (same validation as main generation)
        db = get_db()
        time_slots_count = db.time_slots.count_documents({})
        if time_slots_count == 0:
            from seed_config_data import seed_time_slots_to_db
            try:
                seed_time_slots_to_db(db)
                from app.services.config_loader import invalidate_config_cache
                invalidate_config_cache()
            except Exception as seed_error:
                return jsonify({
                    'error': 'No time slots configured. Please seed time slots first.'
                }), 500
        
        # Run generation in background (similar to main generation)
        import subprocess
        import sys
        from pathlib import Path
        
        current_file = Path(__file__).resolve()
        backend_dir = current_file.parent.parent.parent.parent
        script_path = backend_dir / 'generate_faculty_timetable.py'
        
        cmd = [sys.executable, str(script_path), '--term', str(term), '--faculty', faculty]
        if academic_year:
            cmd.extend(['--academic-year', academic_year])
        if regenerate:
            cmd.append('--regenerate')
        
        # Run in background
        process = subprocess.Popen(
            cmd,
            cwd=str(backend_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        return jsonify({
            'success': True,
            'message': f'Timetable generation started for {faculty}',
            'faculty': faculty,
            'term': term,
            'process_id': process.pid
        }), 202
        
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        return jsonify({
            'error': str(e),
            'traceback': error_traceback
        }), 500


@bp.route('/generate/all-faculties', methods=['POST'])
@require_auth
@require_role('scheduler')
def generate_all_faculties_timetable():
    """
    Generate timetables for all faculties sequentially
    
    Request body:
    {
        "term": 1,
        "academic_year": "2024-2025",
        "faculties": ["ICT", "Business", "Engineering", "Arts", "Science"]  # Optional
    }
    """
    try:
        data = request.get_json()
        term = data.get('term')
        academic_year = data.get('academic_year')
        faculties = data.get('faculties')
        
        if term not in [1, 2]:
            return jsonify({'error': 'Term must be 1 or 2'}), 400
        
        # Get all faculties if not provided
        if not faculties:
            db = get_db()
            faculties_data = db.programs.distinct('faculty')
            faculties = [f for f in faculties_data if f]  # Filter out None values
            if not faculties:
                return jsonify({
                    'error': 'No faculties found. Please add faculty field to programs first.'
                }), 400
        
        # Run generation sequentially (in background)
        import subprocess
        import sys
        from pathlib import Path
        
        current_file = Path(__file__).resolve()
        backend_dir = current_file.parent.parent.parent.parent
        script_path = backend_dir / 'generate_faculty_timetable.py'
        
        results = []
        for faculty in faculties:
            cmd = [sys.executable, str(script_path), '--term', str(term), '--faculty', faculty]
            if academic_year:
                cmd.extend(['--academic-year', academic_year])
            
            process = subprocess.Popen(
                cmd,
                cwd=str(backend_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            results.append({
                'faculty': faculty,
                'process_id': process.pid,
                'status': 'started'
            })
        
        return jsonify({
            'success': True,
            'message': f'Started generation for {len(faculties)} faculties',
            'faculties': faculties,
            'term': term,
            'results': results
        }), 202
        
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@bp.route('/resources/availability', methods=['GET'])
@require_auth
def get_resource_availability():
    """
    Get resource availability information
    
    Query parameters:
    - term: Term number (1 or 2)
    - resource_type: 'room' or 'lecturer'
    - resource_id: Resource identifier
    - academic_year: Academic year (optional)
    """
    try:
        term = request.args.get('term')
        resource_type = request.args.get('resource_type')
        resource_id = request.args.get('resource_id')
        academic_year = request.args.get('academic_year')
        
        if not term or term not in ['1', '2']:
            return jsonify({'error': 'Term is required and must be 1 or 2'}), 400
        
        if not resource_type or resource_type not in ['room', 'lecturer']:
            return jsonify({'error': 'resource_type must be "room" or "lecturer"'}), 400
        
        if not resource_id:
            return jsonify({'error': 'resource_id is required'}), 400
        
        from app.services.resource_booking import ResourceBookingManager
        db = get_db()
        booking_manager = ResourceBookingManager(db, f"Term{term}", academic_year)
        
        availability = booking_manager.get_resource_availability(resource_type, resource_id)
        
        return jsonify({
            'success': True,
            'availability': availability
        }), 200
        
    except ConnectionError as e:
        return jsonify({"error": "Database Connection Error", "message": str(e)}), 503
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500