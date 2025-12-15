"""API routes for room specializations."""

from flask import Blueprint, request, jsonify
from app import get_db
from app.models.room_specialization import RoomSpecialization
from app.middleware.auth import require_auth
from bson import ObjectId
import traceback

bp = Blueprint('room_specializations', __name__, url_prefix='/api/room-specializations')

@bp.route('/', methods=['GET'])
def get_room_specializations():
    """Get all room specializations"""
    try:
        db = get_db()
        specializations = list(db.room_specializations.find().sort('name', 1))
        
        for spec in specializations:
            spec['_id'] = str(spec['_id'])
        
        return jsonify({'room_specializations': specializations}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<spec_id>', methods=['GET'])
def get_room_specialization(spec_id):
    """Get specific room specialization"""
    try:
        db = get_db()
        specialization = db.room_specializations.find_one({'id': spec_id})
        
        if not specialization:
            return jsonify({'error': 'Room specialization not found'}), 404
        
        specialization['_id'] = str(specialization['_id'])
        return jsonify(specialization), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/', methods=['POST'])
@require_auth
def create_room_specialization():
    """
    Create new room specialization
    
    Request body:
    {
        "id": "ICT",
        "name": "ICT",
        "description": "Information and Communication Technology"
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['id', 'name']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create specialization
        specialization = RoomSpecialization.from_dict(data)
        
        db = get_db()
        
        # Check if ID already exists
        existing = db.room_specializations.find_one({'id': specialization.id})
        if existing:
            return jsonify({'error': 'Room specialization ID already exists'}), 409
        
        result = db.room_specializations.insert_one(specialization.to_dict())
        
        # Invalidate cache after creating new specialization
        from app.services.config_loader import invalidate_config_cache
        invalidate_config_cache()
        
        return jsonify({
            'message': 'Room specialization created successfully',
            'id': specialization.id,
            '_id': str(result.inserted_id)
        }), 201
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/<spec_id>', methods=['PUT'])
@require_auth
def update_room_specialization(spec_id):
    """Update room specialization"""
    try:
        data = request.get_json()
        
        # Don't allow changing the ID
        if 'id' in data and data['id'] != spec_id:
            return jsonify({'error': 'Cannot change room specialization ID'}), 400
        
        db = get_db()
        result = db.room_specializations.update_one(
            {'id': spec_id},
            {'$set': data}
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'Room specialization not found'}), 404
        
        # Invalidate cache after updating specialization
        from app.services.config_loader import invalidate_config_cache
        invalidate_config_cache()
        
        return jsonify({'message': 'Room specialization updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<spec_id>', methods=['DELETE'])
@require_auth
def delete_room_specialization(spec_id):
    """Delete room specialization"""
    try:
        db = get_db()
        
        # Check if any rooms are using this specialization
        rooms_using = db.rooms.count_documents({'specializations': spec_id})
        if rooms_using > 0:
            return jsonify({
                'error': f'Cannot delete room specialization: {rooms_using} room(s) are using it'
            }), 409
        
        result = db.room_specializations.delete_one({'id': spec_id})
        
        if result.deleted_count == 0:
            return jsonify({'error': 'Room specialization not found'}), 404
        
        # Invalidate cache after deleting specialization
        from app.services.config_loader import invalidate_config_cache
        invalidate_config_cache()
        
        return jsonify({'message': 'Room specialization deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
