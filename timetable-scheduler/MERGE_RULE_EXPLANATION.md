# Merge Rule Explanation

## How the Merge Rule Currently Works

The merge rule works **reactively** during CSP assignment, checking multiple constraints simultaneously:

### Step-by-Step Process

When assigning a group's course session to a room/time slot:

#### 1. **Pre-filtering (Domain Initialization)**
   - **Room Type**: Already filtered - only rooms with correct type are in `available_rooms`
     - Lab courses → Only Lab rooms
     - Theory courses → Only Classroom/Lecture Hall/Seminar Room
   - **Lecturer Specialization**: Already filtered - only qualified lecturers are in `available_lecturers`
     - Only lecturers with the course in their `specializations` list
   - **Room Capacity (single group)**: Already filtered - rooms too small for the group are excluded
     - Only rooms where `room.capacity >= student_group.size`

#### 2. **During Assignment (Constraint Checking)**

When CSP tries to assign a value `(time_slot, lecturer_id, room_id)`:

   ```
   ┌─────────────────────────────────────────────────┐
   │ For each possible assignment (time, lecturer, room) │
   └─────────────────────────────────────────────────┘
                    │
                    ▼
   ┌──────────────────────────────────────────────────────┐
   │ 1. NO DOUBLE-BOOKING                                 │
   │    • Student group not busy at this time?            │
   │    • Lecturer not busy at this time?                 │
   │    • Room not busy at this time?                     │
   └──────────────────────────────────────────────────────┘
                    │ ✓ Pass
                    ▼
   ┌──────────────────────────────────────────────────────┐
   │ 2. ROOM CAPACITY (single group)                      │
   │    • Does room capacity >= current group size?       │
   └──────────────────────────────────────────────────────┘
                    │ ✓ Pass
                    ▼
   ┌──────────────────────────────────────────────────────┐
   │ 3. ROOM TYPE MATCHING                                │
   │    • Is room type correct for course type?           │
   │    (Lab → Lab room, Theory → Classroom/Lecture Hall) │
   └──────────────────────────────────────────────────────┘
                    │ ✓ Pass
                    ▼
   ┌──────────────────────────────────────────────────────┐
   │ 4. LECTURER SPECIALIZATION                           │
   │    • Already validated in domain initialization      │
   │    (Only qualified lecturers in available_lecturers) │
   └──────────────────────────────────────────────────────┘
                    │ ✓ Pass
                    ▼
   ┌──────────────────────────────────────────────────────┐
   │ 5. CLASS MERGING (THE MERGE RULE)                    │
   │                                                      │
   │    IF (other groups already assigned to this         │
   │         room/time slot):                             │
   │                                                      │
   │       Step 5.1: Get all assignments for this         │
   │                 room + time slot                     │
   │                                                      │
   │       Step 5.2: Calculate TOTAL students:            │
   │                 total = 0                            │
   │                 For each existing assignment:        │
   │                   total += group_size                │
   │                 total += current_group_size          │
   │                                                      │
   │       Step 5.3: Check capacity:                      │
   │                 IF total <= room_capacity:           │
   │                   ✓ ALLOW MERGE                      │
   │                 ELSE:                                │
   │                   ✗ REJECT (too many students)       │
   │                                                      │
   │    ELSE:                                             │
   │       ✓ No merge needed (first assignment)           │
   └──────────────────────────────────────────────────────┘
                    │ ✓ Pass
                    ▼
   ┌──────────────────────────────────────────────────────┐
   │ 6. CLASS SPLITTING                                   │
   │    • If group size > room capacity, must be split    │
   │    (Already handled by room capacity pre-filter)     │
   └──────────────────────────────────────────────────────┘
                    │ ✓ Pass
                    ▼
            ✅ ASSIGNMENT ACCEPTED
   ```

### Important Notes

1. **Room Type & Lecturer Specialization**: These are checked **BEFORE** merge checking:
   - Only rooms with correct type are considered
   - Only qualified lecturers are considered
   - These constraints are already satisfied when merge checking happens

2. **Merge Rule Only Checks Capacity**: The `ClassMergingConstraint` only validates:
   - That multiple groups in the same room/time have the same course (via merge preference)
   - That total students ≤ room capacity
   - It assumes room type and lecturer specialization are already correct

3. **Reactive vs Proactive**:
   - **Current (Reactive)**: Checks merge when assigning - if another group with same course is already in that room/time, allows merge if capacity allows
   - **Proactive Alternative**: Could identify all groups with same course upfront, sum students, find suitable room - but this is more complex and less flexible

### Example

**Scenario**: CS103 (Database Systems) is taken by:
- BSCAIT-126 (50 students)
- BSCAIT-226 (28 students)  
- BCS-126 (45 students)

**Total if merged**: 123 students

**Assignment Process**:
1. First group (BSCAIT-126, 50 students) assigned:
   - Finds Lab room (CS103 is Lab course)
   - Finds qualified lecturer (L028, L003, L013)
   - Assigned to Room 601 (Lab, capacity 88) at MON 14:00-16:00

2. Second group (BSCAIT-226, 28 students) tries same room/time:
   - Room type: ✓ (Lab)
   - Lecturer: ✓ (qualified)
   - Merge check: 50 + 28 = 78 ≤ 88 ✓
   - **MERGED** ✅

3. Third group (BCS-126, 45 students) tries same room/time:
   - Room type: ✓ (Lab)
   - Lecturer: ✓ (qualified)
   - Merge check: 78 + 45 = 123 > 88 ✗
   - **REJECTED** - must find different room/time

### Summary

**The merge rule:**
1. ✅ **Sums students** from groups taking the **same course**
2. ✅ **Checks if total ≤ room capacity**
3. ✅ **Room type** is already validated (pre-filtered)
4. ✅ **Lecturer specialization** is already validated (pre-filtered)

**But it does NOT:**
- Proactively find all groups with same course first
- Pre-calculate which rooms can handle the merged group
- Guarantee merging (depends on assignment order)

The merge preference logic I added will help prioritize merge opportunities when they exist!

