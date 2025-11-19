# Data Structures & Models Verification

## ✅ All Data Structures Properly Integrated

This document verifies that all data structures and models are correctly handled throughout the ISBAT Timetable Scheduling System.

---

## 📦 **Core Models (5 Models)**

### Location: `app/models/`

| Model | File | Purpose | Key Attributes |
|-------|------|---------|----------------|
| **Lecturer** | `lecturer.py` | Faculty/staff data | id, name, role, specializations, availability, max_weekly_hours |
| **Room** | `room.py` | Physical spaces | id, room_number, capacity, room_type, facilities |
| **CourseUnit** | `course.py` | Academic courses | id, code, name, weekly_hours, credits, is_lab, difficulty, prerequisites |
| **StudentGroup** | `student_group.py` | Student cohorts | id, batch, program, semester, term, size, course_units |
| **User** | `user.py` | System users | id, email, password_hash, role, department |

### Model Features
- ✅ All models use `@dataclass` for consistency
- ✅ All have `to_dict()` methods for serialization
- ✅ All have `from_dict()` static methods for deserialization
- ✅ Compatible with MongoDB storage
- ✅ Compatible with both object and dict access patterns

---

## 🔧 **CSP Data Structures**

### Location: `app/services/csp/`

#### 1. **TimeSlot** (`domain.py`)
```python
@dataclass
class TimeSlot:
    day: str              # MON, TUE, WED, THU, FRI
    period: str           # SLOT_1, SLOT_2, SLOT_3, SLOT_4
    start: str            # HH:MM format
    end: str              # HH:MM format
    is_afternoon: bool    # True for SLOT_3, SLOT_4
```

**Features:**
- Hashable for use in sets
- Convertible to dict
- Used in all scheduling operations

#### 2. **Assignment** (`domain.py`)
```python
@dataclass
class Assignment:
    variable_id: str
    course_unit_id: str
    student_group_id: str
    lecturer_id: str
    room_id: str
    time_slot: TimeSlot
    term: str
    session_number: int
```

**Usage:**
- Represents a complete session assignment
- Used by CSP engine for scheduling
- Converted to Gene objects for GGA
- Serializable to dict

#### 3. **SchedulingVariable** (`domain.py`)
```python
@dataclass
class SchedulingVariable:
    id: str
    course_unit_id: str
    student_group_id: str
    term: str
    session_number: int
    sessions_required: int
    
    # Domains
    available_time_slots: Set[TimeSlot]
    available_lecturers: Set[str]
    available_rooms: Set[str]
    
    # Current assignment
    assignment: Optional[Assignment]
```

**Features:**
- Maintains domains for CSP search
- Tracks assignment state
- Supports domain filtering

#### 4. **ConstraintContext** (`constraints.py`)
```python
class ConstraintContext:
    # O(1) indexed lookups
    lecturer_schedule: Dict[str, Dict[str, Set[str]]]
    room_schedule: Dict[str, Dict[str, Set[str]]]
    student_group_schedule: Dict[str, Dict[str, Set[str]]]
    
    # Daily tracking
    lecturer_daily_count: Dict[str, Dict[str, int]]
    lecturer_morning_used: Dict[str, Dict[str, bool]]
    lecturer_afternoon_used: Dict[str, Dict[str, bool]]
    
    # Weekly tracking
    lecturer_weekly_hours: Dict[str, float]
    
    # Same-day tracking
    unit_daily_schedule: Dict[tuple, Dict[str, bool]]
    
    # Resource data
    lecturers: Dict[str, Any]
    rooms: Dict[str, Any]
    course_units: Dict[str, Any]
    student_groups: Dict[str, Any]
```

**Features:**
- Efficient O(1) constraint checking
- Maintains all scheduling state
- Supports both dict and object model access
- Incremental updates during backtracking

---

## 🧬 **GGA Data Structures**

### Location: `app/services/gga/`

#### 1. **Gene** (`chromosome.py`)
```python
@dataclass
class Gene:
    session_id: str
    course_unit_id: str
    student_group_id: str
    lecturer_id: str
    room_id: str
    time_slot: Dict            # TimeSlot as dict
    term: str
    session_number: int
    
    # Metadata for optimization
    flexibility: float
    conflict_score: float
```

**Features:**
- Represents single session in chromosome
- Convertible to Assignment object
- Cloneable for genetic operations
- Tracks optimization metadata

#### 2. **Chromosome** (`chromosome.py`)
```python
@dataclass
class Chromosome:
    id: str
    genes: List[Gene]
    fitness: Optional[FitnessScore]
    generation: int
    age: int
```

**Features:**
- Complete timetable representation
- Created from CSP solution
- Manipulated by genetic operators
- Evaluated for fitness
- Grouping utilities (by student, lecturer, room, day)

#### 3. **FitnessScore** (both `chromosome.py` and `fitness.py`)
```python
@dataclass
class FitnessScore:
    overall_fitness: float
    student_idle_time: float
    lecturer_workload_balance: float
    room_utilization: float
    weekday_distribution: float
    breakdown: FitnessBreakdown
```

**Components:**
- Overall weighted fitness (0.0-1.0)
- Individual component scores
- Detailed breakdown for analysis

#### 4. **FitnessBreakdown** (`fitness.py`)
```python
@dataclass
class FitnessBreakdown:
    # Student metrics
    avg_gap_length: float
    max_gap_length: float
    students_with_long_gaps: int
    avg_daily_span: float
    
    # Lecturer metrics
    workload_std_dev: float
    overloaded_days: int
    
    # Room metrics
    avg_room_occupancy: float
    underutilized_rooms: int
    room_waste: float
    
    # Distribution metrics
    day_loads: List[int]
    day_load_variance: float
    empty_days: int
    back_to_back_long_days: int
```

---

## 🔄 **Data Flow & Integration**

### 1. **Model → CSP Engine**

```
Models (dataclass objects)
    ↓
CSPEngine.initialize(lecturers, rooms, course_units, student_groups)
    ↓
Stored as Dict[id, Model] for O(1) lookup
    ↓
Used to create SchedulingVariables
    ↓
DomainManager filters domains based on model attributes
    ↓
ConstraintContext receives model.to_dict() data
    ↓
Constraints check against dict representations
```

**Key Points:**
- Models converted to dicts for constraint checking
- Original objects retained for attribute access
- Both formats supported throughout

### 2. **CSP → GGA Pipeline**

```
CSP Assignment objects
    ↓
Chromosome.from_csp_solution(assignments)
    ↓
Creates Gene objects from assignments
    ↓
FitnessEvaluator receives resource dicts
    ↓
Converts Chromosome to evaluation dict format
    ↓
Evaluates fitness using model data
    ↓
GeneticOperators manipulate genes
    ↓
Uses model dicts for compatibility checking
```

**Key Points:**
- Assignment → Gene conversion preserves all data
- FitnessEvaluator handles both object and dict models
- GeneticOperators work with gene objects directly

### 3. **Resource Dictionary Format**

All engines receive resources as dictionaries:

```python
# Example lecturer dictionary entry
{
    'L001': Lecturer(
        id='L001',
        name='Dr. Jane Doe',
        role='Full-Time',
        specializations=['CS101', 'CS102'],
        max_weekly_hours=22
    )
}

# Can be accessed as:
lecturer = lecturers['L001']
lecturer.name                    # Object access
lecturer.to_dict()['name']       # Dict access
```

---

## ✅ **Integration Verification**

### CSP Engine Integration
| Component | Receives | Uses | Status |
|-----------|----------|------|--------|
| CSPEngine | Model objects | Creates dicts for constraints | ✅ |
| ConstraintContext | Model dicts | O(1) lookups | ✅ |
| ConstraintChecker | Context + models | Validates assignments | ✅ |
| DomainManager | Model objects | Filters domains | ✅ |

### GGA Engine Integration
| Component | Receives | Uses | Status |
|-----------|----------|------|--------|
| GGAEngine | Model dicts | Initializes evaluator & operators | ✅ |
| FitnessEvaluator | Model dicts + chromosome | Evaluates fitness | ✅ |
| GeneticOperators | Model dicts + chromosome | Manipulates genes | ✅ |
| Chromosome | Assignment objects | Creates genes | ✅ |

### API Layer Integration
| Component | Receives | Returns | Status |
|-----------|----------|---------|--------|
| Routes | JSON/dict | Model objects | ✅ |
| Models | Dict via `from_dict()` | Objects | ✅ |
| Database | Dict via `to_dict()` | MongoDB docs | ✅ |

---

## 🎯 **Dual Access Pattern**

The system supports **both object and dict access** throughout:

### Object Access
```python
lecturer = Lecturer(id='L001', name='Dr. Smith', ...)
name = lecturer.name                    # Direct attribute
specs = lecturer.specializations        # List access
qualified = lecturer.is_qualified_for('CS101')  # Method call
```

### Dict Access
```python
lecturer_dict = lecturer.to_dict()
name = lecturer_dict['name']           # Dict key
specs = lecturer_dict['specializations']  # List in dict
qualified = 'CS101' in lecturer_dict['specializations']  # Manual check
```

### Flexible Handlers
```python
# In FitnessEvaluator._chromosome_to_dict()
if hasattr(student_group, 'size'):
    group_size = student_group.size          # Object
else:
    group_size = student_group.get('size', 0)  # Dict

# In GeneticOperators._mutate_lecturer()
if hasattr(lecturer, 'specializations'):
    specs = lecturer.specializations         # Object
else:
    specs = lecturer.get('specializations', [])  # Dict
```

---

## 📊 **Data Structure Summary**

| Category | Count | Status | Notes |
|----------|-------|--------|-------|
| **Core Models** | 5 | ✅ | Lecturer, Room, CourseUnit, StudentGroup, User |
| **CSP Structures** | 4 | ✅ | TimeSlot, Assignment, SchedulingVariable, ConstraintContext |
| **GGA Structures** | 4 | ✅ | Gene, Chromosome, FitnessScore, FitnessBreakdown |
| **Constraint Classes** | 10 | ✅ | All hard constraints implemented |
| **Integration Points** | 8 | ✅ | Models ↔ CSP ↔ GGA ↔ API ↔ DB |

---

## 🔍 **Type Safety & Validation**

### Type Hints
```python
# All functions properly typed
def evaluate(self, chromosome: Chromosome) -> FitnessScore
def initialize(self, lecturers: List[Lecturer], ...)
def to_dict(self) -> Dict[str, Any]
```

### Validation
- ✅ Model creation validates required fields
- ✅ Constraints validate domain values
- ✅ Fitness evaluator handles missing data gracefully
- ✅ Operators check compatibility before mutations

---

## 🚀 **Performance Characteristics**

| Operation | Complexity | Data Structure | Notes |
|-----------|------------|----------------|-------|
| Constraint check | O(1) | Hash maps in ConstraintContext | Indexed lookups |
| Model access | O(1) | Dict[id, Model] | Direct key access |
| Domain filtering | O(D) | Sets | D = domain size |
| Fitness evaluation | O(S × G) | List iteration | S = sessions, G = groups |
| Genetic mutation | O(G) | List/gene access | G = genes to mutate |

---

## ✅ **Conclusion**

**All data structures and models are properly handled:**

1. ✅ **5 Core Models** - All implemented with consistent interfaces
2. ✅ **8 CSP Structures** - Efficient constraint checking & domain management
3. ✅ **4 GGA Structures** - Complete genetic algorithm support
4. ✅ **Dual Access Pattern** - Works with both objects and dicts
5. ✅ **Full Integration** - Seamless flow: API → Models → CSP → GGA → DB
6. ✅ **Type Safety** - Comprehensive type hints throughout
7. ✅ **Performance** - O(1) lookups, efficient algorithms
8. ✅ **Flexibility** - Handles dict and object formats interchangeably

**Status: ALL DATA STRUCTURES FULLY INTEGRATED** 🎉

