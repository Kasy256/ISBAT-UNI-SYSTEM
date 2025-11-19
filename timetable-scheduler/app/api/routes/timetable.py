from flask import Blueprint, request, jsonify
from app import get_db
from app.models.lecturer import Lecturer
from app.models.room import Room
from app.models.course import CourseUnit
from app.models.student import StudentGroup
from app.services.preprocessing.term_splitter import TermSplitter
from app.services.csp.csp_engine import CSPEngine
from app.services.gga.gga_engine import GGAEngine
from app.services.gga.chromosome import Chromosome
from app.middleware.auth import require_auth, require_role
from bson import ObjectId
import traceback

bp = Blueprint('timetable', __name__, url_prefix='/api/timetable')

@bp.route('/generate', methods=['POST'])
@require_auth
@require_role('scheduler')
def generate_timetable():
    """
    Generate timetable for given program and semesters
    
    Request body:
    {
        "program": "BSCAIT",
        "batch": "BSCAIT-126",
        "semesters": ["S1", "S2"],
        "optimize": true
    }
    """
    try:
        data = request.get_json()
        program = data.get('program')
        batch = data.get('batch')
        semesters = data.get('semesters', [])
        optimize = data.get('optimize', True)
        
        if not program or not batch or not semesters:
            return jsonify({'error': 'Missing required fields'}), 400
        
        db = get_db()
        
        # Fetch data from database
        lecturers_data = list(db.lecturers.find())
        rooms_data = list(db.rooms.find())
        course_units_data = list(db.course_units.find())
        student_groups_data = list(db.student_groups.find({
            'batch': batch,
            'program': program,
            'semester': {'$in': semesters}
        }))
        
        if not student_groups_data:
            return jsonify({'error': 'No student groups found for given criteria'}), 404
        
        # Convert to models
        lecturers = [Lecturer.from_dict(l) for l in lecturers_data]
        rooms = [Room.from_dict(r) for r in rooms_data]
        course_units = [CourseUnit.from_dict(cu) for cu in course_units_data]
        student_groups = [StudentGroup.from_dict(sg) for sg in student_groups_data]
        
        print(f"Loaded: {len(lecturers)} lecturers, {len(rooms)} rooms, "
              f"{len(course_units)} course units, {len(student_groups)} student groups")
        
        # Step 1: Term Splitting
        print("\n=== STEP 1: TERM SPLITTING ===")
        term_splitter = TermSplitter()
        term_splits = {}
        
        for semester in semesters:
            # Get course units for this semester
            semester_units = [
                cu for cu in course_units 
                if any(sg.semester == semester and cu.id in sg.course_units for sg in student_groups)
            ]
            
            if semester_units:
                try:
                    term1, term2 = term_splitter.split_semester(semester, semester_units)
                    term_splits[semester] = {'term1': term1, 'term2': term2}
                    print(f"{semester}: T1={len(term1.assigned_units)} units, T2={len(term2.assigned_units)} units")
                except Exception as e:
                    print(f"Term split error for {semester}: {str(e)}")
                    continue
        
        # Step 2: CSP Scheduling
        print("\n=== STEP 2: CSP SCHEDULING ===")
        csp_engine = CSPEngine()
        csp_engine.initialize(lecturers, rooms, course_units, student_groups)
        
        csp_solution = csp_engine.solve()
        
        if not csp_solution:
            return jsonify({
                'error': 'Failed to generate valid timetable',
                'message': 'CSP could not find a solution. Try relaxing constraints or adding resources.'
            }), 500
        
        csp_result = csp_engine.get_solution()
        print(f"CSP generated {csp_result['statistics']['total_sessions']} sessions")
        
        # Step 3: GGA Optimization (if requested)
        final_result = csp_result
        
        if optimize:
            print("\n=== STEP 3: GGA OPTIMIZATION ===")
            
            # Create chromosome from CSP solution
            initial_chromosome = Chromosome.from_csp_solution(csp_solution)
            
            # Initialize GGA
            gga_engine = GGAEngine(
                {cu.id: cu for cu in course_units},
                {sg.id: sg for sg in student_groups},
                {l.id: l for l in lecturers},
                {r.id: r for r in rooms}
            )
            
            # Optimize
            optimized_chromosome = gga_engine.optimize(initial_chromosome)
            
            # Convert back to timetable format
            optimized_timetable = {}
            for gene in optimized_chromosome.genes:
                sg_id = gene.student_group_id
                if sg_id not in optimized_timetable:
                    optimized_timetable[sg_id] = []
                
                course_unit = next((cu for cu in course_units if cu.id == gene.course_unit_id), None)
                lecturer = next((l for l in lecturers if l.id == gene.lecturer_id), None)
                room = next((r for r in rooms if r.id == gene.room_id), None)
                
                session = {
                    'session_id': gene.session_id,
                    'course_unit': {
                        'id': course_unit.id,
                        'code': course_unit.code,
                        'name': course_unit.name,
                        'is_lab': course_unit.is_lab
                    } if course_unit else {},
                    'lecturer': {
                        'id': lecturer.id,
                        'name': lecturer.name
                    } if lecturer else {},
                    'room': {
                        'id': room.id,
                        'number': room.room_number,
                        'capacity': room.capacity,
                        'type': room.room_type
                    } if room else {},
                    'time_slot': gene.time_slot,
                    'term': gene.term,
                    'session_number': gene.session_number
                }
                optimized_timetable[sg_id].append(session)
            
            gga_report = gga_engine.get_optimization_report()
            
            final_result = {
                'success': True,
                'timetable': optimized_timetable,
                'statistics': {
                    'total_sessions': len(optimized_chromosome.genes),
                    'csp_time': csp_result['statistics']['time_elapsed'],
                    'gga_time': gga_report['time_elapsed'],
                    'total_time': csp_result['statistics']['time_elapsed'] + gga_report['time_elapsed'],
                    'fitness': {
                        'overall': optimized_chromosome.fitness.overall_fitness if optimized_chromosome.fitness else 0,
                        'breakdown': gga_report['fitness_breakdown']
                    }
                },
                'optimization': gga_report
            }
        
        # Save to database
        timetable_doc = {
            'program': program,
            'batch': batch,
            'semesters': semesters,
            'timetable': final_result['timetable'],
            'statistics': final_result['statistics'],
            'optimized': optimize,
            'created_at': None
        }
        
        from datetime import datetime
        timetable_doc['created_at'] = datetime.utcnow()
        
        result = db.timetables.insert_one(timetable_doc)
        final_result['timetable_id'] = str(result.inserted_id)
        
        return jsonify(final_result), 200
        
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