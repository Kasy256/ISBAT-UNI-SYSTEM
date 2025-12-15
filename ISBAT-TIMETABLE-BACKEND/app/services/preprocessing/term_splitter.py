import math
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from app.models.subject import CourseUnit

@dataclass
class TermSplitRatio:
    """Term split ratio configuration"""
    semester: str
    ratio_type: str  # "3:2", "2:3", "4:4"
    term1_units: int
    term2_units: int

@dataclass
class TermPlan:
    """Plan for a single term"""
    term_id: str
    semester: str
    term_number: int
    assigned_units: List[CourseUnit]
    total_weekly_hours: int
    total_credits: int

@dataclass
class SplitScore:
    """Score for splitting a unit into a term"""
    unit_id: str
    term1_score: float
    term2_score: float
    reasoning: List[str]

def _normalize_term_value(value) -> int:
    if value is None:
        return None
    text = str(value).strip().lower()
    if text in {'term1', 'term 1', '1'}:
        return 1
    if text in {'term2', 'term 2', '2'}:
        return 2
    return None


class TermSplitter:
    """Intelligent term splitting system with flexible unit count support"""
    
    def __init__(self):
        # Default term split ratios for BIT and BCS programs (Computing Faculty):
        # S1-S5: 5 units per semester
        # S6: 4 units per semester
        self.default_split_ratios = {
            'S1': TermSplitRatio('S1', '3:2', 3, 2),  # 3 units Term 1, 2 units Term 2 = 5 total
            'S2': TermSplitRatio('S2', '2:3', 2, 3),  # 2 units Term 1, 3 units Term 2 = 5 total
            'S3': TermSplitRatio('S3', '3:2', 3, 2),  # 3 units Term 1, 2 units Term 2 = 5 total
            'S4': TermSplitRatio('S4', '3:2', 3, 2),  # 3 units Term 1, 2 units Term 2 = 5 total
            'S5': TermSplitRatio('S5', '2:3', 2, 3),  # 2 units Term 1, 3 units Term 2 = 5 total
            'S6': TermSplitRatio('S6', '2:2', 2, 2)   # 2 units Term 1, 2 units Term 2 = 4 total
        }
        
        # Dynamic split ratios based on unit count (for future faculties like Health):
        # These ratios are used when actual unit count differs from defaults
        self.unit_count_ratios = {
            4: TermSplitRatio('4units', '2:2', 2, 2),      # 4 units: 2:2 (balanced)
            5: TermSplitRatio('5units', '3:2', 3, 2),      # 5 units: 3:2 (Term 1 heavier)
            6: TermSplitRatio('6units', '3:3', 3, 3),      # 6 units: 3:3 (balanced)
            7: TermSplitRatio('7units', '4:3', 4, 3),      # 7 units: 4:3 (Term 1 heavier)
            8: TermSplitRatio('8units', '4:4', 4, 4),      # 8 units: 4:4 (balanced)
        }
    
    def _get_program_alternating_ratio(self, base_ratio: TermSplitRatio, program: Optional[str], 
                                       unit_count: int, semester: str) -> TermSplitRatio:
        """
        Get alternating ratio for programs with 5 units per semester.
        
        For programs with 5 units (3:2 or 2:3 splits), different programs should
        alternate ratios to avoid resource competition. Uses alphabetical ordering
        to ensure deterministic assignment (e.g., BCS always gets opposite of BIT).
        
        Only applies to 5-unit semesters. Programs with balanced ratios (3:3, 4:4)
        are not alternated as they're already balanced.
        
        Args:
            base_ratio: The base ratio from defaults
            program: Program identifier (e.g., 'BSCAIT', 'BCS')
            unit_count: Effective unit count
            semester: Semester identifier
            
        Returns:
            TermSplitRatio with potentially alternated values for 5-unit semesters
        """
        # Only alternate for 5-unit semesters (3:2 or 2:3 ratios)
        if unit_count != 5:
            return base_ratio
        
        # Only alternate if the ratio is asymmetric (3:2 or 2:3)
        if base_ratio.term1_units == base_ratio.term2_units:
            # Already balanced (like 2:2 for S6), no need to alternate
            return base_ratio
        
        # If no program specified, use base ratio
        if not program:
            return base_ratio
        
        # Normalize program name for deterministic ordering
        program_normalized = program.upper().strip()
        
        # Use alphabetical ordering: Programs earlier in alphabet get base ratio
        # Programs later in alphabet get flipped ratio
        # This ensures: BSCAIT (alphabetically first) gets base, BCS gets flipped
        
        # Extract program key for comparison
        # Handle common program identifiers
        if 'BSCAIT' in program_normalized or program_normalized.startswith('BIT') or 'BIT' in program_normalized:
            # BSCAIT/BIT - alphabetically first
            should_flip = False
        elif 'BCS' in program_normalized:
            # BCS - alphabetically second
            should_flip = True
        else:
            # For unknown programs, use hash-based ordering for determinism
            # This ensures consistent assignment even for new programs
            program_hash = hash(program_normalized) % 2
            should_flip = (program_hash == 1)
        
        if should_flip:
            # This program gets flipped ratio (if base is 3:2, gets 2:3, and vice versa)
            return TermSplitRatio(
                semester,
                f"{base_ratio.term2_units}:{base_ratio.term1_units}",
                base_ratio.term2_units,
                base_ratio.term1_units
            )
        else:
            # This program gets base ratio (first program alphabetically)
            return base_ratio
    
    def _calculate_dynamic_ratio(self, unit_count: int, semester: str, program: Optional[str] = None) -> TermSplitRatio:
        """
        Calculate appropriate split ratio based on unit count.
        
        Returns predefined ratio for common unit counts, or calculates one dynamically.
        For 5-unit semesters, applies program-based alternating if program is provided.
        
        Args:
            unit_count: Number of effective units
            semester: Semester identifier
            program: Optional program identifier for alternating ratios
        """
        # Use predefined ratio if available
        if unit_count in self.unit_count_ratios:
            base_ratio = self.unit_count_ratios[unit_count]
            
            # For 5 units, apply program-based alternating
            if unit_count == 5 and program:
                return self._get_program_alternating_ratio(base_ratio, program, unit_count, semester)
            
            return TermSplitRatio(semester, base_ratio.ratio_type, base_ratio.term1_units, base_ratio.term2_units)
        
        # For other unit counts, calculate balanced or slightly Term 1 heavier split
        term1_units = math.ceil(unit_count / 2)
        term2_units = unit_count - term1_units
        
        # Ensure at least 1 unit per term
        if term1_units == 0:
            term1_units = 1
            term2_units = unit_count - 1
        elif term2_units == 0:
            term2_units = 1
            term1_units = unit_count - 1
        
        ratio_type = f"{term1_units}:{term2_units}"
        return TermSplitRatio(semester, ratio_type, term1_units, term2_units)
    
    def split_semester(self, semester: str, course_units: List[CourseUnit], 
                      canonical_alignment: Dict[str, int] = None, 
                      program: Optional[str] = None) -> Tuple[TermPlan, TermPlan]:
        """
        Split semester course units into two terms.
        
        Automatically detects unit count and uses appropriate split ratio:
        - Uses default ratios for known semesters (S1-S6) with expected unit counts
        - Applies program-based alternating for 5-unit semesters (3:2 vs 2:3)
        - Calculates dynamic ratios for semesters with different unit counts (6-8 units)
        - Supports future faculties like Health with different unit counts per semester
        
        Args:
            semester: Semester identifier (S1-S6)
            course_units: List of course units to split
            canonical_alignment: Optional dict of canonical_id -> term_number for alignment
            program: Optional program identifier (e.g., 'BSCAIT', 'BCS') for alternating ratios
        """
        canonical_alignment = canonical_alignment or {}
        
        # Extract program from course units if not provided
        if not program and course_units:
            # Try to get program from first subject (most subjects in a group share same program)
            program = getattr(course_units[0], 'program', None)
        
        # Count subject groups as 1 unit (Theory + Practical = 1 unit)
        course_groups = {}
        for unit in course_units:
            if unit.course_group:
                if unit.course_group not in course_groups:
                    course_groups[unit.course_group] = []
                course_groups[unit.course_group].append(unit)
        
        # Calculate effective unit count (groups count as 1, standalone subjects count as 1)
        standalone_units = [u for u in course_units if not u.course_group]
        effective_unit_count = len(course_groups) + len(standalone_units)

        if effective_unit_count == 0:
            raise ValueError("No course units available to split")

        # Get split ratio - try default first, then use dynamic calculation
        default_ratio = self.default_split_ratios.get(semester)
        
        if default_ratio:
            # Check if actual unit count matches default expectation
            expected_units = default_ratio.term1_units + default_ratio.term2_units
            
            if expected_units == effective_unit_count:
                # Use default ratio - matches expected unit count
                # Apply program-based alternating for 5-unit semesters
                if effective_unit_count == 5:
                    ratio = self._get_program_alternating_ratio(default_ratio, program, effective_unit_count, semester)
                else:
                    ratio = default_ratio
                term1_target_units = ratio.term1_units
                term2_target_units = ratio.term2_units
            else:
                # Unit count differs from default - calculate dynamic ratio
                ratio = self._calculate_dynamic_ratio(effective_unit_count, semester, program)
                term1_target_units = ratio.term1_units
                term2_target_units = ratio.term2_units
        else:
            # Unknown semester - calculate dynamic ratio based on unit count
            ratio = self._calculate_dynamic_ratio(effective_unit_count, semester, program)
            term1_target_units = ratio.term1_units
            term2_target_units = ratio.term2_units
        
        # SIMPLIFIED APPROACH: Term splitting is based ONLY on preferred_term from database
        # Since preferred_term is mandatory in the frontend, all subjects must have it
        # No fallback logic needed - if preferred_term is missing, raise an error
        
        # Step 1: Group subjects by course_group first (Theory+Practical pairs)
        course_groups_dict = {}
        standalone_courses = []
        
        for unit in course_units:
            if unit.course_group:
                if unit.course_group not in course_groups_dict:
                    course_groups_dict[unit.course_group] = []
                course_groups_dict[unit.course_group].append(unit)
            else:
                standalone_courses.append(unit)
        
        # Step 2: Assign subjects to terms based on:
        # Priority 1: Canonical alignment (for merging equivalent subjects across programs)
        # Priority 2: Preferred term from database/client input (main driver)
        
        term1_units = []
        term2_units = []
        missing_preferred_term = []  # Track units without preferred_term for error reporting
        
        # Process subject groups first (they count as 1 unit, Theory+Practical stay together)
        for group_id, group_units in course_groups_dict.items():
            # Check canonical alignment for any subject in the group
            group_canonical_term = None
            for unit in group_units:
                canonical_id = unit.canonical_id
                if canonical_id and canonical_id in canonical_alignment:
                    group_canonical_term = canonical_alignment[canonical_id]
                    break  # Use first canonical alignment found
            
            # Priority 1: Canonical alignment overrides preferred_term (for merging)
            if group_canonical_term is not None:
                if group_canonical_term == 1:
                    term1_units.extend(group_units)
                elif group_canonical_term == 2:
                    term2_units.extend(group_units)
                continue
            
            # Priority 2: Use preferred_term from database
            # For subject groups, all subjects in the group should have the same preferred_term
            # Take majority if they differ (shouldn't happen in practice)
            from collections import Counter
            group_preferred_terms = []
            for unit in group_units:
                preferred_term = _normalize_term_value(unit.preferred_term)
                if preferred_term:
                    group_preferred_terms.append(preferred_term)
                else:
                    missing_preferred_term.append(unit)
            
            if group_preferred_terms:
                # Use majority preferred_term (should all be same)
                term_counts = Counter(group_preferred_terms)
                assigned_term = term_counts.most_common(1)[0][0]
                
                if assigned_term == 1:
                    term1_units.extend(group_units)
                elif assigned_term == 2:
                    term2_units.extend(group_units)
            else:
                # No preferred_term found - this should not happen (mandatory field)
                missing_preferred_term.extend(group_units)
        
        # Process standalone subjects
        for unit in standalone_courses:
            canonical_id = unit.canonical_id
            forced_term = canonical_alignment.get(canonical_id) if canonical_id else None
            preferred_term = _normalize_term_value(unit.preferred_term)

            # Priority 1: Canonical alignment overrides preferred_term (for merging)
            if forced_term == 1:
                term1_units.append(unit)
            elif forced_term == 2:
                term2_units.append(unit)
            # Priority 2: Use preferred_term from database
            elif preferred_term == 1:
                term1_units.append(unit)
            elif preferred_term == 2:
                term2_units.append(unit)
            else:
                # No preferred_term - this should not happen (mandatory field)
                missing_preferred_term.append(unit)
        
        # Error if any subject is missing preferred_term (it's mandatory)
        if missing_preferred_term:
            missing_codes = [u.code for u in missing_preferred_term]
            raise ValueError(
                f"Term splitting failed: {len(missing_preferred_term)} subject(s) are missing preferred_term "
                f"(mandatory field). Subjects: {', '.join(missing_codes)}. "
                f"Please set preferred_term for all subjects in the database/frontend."
            )
        
        # Create term plans
        term1_plan = TermPlan(
            term_id=f"{semester}_T1",
            semester=semester,
            term_number=1,
            assigned_units=term1_units,
            total_weekly_hours=sum(u.weekly_hours for u in term1_units),
            total_credits=sum(u.credits for u in term1_units)
        )
        
        term2_plan = TermPlan(
            term_id=f"{semester}_T2",
            semester=semester,
            term_number=2,
            assigned_units=term2_units,
            total_weekly_hours=sum(u.weekly_hours for u in term2_units),
            total_credits=sum(u.credits for u in term2_units)
        )
        
        return term1_plan, term2_plan
    
    def _calculate_split_scores(self, flexible_units: List[CourseUnit], 
                                 term1_units: List[CourseUnit], 
                                 term2_units: List[CourseUnit]) -> Dict[str, SplitScore]:
        """Calculate split scores for each flexible unit"""
        scores = {}
        
        # Current term loading
        term1_hours = sum(u.weekly_hours for u in term1_units)
        term2_hours = sum(u.weekly_hours for u in term2_units)
        term1_labs = sum(1 for u in term1_units if u.preferred_room_type == "Lab")
        term2_labs = sum(1 for u in term2_units if u.preferred_room_type == "Lab")
        # Difficulty is no longer used - removed difficulty calculations
        
        for unit in flexible_units:
            term1_score = 0.5
            term2_score = 0.5
            reasoning = []
            
            # Note: is_foundational and difficulty are no longer used
            # All subjects should have preferred_term set (mandatory field)
            # This code path should rarely be reached
            
            # Factor 3: Resource demand (labs)
            if unit.preferred_room_type == "Lab":
                if term1_labs < term2_labs:
                    term1_score += 0.15
                    reasoning.append("Lab distribution")
                else:
                    term2_score += 0.15
                    reasoning.append("Lab distribution")
            
            # Factor 4: Lecturer availability (if available)
            lecturer_availability = getattr(unit, 'lecturer_availability', 1.0)
            if lecturer_availability < 0.6:
                term2_score += 0.10
                reasoning.append("Limited lecturer availability")
            
            # Factor 5: Workload balancing
            hours_imbalance = abs(term1_hours - term2_hours)
            if term1_hours < term2_hours:
                term1_score += 0.15 * min(hours_imbalance / 10.0, 1.0)
                reasoning.append("Workload balancing")
            else:
                term2_score += 0.15 * min(hours_imbalance / 10.0, 1.0)
                reasoning.append("Workload balancing")
            
            # Normalize scores
            total = term1_score + term2_score
            term1_score = term1_score / total
            term2_score = term2_score / total
            
            scores[unit.id] = SplitScore(unit.id, term1_score, term2_score, reasoning)
        
        return scores
    
    def _identify_pairs(self, units: List[CourseUnit]) -> List[List[CourseUnit]]:
        """Identify units that must be paired together (same course_group)"""
        pairs = []
        processed = set()
        
        # Group units by course_group
        groups = {}
        for unit in units:
            if unit.course_group:
                if unit.course_group not in groups:
                    groups[unit.course_group] = []
                groups[unit.course_group].append(unit)
        
        # Add all units in the same group as a pair
        for group_id, group_units in groups.items():
            if len(group_units) > 0:
                pairs.append(group_units)
                for unit in group_units:
                    processed.add(unit.id)
        
        return pairs
    
    def _difficulty_weight(self, difficulty: str) -> int:
        """Legacy method - difficulty is no longer used, always returns 0"""
        return 0
    
    def validate_split(self, term1: TermPlan, term2: TermPlan) -> Dict:
        """Validate term split"""
        issues = []
        
        # Check for duplicates
        term1_ids = set(u.id for u in term1.assigned_units)
        term2_ids = set(u.id for u in term2.assigned_units)
        duplicates = term1_ids & term2_ids
        
        if duplicates:
            issues.append(f"Duplicate units in both terms: {duplicates}")
        
        # Check workload balance
        hours_diff = abs(term1.total_weekly_hours - term2.total_weekly_hours)
        if hours_diff > 6:
            issues.append(f"Large workload imbalance: {hours_diff} hours difference")
        
        # Prerequisite validation removed - system now uses preferred_term directly
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'workload_balance': {
                'term1_hours': term1.total_weekly_hours,
                'term2_hours': term2.total_weekly_hours,
                'difference': hours_diff
            }
        }