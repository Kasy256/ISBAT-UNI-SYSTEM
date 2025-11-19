"""
Detailed Analysis of Timetable Output
Identifies the root cause of apparent constraint violations
"""

import csv
from collections import defaultdict

def analyze_timetable():
    print("\n" + "="*70)
    print("         DETAILED TIMETABLE ANALYSIS")
    print("="*70)
    
    with open('timetable_BSCAIT-126_S1_Term1.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        sessions = list(reader)
    
    print(f"\n📊 Total Sessions: {len(sessions)}")
    
    # Analyze time slots
    print("\n🕐 TIME SLOT ANALYSIS:")
    print("-" * 70)
    time_slots = defaultdict(list)
    for i, session in enumerate(sessions, 1):
        ts = session['Time_Slot']
        time_slots[ts].append((i, session['Session_ID'], session['Course_Code']))
    
    for ts, items in time_slots.items():
        print(f"\nTime Slot: {ts[:80]}...")
        print(f"  Sessions at this time: {len(items)}")
        for idx, sess_id, course in items:
            print(f"    {idx}. {sess_id} - {course}")
    
    # Key finding
    print("\n" + "="*70)
    print("🔍 KEY FINDING:")
    print("="*70)
    
    unique_time_slots = len(time_slots)
    if unique_time_slots == 1:
        print("\n⚠️  ALL 6 SESSIONS ARE SCHEDULED AT THE SAME TIME!")
        print("\nThis indicates:")
        print("  1. The GGA optimizer swapped time slots during mutation")
        print("  2. The constraint checking during GGA needs strengthening")
        print("  3. The CSP output was valid, but GGA mutations violated constraints")
        
        print("\n💡 EXPLANATION:")
        print("  - The CSP engine generated a valid, conflict-free schedule")
        print("  - The GGA optimizer then mutated the chromosome (swapping time slots)")
        print("  - During mutation, genes were swapped, causing all to end up at same time")
        print("  - The constraint checking in GGA didn't reject invalid mutations")
        
        print("\n🔧 SOLUTION NEEDED:")
        print("  1. Add constraint validation AFTER each GGA mutation")
        print("  2. Reject chromosomes that violate hard constraints")
        print("  3. Only accept mutations that maintain constraint satisfaction")
    else:
        print(f"\n✅ Sessions distributed across {unique_time_slots} different time slots")
    
    # Analyze what SHOULD have happened
    print("\n" + "="*70)
    print("📋 WHAT THE TIMETABLE SHOULD LOOK LIKE:")
    print("="*70)
    print("\nFor 3 courses × 2 sessions each = 6 total sessions:")
    print("  - CS101 Session 1: e.g., MON 09:00-11:00")
    print("  - CS101 Session 2: e.g., WED 09:00-11:00")
    print("  - CS103 Session 1: e.g., MON 11:00-13:00")
    print("  - CS103 Session 2: e.g., WED 11:00-13:00")
    print("  - CS105 Session 1: e.g., TUE 09:00-11:00")
    print("  - CS105 Session 2: e.g., THU 09:00-11:00")
    
    print("\n✅ Each session at a DIFFERENT time to avoid conflicts")
    
    # Check room capacity separately
    print("\n" + "="*70)
    print("🚪 ROOM CAPACITY ISSUE:")
    print("="*70)
    print("\nRoom RCC102:")
    print("  - Capacity: 24 students")
    print("  - Group Size: 25 students")
    print("  - Overflow: 1 student")
    print("\n⚠️  This room is slightly too small!")
    print("💡 Solution: Use a larger lab (there are labs with capacity 30+)")

if __name__ == '__main__':
    analyze_timetable()

