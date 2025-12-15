"""Program management routes."""

from flask import Blueprint, request, jsonify
from app import get_db
from app.models.program import Program
from app.middleware.auth import require_auth, require_role

bp = Blueprint('programs', __name__, url_prefix='/api/programs')


def normalize_program_payload(payload: dict) -> dict:
    """Ensure payload uses the canonical program field name."""
    normalized = dict(payload or {})
    if 'program' not in normalized and 'program_name' in normalized:
        normalized['program'] = normalized['program_name']
    return normalized


@bp.route('/', methods=['GET'])
@require_auth
def get_programs():
    """
    Get all programs
    
    Query parameters:
    - program: Filter by program (BSCAIT, BSCSE, etc.)
    - batch: Filter by batch
    - semester: Filter by semester (S1, S2, etc.)
    - term: Filter by term (Term1, Term2)
    - active: Filter by active status (true/false)
    """
    try:
        db = get_db()
        
        # Build query from parameters
        query = {}
        
        program_name = request.args.get('program_name') or request.args.get('program')
        if program_name:
            query['program'] = program_name
        
        batch = request.args.get('batch')
        if batch:
            query['batch'] = batch
        
        semester = request.args.get('semester')
        if semester:
            query['semester'] = semester
        
        term = request.args.get('term')
        if term:
            query['term'] = term
        
        active = request.args.get('active')
        if active is not None:
            query['is_active'] = active.lower() == 'true'
        
        programs = list(db.programs.find(query))
        
        for program in programs:
            program['_id'] = str(program['_id'])
        
        return jsonify({
            'success': True,
            'count': len(programs),
            'programs': programs
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<program_id>', methods=['GET'])
@require_auth
def get_program(program_id):
    """Get specific program by ID"""
    try:
        db = get_db()
        group = db.programs.find_one({'id': program_id})
        
        if not group:
            return jsonify({'error': 'Program not found'}), 404
        
        group['_id'] = str(group['_id'])
        return jsonify({
            'success': True,
            'program': group
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/', methods=['POST'])
@require_role('scheduler')
def create_program():
    """
    Create new program
    
    Request body:
    {
        "id": "SG_BSCAIT_S126_S1_T1",
        "batch": "BSCAIT-126",
        "program": "BSCAIT",
        "semester": "S1",
        "term": "Term1",
        "size": 45,
        "course_units": ["CS101", "CS102"]
    }
    """
    try:
        data = normalize_program_payload(request.get_json())
        
        # Validate required fields
        required = ['id', 'batch', 'program', 'semester', 'term', 'size']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate size
        if data['size'] <= 0:
                return jsonify({'error': 'Student size must be greater than 0'}), 400
        
        # Validate semester
        valid_semesters = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6']
        if data['semester'] not in valid_semesters:
            return jsonify({
                'error': f'Invalid semester. Must be one of: {", ".join(valid_semesters)}'
            }), 400
        
        # Validate term
        valid_terms = ['Term1', 'Term2']
        if data['term'] not in valid_terms:
            return jsonify({
                'error': f'Invalid term. Must be one of: {", ".join(valid_terms)}'
            }), 400
        
        group = Program.from_dict(data)
        
        db = get_db()
        
        # Check if ID already exists
        existing = db.programs.find_one({'id': group.id})
        if existing:
            return jsonify({'error': 'Program ID already exists'}), 409
        
        result = db.programs.insert_one(group.to_dict())
        
        return jsonify({
            'success': True,
            'message': 'Program created successfully',
            'id': group.id,
            '_id': str(result.inserted_id)
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<program_id>', methods=['PUT'])
@require_role('scheduler')
def update_program(program_id):
    """
    Update program
    
    Request body: Same as create, all fields optional
    """
    try:
        data = normalize_program_payload(request.get_json())
        
        # Validate size if provided
        if 'size' in data and data['size'] <= 0:
            return jsonify({'error': 'Student size must be greater than 0'}), 400
        
        # Validate semester if provided
        if 'semester' in data:
            valid_semesters = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6']
            if data['semester'] not in valid_semesters:
                return jsonify({
                    'error': f'Invalid semester. Must be one of: {", ".join(valid_semesters)}'
                }), 400
        
        # Validate term if provided
        if 'term' in data:
            valid_terms = ['Term1', 'Term2']
            if data['term'] not in valid_terms:
                return jsonify({
                    'error': f'Invalid term. Must be one of: {", ".join(valid_terms)}'
                }), 400
        
        db = get_db()
        result = db.programs.update_one(
            {'id': program_id},
            {'$set': data}
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'Program not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Program updated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<program_id>', methods=['DELETE'])
@require_role('admin')
def delete_program(program_id):
    """Delete program (admin only)"""
    try:
        db = get_db()
        result = db.programs.delete_one({'id': program_id})
        
        if result.deleted_count == 0:
            return jsonify({'error': 'Program not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Program deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/bulk', methods=['POST'])
@require_role('scheduler')
def bulk_create_programs():
    """
    Bulk create programs
    
    Request body:
    {
        "programs": [
            {...group data...},
            {...group data...}
        ]
    }
    """
    try:
        data = request.get_json()
        groups_data = data.get('programs', [])
        
        if not groups_data:
            return jsonify({'error': 'No programs provided'}), 400
        
        # Validate all groups
        for idx, group_data in enumerate(groups_data):
            required = ['id', 'batch', 'program', 'semester', 'term', 'size']
            for field in required:
                if field not in group_data:
                    if field == 'program' and 'program_name' in group_data:
                        continue
                    return jsonify({
                        'error': f'Program {idx}: Missing required field: {field}'
                    }), 400
        
        db = get_db()
        normalized_groups = [normalize_program_payload(g) for g in groups_data]
        groups = [Program.from_dict(g).to_dict() for g in normalized_groups]
        
        # Check for duplicate IDs in database
        existing_ids = [g['id'] for g in groups]
        duplicates = list(db.programs.find({'id': {'$in': existing_ids}}))
        
        if duplicates:
            dup_ids = [d['id'] for d in duplicates]
            return jsonify({
                'error': f'Duplicate program IDs found: {", ".join(dup_ids)}'
            }), 409
        
        result = db.programs.insert_many(groups)
        
        return jsonify({
            'success': True,
            'message': f'{len(result.inserted_ids)} programs created successfully',
            'count': len(result.inserted_ids)
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<program_id>/subjects', methods=['POST'])
@require_role('scheduler')
def add_courses_to_program(program_id):
    """
    Add subjects to program
    
    Request body:
    {
        "course_units": ["CS101", "CS102"]
    }
    """
    try:
        data = request.get_json()
        course_units = data.get('course_units', [])
        
        if not course_units:
            return jsonify({'error': 'No course units provided'}), 400
        
        db = get_db()
        result = db.programs.update_one(
            {'id': program_id},
            {'$addToSet': {'course_units': {'$each': course_units}}}
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'Program not found'}), 404
        
        return jsonify({
            'success': True,
            'message': f'Added {len(course_units)} subject(s) to program'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<program_id>/subjects/<course_id>', methods=['DELETE'])
@require_role('scheduler')
def remove_course_from_program(program_id, course_id):
    """Remove subject from program"""
    try:
        db = get_db()
        result = db.programs.update_one(
            {'id': program_id},
            {'$pull': {'course_units': course_id}}
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'Program not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Subject removed from program'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/search', methods=['POST'])
@require_auth
def search_programs():
    """
    Advanced program search
    
    Request body:
    {
        "program": "BSCAIT",
        "semester": "S1",
        "min_size": 30,
        "max_size": 50,
        "course_units": ["CS101"]
    }
    """
    try:
        criteria = request.get_json() or {}
        
        db = get_db()
        query = {}
        
        program_filter = criteria.get('program') or criteria.get('program_name')
        if program_filter:
            query['program'] = program_filter
        
        if 'batch' in criteria:
            query['batch'] = criteria['batch']
        
        if 'semester' in criteria:
            query['semester'] = criteria['semester']
        
        if 'term' in criteria:
            query['term'] = criteria['term']
        
        if 'min_size' in criteria or 'max_size' in criteria:
            query['size'] = {}
            if 'min_size' in criteria:
                query['size']['$gte'] = criteria['min_size']
            if 'max_size' in criteria:
                query['size']['$lte'] = criteria['max_size']
        
        if 'course_units' in criteria and criteria['course_units']:
            query['course_units'] = {'$all': criteria['course_units']}
        
        if 'is_active' in criteria:
            query['is_active'] = criteria['is_active']
        
        programs = list(db.programs.find(query))
        
        for program in programs:
            program['_id'] = str(program['_id'])
        
        return jsonify({
            'success': True,
            'count': len(programs),
            'programs': programs
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/statistics', methods=['GET'])
@require_auth
def get_program_statistics():
    """Get program statistics"""
    try:
        db = get_db()
        
        # Total programs
        total_programs = db.programs.count_documents({})
        
        # Groups by program
        by_program = list(db.programs.aggregate([
            {'$group': {
                '_id': '$program',
                'count': {'$sum': 1},
                'total_students': {'$sum': '$size'},
                'avg_group_size': {'$avg': '$size'}
            }}
        ]))
        
        # Groups by semester
        by_semester = list(db.programs.aggregate([
            {'$group': {
                '_id': '$semester',
                'count': {'$sum': 1},
                'total_students': {'$sum': '$size'}
            }}
        ]))
        
        # Size statistics
        size_stats = list(db.programs.aggregate([
            {'$group': {
                '_id': None,
                'min_size': {'$min': '$size'},
                'max_size': {'$max': '$size'},
                'avg_size': {'$avg': '$size'},
                'total_students': {'$sum': '$size'}
            }}
        ]))
        
        # Active vs inactive
        active_count = db.programs.count_documents({'is_active': True})
        inactive_count = db.programs.count_documents({'is_active': False})
        
        return jsonify({
            'success': True,
            'statistics': {
                'total_programs': total_programs,
                'total_groups': total_programs,
                'active': active_count,
                'inactive': inactive_count,
                'by_program': by_program,
                'by_semester': by_semester,
                'size_statistics': size_stats[0] if size_stats else {}
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

