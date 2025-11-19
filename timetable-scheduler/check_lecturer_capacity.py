"""Check if there are enough lecturers to handle all sessions"""

from seed_lecturers_data import get_all_lecturers

lecturers = get_all_lecturers()

print("="*70)
print("          LECTURER CAPACITY ANALYSIS")
print("="*70)

full_time = [l for l in lecturers if l['role'] == 'Full-Time']
part_time = [l for l in lecturers if l['role'] == 'Part-Time']
faculty_dean = [l for l in lecturers if l['role'] == 'Faculty Dean']

print(f"\nTotal Lecturers: {len(lecturers)}")
print(f"  • Full-Time: {len(full_time)}")
print(f"  • Part-Time: {len(part_time)}")
print(f"  • Faculty Dean: {len(faculty_dean)}")

# Calculate capacity
full_time_capacity = sum(l['max_weekly_hours'] for l in full_time)
part_time_capacity = sum(l['max_weekly_hours'] for l in part_time)
dean_capacity = sum(l['max_weekly_hours'] for l in faculty_dean)
total_capacity = full_time_capacity + part_time_capacity + dean_capacity

print(f"\nWeekly Hour Capacity:")
print(f"  • Full-Time: {full_time_capacity} hours/week")
print(f"  • Part-Time: {part_time_capacity} hours/week")
print(f"  • Faculty Dean: {dean_capacity} hours/week")
print(f"  • TOTAL: {total_capacity} hours/week")

# Term 1 needs: 58 sessions * 2 hours = 116 hours
term1_hours_needed = 58 * 2
print(f"\nTerm 1 Requirements:")
print(f"  • Sessions: 58")
print(f"  • Hours needed: {term1_hours_needed} hours/week")

if total_capacity >= term1_hours_needed:
    print(f"\n[OK] SUFFICIENT CAPACITY: {total_capacity} >= {term1_hours_needed}")
else:
    print(f"\n[FAIL] INSUFFICIENT CAPACITY: {total_capacity} < {term1_hours_needed}")
    print(f"   Shortfall: {term1_hours_needed - total_capacity} hours")

# Check daily limits
print(f"\nDaily Session Capacity:")
print(f"  • Full-Time: {len(full_time)} lecturers * 2 sessions/day * 5 days = {len(full_time) * 2 * 5} sessions/week")
print(f"  • Part-Time: {len(part_time)} lecturers * 1 session/day * 5 days = {len(part_time) * 1 * 5} sessions/week")
total_daily_capacity = (len(full_time) * 2 * 5) + (len(part_time) * 1 * 5)
print(f"  • TOTAL: {total_daily_capacity} sessions/week")
print(f"  • Needed: 58 sessions")
if total_daily_capacity >= 58:
    print(f"  [OK] SUFFICIENT")
else:
    print(f"  [FAIL] INSUFFICIENT")

print("\n" + "="*70)

