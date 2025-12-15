from flask import Blueprint, request, jsonify
from app import get_db
from app.models.subject import CourseUnit

bp = Blueprint('subjects', __name__, url_prefix='/api/subjects')

@bp.route('/', methods=['GET'])
def get_courses():
    """Get all subjects"""
    try:
        db = get_db()
        subjects = list(db.course_units.find())
        
        for subject in subjects:
            subject['_id'] = str(subject['_id'])
        
        return jsonify({'subjects': subjects}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<course_id>', methods=['GET'])
def get_course(course_id):
    """Get specific subject"""
    try:
        db = get_db()
        subject = db.course_units.find_one({'id': course_id})
        
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
        
        subject['_id'] = str(subject['_id'])
        return jsonify(subject), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/', methods=['POST'])
def create_course():
    """Create new subject - uses code as primary key (id)"""
    try:
        data = request.get_json()
        
        # Code is required and will be used as id
        required = ['code', 'name', 'weekly_hours']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Use code as id if id is not provided
        if 'id' not in data or not data['id']:
            data['id'] = data['code']
        
        # preferred_room_type is required
        if 'preferred_room_type' not in data or data['preferred_room_type'] is None:
            # Backward compatibility: derive from is_lab if available
            if 'is_lab' in data:
                data['preferred_room_type'] = "Lab" if data['is_lab'] else "Theory"
            else:
                return jsonify({'error': 'Missing required field: preferred_room_type'}), 400
        
        subject = CourseUnit.from_dict(data)
        
        db = get_db()
        # Check if subject with this code/id already exists
        existing = db.course_units.find_one({'id': subject.id})
        if existing:
            return jsonify({'error': f'Subject with code "{subject.code}" already exists'}), 409
        
        result = db.course_units.insert_one(subject.to_dict())
        
        return jsonify({
            'message': 'Subject created successfully',
            'id': subject.id,
            'code': subject.code,
            '_id': str(result.inserted_id)
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<course_id>', methods=['PUT'])
def update_course(course_id):
    """Update subject - course_id is the code"""
    try:
        data = request.get_json()
        
        # Prevent changing the code/id if it's in the update data
        if 'code' in data:
            # If code is being changed, update the id as well
            if data['code'] != course_id:
                # Check if new code already exists
                db = get_db()
                existing = db.course_units.find_one({'id': data['code']})
                if existing and existing.get('id') != course_id:
                    return jsonify({'error': f'Subject with code "{data["code"]}" already exists'}), 409
                # Update id to match new code
                data['id'] = data['code']
        
        db = get_db()
        result = db.course_units.update_one(
            {'id': course_id},
            {'$set': data}
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'Subject not found'}), 404
        
        return jsonify({'message': 'Subject updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<course_id>', methods=['DELETE'])
def delete_course(course_id):
    """Delete subject"""
    try:
        db = get_db()
        result = db.course_units.delete_one({'id': course_id})
        
        if result.deleted_count == 0:
            return jsonify({'error': 'Subject not found'}), 404
        
        return jsonify({'message': 'Subject deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/bulk', methods=['POST'])
def bulk_create_courses():
    """Bulk create subjects"""
    try:
        data = request.get_json()
        courses_data = data.get('subjects', [])
        
        if not courses_data:
            return jsonify({'error': 'No subjects provided'}), 400
        
        db = get_db()
        subjects = [CourseUnit.from_dict(c).to_dict() for c in courses_data]
        
        result = db.course_units.insert_many(subjects)
        
        return jsonify({
            'message': f'{len(result.inserted_ids)} subjects created successfully',
            'count': len(result.inserted_ids)
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500