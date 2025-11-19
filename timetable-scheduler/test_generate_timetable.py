"""
Test script to generate a timetable and export to CSV
"""

import csv
import json
from datetime import datetime
from pymongo import MongoClient
from seed_data import seed_all

# Import necessary components
import sys
sys.path.insert(0, '.')

from app.services.preprocessing.term_splitter import TermSplitter
from app.services.csp.csp_engine import CSPEngine
from app.services.gga.gga_engine import GGAEngine
from app.config import Config
from app.models.lecturer import Lecturer
from app.models.course import CourseUnit
from app.models.room import Room
from app.models.student import StudentGroup


def setup_database():
    """Seed the database with sample data"""
    print("\n" + "="*70)
    print(" "*20 + "DATABASE SETUP")
    print("="*70 + "\n")
    
    print("Seeding database with sample data...")
    success = seed_all()
    
    if not success:
        print("\n❌ Failed to seed database. Exiting.")
        sys.exit(1)
    
    print("\n✅ Database seeded successfully!\n")
    return True


def generate_timetable(batch='BSCAIT-126', semester='S1', term='Term1'):
    """Generate a timetable for the specified parameters"""
    
    print("\n" + "="*70)
    print(" "*20 + "TIMETABLE GENERATION")
    print("="*70 + "\n")
    
    print(f"📊 Generating timetable for:")
    print(f"   - Batch: {batch}")
    print(f"   - Semester: {semester}")
    print(f"   - Term: {term}\n")
    
    # Connect to database
    client = MongoClient('mongodb://localhost:27017/')
    db = client['timetable_scheduler']
    
    # Fetch required data
    print("📥 Fetching data from database...")
    
    # Get student group
    student_group = db.student_groups.find_one({
        'batch': batch,
        'semester': semester
    })
    
    if not student_group:
        print(f"❌ Student group not found for {batch} - {semester}")
        return None
    
    print(f"   ✅ Student group: {student_group['id']} ({student_group['size']} students)")
    
    # Get all courses for this group
    course_ids = student_group['course_units']
    course_docs = list(db.course_units.find({'id': {'$in': course_ids}}))
    print(f"   ✅ Courses: {len(course_docs)} loaded")
    
    # Get all lecturers
    lecturer_docs = list(db.lecturers.find({}))
    print(f"   ✅ Lecturers: {len(lecturer_docs)} loaded")
    
    # Get all rooms
    room_docs = list(db.rooms.find({}))
    print(f"   ✅ Rooms: {len(room_docs)} loaded\n")
    
    # Convert MongoDB documents to model objects
    courses = [CourseUnit.from_dict(c) for c in course_docs]
    lecturers = [Lecturer.from_dict(l) for l in lecturer_docs]
    rooms = [Room.from_dict(r) for r in room_docs]
    
    # Step 1: Preprocessing - Split into terms
    print("⚙️  Step 1: Preprocessing - Term Splitting...")
    term_splitter = TermSplitter()
    
    # Split courses into terms
    term1_plan, term2_plan = term_splitter.split_semester(semester, courses)
    
    # Select the requested term
    if term == 'Term1':
        term_plan = term1_plan
    else:
        term_plan = term2_plan
    
    term_courses = term_plan.assigned_units
    print(f"   ✅ {len(term_courses)} courses assigned to {term}")
    for course in term_courses:
        print(f"      - {course.code}: {course.name}")
    
    # Create student group model for this term
    term_student_group = StudentGroup.from_dict({
        **student_group,
        'term': term,
        'course_units': [c.id for c in term_courses]
    })
    
    # Step 2: CSP - Generate initial timetable
    print("\n🧩 Step 2: CSP Engine - Satisfying Hard Constraints...")
    
    # Initialize CSP engine
    csp_engine = CSPEngine()
    csp_engine.initialize(
        lecturers=lecturers,
        rooms=rooms,
        course_units=term_courses,
        student_groups=[term_student_group]
    )
    
    print("   Running CSP solver...")
    csp_solution = csp_engine.solve()
    
    if not csp_solution:
        print("   ❌ CSP failed to find a solution")
        return None
    
    print(f"   ✅ CSP solution found: {len(csp_solution)} assignments")
    
    # Convert CSP solution (list of Assignments) to Chromosome
    from app.services.gga.chromosome import Chromosome, Gene
    
    genes = []
    for assignment in csp_solution:
        gene = Gene(
            session_id=assignment.variable_id,
            course_unit_id=assignment.course_unit_id,
            student_group_id=assignment.student_group_id,
            lecturer_id=assignment.lecturer_id,
            room_id=assignment.room_id,
            time_slot=assignment.time_slot,  # TimeSlot object
            term=assignment.term,
            session_number=assignment.session_number
        )
        genes.append(gene)
    
    csp_chromosome = Chromosome(id='CSP_initial', genes=genes)
    
    # Step 3: GGA - Optimize for soft constraints
    print("\n🧬 Step 3: GGA Engine - Optimizing Soft Constraints...")
    
    gga_engine = GGAEngine(
        course_units={c.id: c for c in term_courses},
        student_groups={term_student_group.id: term_student_group},
        lecturers={l.id: l for l in lecturers},
        rooms={r.id: r for r in rooms}
    )
    
    print("   Running GGA optimizer...")
    # Initialize population from CSP solution
    optimized_chromosome = gga_engine.optimize(csp_chromosome)
    
    print(f"   ✅ Optimized solution: {len(optimized_chromosome.genes)} assignments")
    print(f"   ✅ Fitness Score: {optimized_chromosome.fitness.overall_fitness:.4f}")
    
    print("\n✅ Timetable generation complete!\n")
    
    # Close database connection
    client.close()
    
    # Convert chromosome genes to assignment dicts
    assignment_dicts = []
    for gene in optimized_chromosome.genes:
        assignment_dicts.append({
            'id': gene.session_id,
            'course_id': gene.course_unit_id,
            'lecturer_id': gene.lecturer_id,
            'room_id': gene.room_id,
            'day': gene.time_slot.day,
            'time_slot': gene.time_slot.to_dict(),
            'student_group_id': gene.student_group_id
        })
    
    return {
        'batch': batch,
        'semester': semester,
        'term': term,
        'student_group': student_group,
        'assignments': assignment_dicts,
        'courses': {c.id: c.to_dict() for c in term_courses},
        'lecturers': {l.id: l.to_dict() for l in lecturers},
        'rooms': {r.id: r.to_dict() for r in rooms},
        'fitness_score': optimized_chromosome.fitness.overall_fitness,
        'generated_at': datetime.now().isoformat()
    }


def export_to_csv(timetable_data, filename='timetable_output.csv'):
    """Export timetable to a well-structured CSV file"""
    
    print("\n" + "="*70)
    print(" "*20 + "CSV EXPORT")
    print("="*70 + "\n")
    
    if not timetable_data:
        print("❌ No timetable data to export")
        return False
    
    print(f"📝 Exporting timetable to: {filename}")
    
    assignments = timetable_data['assignments']
    courses = timetable_data['courses']
    lecturers = timetable_data['lecturers']
    rooms = timetable_data['rooms']
    
    # Prepare CSV data
    csv_rows = []
    
    for assignment in assignments:
        course = courses.get(assignment['course_id'], {})
        lecturer = lecturers.get(assignment['lecturer_id'], {})
        room = rooms.get(assignment['room_id'], {})
        
        row = {
            'Session_ID': assignment.get('id', 'N/A'),
            'Day': assignment['day'],
            'Time_Slot': assignment['time_slot'],
            'Course_Code': course.get('code', 'N/A'),
            'Course_Name': course.get('name', 'N/A'),
            'Course_Type': 'Lab' if course.get('is_lab', False) else 'Theory',
            'Credits': course.get('credits', 'N/A'),
            'Lecturer_ID': assignment['lecturer_id'],
            'Lecturer_Name': lecturer.get('name', 'N/A'),
            'Lecturer_Role': lecturer.get('role', 'N/A'),
            'Room_Number': assignment['room_id'],
            'Room_Type': room.get('room_type', 'N/A'),
            'Room_Capacity': room.get('capacity', 'N/A'),
            'Room_Building': room.get('building', 'N/A'),
            'Room_Campus': room.get('campus', 'N/A'),
            'Student_Group': timetable_data['student_group']['id'],
            'Batch': timetable_data['batch'],
            'Semester': timetable_data['semester'],
            'Term': timetable_data['term'],
            'Group_Size': timetable_data['student_group']['size']
        }
        
        csv_rows.append(row)
    
    # Sort by Day and Time
    day_order = {'MON': 1, 'TUE': 2, 'WED': 3, 'THU': 4, 'FRI': 5}
    csv_rows.sort(key=lambda x: (day_order.get(x['Day'], 6), x['Time_Slot']))
    
    # Write to CSV
    if csv_rows:
        fieldnames = [
            'Session_ID', 'Day', 'Time_Slot',
            'Course_Code', 'Course_Name', 'Course_Type', 'Credits',
            'Lecturer_ID', 'Lecturer_Name', 'Lecturer_Role',
            'Room_Number', 'Room_Type', 'Room_Capacity', 'Room_Building', 'Room_Campus',
            'Student_Group', 'Batch', 'Semester', 'Term', 'Group_Size'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_rows)
        
        print(f"   ✅ Exported {len(csv_rows)} sessions to CSV")
        print(f"   📊 Columns: {len(fieldnames)}")
        print(f"   📁 File: {filename}\n")
        
        # Display summary
        print("📊 Timetable Summary:")
        print(f"   - Total Sessions: {len(csv_rows)}")
        print(f"   - Courses: {len(set(r['Course_Code'] for r in csv_rows))}")
        print(f"   - Lecturers: {len(set(r['Lecturer_Name'] for r in csv_rows))}")
        print(f"   - Rooms: {len(set(r['Room_Number'] for r in csv_rows))}")
        print(f"   - Days: {', '.join(sorted(set(r['Day'] for r in csv_rows), key=lambda x: day_order.get(x, 6)))}")
        
        # Session distribution by day
        print("\n📅 Sessions by Day:")
        day_counts = {}
        for row in csv_rows:
            day_counts[row['Day']] = day_counts.get(row['Day'], 0) + 1
        for day in sorted(day_counts.keys(), key=lambda x: day_order.get(x, 6)):
            print(f"   - {day}: {day_counts[day]} sessions")
        
        return True
    else:
        print("❌ No data to export")
        return False


def create_readable_summary(timetable_data, filename='timetable_summary.txt'):
    """Create a human-readable summary file"""
    
    if not timetable_data:
        return False
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write(" "*20 + "ISBAT TIMETABLE SUMMARY\n")
        f.write("="*70 + "\n\n")
        
        f.write(f"Batch: {timetable_data['batch']}\n")
        f.write(f"Semester: {timetable_data['semester']}\n")
        f.write(f"Term: {timetable_data['term']}\n")
        f.write(f"Student Group: {timetable_data['student_group']['id']}\n")
        f.write(f"Group Size: {timetable_data['student_group']['size']} students\n")
        f.write(f"Fitness Score: {timetable_data['fitness_score']:.2f}\n")
        f.write(f"Generated: {timetable_data['generated_at']}\n")
        f.write("\n" + "="*70 + "\n\n")
        
        # Group by day
        assignments = timetable_data['assignments']
        courses = timetable_data['courses']
        lecturers = timetable_data['lecturers']
        rooms = timetable_data['rooms']
        
        day_order = ['MON', 'TUE', 'WED', 'THU', 'FRI']
        by_day = {}
        
        for assignment in assignments:
            day = assignment['day']
            if day not in by_day:
                by_day[day] = []
            by_day[day].append(assignment)
        
        for day in day_order:
            if day not in by_day:
                continue
            
            f.write(f"\n{day}\n")
            f.write("-"*70 + "\n")
            
            day_assignments = sorted(by_day[day], key=lambda x: x['time_slot']['start'] if isinstance(x['time_slot'], dict) else x['time_slot'])
            
            for assignment in day_assignments:
                course = courses.get(assignment['course_id'], {})
                lecturer = lecturers.get(assignment['lecturer_id'], {})
                room = rooms.get(assignment['room_id'], {})
                
                f.write(f"\n  {assignment['time_slot']}\n")
                f.write(f"    Course: {course.get('code', 'N/A')} - {course.get('name', 'N/A')}\n")
                f.write(f"    Type: {'Lab' if course.get('is_lab', False) else 'Theory'}\n")
                f.write(f"    Lecturer: {lecturer.get('name', 'N/A')} ({lecturer.get('role', 'N/A')})\n")
                f.write(f"    Room: {assignment['room_id']} ({room.get('room_type', 'N/A')}, Capacity: {room.get('capacity', 'N/A')})\n")
                f.write(f"    Building: {room.get('building', 'N/A')}, {room.get('campus', 'N/A')} Campus\n")
        
        f.write("\n" + "="*70 + "\n")
    
    print(f"   ✅ Created readable summary: {filename}\n")
    return True


def main():
    """Main test function"""
    
    print("\n" + "="*70)
    print(" "*15 + "ISBAT TIMETABLE SYSTEM - TEST")
    print("="*70)
    
    try:
        # Step 1: Setup database
        setup_database()
        
        # Step 2: Generate timetable
        timetable = generate_timetable(
            batch='BSCAIT-126',
            semester='S1',
            term='Term1'
        )
        
        if not timetable:
            print("\n❌ Timetable generation failed")
            return False
        
        # Step 3: Export to CSV
        csv_filename = f"timetable_{timetable['batch']}_{timetable['semester']}_{timetable['term']}.csv"
        export_success = export_to_csv(timetable, csv_filename)
        
        if not export_success:
            print("\n❌ CSV export failed")
            return False
        
        # Step 4: Create readable summary
        summary_filename = f"timetable_{timetable['batch']}_{timetable['semester']}_{timetable['term']}_summary.txt"
        create_readable_summary(timetable, summary_filename)
        
        # Final summary
        print("\n" + "="*70)
        print(" "*20 + "✅ TEST COMPLETE!")
        print("="*70)
        print(f"\n📁 Generated Files:")
        print(f"   1. {csv_filename} (CSV format)")
        print(f"   2. {summary_filename} (Human-readable)")
        
        print(f"\n🎉 Timetable successfully generated and exported!")
        print(f"\n💡 Tip: Open {csv_filename} in Excel or Google Sheets\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

