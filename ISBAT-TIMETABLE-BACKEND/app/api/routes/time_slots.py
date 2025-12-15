"""API routes for time slots."""

from flask import Blueprint, request, jsonify
from app import get_db
from app.models.time_slot import TimeSlot
from app.middleware.auth import require_auth
from bson import ObjectId
import traceback

bp = Blueprint('time_slots', __name__, url_prefix='/api/time-slots')

@bp.route('/', methods=['GET'])
def get_time_slots():
    """Get all time slots"""
    try:
        db = get_db()
        time_slots = list(db.time_slots.find().sort('order', 1))
        
        for slot in time_slots:
            slot['_id'] = str(slot['_id'])
        
        return jsonify({'time_slots': time_slots}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<period>', methods=['GET'])
def get_time_slot(period):
    """Get specific time slot"""
    try:
        db = get_db()
        time_slot = db.time_slots.find_one({'period': period})
        
        if not time_slot:
            return jsonify({'error': 'Time slot not found'}), 404
        
        time_slot['_id'] = str(time_slot['_id'])
        return jsonify(time_slot), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/', methods=['POST'])
@require_auth
def create_time_slot():
    """
    Create new time slot
    
    Request body:
    {
        "period": "SLOT_1",
        "start": "09:00",
        "end": "11:00",
        "is_afternoon": false,
        "display_name": "09:00 AM - 11:00 AM",
        "order": 1
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['period', 'start', 'end']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Auto-generate display_name if not provided
        if 'display_name' not in data or not data['display_name']:
            from app.services.config_loader import format_time_for_display
            data['display_name'] = format_time_for_display(data['start'], data['end'])
        
        # Create time slot
        time_slot = TimeSlot.from_dict(data)
        
        db = get_db()
        
        # Check if period already exists
        existing = db.time_slots.find_one({'period': time_slot.period})
        if existing:
            return jsonify({'error': 'Time slot period already exists'}), 409
        
        result = db.time_slots.insert_one(time_slot.to_dict())
        
        # Invalidate cache after creating new time slot
        from app.services.config_loader import invalidate_config_cache
        invalidate_config_cache()
        
        return jsonify({
            'message': 'Time slot created successfully',
            'period': time_slot.period,
            '_id': str(result.inserted_id)
        }), 201
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/<period>', methods=['PUT'])
@require_auth
def update_time_slot(period):
    """Update time slot"""
    try:
        data = request.get_json()
        
        # Don't allow changing the period
        if 'period' in data and data['period'] != period:
            return jsonify({'error': 'Cannot change time slot period'}), 400
        
        # Auto-generate display_name if start/end changed and display_name not explicitly provided
        if ('start' in data or 'end' in data) and 'display_name' not in data:
            # Get current time slot to use existing start/end if not provided
            db = get_db()
            current = db.time_slots.find_one({'period': period})
            if current:
                start = data.get('start', current.get('start'))
                end = data.get('end', current.get('end'))
                from app.services.config_loader import format_time_for_display
                data['display_name'] = format_time_for_display(start, end)
        
        db = get_db()
        result = db.time_slots.update_one(
            {'period': period},
            {'$set': data}
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'Time slot not found'}), 404
        
        # Invalidate cache after updating time slot
        from app.services.config_loader import invalidate_config_cache
        invalidate_config_cache()
        
        return jsonify({'message': 'Time slot updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<period>', methods=['DELETE'])
@require_auth
def delete_time_slot(period):
    """Delete time slot"""
    try:
        db = get_db()
        
        # Check if time slot is being used in any timetable
        # This is a basic check - you might want to check actual timetable data
        result = db.time_slots.delete_one({'period': period})
        
        if result.deleted_count == 0:
            return jsonify({'error': 'Time slot not found'}), 404
        
        # Invalidate cache after deleting time slot
        from app.services.config_loader import invalidate_config_cache
        invalidate_config_cache()
        
        return jsonify({'message': 'Time slot deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
