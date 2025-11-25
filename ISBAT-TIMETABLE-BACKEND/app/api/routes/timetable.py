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
        
        # Run generation script
        try:
            result = subprocess.run(
                [python_exe, str(generate_script), '--term', str(term)],
                cwd=str(backend_dir),
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=600  # 10 minute timeout
            )
        except subprocess.TimeoutExpired:
            return jsonify({
                'error': 'Timetable generation timed out (exceeded 10 minutes)'
            }), 500
        except Exception as e:
            return jsonify({
                'error': f'Failed to run generation script: {str(e)}',
                'python_exe': python_exe,
                'script_path': str(generate_script)
            }), 500
        
        if result.returncode != 0:
            error_msg = result.stderr or result.stdout or 'No error output'
            print(f"Generation script error:\n{error_msg}")
            return jsonify({
                'error': 'Timetable generation failed',
                'details': error_msg[-2000:] if len(error_msg) > 2000 else error_msg,
                'returncode': result.returncode
            }), 500
        
        # Step 2: Verify constraints by calling verification script
        csv_filename = f'TIMETABLE_TERM{term}_COMPLETE.csv'
        csv_path = backend_dir / csv_filename
        
        if not csv_path.exists():
            return jsonify({
                'error': f'Generated CSV file not found: {csv_filename}',
                'searched_path': str(csv_path),
                'generation_output': result.stdout[-1000:] if result.stdout else 'No output',
                'generation_stderr': result.stderr[-1000:] if result.stderr else 'No error output'
            }), 500
        
        print(f"\n{'='*70}")
        print(f"Verifying Timetable Constraints")
        print(f"CSV file: {csv_path}")
        print(f"{'='*70}\n")
        
        verify_script = backend_dir / 'verify_timetable_constraints.py'
        violations_file = backend_dir / f'violations_term{term}.json'
        
        if not verify_script.exists():
            print(f"Warning: Verification script not found at {verify_script}, skipping verification")
            violations_data = None
        else:
            # Run verification script
            try:
                verify_result = subprocess.run(
                    [python_exe, str(verify_script), str(csv_path), '--export', str(violations_file)],
                    cwd=str(backend_dir),
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    timeout=300  # 5 minute timeout
                )
            except subprocess.TimeoutExpired:
                print("Warning: Verification script timed out")
                violations_data = None
            except Exception as e:
                print(f"Warning: Verification script failed: {e}")
                violations_data = None
            else:
                # Load violations if file exists (verification may have failed but still created file)
                if violations_file.exists():
                    try:
                        with open(violations_file, 'r', encoding='utf-8') as f:
                            violations_data = json.load(f)
                    except Exception as e:
                        print(f"Warning: Could not load violations file: {e}")
                        violations_data = None
                else:
                    violations_data = None
        
        # Step 3: Parse CSV and save to database
        import csv
        db = get_db()
        
        # Parse the CSV file
        timetable_data = {}
        sessions_list = []
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                student_group = row.get('Student_Group', '')
                if not student_group:
                    continue
                
                # Organize by student group
                if student_group not in timetable_data:
                    timetable_data[student_group] = []
                
                # Map time slot to period identifier
                start_time = row.get('Start_Time', '')
                end_time = row.get('End_Time', '')
                period = ''
                if start_time == '09:00' and end_time == '11:00':
                    period = 'SLOT_1'
                elif start_time == '11:00' and end_time == '13:00':
                    period = 'SLOT_2'
                elif start_time == '14:00' and end_time == '16:00':
                    period = 'SLOT_3'
                elif start_time == '16:00' and end_time == '18:00':
                    period = 'SLOT_4'
                
                # Parse student group to extract program and semester
                student_group_name = row.get('Student_Group', '')
                program = ''
                semester = row.get('Semester', '')
                
                # Extract program from student group name
                if student_group_name:
                    # Format: BSCAIT_BSCAIT-126_S1_None or BCS_BCS-126_S1_None
                    parts = student_group_name.split('_')
                    if len(parts) > 0:
                        program_raw = parts[0]  # BSCAIT or BCS
                        # Map BSCAIT to BIT, keep BCS as is
                        if program_raw == 'BSCAIT':
                            program = 'BIT'
                        elif program_raw == 'BCS':
                            program = 'BCS'
                        else:
                            program = program_raw
                
                # Ensure semester is in correct format (S1, S2, etc.)
                if semester:
                    # Make sure it starts with S and is uppercase
                    if not semester.upper().startswith('S'):
                        semester = f'S{semester}'
                    else:
                        semester = semester.upper()
                elif student_group_name:
                    # Fallback: extract from group name if not in CSV
                    parts = student_group_name.split('_')
                    for part in parts:
                        if part.startswith('S') and len(part) == 2:
                            semester = part.upper()
                            break
                
                session = {
                    'session_id': row.get('Session_ID', ''),
                    'course_unit': {
                        'id': row.get('Course_Code', ''),
                        'code': row.get('Course_Code', ''),
                        'name': row.get('Course_Name', ''),
                        'preferred_room_type': row.get('Course_Type', 'Theory'),
                        'credits': int(row.get('Credits', 0)) if row.get('Credits') else 0
                    },
                    'lecturer': {
                        'id': row.get('Lecturer_ID', ''),
                        'name': row.get('Lecturer_Name', ''),
                        'role': row.get('Lecturer_Role', '')
                    },
                    'room': {
                        'id': row.get('Room_Number', ''),
                        'number': row.get('Room_Number', ''),
                        'capacity': int(row.get('Room_Capacity', 0)) if row.get('Room_Capacity') else 0,
                        'type': row.get('Room_Type', 'Theory'),
                        'campus': row.get('Room_Campus', 'N/A')
                    },
                    'time_slot': {
                        'day': row.get('Day', ''),
                        'period': period,
                        'start': start_time,
                        'end': end_time,
                        'time_slot': row.get('Time_Slot', f'{start_time}-{end_time}')
                    },
                    'term': row.get('Term', f'Term{term}'),
                    'semester': semester,
                    'program': program,
                    'student_group_name': student_group_name,
                    'group_size': int(row.get('Group_Size', 0)) if row.get('Group_Size') else 0,
                    'session_number': 1
                }
                
                timetable_data[student_group].append(session)
                sessions_list.append(session)
        
        # Save to database
        timetable_doc = {
            'term': f'Term{term}',
            'timetable': timetable_data,
            'statistics': {
                'total_sessions': len(sessions_list),
                'student_groups': len(timetable_data),
                'generated_at': datetime.utcnow().isoformat()
            },
            'optimized': True,  # GGA optimization is part of the script
            'created_at': datetime.utcnow()
        }
        
        # Save to database (rename to avoid conflict with subprocess result)
        db_result = db.timetables.insert_one(timetable_doc)
        timetable_doc['_id'] = str(db_result.inserted_id)
        
        # Add verification results to timetable document
        if violations_data:
            db.timetables.update_one(
                {'_id': ObjectId(timetable_doc['_id'])},
                {'$set': {
                    'verification': violations_data,
                    'verified_at': datetime.utcnow()
                }}
            )
            timetable_doc['verification'] = violations_data
        
        # Get verification output if available
        verification_output = ''
        if 'verify_result' in locals() and hasattr(verify_result, 'stdout'):
            verification_output = verify_result.stdout[-1000:] if verify_result.stdout else ''
        
        return jsonify({
            'success': True,
            'timetable_id': timetable_doc['_id'],
            'timetable': timetable_doc,
            'verification': violations_data,
            'generation_output': result.stdout[-1000:] if result.stdout else '',
            'verification_output': verification_output
        }), 200
        
    except Exception as e:
        print(f"Error generating timetable: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@bp.route('/<timetable_id>', methods=['GET'])
def get_timetable(timetable_id):
    """Get specific timetable by ID"""
    try:
        db = get_db()
        timetable = db.timetables.find_one({'_id': ObjectId(timetable_id)})
        
        if not timetable:
            return jsonify({'error': 'Timetable not found'}), 404
        
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