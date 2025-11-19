"""
Generate Complete University Timetable
Generates timetables for ALL student groups across all semesters and terms
"""

import sys
sys.path.insert(0, '.')

from pymongo import MongoClient
from datetime import datetime
import csv
from collections import defaultdict

from app.models.lecturer import Lecturer
from app.models.course import CourseUnit
from app.models.room import Room
from app.models.student import StudentGroup
from app.services.preprocessing.term_splitter import TermSplitter
from app.services.csp.csp_engine import CSPEngine
from app.services.gga.gga_engine import GGAEngine
from app.config import Config

def setup_database():
    """Connect to MongoDB and seed data if needed"""
    client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
    db = client['timetable_scheduler']
    
    print("\n" + "="*70)
    print("          COMPREHENSIVE UNIVERSITY TIMETABLE GENERATION")
    print("="*70)
    
    return client, db

def fetch_all_data(db):
    """Fetch all data from database"""
    print("\n📥 Loading university data...")
    
    # Load all student groups
    student_groups_data = list(db.student_groups.find({'is_active': True}))
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

def generate_timetable_for_group(student_group, courses, lecturers, rooms, all_assignments):
    """Generate timetable for a single student group"""
    
    print(f"\n{'─'*70}")
    print(f"📚 Generating: {student_group.display_name}")
    print(f"   Students: {student_group.size} | Courses: {len(student_group.course_units)}")
    
    # Get courses for this group
    group_courses = [courses[cu_id] for cu_id in student_group.course_units if cu_id in courses]
    
    if not group_courses:
        print("   ⚠️  No courses assigned - skipping")
        return []
    
    # Step 1: Term splitting
    term_splitter = TermSplitter()
    try:
        term1_plan, term2_plan = term_splitter.split_semester(student_group.semester, group_courses)
    except ValueError as e:
        # If not enough courses for proper split, put all in Term1
        print(f"   ⚠️  Cannot split {len(group_courses)} courses - using all in Term1")
        from app.services.preprocessing.term_splitter import TermPlan
        term1_plan = TermPlan(
            term_id=f"{student_group.semester}_Term1",
            semester=student_group.semester,
            term_number=1,
            assigned_units=group_courses,
            total_weekly_hours=sum(c.weekly_hours for c in group_courses),
            total_credits=sum(c.credits for c in group_courses)
        )
        term2_plan = TermPlan(
            term_id=f"{student_group.semester}_Term2",
            semester=student_group.semester,
            term_number=2,
            assigned_units=[],
            total_weekly_hours=0,
            total_credits=0
        )
    
    group_assignments = []
    
    # Process both terms
    terms = [
        ('Term1', term1_plan.assigned_units),
        ('Term2', term2_plan.assigned_units)
    ]
    
    for term, term_courses in terms:
        
        if not term_courses:
            continue
        
        print(f"   📅 {term}: {len(term_courses)} courses")
        
        # Create term-specific student group
        term_student_group = StudentGroup.from_dict({
            **student_group.to_dict(),
            'term': term,
            'course_units': [c.id for c in term_courses]
        })
        
        # Step 2: CSP - Satisfy hard constraints
        csp_engine = CSPEngine()
        csp_engine.initialize(
            lecturers=list(lecturers.values()),
            rooms=list(rooms.values()),
            course_units=term_courses,
            student_groups=[term_student_group]
        )
        
        try:
            csp_solution = csp_engine.solve()
            
            if not csp_solution:
                print(f"      ❌ CSP failed for {term}")
                continue
            
            # Convert to chromosome for GGA
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
            
            csp_chromosome = Chromosome(id=f'CSP_{student_group.id}_{term}', genes=genes)
            
            # Step 3: GGA - Optimize soft constraints
            gga_engine = GGAEngine(
                course_units={c.id: c for c in term_courses},
                student_groups={student_group.id: student_group},
                lecturers=lecturers,
                rooms=rooms
            )
            
            # Quick optimization (fewer generations for multiple groups)
            gga_engine.max_generations = 50  # Reduced for speed
            optimized_chromosome = gga_engine.optimize(csp_chromosome)
            
            # Convert to assignment dicts
            for gene in optimized_chromosome.genes:
                group_assignments.append({
                    'session_id': gene.session_id,
                    'student_group_id': gene.student_group_id,
                    'student_group_name': student_group.display_name,
                    'semester': student_group.semester,
                    'term': term,
                    'group_size': student_group.size,
                    'course_id': gene.course_unit_id,
                    'lecturer_id': gene.lecturer_id,
                    'room_id': gene.room_id,
                    'day': gene.time_slot.day,
                    'time_slot': gene.time_slot.to_dict(),
                    'session_number': gene.session_number
                })
            
            print(f"      ✅ {len(optimized_chromosome.genes)} sessions scheduled")
            
        except Exception as e:
            print(f"      ❌ Error: {str(e)}")
            continue
    
    return group_assignments

def export_full_timetable(all_assignments, courses, lecturers, rooms, filename='FULL_UNIVERSITY_TIMETABLE.csv'):
    """Export complete university timetable to CSV"""
    
    print(f"\n{'='*70}")
    print("                    📊 EXPORTING FULL TIMETABLE")
    print("="*70)
    
    headers = [
        "Session_ID", "Day", "Time_Slot", "Start_Time", "End_Time",
        "Course_Code", "Course_Name", "Course_Type", "Credits",
        "Lecturer_ID", "Lecturer_Name", "Lecturer_Role",
        "Room_Number", "Room_Type", "Room_Capacity", "Room_Building", "Room_Campus",
        "Student_Group", "Semester", "Term", "Group_Size"
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        
        for assignment in all_assignments:
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
                "Term": assignment['term'],
                "Group_Size": assignment['group_size']
            }
            writer.writerow(row)
    
    print(f"\n✅ Exported {len(all_assignments)} total sessions")
    print(f"📁 File: {filename}")
    
    # Generate statistics
    generate_statistics(all_assignments, courses, lecturers, rooms, filename)

def generate_statistics(all_assignments, courses, lecturers, rooms, csv_filename):
    """Generate comprehensive statistics"""
    
    # Group by various dimensions
    by_semester = defaultdict(int)
    by_day = defaultdict(int)
    by_course = defaultdict(int)
    by_lecturer = defaultdict(int)
    by_room = defaultdict(int)
    
    for assignment in all_assignments:
        by_semester[assignment['semester']] += 1
        by_day[assignment['day']] += 1
        by_course[assignment['course_id']] += 1
        by_lecturer[assignment['lecturer_id']] += 1
        by_room[assignment['room_id']] += 1
    
    # Create summary file
    summary_filename = csv_filename.replace('.csv', '_SUMMARY.txt')
    
    with open(summary_filename, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("          UNIVERSITY TIMETABLE - COMPREHENSIVE SUMMARY\n")
        f.write("="*70 + "\n\n")
        
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Sessions: {len(all_assignments)}\n\n")
        
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
    
    print(f"📄 Summary: {summary_filename}")

def main():
    """Main execution"""
    start_time = datetime.now()
    
    try:
        # Setup
        client, db = setup_database()
        
        # Load all data
        student_groups, courses, lecturers, rooms = fetch_all_data(db)
        
        print(f"\n🎯 Generating timetable for all student groups")
        print(f"   Student Groups: {len(student_groups)}")
        print(f"   Semesters: {len(set(sg.semester for sg in student_groups))}")
        
        # Generate timetables for all groups
        all_assignments = []
        
        for i, student_group in enumerate(student_groups, 1):
            print(f"\n[{i}/{len(student_groups)}] Processing...")
            group_assignments = generate_timetable_for_group(
                student_group, courses, lecturers, rooms, all_assignments
            )
            all_assignments.extend(group_assignments)
        
        # Export complete timetable
        if all_assignments:
            export_full_timetable(all_assignments, courses, lecturers, rooms,
                                filename='TIMETABLE_UNIVERSITY_COMPLETE.csv')
        else:
            print("\n❌ No assignments generated!")
        
        # Close connection
        client.close()
        
        # Final summary
        elapsed = (datetime.now() - start_time).total_seconds()
        
        print(f"\n{'='*70}")
        print("                    ✅ GENERATION COMPLETE!")
        print("="*70)
        print(f"\n📊 Statistics:")
        print(f"   • Total Sessions: {len(all_assignments)}")
        print(f"   • Student Groups: {len(student_groups)}")
        print(f"   • Time Elapsed: {elapsed:.2f} seconds")
        print(f"\n📁 Output Files:")
        print(f"   • TIMETABLE_UNIVERSITY_COMPLETE.csv")
        print(f"   • TIMETABLE_UNIVERSITY_COMPLETE_SUMMARY.txt")
        print(f"\n🎉 University timetable successfully generated!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

