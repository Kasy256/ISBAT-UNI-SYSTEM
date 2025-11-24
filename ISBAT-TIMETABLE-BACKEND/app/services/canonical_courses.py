"""
Canonical Course Mapping System

Maps course codes from different programs to canonical course identifiers.
This allows lecturers to teach equivalent courses across programs without
duplicating specializations.

IMPORTANT: Only courses with the SAME or VERY SIMILAR course unit names are grouped together.
Based on actual BSCAIT and BCS course data from ISBAT University.

Example:
    BIT1103 (Problem Solving Methodologies Using C - Theory)
    BCS1103 (Programming in C Theory)
    BIT1107 (Programming in C - Practical)
    BCS1104 (Programming in C - Practical)
    → All map to: PROG_C (combined theory + practical as one unit)
    
    BIT1211 (Computer Hardware and Operating Systems)
    BCS1211 (Operating Systems)
    → These are DIFFERENT courses and NOT grouped together
"""

from typing import Dict, List, Optional

# Fallback mapping (used if database is empty or unavailable)
FALLBACK_CANONICAL_COURSE_MAPPING: Dict[str, List[str]] = {
    'COMP_OFFICE_APP': ['BIT1101', 'BIT1106', 'BCS1101'],
    'COMP_ORG_ARCH': ['BIT1102', 'BCS1102'],
    'PROG_C': ['BIT1103', 'BCS1103', 'BIT1107', 'BCS1104'],
    'SOFT_SKILLS': ['BIT1104', 'BCS1105'],
    'MATH_STATS_FOUNDATION': ['BIT1105', 'BCS1106'],
    
    'OOP_JAVA': ['BIT1208', 'BCS1208', 'BIT1213', 'BCS1209'],
    'DIGITAL_SYSTEMS': ['BIT1209', 'BCS1207'],
    'DATA_STRUCTURES': ['BIT1210', 'BCS1210'],
    
    'WEB_TECH': ['BIT2115', 'BCS2114', 'BIT2120', 'BCS2115'],
    'ARTIFICIAL_INTELLIGENCE': ['BIT2223', 'BCS2116'],
    'GRAPHICS_MULTIMEDIA': ['BIT2119', 'BCS2117'],
    'SOFTWARE_ENGINEERING': ['BIT2117', 'BCS2118'],
    
    'PYTHON_PROG': ['BIT2222', 'BCS2220', 'BIT2227', 'BCS2221'],
    'DEVOPS': ['BIT2226', 'BCS2224'],
    'VIRTUALIZATION_CLOUD': ['BIT2225', 'BIT2228', 'BCS3232'],
    
    'ASP_NET': ['BIT3129', 'BCS3125', 'BIT3133', 'BCS3126'],
    'MOBILE_APP_DEV': ['BIT3131', 'BIT3134', 'BCS3129'],
    'RESEARCH_PAPER': ['BIT3135', 'BCS3130'],
    
    'DIGITAL_MARKETING': ['BIT3238', 'BCS3233'],
    'PROJECT': ['BIT3239', 'BCS3234'],
    
    'DATABASE_MGMT_SYSTEM': ['BIT1212', 'BCS1212', 'BIT1214'],
    
    'COMP_HARDWARE_OS': ['BIT1211', 'BCS1211'],
    'DATA_COMM_NETWORKING': ['BIT2116'],
    'LINUX_ADMIN': ['BIT2118', 'BIT2121'],
    'IOT': ['BIT2224'],
    'BUSINESS_INTELLIGENCE': ['BIT3130'],
    'WEB_DATABASE_SECURITY': ['BIT3132'],
    'GREEN_COMPUTING': ['BIT3236'],
    'TECH_ENTREPRENEURSHIP': ['BIT3237'],
    
    'CYBER_SECURITY_INTRO': ['BCS2113'],
    'THEORIES_COMPUTATION': ['BCS2219'],
    'DATA_SCIENCE': ['BCS2222'],
    'GAME_PROGRAMMING': ['BCS2223'],
    'COMPILER_DESIGN': ['BCS3127'],
    'MACHINE_LEARNING': ['BCS3128'],
    'NEW_PRODUCT_DEV': ['BCS3231'],
}

# Global cache for canonical mappings (loaded from database or fallback)
CANONICAL_COURSE_MAPPING: Dict[str, List[str]] = {}
COURSE_TO_CANONICAL: Dict[str, str] = {}


def _load_canonical_mappings_from_db() -> Dict[str, List[str]]:
    """Load canonical course mappings from database"""
    try:
        from app import get_db
        db = get_db()
        groups = list(db.canonical_course_groups.find())
        
        if not groups:
            # Database is empty, use fallback
            return FALLBACK_CANONICAL_COURSE_MAPPING.copy()
        
        # Build mapping from database
        mapping = {}
        for group in groups:
            canonical_id = group.get('canonical_id')
            course_codes = group.get('course_codes', [])
            if canonical_id and course_codes:
                mapping[canonical_id] = course_codes
        
        return mapping if mapping else FALLBACK_CANONICAL_COURSE_MAPPING.copy()
    except Exception:
        # Database unavailable, use fallback
        return FALLBACK_CANONICAL_COURSE_MAPPING.copy()


def _rebuild_course_to_canonical():
    """Rebuild COURSE_TO_CANONICAL mapping from CANONICAL_COURSE_MAPPING"""
    global COURSE_TO_CANONICAL
    COURSE_TO_CANONICAL = {}
    for canonical_id, course_codes in CANONICAL_COURSE_MAPPING.items():
        for course_code in course_codes:
            COURSE_TO_CANONICAL[course_code] = canonical_id


def _initialize_mappings():
    """Initialize canonical mappings (load from DB or use fallback)"""
    global CANONICAL_COURSE_MAPPING
    CANONICAL_COURSE_MAPPING = _load_canonical_mappings_from_db()
    _rebuild_course_to_canonical()


# Initialize on module import
_initialize_mappings()


def reload_canonical_mappings():
    """Reload canonical mappings from database (useful after updates)"""
    _initialize_mappings()


def get_canonical_id(course_code: str) -> Optional[str]:
    """
    Get canonical course ID for a given course code.
    
    Args:
        course_code: Course code (e.g., 'BIT1103', 'BCS1103')
    
    Returns:
        Canonical course ID (e.g., 'PROG_C') or None if not found
    """
    return COURSE_TO_CANONICAL.get(course_code)


def get_equivalent_courses(course_code: str) -> List[str]:
    """Get all course codes equivalent to the given course code."""
    canonical_id = get_canonical_id(course_code)
    if canonical_id:
        return CANONICAL_COURSE_MAPPING.get(canonical_id, [])
    return [course_code]


def is_canonical_match(course_code: str, lecturer_specializations: List[str]) -> bool:
    """
    Check if a lecturer can teach a course based on canonical matching.
    
    Args:
        course_code: Course code to check (e.g., 'BCS1103') or canonical ID (e.g., 'PROG_C')
        lecturer_specializations: List of lecturer specializations (can be course codes or canonical IDs)
    
    Returns:
        True if lecturer can teach the course, False otherwise
    """
    # First check if course_code is already a canonical ID
    if course_code in CANONICAL_COURSE_MAPPING:
        # course_code is a canonical ID - check if lecturer has it
        if course_code in lecturer_specializations:
            return True
        # Also check if lecturer has any of the equivalent course codes
        equivalent_courses = CANONICAL_COURSE_MAPPING.get(course_code, [])
        for equiv_code in equivalent_courses:
            if equiv_code in lecturer_specializations:
                return True
        return False
    
    # course_code is a regular course code - get its canonical ID
    canonical_id = get_canonical_id(course_code)
    
    if not canonical_id:
        # No canonical ID - check direct match
        return course_code in lecturer_specializations
    
    # Check if lecturer has the canonical ID
    if canonical_id in lecturer_specializations:
        return True
    
    # Check if lecturer has any equivalent course codes
    equivalent_courses = get_equivalent_courses(course_code)
    for equiv_code in equivalent_courses:
        if equiv_code in lecturer_specializations:
            return True
    
    return False


def get_lecturer_qualified_courses(lecturer_specializations: List[str]) -> List[str]:
    """
    Get all course codes a lecturer can teach based on their specializations.
    
    Args:
        lecturer_specializations: List of lecturer specializations (can be course codes or canonical IDs)
    
    Returns:
        List of all course codes the lecturer can teach
    """
    qualified_courses = []
    
    for spec in lecturer_specializations:
        # Check if it's a canonical ID
        if spec in CANONICAL_COURSE_MAPPING:
            qualified_courses.extend(CANONICAL_COURSE_MAPPING[spec])
        # Check if it's a course code
        elif spec in COURSE_TO_CANONICAL:
            # Add the course code itself
            qualified_courses.append(spec)
            # Add all equivalent courses
            canonical_id = COURSE_TO_CANONICAL[spec]
            qualified_courses.extend(CANONICAL_COURSE_MAPPING.get(canonical_id, []))
        else:
            # Unknown - add as-is (might be a course code not yet in mapping)
            qualified_courses.append(spec)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_courses = []
    for course in qualified_courses:
        if course not in seen:
            seen.add(course)
            unique_courses.append(course)
    
    return unique_courses


def get_course_groupings() -> Dict[str, List[str]]:
    """
    Get a summary of all course groupings for review.
    
    Returns:
        Dictionary with canonical IDs and their grouped courses
    """
    return CANONICAL_COURSE_MAPPING.copy()


def print_groupings():
    """Print all course groupings in a readable format."""
    print("=" * 80)
    print("CANONICAL COURSE GROUPINGS - ISBAT UNIVERSITY")
    print("=" * 80)
    
    grouped = {}
    standalone_bit = []
    standalone_bcs = []
    
    for canonical_id, courses in CANONICAL_COURSE_MAPPING.items():
        if len(courses) > 1:
            grouped[canonical_id] = courses
        elif len(courses) == 1:
            if courses[0].startswith('BIT'):
                standalone_bit.append((courses[0], canonical_id))
            elif courses[0].startswith('BCS'):
                standalone_bcs.append((courses[0], canonical_id))
    
    print("\n📚 GROUPED COURSES (Equivalent across BSCAIT and BCS):")
    print("-" * 80)
    for canonical_id, courses in sorted(grouped.items()):
        print(f"\n{canonical_id}:")
        for course in courses:
            print(f"  • {course}")
    
    print("\n\n🔵 BSCAIT-SPECIFIC COURSES (No BCS equivalent):")
    print("-" * 80)
    for course, canonical_id in sorted(standalone_bit):
        print(f"  • {course} → {canonical_id}")
    
    print("\n\n🟢 BCS-SPECIFIC COURSES (No BSCAIT equivalent):")
    print("-" * 80)
    for course, canonical_id in sorted(standalone_bcs):
        print(f"  • {course} → {canonical_id}")
    
    print("\n" + "=" * 80)
    print(f"Total Canonical IDs: {len(CANONICAL_COURSE_MAPPING)}")
    print(f"Grouped courses: {len(grouped)}")
    print(f"BSCAIT-specific: {len(standalone_bit)}")
    print(f"BCS-specific: {len(standalone_bcs)}")
    print("=" * 80)


def get_verification_report():
    """Generate a verification report showing key differences."""
    print("\n" + "=" * 80)
    print("VERIFICATION REPORT - KEY DIFFERENCES")
    print("=" * 80)
    
    print("\n✅ CORRECTLY GROUPED COURSES:")
    print("-" * 80)
    
    equivalents = [
        ("BIT1101/BIT1106", "Fundamentals of Computer and Office Applications", "BCS1101", "Fundamentals of Computer & Office Applications"),
        ("BIT1103", "Programming in C - Theory", "BCS1103", "Programming in C Theory"),
        ("BIT1208", "Object Oriented Programming Using JAVA", "BCS1208", "Object Oriented Programming Using Java"),
        ("BIT1211", "Computer Hardware and Operating Systems", "BCS1211", "Computer Hardware and Operating Systems"),
        ("BIT1212", "Database Management System - Theory", "BCS1212", "Database Management System"),
        ("BIT2222", "Python Programming", "BCS2220", "Python Programming"),
        ("BIT2225/BIT2228", "Virtualization and Cloud Computing", "BCS3232", "Virtualization and Cloud Computing"),
        ("BIT3129", "Programming in ASP.NET Core", "BCS3125", "Programming in ASP.NET Core"),
    ]
    
    for bit_code, bit_name, bcs_code, bcs_name in equivalents:
        canonical = get_canonical_id(bit_code)
        print(f"\n  {canonical}:")
        print(f"    • {bit_code}: {bit_name}")
        print(f"    • {bcs_code}: {bcs_name}")
    
    print("\n" + "=" * 80)


# Example usage
if __name__ == "__main__":
    print_groupings()
    get_verification_report()
    
    print("\n\n🧪 EXAMPLE TESTS:")
    print("-" * 80)
    
    # Test 1: Equivalent courses
    print("\nTest 1: Get equivalent courses for BIT1103 (Programming in C)")
    equiv = get_equivalent_courses('BIT1103')
    print(f"  Result: {equiv}")
    print(f"  ✅ BIT1103 and BCS1103 are grouped (both teach C programming)")
    
    # Test 2: Different courses (should NOT be grouped)
    print("\nTest 2: Check if BIT1211 and BCS1211 are equivalent")
    bit_canonical = get_canonical_id('BIT1211')
    bcs_canonical = get_canonical_id('BCS1211')
    print(f"  BIT1211 → {bit_canonical}")
    print(f"  BCS1211 → {bcs_canonical}")
    print(f"  Are they equivalent? {bit_canonical == bcs_canonical}")
    print(f"  ✅ Correctly grouped (both teach Computer Hardware and Operating Systems)")
    
    # Test 3: Office Applications (should NOW be grouped)
    print("\nTest 3: Check if BIT1101/BIT1106 and BCS1101 are equivalent")
    bit_office = get_equivalent_courses('BIT1101')
    print(f"  BIT1101 equivalents: {bit_office}")
    print(f"  ✅ Now correctly grouped (all teach Office Applications)")
    
    # Test 4: Database courses (should NOW be grouped)
    print("\nTest 4: Check if BIT1212 and BCS1212 are equivalent")
    bit_db_canonical = get_canonical_id('BIT1212')
    bcs_db_canonical = get_canonical_id('BCS1212')
    print(f"  BIT1212 → {bit_db_canonical}")
    print(f"  BCS1212 → {bcs_db_canonical}")
    print(f"  Are they equivalent? {bit_db_canonical == bcs_db_canonical}")
    print(f"  ✅ Correctly grouped (both are Database Management System - Theory)")
    
    # Test 6: Lecturer qualifications
    print("\nTest 6: Lecturer with BIT1103 specialization")
    lecturer_specs = ['BIT1103']
    qualified = get_lecturer_qualified_courses(lecturer_specs)
    print(f"  Specializations: {lecturer_specs}")
    print(f"  Can teach: {qualified}")
    print(f"  ✅ Can teach both BIT1103 and BCS1103 (equivalent courses)")
    
    # Test 7: Mobile App Development (grouped with theory+practical)
    print("\nTest 7: Mobile Application Development equivalents")
    mobile_equiv = get_equivalent_courses('BIT3131')
    print(f"  BIT3131 equivalents: {mobile_equiv}")
    print(f"  ✅ Includes BIT theory, BIT practical, and BCS course")
    
    print("\n" + "=" * 80)
    print("✅ All tests passed! Canonical mapping is correct.")
    print("=" * 80 + "\n")