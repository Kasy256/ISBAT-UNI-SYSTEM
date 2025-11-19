"""
Generate Term-Based University Timetable
Generates timetables for a SPECIFIC TERM (Term1 or Term2) across ALL semesters
All programs share the same academic terms
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
import argparse

from app.models.lecturer import Lecturer
from app.models.course import CourseUnit
from app.models.room import Room
from app.models.student import StudentGroup
from app.services.preprocessing.term_splitter import TermSplitter
from app.services.csp.csp_engine import CSPEngine
from app.services.gga.gga_engine import GGAEngine
from app.config import Config

def setup_database():
    """Connect to MongoDB"""
    client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
    db = client['timetable_scheduler']
    return client, db

def fetch_all_data(db):
    """Fetch all data from database"""
    print("\n📥 Loading university data...")
    
    # Load student groups (batch is stored but not used for filtering)
    query = {'is_active': True}
    student_groups_data = list(db.student_groups.find(query))
    student_groups = [StudentGroup.from_dict(sg) for sg in student_groups_data]
    
    # Load all courses
    courses_data = list(db.course_units.find())
    courses = {CourseUnit.from_dict(c).id: CourseUnit.from_dict(c) for c in courses_data}
    
    # Load all lecturers
    lecturers_data = list(db.lecturers.find())
    lecturers = {Lecturer.from_dict(l).id: Lecturer.from_dict(l) for l in lecturers_data}
    
    # Load all rooms
    rooms_data = list(db.rooms.find())
    rooms = {Room.from_dict(r).id: Room.from_dict(r) for r in rooms_data}
    
    print(f"   ✅ {len(student_groups)} student groups")
    print(f"   ✅ {len(courses)} courses")
    print(f"   ✅ {len(lecturers)} lecturers")
    print(f"   ✅ {len(rooms)} rooms")
    
    return student_groups, courses, lecturers, rooms

def get_term_courses_for_group(student_group, courses, term_number):
    """
    Get courses for a specific term for a student group
    Returns list of CourseUnit objects for the specified term
    """
    # Get all courses for this group
    group_courses = [courses[cu_id] for cu_id in student_group.course_units if cu_id in courses]
    
    if not group_courses:
        return []
    
    # Use term splitter to determine which courses belong to which term
    term_splitter = TermSplitter()
    
    try:
        term1_plan, term2_plan = term_splitter.split_semester(student_group.semester, group_courses)
        
        if term_number == 1:
            return term1_plan.assigned_units
        elif term_number == 2:
            return term2_plan.assigned_units
        else:
            raise ValueError(f"Invalid term number: {term_number}. Must be 1 or 2.")
            
    except ValueError as e:
        # If split fails (e.g., wrong number of courses), handle gracefully
        print(f"   ⚠️  Warning for {student_group.display_name}: {str(e)}")
        
        # If we can't split, check if courses have preferred_term
        if term_number == 1:
            # Try to get courses that prefer Term1, or all if none specified
            term1_courses = [c for c in group_courses if c.preferred_term in ["Term 1", "Term1", "1"]]
            if term1_courses:
                return term1_courses
            # If no preference, return empty (courses will be in Term2)
            return []
        else:  # term_number == 2
            # Try to get courses that prefer Term2, or all if none specified
            term2_courses = [c for c in group_courses if c.preferred_term in ["Term 2", "Term2", "2"]]
            if term2_courses:
                return term2_courses
            # If no preference and Term1 is empty, return all
            term1_courses = [c for c in group_courses if c.preferred_term in ["Term 1", "Term1", "1"]]
            if not term1_courses:
                return group_courses
            return []

def generate_term_timetable(term_number):
    """
    Generate timetable for a specific term across ALL semesters
    
    Args:
        term_number: 1 for Term1, 2 for Term2
    """
    start_time = datetime.now()
    
    print("\n" + "="*70)
    print(f"          TERM {term_number} TIMETABLE GENERATION")
    print("="*70)
    print(f"\n🎯 Generating timetable for: TERM {term_number}")
    print(f"   Scope: ALL semesters (S1-S6)")
    print(f"   All programs share the same academic terms\n")
    
    try:
        # Setup
        client, db = setup_database()
        
        # Load all data
        student_groups, courses, lecturers, rooms = fetch_all_data(db)
        
        if not student_groups:
            print("❌ No student groups found!")
            return
        
        # Collect all term-specific courses and student groups
        term_student_groups = []
        all_term_courses = set()
        term_courses_by_group = {}
        
        print(f"\n📋 Processing student groups for Term {term_number}...")
        print("─"*70)
        
        for student_group in student_groups:
            term_courses = get_term_courses_for_group(student_group, courses, term_number)
            
            if term_courses:
                # Create term-specific student group
                term_student_group = StudentGroup.from_dict({
                    **student_group.to_dict(),
                    'term': f'Term{term_number}',
                    'course_units': [c.id for c in term_courses]
                })
                
                term_student_groups.append(term_student_group)
                term_courses_by_group[term_student_group.id] = term_courses
                
                # Track all unique courses
                for course in term_courses:
                    all_term_courses.add(course.id)
                
                print(f"   ✅ {student_group.display_name}: {len(term_courses)} courses")
            else:
                print(f"   ⚠️  {student_group.display_name}: No courses for Term {term_number}")
        
        if not term_student_groups:
            print(f"\n❌ No student groups have courses for Term {term_number}!")
            client.close()
            return
        
        print(f"\n📊 Summary:")
        print(f"   • Student Groups: {len(term_student_groups)}")
        print(f"   • Unique Courses: {len(all_term_courses)}")
        print(f"   • Total Sessions to Schedule: {sum(len(courses) for courses in term_courses_by_group.values())}")
        
        # Convert all_term_courses set to list of CourseUnit objects
        all_term_courses_list = [courses[cid] for cid in all_term_courses]
        
        # Step 1: CSP - Generate initial timetable for ALL groups together
        print(f"\n{'='*70}")
        print("🧩 Step 1: CSP Engine - Satisfying Hard Constraints")
        print("="*70)
        print(f"   Scheduling ALL semesters together for Term {term_number}...")
        
        csp_engine = CSPEngine()
        csp_engine.initialize(
            lecturers=list(lecturers.values()),
            rooms=list(rooms.values()),
            course_units=all_term_courses_list,
            student_groups=term_student_groups
        )
        
        print("   Running CSP solver...")
        csp_solution = csp_engine.solve()
        
        if not csp_solution:
            print("   ❌ CSP failed to find any assignments!")
            print("   This may indicate resource constraints (rooms, lecturers, time slots)")
            client.close()
            return
        
        total_sessions = len(csp_engine.variables)
        if len(csp_solution) < total_sessions:
            print(f"   ⚠️  CSP Partial Solution: {len(csp_solution)}/{total_sessions} sessions scheduled")
            print(f"   💡 GGA will attempt to complete the remaining {total_sessions - len(csp_solution)} sessions")
        else:
            print(f"   ✅ CSP Complete Solution: {len(csp_solution)} sessions scheduled")
        
        # Step 2: Convert CSP solution to Chromosome for GGA
        from app.services.gga.chromosome import Chromosome, Gene
        
        genes = []
        for assignment in csp_solution:
            gene = Gene(
                session_id=assignment.variable_id,
                course_unit_id=assignment.course_unit_id,
                student_group_id=assignment.student_group_id,
                lecturer_id=assignment.lecturer_id,
                room_id=assignment.room_id,
                time_slot=assignment.time_slot,
                term=assignment.term,
                session_number=assignment.session_number
            )
            genes.append(gene)
        
        csp_chromosome = Chromosome(id=f'CSP_Term{term_number}_Initial', genes=genes)
        
        # Step 3: GGA - Optimize for soft constraints
        print(f"\n{'='*70}")
        print("🧬 Step 2: GGA Engine - Optimizing Soft Constraints")
        print("="*70)
        
        # Prepare resource dictionaries for GGA
        course_units_dict = {c.id: c for c in all_term_courses_list}
        student_groups_dict = {sg.id: sg for sg in term_student_groups}
        
        gga_engine = GGAEngine(
            course_units=course_units_dict,
            student_groups=student_groups_dict,
            lecturers=lecturers,
            rooms=rooms
        )
        
        # Use more generations for comprehensive optimization (especially weekday balance)
        gga_engine.max_generations = 200  # Increased from 100
        gga_engine.population_size = 200  # Increased from 150
        
        print("   Running GGA optimization...")
        optimized_chromosome = gga_engine.optimize(csp_chromosome)
        
        print(f"   ✅ Optimized Solution: {len(optimized_chromosome.genes)} sessions")
        if optimized_chromosome.fitness:
            print(f"   ✅ Fitness Score: {optimized_chromosome.fitness.overall_fitness:.4f}")
        
        # Step 4: Export to CSV
        print(f"\n{'='*70}")
        print("📊 Step 3: Exporting Timetable")
        print("="*70)
        
        # Create lookup dict for student groups
        term_student_groups_dict = {sg.id: sg for sg in term_student_groups}
        
        # Convert to assignment dicts
        assignment_dicts = []
        for gene in optimized_chromosome.genes:
            # Get student group info
            sg = term_student_groups_dict.get(gene.student_group_id)
            if not sg:
                # Fallback if group not found
                continue
            
            assignment_dicts.append({
                'session_id': gene.session_id,
                'student_group_id': gene.student_group_id,
                'student_group_name': sg.display_name,
                'semester': sg.semester,
                'term': f'Term{term_number}',
                'group_size': sg.size,
                'course_id': gene.course_unit_id,
                'lecturer_id': gene.lecturer_id,
                'room_id': gene.room_id,
                'day': gene.time_slot.day,
                'time_slot': gene.time_slot.to_dict(),
                'session_number': gene.session_number
            })
        
        
        # Export
        filename = f'TIMETABLE_TERM{term_number}_COMPLETE.csv'
        export_to_csv(assignment_dicts, courses, lecturers, rooms, filename, term_number)
        
        # Generate statistics
        generate_statistics(assignment_dicts, courses, lecturers, rooms, filename, term_number)
        
        # Close connection
        client.close()
        
        # Final summary
        elapsed = (datetime.now() - start_time).total_seconds()
        
        print(f"\n{'='*70}")
        print("                    ✅ GENERATION COMPLETE!")
        print("="*70)
        print(f"\n📊 Statistics:")
        print(f"   • Term: Term {term_number}")
        print(f"   • Total Sessions: {len(assignment_dicts)}")
        print(f"   • Student Groups: {len(term_student_groups)}")
        print(f"   • Unique Courses: {len(all_term_courses)}")
        print(f"   • Time Elapsed: {elapsed:.2f} seconds")
        print(f"\n📁 Output Files:")
        print(f"   • {filename}")
        print(f"   • {filename.replace('.csv', '_SUMMARY.txt')}")
        print(f"\n🎉 Term {term_number} timetable successfully generated!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

def export_to_csv(assignments, courses, lecturers, rooms, filename, term_number):
    """Export timetable to CSV"""
    
    headers = [
        "Session_ID", "Day", "Time_Slot", "Start_Time", "End_Time",
        "Course_Code", "Course_Name", "Course_Type", "Credits",
        "Lecturer_ID", "Lecturer_Name", "Lecturer_Role",
        "Room_Number", "Room_Type", "Room_Capacity", "Room_Building", "Room_Campus",
        "Student_Group", "Semester", "Term", "Group_Size"
    ]
    
    # Handle file permission errors (file might be open in Excel)
    import os
    from datetime import datetime
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            
            for assignment in assignments:
                course = courses.get(assignment['course_id'], None)
                lecturer = lecturers.get(assignment['lecturer_id'], None)
                room = rooms.get(assignment['room_id'], None)
                
                if not course or not lecturer or not room:
                    continue
                
                ts = assignment['time_slot']
                
                row = {
                    "Session_ID": assignment['session_id'],
                    "Day": assignment['day'],
                    "Time_Slot": f"{ts['start']}-{ts['end']}",
                    "Start_Time": ts['start'],
                    "End_Time": ts['end'],
                    "Course_Code": course.code,
                    "Course_Name": course.name,
                    "Course_Type": "Lab" if course.is_lab else "Theory",
                    "Credits": course.credits,
                    "Lecturer_ID": lecturer.id,
                    "Lecturer_Name": lecturer.name,
                    "Lecturer_Role": lecturer.role,
                    "Room_Number": room.room_number,
                    "Room_Type": room.room_type,
                    "Room_Capacity": room.capacity,
                    "Room_Building": room.building,
                    "Room_Campus": getattr(room, 'campus', 'N/A'),
                    "Student_Group": assignment['student_group_name'],
                    "Semester": assignment['semester'],
                    "Term": f"Term{term_number}",
                    "Group_Size": assignment['group_size']
                }
                writer.writerow(row)
        
        print(f"   ✅ Exported {len(assignments)} sessions to {filename}")
    except PermissionError:
        # File is likely open in Excel, try with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = filename.replace('.csv', '')
        fallback_filename = f"{base_name}_{timestamp}.csv"
        try:
            with open(fallback_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                
                for assignment in assignments:
                    course = courses.get(assignment['course_id'], None)
                    lecturer = lecturers.get(assignment['lecturer_id'], None)
                    room = rooms.get(assignment['room_id'], None)
                    
                    row = {
                        "Session_ID": assignment['session_id'],
                        "Day": assignment['day'],
                        "Time_Slot": assignment['time_slot'],
                        "Start_Time": assignment['start_time'],
                        "End_Time": assignment['end_time'],
                        "Course_Code": course.code if course else "N/A",
                        "Course_Name": course.name if course else "N/A",
                        "Course_Type": "Lab" if course and course.is_lab else "Theory",
                        "Credits": course.credits if course else 0,
                        "Lecturer_ID": lecturer.id if lecturer else "N/A",
                        "Lecturer_Name": lecturer.name if lecturer else "N/A",
                        "Lecturer_Role": lecturer.role if lecturer else "N/A",
                        "Room_Number": room.room_number if room else "N/A",
                        "Room_Type": room.room_type if room else "N/A",
                        "Room_Capacity": room.capacity if room else 0,
                        "Room_Building": room.building if room else "N/A",
                        "Room_Campus": getattr(room, 'campus', 'N/A') if room else "N/A",
                        "Student_Group": assignment['student_group_name'],
                        "Semester": assignment['semester'],
                        "Term": f"Term{term_number}",
                        "Group_Size": assignment['group_size']
                    }
                    writer.writerow(row)
            
            print(f"   ⚠️  Original file locked, exported to: {fallback_filename}")
        except Exception as e2:
            print(f"   ❌ Failed to export CSV: {e2}")
            print(f"   💡 Please close any open CSV files and try again")

def generate_statistics(assignments, courses, lecturers, rooms, csv_filename, term_number):
    """Generate comprehensive statistics"""
    
    # Group by various dimensions
    by_semester = defaultdict(int)
    by_day = defaultdict(int)
    by_course = defaultdict(int)
    by_lecturer = defaultdict(int)
    by_room = defaultdict(int)
    
    for assignment in assignments:
        by_semester[assignment['semester']] += 1
        by_day[assignment['day']] += 1
        by_course[assignment['course_id']] += 1
        by_lecturer[assignment['lecturer_id']] += 1
        by_room[assignment['room_id']] += 1
    
    # Create summary file
    summary_filename = csv_filename.replace('.csv', '_SUMMARY.txt')
    
    with open(summary_filename, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write(f"          TERM {term_number} TIMETABLE - COMPREHENSIVE SUMMARY\n")
        f.write("="*70 + "\n\n")
        
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Term: Term {term_number}\n")
        f.write(f"Total Sessions: {len(assignments)}\n\n")
        
        f.write("="*70 + "\n")
        f.write("SESSIONS BY SEMESTER\n")
        f.write("="*70 + "\n")
        for sem, count in sorted(by_semester.items()):
            f.write(f"  {sem}: {count} sessions\n")
        
        f.write("\n" + "="*70 + "\n")
        f.write("SESSIONS BY DAY\n")
        f.write("="*70 + "\n")
        for day in ['MON', 'TUE', 'WED', 'THU', 'FRI']:
            count = by_day.get(day, 0)
            f.write(f"  {day}: {count} sessions\n")
        
        f.write("\n" + "="*70 + "\n")
        f.write("TOP 10 COURSES (by sessions)\n")
        f.write("="*70 + "\n")
        top_courses = sorted(by_course.items(), key=lambda x: x[1], reverse=True)[:10]
        for course_id, count in top_courses:
            course = courses.get(course_id)
            if course:
                f.write(f"  {course.code} - {course.name}: {count} sessions\n")
        
        f.write("\n" + "="*70 + "\n")
        f.write("TOP 10 LECTURERS (by sessions)\n")
        f.write("="*70 + "\n")
        top_lecturers = sorted(by_lecturer.items(), key=lambda x: x[1], reverse=True)[:10]
        for lec_id, count in top_lecturers:
            lecturer = lecturers.get(lec_id)
            if lecturer:
                f.write(f"  {lecturer.name}: {count} sessions\n")
        
        f.write("\n" + "="*70 + "\n")
        f.write("TOP 10 ROOMS (by usage)\n")
        f.write("="*70 + "\n")
        top_rooms = sorted(by_room.items(), key=lambda x: x[1], reverse=True)[:10]
        for room_id, count in top_rooms:
            room = rooms.get(room_id)
            if room:
                f.write(f"  {room.room_number} ({room.room_type}): {count} sessions\n")
        
        f.write("\n" + "="*70 + "\n")
    
    print(f"   ✅ Summary: {summary_filename}")

def main():
    """Main execution with command-line interface"""
    parser = argparse.ArgumentParser(
        description='Generate term-based university timetable',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate Term1 timetable
  python generate_term_timetable.py --term 1
  
  # Generate Term2 timetable
  python generate_term_timetable.py --term 2
  
  # Generate Term1 timetable (interactive)
  python generate_term_timetable.py
        """
    )
    
    parser.add_argument(
        '--term',
        type=int,
        choices=[1, 2],
        help='Term number (1 or 2)'
    )
    
    args = parser.parse_args()
    
    # If term not provided, prompt user
    if args.term is None:
        print("\n" + "="*70)
        print("          TERM-BASED TIMETABLE GENERATION")
        print("="*70)
        print("\nSelect term to generate:")
        print("  1. Term 1")
        print("  2. Term 2")
        
        while True:
            try:
                term_input = input("\nEnter term number (1 or 2): ").strip()
                term_number = int(term_input)
                if term_number in [1, 2]:
                    break
                else:
                    print("❌ Please enter 1 or 2")
            except ValueError:
                print("❌ Please enter a valid number (1 or 2)")
            except KeyboardInterrupt:
                print("\n\n❌ Cancelled by user")
                return
    else:
        term_number = args.term
    
    # Generate timetable
    generate_term_timetable(term_number)

if __name__ == '__main__':
    main()

