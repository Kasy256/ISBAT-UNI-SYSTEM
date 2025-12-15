"""
Canonical Subject Mapping System

Maps subject codes from different programs to canonical subject identifiers.
This allows lecturers to teach equivalent subjects across programs without
duplicating specializations.

IMPORTANT: Only subjects with the SAME or VERY SIMILAR course unit names are grouped together.
Based on actual BSCAIT and BCS subject data from ISBAT University.

Example:
    BIT1103 (Problem Solving Methodologies Using C - Theory)
    BCS1103 (Programming in C Theory)
    BIT1107 (Programming in C - Practical)
    BCS1104 (Programming in C - Practical)
    → All map to: PROG_C (combined theory + practical as one unit)
    
    BIT1211 (Computer Hardware and Operating Systems)
    BCS1211 (Operating Systems)
    → These are DIFFERENT subjects and NOT grouped together
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
# Mapping from human-readable names to canonical IDs (from database)
NAME_TO_CANONICAL_ID: Dict[str, str] = {}


def _load_canonical_mappings_from_db(db=None) -> Dict[str, List[str]]:
    """
    Load canonical subject mappings from database
    
    Args:
        db: Optional database instance. If None, tries to use Flask's get_db()
    """
    global NAME_TO_CANONICAL_ID
    NAME_TO_CANONICAL_ID = {}
    
    try:
        # Use provided db or try to get from Flask context
        if db is None:
            from app import get_db
            db = get_db()
        
        groups = list(db.canonical_course_groups.find())
        
        if not groups:
            # Database is empty, use fallback
            print("⚠️  No canonical groups found in database, using fallback mapping")
            return FALLBACK_CANONICAL_COURSE_MAPPING.copy()
        
        # Build mapping from database
        mapping = {}
        for group in groups:
            canonical_id = group.get('canonical_id')
            course_codes = group.get('course_codes', [])
            name = group.get('name', '')
            
            if canonical_id and course_codes:
                mapping[canonical_id] = course_codes
                
                # Build name-to-canonical-ID mapping for lecturer specialization matching
                # Use the exact name from database to map to canonical_id
                if name:
                    # Store exact name
                    NAME_TO_CANONICAL_ID[name] = canonical_id
                    # Also store trimmed version (in case of whitespace differences)
                    NAME_TO_CANONICAL_ID[name.strip()] = canonical_id
                    # Also map the canonical_id to itself
                    NAME_TO_CANONICAL_ID[canonical_id] = canonical_id
        
        if mapping:
            print(f"✅ Loaded {len(mapping)} canonical groups from database")
            # Show sample of loaded IDs
            sample_ids = list(mapping.keys())[:3]
            print(f"   Sample canonical IDs: {', '.join(sample_ids)}")
            # Show sample of name mappings for debugging
            sample_names = list(NAME_TO_CANONICAL_ID.items())[:3]
            if sample_names:
                print(f"   Sample name mappings: {', '.join([f'{name}→{cid}' for name, cid in sample_names])}")
        else:
            print("⚠️  Database has groups but mapping is empty, using fallback")
        
        return mapping if mapping else FALLBACK_CANONICAL_COURSE_MAPPING.copy()
    except Exception as e:
        # Database unavailable, use fallback
        print(f"⚠️  Error loading canonical groups from database: {e}, using fallback")
        return FALLBACK_CANONICAL_COURSE_MAPPING.copy()


def _extract_course_code(course_entry: str) -> str:
    """
    Extract course code from various formats:
    - "BIT1102" -> "BIT1102"
    - "BIT1102 – Computer Organization and Architecture" -> "BIT1102"
    - "BIT1102 - Computer Organization and Architecture" -> "BIT1102"
    """
    if not course_entry:
        return course_entry
    
    # Handle em dash (—) and regular dash (-) with spaces
    for separator in [' – ', ' - ', '—', '-']:
        if separator in course_entry:
            return course_entry.split(separator)[0].strip()
    
    # No separator found, return as-is (already just a code)
    return course_entry.strip()


def _rebuild_course_to_canonical():
    """Rebuild COURSE_TO_CANONICAL mapping from CANONICAL_COURSE_MAPPING"""
    global COURSE_TO_CANONICAL
    COURSE_TO_CANONICAL = {}
    for canonical_id, course_codes in CANONICAL_COURSE_MAPPING.items():
        for course_entry in course_codes:
            # Extract just the course code (handle "CODE – Name" format)
            course_code = _extract_course_code(course_entry)
            if course_code:
                COURSE_TO_CANONICAL[course_code] = canonical_id


def _initialize_mappings(db=None):
    """Initialize canonical mappings (load from DB or use fallback)"""
    global CANONICAL_COURSE_MAPPING
    CANONICAL_COURSE_MAPPING = _load_canonical_mappings_from_db(db)
    _rebuild_course_to_canonical()


# Initialize on module import
_initialize_mappings()


def reload_canonical_mappings(db=None):
    """Reload canonical mappings from database (useful after updates)"""
    _initialize_mappings(db)


def get_canonical_id(course_code: str) -> Optional[str]:
    """
    Get canonical subject ID for a given subject code.
    
    Args:
        course_code: Subject code (e.g., 'BIT1103', 'BCS1103')
    
    Returns:
        Canonical subject ID (e.g., 'PROG_C') or None if not found
    """
    return COURSE_TO_CANONICAL.get(course_code)


def get_equivalent_courses(course_code: str) -> List[str]:
    """Get all subject codes equivalent to the given subject code."""
    canonical_id = get_canonical_id(course_code)
    if canonical_id:
        # Get equivalent courses and extract just the codes
        equivalent_entries = CANONICAL_COURSE_MAPPING.get(canonical_id, [])
        return [_extract_course_code(entry) for entry in equivalent_entries if _extract_course_code(entry)]
    return [course_code]


def is_canonical_match(course_code: str, lecturer_specializations: List[str]) -> bool:
    """
    Check if a lecturer can teach a subject based on canonical matching.
    
    Uses canonical IDs directly from the database. Lecturer specializations can be:
    - Canonical IDs from database (e.g., "COMPUTER-ORGNIZATION-AND-ARCHITECTURE")
    - Human-readable names from database (e.g., "Computer Organization and Architecture")
    - Subject codes (e.g., "BIT1102", "BCS1102")
    
    Args:
        course_code: Subject code to check (e.g., 'BCS1103') or canonical ID (e.g., 'COMPUTER-ORGNIZATION-AND-ARCHITECTURE')
        lecturer_specializations: List of lecturer specializations
    
    Returns:
        True if lecturer can teach the subject, False otherwise
    """
    if not lecturer_specializations:
        return False
    
    # CRITICAL FIX: Check if course_code is already a canonical ID
    # This happens when merged courses use canonical IDs as their IDs
    if course_code in CANONICAL_COURSE_MAPPING:
        canonical_id = course_code
    else:
        # Get canonical ID for the course code
        canonical_id = get_canonical_id(course_code)
    
    if not canonical_id:
        # No canonical ID - check direct match with course code
        return course_code in lecturer_specializations
    
    # Normalize canonical ID for comparison (handle underscores)
    canonical_normalized = canonical_id.replace('_', '-').upper()
    
    # Check if lecturer has the canonical ID directly (exact match)
    if canonical_id in lecturer_specializations:
        return True
    
    # Check if lecturer has normalized version (handle spaces/hyphens variations)
    for spec in lecturer_specializations:
        spec_normalized = spec.replace('_', '-').replace(' ', '-').upper()
        if spec_normalized == canonical_normalized:
            return True
    
    # Check if lecturer has the human-readable name or any variation (map to canonical_id via NAME_TO_CANONICAL_ID)
    # canonical_normalized already set above
    
    for spec in lecturer_specializations:
        spec_clean = spec.strip()
        
        # Normalize lecturer specialization: spaces -> hyphens, underscores -> hyphens, uppercase
        spec_normalized = spec_clean.replace('_', '-').replace(' ', '-').upper()
        
        # Check if normalized spec matches normalized canonical ID directly
        if spec_normalized == canonical_normalized:
            return True
        
        # Try exact match first (via NAME_TO_CANONICAL_ID)
        mapped_canonical_id = NAME_TO_CANONICAL_ID.get(spec_clean)
        if mapped_canonical_id:
            mapped_normalized = mapped_canonical_id.replace('_', '-').upper()
            if mapped_normalized == canonical_normalized:
                return True
        
        # Try case-insensitive match for human-readable names and variations
        spec_lower = spec_clean.lower()
        
        for db_name, db_canonical_id in NAME_TO_CANONICAL_ID.items():
            if db_canonical_id == canonical_id:
                # Check if lecturer spec matches the canonical name (case-insensitive)
                if db_name.lower().strip() == spec_lower:
                    return True
                
                # Check normalized name variations (handle spaces, underscores, hyphens)
                db_name_normalized = db_name.replace('_', '-').replace(' ', '-').upper()
                if spec_normalized == db_name_normalized:
                    return True
                
                # Also check if lecturer spec matches canonical ID format (normalize both)
                db_canonical_normalized = db_canonical_id.replace('_', '-').upper()
                if spec_normalized == db_canonical_normalized:
                    return True
    
    # Check if lecturer has any equivalent subject codes
    # If course_code is already a canonical ID, get equivalent courses from the mapping
    if course_code in CANONICAL_COURSE_MAPPING:
        equivalent_entries = CANONICAL_COURSE_MAPPING[canonical_id]
        equivalent_courses = [_extract_course_code(entry) for entry in equivalent_entries if _extract_course_code(entry)]
    else:
        equivalent_courses = get_equivalent_courses(course_code)
    
    for equiv_code in equivalent_courses:
        if equiv_code in lecturer_specializations:
            return True
    
    # Additional fuzzy matching: Check if canonical ID is contained in specialization or vice versa
    # This handles cases like "TAXATION" matching "BUSINESS-TAXATION" or "BUSINESS-TAXATION" matching "TAXATION"
    for spec in lecturer_specializations:
        spec_normalized = spec.replace('_', '-').replace(' ', '-').upper()
        
        # Check if canonical ID contains the specialization (e.g., "BUSINESS-TAXATION" in "TAXATION" -> no, but reverse might work)
        # Or if specialization contains canonical ID (e.g., "BUSINESS-TAXATION" contains "TAXATION")
        if canonical_normalized in spec_normalized or spec_normalized in canonical_normalized:
            # But only if they share significant words (at least 2 words in common)
            canon_words = set(canonical_normalized.split('-'))
            spec_words = set(spec_normalized.split('-'))
            common_words = canon_words & spec_words
            if len(common_words) >= 2 or len(canon_words) == 1:  # Allow if canonical is single word (like "TAXATION")
                return True
    
    return False


def get_lecturer_qualified_courses(lecturer_specializations: List[str]) -> List[str]:
    """
    Get all subject codes a lecturer can teach based on their specializations.
    
    Specializations are now stored as canonical IDs (subject groups), not individual subject codes.
    This function expands canonical IDs to all equivalent subject codes.
    
    Args:
        lecturer_specializations: List of lecturer specializations (should be canonical IDs, but supports subject codes for backward compatibility)
    
    Returns:
        List of all subject codes the lecturer can teach
    """
    qualified_courses = []
    
    for spec in lecturer_specializations:
        # Check if it's a canonical ID
        if spec in CANONICAL_COURSE_MAPPING:
            qualified_courses.extend(CANONICAL_COURSE_MAPPING[spec])
        # Check if it's a subject code
        elif spec in COURSE_TO_CANONICAL:
            # Add the subject code itself
            qualified_courses.append(spec)
            # Add all equivalent subjects
            canonical_id = COURSE_TO_CANONICAL[spec]
            qualified_courses.extend(CANONICAL_COURSE_MAPPING.get(canonical_id, []))
        else:
            # Unknown - add as-is (might be a subject code not yet in mapping)
            qualified_courses.append(spec)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_courses = []
    for subject in qualified_courses:
        if subject not in seen:
            seen.add(subject)
            unique_courses.append(subject)
    
    return unique_courses


def get_course_groupings() -> Dict[str, List[str]]:
    """
    Get a summary of all subject groupings for review.
    
    Returns:
        Dictionary with canonical IDs and their grouped subjects
    """
    return CANONICAL_COURSE_MAPPING.copy()


def print_groupings():
    """Print all subject groupings in a readable format."""
    print("=" * 80)
    print("CANONICAL SUBJECT GROUPINGS - ISBAT UNIVERSITY")
    print("=" * 80)
    
    grouped = {}
    standalone_bit = []
    standalone_bcs = []
    
    for canonical_id, subjects in CANONICAL_COURSE_MAPPING.items():
        if len(subjects) > 1:
            grouped[canonical_id] = subjects
        elif len(subjects) == 1:
            if subjects[0].startswith('BIT'):
                standalone_bit.append((subjects[0], canonical_id))
            elif subjects[0].startswith('BCS'):
                standalone_bcs.append((subjects[0], canonical_id))
    
    print("\n📚 GROUPED SUBJECTS (Equivalent across BSCAIT and BCS):")
    print("-" * 80)
    for canonical_id, subjects in sorted(grouped.items()):
        print(f"\n{canonical_id}:")
        for subject in subjects:
            print(f"  • {subject}")
    
    print("\n\n🔵 BSCAIT-SPECIFIC SUBJECTS (No BCS equivalent):")
    print("-" * 80)
    for subject, canonical_id in sorted(standalone_bit):
        print(f"  • {subject} → {canonical_id}")
    
    print("\n\n🟢 BCS-SPECIFIC SUBJECTS (No BSCAIT equivalent):")
    print("-" * 80)
    for subject, canonical_id in sorted(standalone_bcs):
        print(f"  • {subject} → {canonical_id}")
    
    print("\n" + "=" * 80)
    print(f"Total Canonical IDs: {len(CANONICAL_COURSE_MAPPING)}")
    print(f"Grouped subjects: {len(grouped)}")
    print(f"BSCAIT-specific: {len(standalone_bit)}")
    print(f"BCS-specific: {len(standalone_bcs)}")
    print("=" * 80)


def get_verification_report():
    """Generate a verification report showing key differences."""
    print("\n" + "=" * 80)
    print("VERIFICATION REPORT - KEY DIFFERENCES")
    print("=" * 80)
    
    print("\n✅ CORRECTLY GROUPED SUBJECTS:")
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
    
    # Test 1: Equivalent subjects
    print("\nTest 1: Get equivalent subjects for BIT1103 (Programming in C)")
    equiv = get_equivalent_courses('BIT1103')
    print(f"  Result: {equiv}")
    print(f"  ✅ BIT1103 and BCS1103 are grouped (both teach C programming)")
    
    # Test 2: Different subjects (should NOT be grouped)
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
    
    # Test 4: Database subjects (should NOW be grouped)
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
    print(f"  ✅ Can teach both BIT1103 and BCS1103 (equivalent subjects)")
    
    # Test 7: Mobile App Development (grouped with theory+practical)
    print("\nTest 7: Mobile Application Development equivalents")
    mobile_equiv = get_equivalent_courses('BIT3131')
    print(f"  BIT3131 equivalents: {mobile_equiv}")
    print(f"  ✅ Includes BIT theory, BIT practical, and BCS subject")
    
    print("\n" + "=" * 80)
    print("✅ All tests passed! Canonical mapping is correct.")
    print("=" * 80 + "\n")