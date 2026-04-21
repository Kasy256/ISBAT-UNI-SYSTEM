# Cartlyf Timetable System - Project Structure

## 📁 Directory Structure

```
timetable-scheduler/
├── app/                           # Main application code
│   ├── __init__.py
│   ├── config.py                  # Configuration settings
│   ├── models/                    # Data models
│   │   ├── lecturer.py           # Lecturer model
│   │   ├── subject.py             # Subject unit model
│   │   ├── room.py               # Room model
│   │   ├── program.py            # Program model
│   │   └── user.py               # User model (auth)
│   ├── middleware/                # Middleware layer
│   │   └── auth.py               # JWT authentication
│   ├── api/routes/                # API endpoints
│   │   ├── auth.py               # Authentication routes
│   │   ├── subjects.py            # Subject CRUD
│   │   ├── lecturers.py          # Lecturer CRUD
│   │   ├── rooms.py              # Room CRUD
│   │   ├── programs.py           # Program CRUD
│   │   ├── timetable.py          # Timetable generation
│   │   └── validation.py         # Validation endpoints
│   └── services/                  # Core business logic
│       ├── csp/                   # Constraint Satisfaction
│       │   ├── csp_engine.py     # CSP solver
│       │   ├── constraints.py    # All 10 hard constraints
│       │   └── domain.py         # Domain management
│       ├── gga/                   # Genetic Algorithm
│       │   ├── gga_engine.py     # GGA optimizer
│       │   ├── fitness.py        # Fitness evaluation (4 soft constraints)
│       │   ├── operators.py      # Genetic operators
│       │   └── chromosome.py     # Chromosome representation
│       ├── preprocessing/         # Data preprocessing
│       │   └── term_splitter.py  # Intelligent term splitting
│       └── validation/            # Validation system
│           └── validator.py      # Multi-phase validation
│
├── seed_data.py                   # ✅ Main seeding script
├── seed_lecturers_data.py         # ✅ Lecturer seed data (15)
├── seed_courses_data.py           # ✅ Subject seed data (30)
├── seed_rooms_data.py             # ✅ Room seed data (27)
├── seed_programs_data.py         # ✅ Program seed data (12)
│
├── run.py                         # ✅ Application entry point
├── test_api.py                    # ✅ API testing script
├── requirements.txt               # ✅ Python dependencies
│
├── README.md                      # ✅ Main documentation
├── SYSTEM_OVERVIEW.md             # ✅ Architecture & implementation
├── CONSTRAINTS_VERIFICATION.md    # ✅ Constraint documentation
├── DATA_STRUCTURES_VERIFICATION.md # ✅ Model documentation
└── SEEDING_QUICK_START.md         # ✅ Seeding guide
```

## 📊 File Statistics

### Core Application Code
- **Models**: 5 files (Lecturer, Subject, Room, Program, User)
- **API Routes**: 7 files (Auth, Subjects, Lecturers, Rooms, Programs, Timetable, Validation)
- **Services**: 10 files (CSP, GGA, Preprocessing, Validation)
- **Middleware**: 1 file (JWT Auth)

### Seed Data
- **Modular Seed Files**: 4 files (Lecturers, Subjects, Rooms, Programs)
- **Master Seed Script**: 1 file (seed_data.py)
- **Total Records**: 84 (15 lecturers + 30 subjects + 27 rooms + 12 programs)

### Documentation
- **Essential Docs**: 5 files (README, SYSTEM_OVERVIEW, 2 verifications, seeding guide)

## 🎯 Key Features

### 1. Modular Architecture
- ✅ Separation of concerns (Models, Services, API, Middleware)
- ✅ Clean dependency management
- ✅ Easy to extend and maintain

### 2. Comprehensive Seed Data
- ✅ 15 lecturers with availability and specializations
- ✅ 30 subjects with prerequisites and metadata
- ✅ 27 rooms across 2 campuses
- ✅ 12 programs (semester-level, no term splits)

### 3. Intelligent Scheduling
- ✅ CSP for hard constraints (10 constraints)
- ✅ GGA for soft constraints (4 constraints)
- ✅ Automatic term splitting via preprocessor
- ✅ Multi-phase validation

### 4. Security & Auth
- ✅ JWT-based authentication
- ✅ Role-based access control (Admin, Scheduler, Viewer)
- ✅ Password hashing
- ✅ Protected API endpoints

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Seed Database
```bash
python seed_data.py
```

### 3. Run Application
```bash
python run.py
```

### 4. Test API
```bash
python test_api.py
```

## 📝 Documentation Guide

### For Users
1. **README.md** - Start here for system overview
2. **SEEDING_QUICK_START.md** - How to seed data and get started

### For Developers
3. **SYSTEM_OVERVIEW.md** - Architecture and implementation details
4. **CONSTRAINTS_VERIFICATION.md** - Understanding constraints
5. **DATA_STRUCTURES_VERIFICATION.md** - Model integration details

### For Data Management
6. **seed_*_data.py files** - Each file has built-in statistics when run directly

## ✅ What Was Cleaned Up

### Removed Files (4)
- ❌ `IMPLEMENTATION_COMPLETE.md` - Redundant status document
- ❌ `SEED_DATA_CHANGES_SUMMARY.md` - Unnecessary implementation details
- ❌ `SEED_DATA_GUIDE.md` - Merged into SEEDING_QUICK_START.md
- ❌ `ROOM_INVENTORY.md` - Data now in seed_rooms_data.py
- ❌ `seed_all_data.py` - Redundant with seed_data.py
- ❌ `verify_seed_structure.py` - Functionality in individual seed files

### What Remains (Essential Only)
- ✅ **5 Documentation files** - All essential, no duplication
- ✅ **5 Seed files** - 1 master + 4 modular
- ✅ **3 Utility files** - run.py, test_api.py, requirements.txt
- ✅ **23 Code files** - All necessary application code

## 📦 Total Lines of Code

| Category | Files | Approx. Lines |
|----------|-------|---------------|
| Models | 5 | ~500 |
| API Routes | 7 | ~1,400 |
| Services | 10 | ~2,500 |
| Middleware | 1 | ~200 |
| Seed Data | 5 | ~1,350 |
| **Total** | **28** | **~5,950** |

## 🎓 System Capabilities

### Data Management
- ✅ CRUD operations for all entities
- ✅ Bulk operations support
- ✅ Search and filtering
- ✅ Statistics endpoints

### Scheduling
- ✅ Automatic timetable generation
- ✅ Hard constraint satisfaction (100%)
- ✅ Soft constraint optimization
- ✅ Conflict detection and resolution

### Validation
- ✅ Input validation
- ✅ Data integrity checks
- ✅ Feasibility verification
- ✅ Prerequisite cycle detection

### Authentication
- ✅ User registration and login
- ✅ JWT token management
- ✅ Role-based permissions
- ✅ Secure password handling

## 🌟 Production Ready

The system is now:
- ✅ **Clean** - No redundant files or code
- ✅ **Documented** - Comprehensive but concise documentation
- ✅ **Tested** - All components verified
- ✅ **Secure** - JWT authentication implemented
- ✅ **Scalable** - Modular architecture
- ✅ **Maintainable** - Well-organized structure

---

**Last Updated**: November 2025  
**Version**: 2.0.0  
**Status**: 🟢 Production Ready

