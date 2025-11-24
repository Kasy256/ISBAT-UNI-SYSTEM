from flask import Blueprint, request, jsonify
from app import get_db
from app.models.lecturer import Lecturer
from bson import ObjectId

bp = Blueprint('lecturers', __name__, url_prefix='/api/lecturers')

@bp.route('/', methods=['GET'])
def get_lecturers():
    """Get all lecturers"""
    try:
        db = get_db()
        lecturers = list(db.lecturers.find())
        
        for lec in lecturers:
            lec['_id'] = str(lec['_id'])
        
        return jsonify({'lecturers': lecturers}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<lecturer_id>', methods=['GET'])
def get_lecturer(lecturer_id):
    """Get specific lecturer"""
    try:
        db = get_db()
        lecturer = db.lecturers.find_one({'id': lecturer_id})
        
        if not lecturer:
            return jsonify({'error': 'Lecturer not found'}), 404
        
        lecturer['_id'] = str(lecturer['_id'])
        return jsonify(lecturer), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/', methods=['POST'])
def create_lecturer():
    """
    Create new lecturer
    
    Request body:
    {
        "id": "L001",
        "name": "Dr. Jane Doe",
        "role": "Full-Time",
        "faculty": "Computing",
        "specializations": ["CS101", "CS102"],
        "availability": {"MON": ["09:00-11:00"], "TUE": ["14:00-16:00"]},
        "sessions_per_day": 2
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['id', 'name', 'role', 'faculty', 'specializations']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create lecturer
        lecturer = Lecturer.from_dict(data)
        
        db = get_db()
        
        # Check if ID already exists
        existing = db.lecturers.find_one({'id': lecturer.id})
        if existing:
            return jsonify({'error': 'Lecturer ID already exists'}), 409
        
        result = db.lecturers.insert_one(lecturer.to_dict())
        
        return jsonify({
            'message': 'Lecturer created successfully',
            'id': lecturer.id,
            '_id': str(result.inserted_id)
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<lecturer_id>', methods=['PUT'])
def update_lecturer(lecturer_id):
    """Update lecturer"""
    try:
        data = request.get_json()
        
        db = get_db()
        result = db.lecturers.update_one(
            {'id': lecturer_id},
            {'$set': data}
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'Lecturer not found'}), 404
        
        return jsonify({'message': 'Lecturer updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<lecturer_id>', methods=['DELETE'])
def delete_lecturer(lecturer_id):
    """Delete lecturer"""
    try:
        db = get_db()
        result = db.lecturers.delete_one({'id': lecturer_id})
        
        if result.deleted_count == 0:
            return jsonify({'error': 'Lecturer not found'}), 404
        
        return jsonify({'message': 'Lecturer deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/bulk', methods=['POST'])
def bulk_create_lecturers():
    """Bulk create lecturers"""
    try:
        data = request.get_json()
        lecturers_data = data.get('lecturers', [])
        
        if not lecturers_data:
            return jsonify({'error': 'No lecturers provided'}), 400
        
        db = get_db()
        lecturers = [Lecturer.from_dict(l).to_dict() for l in lecturers_data]
        
        result = db.lecturers.insert_many(lecturers)
        
        return jsonify({
            'message': f'{len(result.inserted_ids)} lecturers created successfully',
            'count': len(result.inserted_ids)
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500