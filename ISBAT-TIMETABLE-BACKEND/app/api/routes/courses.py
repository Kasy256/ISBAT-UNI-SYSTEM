from flask import Blueprint, request, jsonify
from app import get_db
from app.models.course import CourseUnit

bp = Blueprint('courses', __name__, url_prefix='/api/courses')

@bp.route('/', methods=['GET'])
def get_courses():
    """Get all course units"""
    try:
        db = get_db()
        courses = list(db.course_units.find())
        
        for course in courses:
            course['_id'] = str(course['_id'])
        
        return jsonify({'courses': courses}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<course_id>', methods=['GET'])
def get_course(course_id):
    """Get specific course unit"""
    try:
        db = get_db()
        course = db.course_units.find_one({'id': course_id})
        
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        course['_id'] = str(course['_id'])
        return jsonify(course), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/', methods=['POST'])
def create_course():
    """Create new course unit"""
    try:
        data = request.get_json()
        
        required = ['id', 'code', 'name', 'weekly_hours']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # preferred_room_type is required
        if 'preferred_room_type' not in data or data['preferred_room_type'] is None:
            # Backward compatibility: derive from is_lab if available
            if 'is_lab' in data:
                data['preferred_room_type'] = "Lab" if data['is_lab'] else "Theory"
            else:
                return jsonify({'error': 'Missing required field: preferred_room_type'}), 400
        
        course = CourseUnit.from_dict(data)
        
        db = get_db()
        existing = db.course_units.find_one({'id': course.id})
        if existing:
            return jsonify({'error': 'Course ID already exists'}), 409
        
        result = db.course_units.insert_one(course.to_dict())
        
        return jsonify({
            'message': 'Course created successfully',
            'id': course.id,
            '_id': str(result.inserted_id)
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<course_id>', methods=['PUT'])
def update_course(course_id):
    """Update course unit"""
    try:
        data = request.get_json()
        
        db = get_db()
        result = db.course_units.update_one(
            {'id': course_id},
            {'$set': data}
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'Course not found'}), 404
        
        return jsonify({'message': 'Course updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<course_id>', methods=['DELETE'])
def delete_course(course_id):
    """Delete course unit"""
    try:
        db = get_db()
        result = db.course_units.delete_one({'id': course_id})
        
        if result.deleted_count == 0:
            return jsonify({'error': 'Course not found'}), 404
        
        return jsonify({'message': 'Course deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/bulk', methods=['POST'])
def bulk_create_courses():
    """Bulk create course units"""
    try:
        data = request.get_json()
        courses_data = data.get('courses', [])
        
        if not courses_data:
            return jsonify({'error': 'No courses provided'}), 400
        
        db = get_db()
        courses = [CourseUnit.from_dict(c).to_dict() for c in courses_data]
        
        result = db.course_units.insert_many(courses)
        
        return jsonify({
            'message': f'{len(result.inserted_ids)} courses created successfully',
            'count': len(result.inserted_ids)
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500