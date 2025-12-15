"""API routes for canonical subject groups."""

from flask import Blueprint, request, jsonify
from datetime import datetime
from app import get_db
from app.models.canonical_course_group import CanonicalCourseGroup

bp = Blueprint('canonical_groups', __name__, url_prefix='/api/canonical-groups')


@bp.route('/', methods=['GET'])
def get_canonical_groups():
    """Get all canonical subject groups"""
    try:
        db = get_db()
        groups = list(db.canonical_course_groups.find())
        
        for group in groups:
            group['_id'] = str(group['_id'])
        
        return jsonify({'canonical_groups': groups}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<canonical_id>', methods=['GET'])
def get_canonical_group(canonical_id: str):
    """Get specific canonical subject group"""
    try:
        db = get_db()
        group = db.canonical_course_groups.find_one({'canonical_id': canonical_id})
        
        if not group:
            return jsonify({'error': 'Canonical group not found'}), 404
        
        group['_id'] = str(group['_id'])
        return jsonify(group), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/', methods=['POST'])
def create_canonical_group():
    """Create new canonical subject group"""
    try:
        data = request.get_json()
        
        required = ['canonical_id', 'name', 'course_codes']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate course_codes is a list
        if not isinstance(data['course_codes'], list):
            return jsonify({'error': 'course_codes must be a list'}), 400
        
        if len(data['course_codes']) == 0:
            return jsonify({'error': 'course_codes cannot be empty'}), 400
        
        group = CanonicalCourseGroup(
            canonical_id=data['canonical_id'],
            name=data['name'],
            course_codes=data['course_codes'],
            description=data.get('description'),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by=data.get('created_by')
        )
        
        db = get_db()
        existing = db.canonical_course_groups.find_one({'canonical_id': group.canonical_id})
        if existing:
            return jsonify({'error': 'Canonical ID already exists'}), 409
        
        result = db.canonical_course_groups.insert_one(group.to_dict())
        
        return jsonify({
            'message': 'Canonical group created successfully',
            'canonical_id': group.canonical_id,
            '_id': str(result.inserted_id)
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<canonical_id>', methods=['PUT'])
def update_canonical_group(canonical_id: str):
    """Update canonical subject group"""
    try:
        data = request.get_json()
        
        db = get_db()
        
        # Update updated_at timestamp
        data['updated_at'] = datetime.now()
        
        result = db.canonical_course_groups.update_one(
            {'canonical_id': canonical_id},
            {'$set': data}
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'Canonical group not found'}), 404
        
        return jsonify({'message': 'Canonical group updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<canonical_id>', methods=['DELETE'])
def delete_canonical_group(canonical_id: str):
    """Delete canonical subject group"""
    try:
        db = get_db()
        result = db.canonical_course_groups.delete_one({'canonical_id': canonical_id})
        
        if result.deleted_count == 0:
            return jsonify({'error': 'Canonical group not found'}), 404
        
        return jsonify({'message': 'Canonical group deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<canonical_id>/subjects', methods=['GET'])
def get_courses_in_group(canonical_id: str):
    """Get all subjects in a canonical group"""
    try:
        db = get_db()
        group = db.canonical_course_groups.find_one({'canonical_id': canonical_id})
        
        if not group:
            return jsonify({'error': 'Canonical group not found'}), 404
        
        # Get subject details for all subject codes in the group
        course_codes = group.get('course_codes', [])
        subjects = list(db.course_units.find({'code': {'$in': course_codes}}))
        
        for subject in subjects:
            subject['_id'] = str(subject['_id'])
        
        return jsonify({
            'canonical_id': canonical_id,
            'name': group.get('name'),
            'subjects': subjects
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

