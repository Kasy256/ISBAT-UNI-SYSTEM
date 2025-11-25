"""Room management routes."""

from flask import Blueprint, request, jsonify
from app import get_db
from app.models.room import Room
from app.middleware.auth import require_auth, require_role

bp = Blueprint('rooms', __name__, url_prefix='/api/rooms')


@bp.route('/', methods=['GET'])
@require_auth
def get_rooms():
    """
    Get all rooms
    
    Query parameters:
    - room_type: Filter by room type (Theory, Lab)
    - min_capacity: Minimum capacity
    - available: Filter by availability (true/false)
    """
    try:
        db = get_db()
        
        # Build query from parameters
        query = {}
        
        room_type = request.args.get('room_type')
        if room_type:
            query['room_type'] = room_type
        
        min_capacity = request.args.get('min_capacity', type=int)
        if min_capacity:
            query['capacity'] = {'$gte': min_capacity}
        
        available = request.args.get('available')
        if available is not None:
            query['is_available'] = available.lower() == 'true'
        
        rooms = list(db.rooms.find(query))
        
        for room in rooms:
            room['_id'] = str(room['_id'])
        
        return jsonify({
            'success': True,
            'count': len(rooms),
            'rooms': rooms
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<room_id>', methods=['GET'])
@require_auth
def get_room(room_id):
    """Get specific room by ID"""
    try:
        db = get_db()
        room = db.rooms.find_one({'id': room_id})
        
        if not room:
            return jsonify({'error': 'Room not found'}), 404
        
        room['_id'] = str(room['_id'])
        return jsonify({
            'success': True,
            'room': room
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/', methods=['POST'])
@require_role('scheduler')
def create_room():
    """
    Create new room
    
    Request body:
    {
        "id": "R001",
        "room_number": "L201",
        "capacity": 60,
        "room_type": "Theory",
        "is_available": true
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['id', 'room_number', 'capacity', 'room_type']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate capacity
        if data['capacity'] <= 0:
            return jsonify({'error': 'Capacity must be greater than 0'}), 400
        
        # Validate room type
        valid_types = ['Theory', 'Lab']
        if data['room_type'] not in valid_types:
            return jsonify({
                'error': f'Invalid room type. Must be one of: {", ".join(valid_types)}'
            }), 400
        
        room = Room.from_dict(data)
        
        db = get_db()
        
        # Check if ID already exists
        existing = db.rooms.find_one({'id': room.id})
        if existing:
            return jsonify({'error': 'Room ID already exists'}), 409
        
        result = db.rooms.insert_one(room.to_dict())
        
        return jsonify({
            'success': True,
            'message': 'Room created successfully',
            'id': room.id,
            '_id': str(result.inserted_id)
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<room_id>', methods=['PUT'])
@require_role('scheduler')
def update_room(room_id):
    """
    Update room
    
    Request body: Same as create, all fields optional
    """
    try:
        data = request.get_json()
        
        # Validate capacity if provided
        if 'capacity' in data and data['capacity'] <= 0:
            return jsonify({'error': 'Capacity must be greater than 0'}), 400
        
        # Validate room type if provided
        if 'room_type' in data:
            valid_types = ['Theory', 'Lab']
            if data['room_type'] not in valid_types:
                return jsonify({
                    'error': f'Invalid room type. Must be one of: {", ".join(valid_types)}'
                }), 400
        
        db = get_db()
        result = db.rooms.update_one(
            {'id': room_id},
            {'$set': data}
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'Room not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Room updated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<room_id>', methods=['DELETE'])
@require_role('admin')
def delete_room(room_id):
    """Delete room (admin only)"""
    try:
        db = get_db()
        result = db.rooms.delete_one({'id': room_id})
        
        if result.deleted_count == 0:
            return jsonify({'error': 'Room not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Room deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/bulk', methods=['POST'])
@require_role('scheduler')
def bulk_create_rooms():
    """
    Bulk create rooms
    
    Request body:
    {
        "rooms": [
            {...room data...},
            {...room data...}
        ]
    }
    """
    try:
        data = request.get_json()
        rooms_data = data.get('rooms', [])
        
        if not rooms_data:
            return jsonify({'error': 'No rooms provided'}), 400
        
        # Validate all rooms
        for idx, room_data in enumerate(rooms_data):
            required = ['id', 'room_number', 'capacity', 'room_type']
            for field in required:
                if field not in room_data:
                    return jsonify({
                        'error': f'Room {idx}: Missing required field: {field}'
                    }), 400
        
        db = get_db()
        rooms = [Room.from_dict(r).to_dict() for r in rooms_data]
        
        # Check for duplicate IDs in database
        existing_ids = [r['id'] for r in rooms]
        duplicates = list(db.rooms.find({'id': {'$in': existing_ids}}))
        
        if duplicates:
            dup_ids = [d['id'] for d in duplicates]
            return jsonify({
                'error': f'Duplicate room IDs found: {", ".join(dup_ids)}'
            }), 409
        
        result = db.rooms.insert_many(rooms)
        
        return jsonify({
            'success': True,
            'message': f'{len(result.inserted_ids)} rooms created successfully',
            'count': len(result.inserted_ids)
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/search', methods=['POST'])
@require_auth
def search_rooms():
    """
    Advanced room search
    
    Request body:
    {
        "room_type": "Lab",
        "min_capacity": 30,
        "max_capacity": 60
    }
    """
    try:
        criteria = request.get_json()
        
        db = get_db()
        query = {}
        
        if 'room_type' in criteria:
            query['room_type'] = criteria['room_type']
        
        if 'min_capacity' in criteria or 'max_capacity' in criteria:
            query['capacity'] = {}
            if 'min_capacity' in criteria:
                query['capacity']['$gte'] = criteria['min_capacity']
        if 'max_capacity' in criteria:
            query['capacity']['$lte'] = criteria['max_capacity']
        
        if 'is_available' in criteria:
            query['is_available'] = criteria['is_available']
        
        rooms = list(db.rooms.find(query))
        
        for room in rooms:
            room['_id'] = str(room['_id'])
        
        return jsonify({
            'success': True,
            'count': len(rooms),
            'rooms': rooms
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/statistics', methods=['GET'])
@require_auth
def get_room_statistics():
    """Get room statistics"""
    try:
        db = get_db()
        
        # Total rooms
        total_rooms = db.rooms.count_documents({})
        
        # Rooms by type
        pipeline = [
            {'$group': {
                '_id': '$room_type',
                'count': {'$sum': 1},
                'avg_capacity': {'$avg': '$capacity'},
                'total_capacity': {'$sum': '$capacity'}
            }}
        ]
        by_type = list(db.rooms.aggregate(pipeline))
        
        # Capacity statistics
        capacity_stats = list(db.rooms.aggregate([
            {'$group': {
                '_id': None,
                'min_capacity': {'$min': '$capacity'},
                'max_capacity': {'$max': '$capacity'},
                'avg_capacity': {'$avg': '$capacity'},
                'total_capacity': {'$sum': '$capacity'}
            }}
        ]))
        
        # Available vs unavailable
        available_count = db.rooms.count_documents({'is_available': True})
        unavailable_count = db.rooms.count_documents({'is_available': False})
        
        return jsonify({
            'success': True,
            'statistics': {
                'total_rooms': total_rooms,
                'available': available_count,
                'unavailable': unavailable_count,
                'by_type': by_type,
                'capacity': capacity_stats[0] if capacity_stats else {}
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

