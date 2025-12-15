"""
Generate Term-Based Timetable for a Specific Faculty
Uses ResourceBookingManager to prevent conflicts with other faculties
"""

import sys
import io
sys.path.insert(0, '.')

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from pymongo import MongoClient
from datetime import datetime
import csv
from collections import defaultdict

from app.models.lecturer import Lecturer
from app.models.subject import CourseUnit
from app.models.room import Room
from app.models.program import Program
from app.services.preprocessing.term_splitter import TermSplitter
from app.services.preprocessing.canonical_term_planner import build_canonical_term_alignment
from app.services.csp.csp_engine import CSPEngine
from app.services.gga.gga_engine import GGAEngine
from app.config import Config
from app.services.canonical_courses import get_canonical_id, CANONICAL_COURSE_MAPPING
from app.services.resource_booking import ResourceBookingManager
from generate_term_timetable import (
    get_term_courses_for_group,
    merge_equivalent_courses,
    expand_assignment_dicts,
    export_to_csv,
    generate_statistics,
    clean_course_name,
    update_progress
)

PROGRESS_FILE_TEMPLATE = 'timetable_generation_progress_faculty_{}_term{}.json'


def setup_database():
    """Connect to MongoDB"""
    from app.config import Config
    mongo_uri = Config.MONGO_URI
    db_name = Config.MONGO_DB_NAME
    client = MongoClient(
        mongo_uri,
        serverSelectionTimeoutMS=30000,
        connectTimeoutMS=30000,
        socketTimeoutMS=30000,
        maxPoolSize=10,
        retryWrites=True,
        retryReads=True
    )
    db = client[db_name]
    return client, db


def fetch_faculty_data(db, faculty: str):
    """Fetch data for a specific faculty"""
    print(f"\n📥 Loading data for faculty: {faculty}...")
    
    # Load student groups for this faculty
    query = {'is_active': True, 'faculty': faculty}
    student_groups_data = list(db.programs.find(query))
    student_groups = [Program.from_dict(sg) for sg in student_groups_data]
    
    # Load all courses (shared across faculties)
    courses_data = list(db.course_units.find())
    courses = {CourseUnit.from_dict(c).id: CourseUnit.from_dict(c) for c in courses_data}
    
    # Load all lecturers (shared across faculties)
    lecturers_data = list(db.lecturers.find())
    lecturers = {Lecturer.from_dict(l).id: Lecturer.from_dict(l) for l in lecturers_data}
    
    # Load all rooms (shared across faculties)
    rooms_data = list(db.rooms.find())
    rooms = {Room.from_dict(r).id: Room.from_dict(r) for r in rooms_data}
    
    print(f"   ✅ {len(student_groups)} student groups")
    print(f"   ✅ {len(courses)} courses")
    print(f"   ✅ {len(lecturers)} lecturers")
    print(f"   ✅ {len(rooms)} rooms")
    
    return student_groups, courses, lecturers, rooms


def generate_faculty_term_timetable(term_number: int, faculty: str, 
                                    academic_year: str = None,
                                    regenerate: bool = False):
    """
    Generate timetable for a specific faculty and term
    
    Args:
        term_number: Term number (1 or 2)
        faculty: Faculty name (e.g., "ICT", "Business")
        academic_year: Academic year (optional)
        regenerate: If True, deletes existing assignments first
    
    Returns:
        Dictionary with generation results
    """
    start_time = datetime.now()
    
    # Initialize progress
    update_progress(term_number, 0, "Initializing", 
                   f"Starting timetable generation for {faculty}...")
    
    print("\n" + "="*70)
    print(f"   FACULTY: {faculty} - TERM {term_number} TIMETABLE GENERATION")
    print("="*70)
    print(f"\n🎯 Generating timetable for: {faculty} - TERM {term_number}")
    print(f"   Scope: ALL semesters (S1-S6) for {faculty} only\n")
    
    try:
        # Setup
        update_progress(term_number, 5, "Setup", "Connecting to database...")
        client, db = setup_database()
        
        # Initialize resource booking manager
        term_str = f"Term{term_number}"
        booking_manager = ResourceBookingManager(db, term_str, academic_year)
        
        # If regenerating, delete existing assignments for this faculty
        if regenerate:
            update_progress(term_number, 6, "Cleanup", 
                          f"Deleting existing assignments for {faculty}...")
            deleted = booking_manager.delete_faculty_assignments(faculty)
            print(f"   🗑️  Deleted {deleted['assignments_deleted']} assignments and "
                  f"{deleted['bookings_deleted']} bookings for {faculty}")
        
        # Load faculty-specific data
        update_progress(term_number, 10, "Loading Data", 
                       f"Loading data for {faculty}...")
        student_groups, courses, lecturers, rooms = fetch_faculty_data(db, faculty)
        
        if not student_groups:
            print(f"❌ No student groups found for faculty: {faculty}!")
            client.close()
            return {'success': False, 'error': f'No student groups found for {faculty}'}
        
        # Build canonical alignment
        update_progress(term_number, 15, "Canonical Alignment", 
                       "Building canonical course alignment...")
        canonical_alignment, canonical_decisions = build_canonical_term_alignment(
            student_groups, courses
        )
        
        if canonical_alignment:
            print(f"\n🔗 Canonical course alignment:")
            print(f"   • {len(canonical_alignment)} canonical families")
        
        # Process student groups for this term
        update_progress(term_number, 20, "Processing Groups", 
                       "Processing student groups and courses...")
        group_term_entries = []
        
        for student_group in student_groups:
            term_courses = get_term_courses_for_group(
                student_group,
                courses,
                term_number,
                canonical_alignment=canonical_alignment
            )
            
            if term_courses:
                term_student_group = Program.from_dict({
                    **student_group.to_dict(),
                    'term': f'Term{term_number}',
                    'course_units': [c.id for c in term_courses]
                })
                
                group_term_entries.append({
                    'original_group': student_group,
                    'term_group': term_student_group,
                    'term_courses': term_courses
                })
                
                print(f"   ✅ {student_group.display_name}: {len(term_courses)} courses")
        
        if not group_term_entries:
            print(f"\n❌ No student groups have courses for Term {term_number}!")
            client.close()
            return {'success': False, 'error': f'No courses for Term {term_number}'}
        
        # Merge equivalent courses
        update_progress(term_number, 30, "Merging Courses", 
                       "Merging equivalent courses...")
        original_student_groups_dict = {sg.id: sg for sg in student_groups}
        merged_student_groups, merged_course_units, merged_group_details = merge_equivalent_courses(
            group_term_entries,
            term_number,
            courses
        )
        
        print(f"\n📊 Summary:")
        total_sessions_to_schedule = sum(course.sessions_required for course in merged_course_units)
        print(f"   • Student Groups: {len(merged_student_groups)} (merged)")
        print(f"   • Unique Courses: {len(merged_course_units)}")
        print(f"   • Total Sessions to Schedule: {total_sessions_to_schedule}")
        
        # Validate configuration
        update_progress(term_number, 35, "Validation", "Validating configuration...")
        from app.services.config_loader import get_time_slots_for_config
        time_slots_config = get_time_slots_for_config(use_cache=True)
        if not time_slots_config:
            print("   ❌ ERROR: No time slots found in database!")
            client.close()
            return {'success': False, 'error': 'No time slots configured'}
        
        # CSP Solving with resource booking manager
        update_progress(term_number, 40, "CSP Solving", 
                       "Running CSP solver with conflict awareness...")
        print(f"\n{'='*70}")
        print("🧩 Step 1: CSP Engine - Satisfying Hard Constraints")
        print("="*70)
        print(f"   Scheduling {faculty} for Term {term_number}...")
        print(f"   🔒 Using global resource booking to prevent conflicts")
        
        csp_engine = CSPEngine(resource_booking_manager=booking_manager)
        csp_engine.initialize(
            lecturers=list(lecturers.values()),
            rooms=list(rooms.values()),
            course_units=merged_course_units,
            programs=merged_student_groups,
            merged_group_details=merged_group_details,
            faculty=faculty
        )
        
        print("   Running CSP solver...")
        csp_solution = csp_engine.solve()
        update_progress(term_number, 60, "CSP Complete", 
                      f"CSP solver completed: {len(csp_solution) if csp_solution else 0} sessions")
        
        if not csp_solution:
            print("   ❌ CSP failed to find any assignments!")
            client.close()
            return {'success': False, 'error': 'CSP solver failed'}
        
        total_sessions = len(csp_engine.variables)
        if len(csp_solution) < total_sessions:
            print(f"   ⚠️  CSP Partial Solution: {len(csp_solution)}/{total_sessions} sessions")
        else:
            print(f"   ✅ CSP Complete Solution: {len(csp_solution)} sessions scheduled")
        
        # Convert to chromosome for GGA
        from app.services.gga.chromosome import Chromosome, Gene
        
        genes = []
        for assignment in csp_solution:
            gene = Gene(
                session_id=assignment.variable_id,
                course_unit_id=assignment.course_unit_id,
                program_id=assignment.program_id,
                lecturer_id=assignment.lecturer_id,
                room_id=assignment.room_number,
                time_slot=assignment.time_slot.to_dict(),
                term=assignment.term,
                session_number=assignment.session_number
            )
            genes.append(gene)
        
        csp_chromosome = Chromosome(id=f'CSP_{faculty}_Term{term_number}_Initial', genes=genes)
        
        # Extract variable pairs
        variable_pairs = csp_engine.variable_pairs
        canonical_course_groups = {}
        
        from collections import defaultdict
        canonical_genes_map = defaultdict(lambda: defaultdict(list))
        
        for g in genes:
            canonical_id = get_canonical_id(g.course_unit_id) or g.course_unit_id
            if canonical_id in CANONICAL_COURSE_MAPPING:
                canonical_genes_map[canonical_id][g.session_number].append(g.session_id)
        
        for canonical_id, session_map in canonical_genes_map.items():
            if any(len(gene_ids) > 1 for gene_ids in session_map.values()):
                canonical_course_groups[canonical_id] = dict(session_map)
        
        # GGA Optimization
        update_progress(term_number, 65, "GGA Optimization", 
                       "Running GGA optimization...")
        print(f"\n{'='*70}")
        print("🧬 Step 2: GGA Engine - Optimizing Soft Constraints")
        print("="*70)
        
        course_units_dict = {c.id: c for c in merged_course_units}
        student_groups_dict = {sg.id: sg for sg in merged_student_groups}
        
        gga_engine = GGAEngine(
            course_units=course_units_dict,
            programs=student_groups_dict,
            lecturers=lecturers,
            rooms=rooms,
            variable_pairs=variable_pairs,
            canonical_course_groups=canonical_course_groups
        )
        
        gga_engine.max_generations = 200
        gga_engine.population_size = 200
        
        print("   Running GGA optimization...")
        optimized_chromosome = gga_engine.optimize(csp_chromosome)
        update_progress(term_number, 85, "GGA Complete", 
                       f"GGA optimization completed: {len(optimized_chromosome.genes)} sessions")
        
        print(f"   ✅ Optimized Solution: {len(optimized_chromosome.genes)} sessions")
        if optimized_chromosome.fitness:
            print(f"   ✅ Fitness Score: {optimized_chromosome.fitness.overall_fitness:.4f}")
        
        # Save assignments to database
        update_progress(term_number, 85, "Saving", "Saving assignments to database...")
        print(f"\n{'='*70}")
        print("💾 Step 3: Saving Assignments")
        print("="*70)
        
        generation_id = f"gen_term{term_number}_{faculty.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        assignments_saved = []
        
        for gene in optimized_chromosome.genes:
            # Convert gene to assignment
            from app.services.csp.domain import Assignment, TimeSlot
            time_slot_dict = gene.time_slot if isinstance(gene.time_slot, dict) else gene.time_slot
            time_slot = TimeSlot(
                day=time_slot_dict.get('day') if isinstance(time_slot_dict, dict) else time_slot_dict.day,
                period=time_slot_dict.get('period') if isinstance(time_slot_dict, dict) else time_slot_dict.period,
                start=time_slot_dict.get('start') if isinstance(time_slot_dict, dict) else time_slot_dict.start,
                end=time_slot_dict.get('end') if isinstance(time_slot_dict, dict) else time_slot_dict.end
            )
            
            assignment = Assignment(
                variable_id=gene.session_id,
                course_unit_id=gene.course_unit_id,
                program_id=gene.program_id,
                lecturer_id=gene.lecturer_id,
                room_number=gene.room_id,
                time_slot=time_slot,
                term=gene.term,
                session_number=gene.session_number
            )
            
            # Save assignment
            assignment_doc = booking_manager.save_assignment(assignment, faculty, generation_id)
            
            # Book resources
            booking_manager.book_resource(assignment, faculty, generation_id)
            assignments_saved.append(assignment_doc)
        
        print(f"   ✅ Saved {len(assignments_saved)} assignments to database")
        print(f"   ✅ Booked all resources in global system")
        
        # Export to CSV
        update_progress(term_number, 90, "Exporting", "Exporting to CSV...")
        assignment_dicts = []
        for gene in optimized_chromosome.genes:
            expanded = expand_assignment_dicts(
                gene,
                merged_group_details,
                original_student_groups_dict,
                courses,
                term_number
            )
            assignment_dicts.extend(expanded)
        
        filename = f'TIMETABLE_{faculty}_TERM{term_number}_COMPLETE.csv'
        export_to_csv(assignment_dicts, courses, lecturers, rooms, filename, term_number)
        generate_statistics(assignment_dicts, courses, lecturers, rooms, filename, term_number)
        
        client.close()
        
        elapsed = (datetime.now() - start_time).total_seconds()
        update_progress(term_number, 100, "Complete", 
                      f"Timetable generation completed successfully! ({elapsed:.2f}s)")
        
        print(f"\n{'='*70}")
        print("                    ✅ GENERATION COMPLETE!")
        print("="*70)
        print(f"\n📊 Statistics:")
        print(f"   • Faculty: {faculty}")
        print(f"   • Term: Term {term_number}")
        print(f"   • Total Sessions: {len(assignments_saved)}")
        print(f"   • Time Elapsed: {elapsed:.2f} seconds")
        print(f"\n📁 Output Files:")
        print(f"   • {filename}")
        print(f"   • {filename.replace('.csv', '_SUMMARY.txt')}")
        print(f"\n🎉 {faculty} Term {term_number} timetable successfully generated!")
        print("="*70 + "\n")
        
        return {
            'success': True,
            'faculty': faculty,
            'term': term_number,
            'sessions_count': len(assignments_saved),
            'time_elapsed': elapsed,
            'filename': filename
        }
        
    except Exception as e:
        update_progress(term_number, -1, "Error", f"Generation failed: {str(e)}")
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate faculty timetable')
    parser.add_argument('--term', type=int, choices=[1, 2], required=True, help='Term number')
    parser.add_argument('--faculty', type=str, required=True, help='Faculty name')
    parser.add_argument('--academic-year', type=str, help='Academic year (e.g., 2024-2025)')
    parser.add_argument('--regenerate', action='store_true', help='Delete existing assignments first')
    
    args = parser.parse_args()
    
    result = generate_faculty_term_timetable(
        term_number=args.term,
        faculty=args.faculty,
        academic_year=args.academic_year,
        regenerate=args.regenerate
    )
    
    if not result.get('success'):
        sys.exit(1)
