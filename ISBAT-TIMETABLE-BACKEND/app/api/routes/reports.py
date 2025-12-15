from flask import Blueprint, request, jsonify
from app import get_db
from app.middleware.auth import require_auth
from bson import ObjectId

bp = Blueprint('reports', __name__, url_prefix='/api/reports')

DAYS = ["MON", "TUE", "WED", "THU", "FRI"]


@bp.route('/<timetable_id>/lecturer-workload', methods=['GET'])
@require_auth
def get_lecturer_workload(timetable_id):
    """
    Get lecturer workload report for a specific timetable
    
    Returns workload by day for each lecturer
    """
    try:
        db = get_db()
        timetable = db.timetables.find_one({'_id': ObjectId(timetable_id)})
        
        if not timetable:
            return jsonify({'error': 'Timetable not found'}), 404
        
        timetable_data = timetable.get('timetable', {})
        
        # Process lecturer workload
        workload = {}
        
        # Extract all sessions
        for program_id, group_sessions in timetable_data.items():
            if isinstance(group_sessions, list):
                for session in group_sessions:
                    lecturer_id = session.get('lecturer', {}).get('id') or session.get('lecturer', {}).get('name') or 'Unknown'
                    lecturer_name = session.get('lecturer', {}).get('name') or lecturer_id
                    day = session.get('time_slot', {}).get('day')
                    
                    if not day:
                        continue
                    
                    if lecturer_id not in workload:
                        workload[lecturer_id] = {
                            'id': lecturer_id,
                            'name': lecturer_name,
                            'days': {day: 0 for day in DAYS},
                            'total': 0
                        }
                    
                    if day in workload[lecturer_id]['days']:
                        workload[lecturer_id]['days'][day] += 1
                        workload[lecturer_id]['total'] += 1
        
        # Convert to list and sort by total
        workload_list = sorted(workload.values(), key=lambda x: x['total'], reverse=True)
        
        return jsonify({
            'timetable_id': timetable_id,
            'timetable_term': timetable.get('term', 'N/A'),
            'lecturer_workload': workload_list
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<timetable_id>/room-utilization', methods=['GET'])
@require_auth
def get_room_utilization(timetable_id):
    """
    Get room utilization report for a specific timetable
    
    Returns utilization by day for each room
    """
    try:
        db = get_db()
        timetable = db.timetables.find_one({'_id': ObjectId(timetable_id)})
        
        if not timetable:
            return jsonify({'error': 'Timetable not found'}), 404
        
        timetable_data = timetable.get('timetable', {})
        
        # Process room utilization
        utilization = {}
        
        # Extract all sessions
        for program_id, group_sessions in timetable_data.items():
            if isinstance(group_sessions, list):
                for session in group_sessions:
                    room_number = session.get('room', {}).get('room_number') or session.get('room', {}).get('number') or 'Unknown'
                    room_name = room_number
                    room_type = session.get('room', {}).get('type', 'N/A')
                    room_capacity = session.get('room', {}).get('capacity', 0)
                    day = session.get('time_slot', {}).get('day')
                    
                    if not day:
                        continue
                    
                    if room_number not in utilization:
                        utilization[room_number] = {
                            'room_number': room_number,
                            'name': room_name,
                            'type': room_type,
                            'capacity': room_capacity,
                            'days': {day: 0 for day in DAYS},
                            'total': 0
                        }
                    
                    if day in utilization[room_number]['days']:
                        utilization[room_number]['days'][day] += 1
                        utilization[room_number]['total'] += 1
        
        # Convert to list and sort by total
        utilization_list = sorted(utilization.values(), key=lambda x: x['total'], reverse=True)
        
        return jsonify({
            'timetable_id': timetable_id,
            'timetable_term': timetable.get('term', 'N/A'),
            'room_utilization': utilization_list
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<timetable_id>', methods=['GET'])
@require_auth
def get_reports(timetable_id):
    """
    Get all reports for a specific timetable
    
    Returns both lecturer workload and room utilization
    """
    try:
        db = get_db()
        timetable = db.timetables.find_one({'_id': ObjectId(timetable_id)})
        
        if not timetable:
            return jsonify({'error': 'Timetable not found'}), 404
        
        timetable_data = timetable.get('timetable', {})
        
        # Process lecturer workload
        workload = {}
        utilization = {}
        
        # Extract all sessions
        for program_id, group_sessions in timetable_data.items():
            if isinstance(group_sessions, list):
                for session in group_sessions:
                    # Lecturer workload
                    lecturer_id = session.get('lecturer', {}).get('id') or session.get('lecturer', {}).get('name') or 'Unknown'
                    lecturer_name = session.get('lecturer', {}).get('name') or lecturer_id
                    day = session.get('time_slot', {}).get('day')
                    
                    if day:
                        if lecturer_id not in workload:
                            workload[lecturer_id] = {
                                'id': lecturer_id,
                                'name': lecturer_name,
                                'days': {day: 0 for day in DAYS},
                                'total': 0
                            }
                        
                        if day in workload[lecturer_id]['days']:
                            workload[lecturer_id]['days'][day] += 1
                            workload[lecturer_id]['total'] += 1
                    
                    # Room utilization
                    room_number = session.get('room', {}).get('room_number') or session.get('room', {}).get('number') or 'Unknown'
                    room_name = room_number
                    room_type = session.get('room', {}).get('type', 'N/A')
                    room_capacity = session.get('room', {}).get('capacity', 0)
                    
                    if day:
                        if room_number not in utilization:
                            utilization[room_number] = {
                                'room_number': room_number,
                                'name': room_name,
                                'type': room_type,
                                'capacity': room_capacity,
                                'days': {day: 0 for day in DAYS},
                                'total': 0
                            }
                        
                        if day in utilization[room_number]['days']:
                            utilization[room_number]['days'][day] += 1
                            utilization[room_number]['total'] += 1
        
        # Convert to lists and sort
        workload_list = sorted(workload.values(), key=lambda x: x['total'], reverse=True)
        utilization_list = sorted(utilization.values(), key=lambda x: x['total'], reverse=True)
        
        return jsonify({
            'timetable_id': timetable_id,
            'timetable_term': timetable.get('term', 'N/A'),
            'lecturer_workload': workload_list,
            'room_utilization': utilization_list
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

