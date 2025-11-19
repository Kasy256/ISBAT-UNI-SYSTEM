import math
from typing import List, Dict, Tuple
from dataclasses import dataclass
from app.models.course import CourseUnit

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

class TermSplitter:
    """Intelligent term splitting system"""
    
    def __init__(self):
        self.split_ratios = {
            'S1': TermSplitRatio('S1', '3:2', 3, 2),
            'S2': TermSplitRatio('S2', '2:3', 2, 3),
            'S3': TermSplitRatio('S3', '4:4', 4, 4),
            'S4': TermSplitRatio('S4', '3:2', 3, 2),
            'S5': TermSplitRatio('S5', '2:3', 2, 3),
            'S6': TermSplitRatio('S6', '4:4', 4, 4)
        }
    
    def split_semester(self, semester: str, course_units: List[CourseUnit]) -> Tuple[TermPlan, TermPlan]:
        """Split semester course units into two terms"""
        
        # Get split ratio
        ratio = self.split_ratios.get(semester)
        if not ratio:
            raise ValueError(f"Unknown semester: {semester}")
        
        # Validate unit count
        if len(course_units) != (ratio.term1_units + ratio.term2_units):
            raise ValueError(f"Expected {ratio.term1_units + ratio.term2_units} units, got {len(course_units)}")
        
        # Identify fixed assignments
        fixed_term1 = [u for u in course_units if u.preferred_term == "Term 1"]
        fixed_term2 = [u for u in course_units if u.preferred_term == "Term 2"]
        flexible = [u for u in course_units if u.preferred_term is None or u.preferred_term == "Either"]
        
        # Validate fixed assignments
        if len(fixed_term1) > ratio.term1_units:
            raise ValueError(f"Too many units prefer Term 1: {len(fixed_term1)} > {ratio.term1_units}")
        if len(fixed_term2) > ratio.term2_units:
            raise ValueError(f"Too many units prefer Term 2: {len(fixed_term2)} > {ratio.term2_units}")
        
        # Calculate split scores for flexible units
        scores = self._calculate_split_scores(flexible, fixed_term1, fixed_term2)
        
        # Sort by term1 preference
        sorted_units = sorted(flexible, key=lambda u: scores[u.id].term1_score, reverse=True)
        
        # Assign to terms
        term1_slots = ratio.term1_units - len(fixed_term1)
        term2_slots = ratio.term2_units - len(fixed_term2)
        
        term1_units = fixed_term1.copy()
        term2_units = fixed_term2.copy()
        
        # Handle pairing constraints
        paired_units = self._identify_pairs(flexible)
        for pair in paired_units:
            if len(pair) == 2:
                score1 = scores[pair[0].id].term1_score + scores[pair[1].id].term1_score
                score2 = scores[pair[0].id].term2_score + scores[pair[1].id].term2_score
                
                if score1 > score2 and term1_slots >= 2:
                    term1_units.extend(pair)
                    term1_slots -= 2
                elif term2_slots >= 2:
                    term2_units.extend(pair)
                    term2_slots -= 2
                
                # Remove from sorted list
                for unit in pair:
                    if unit in sorted_units:
                        sorted_units.remove(unit)
        
        # Assign remaining units
        for unit in sorted_units:
            # Check conflict constraints
            has_term1_conflict = any(c in [u.id for u in term1_units] for c in unit.cannot_pair_with)
            has_term2_conflict = any(c in [u.id for u in term2_units] for c in unit.cannot_pair_with)
            
            if has_term1_conflict and term2_slots > 0:
                term2_units.append(unit)
                term2_slots -= 1
            elif has_term2_conflict and term1_slots > 0:
                term1_units.append(unit)
                term1_slots -= 1
            elif scores[unit.id].term1_score > scores[unit.id].term2_score and term1_slots > 0:
                term1_units.append(unit)
                term1_slots -= 1
            elif term2_slots > 0:
                term2_units.append(unit)
                term2_slots -= 1
            elif term1_slots > 0:
                term1_units.append(unit)
                term1_slots -= 1
            else:
                raise ValueError("Cannot fit all units into terms")
        
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
        term1_labs = sum(1 for u in term1_units if u.is_lab)
        term2_labs = sum(1 for u in term2_units if u.is_lab)
        term1_difficulty = sum(self._difficulty_weight(u.difficulty) for u in term1_units)
        term2_difficulty = sum(self._difficulty_weight(u.difficulty) for u in term2_units)
        
        for unit in flexible_units:
            term1_score = 0.5
            term2_score = 0.5
            reasoning = []
            
            # Factor 1: Foundational courses prefer Term 1
            if unit.is_foundational:
                term1_score += 0.25
                reasoning.append("Foundational course")
            
            # Factor 2: Difficulty distribution
            unit_difficulty = self._difficulty_weight(unit.difficulty)
            if term1_difficulty < term2_difficulty:
                term1_score += 0.10
                reasoning.append("Balance difficulty")
            else:
                term2_score += 0.10
                reasoning.append("Balance difficulty")
            
            # Factor 3: Resource demand (labs)
            if unit.is_lab:
                if term1_labs < term2_labs:
                    term1_score += 0.15
                    reasoning.append("Lab distribution")
                else:
                    term2_score += 0.15
                    reasoning.append("Lab distribution")
            
            # Factor 4: Lecturer availability
            if unit.lecturer_availability < 0.6:
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
        """Identify units that must be paired together"""
        pairs = []
        processed = set()
        
        for unit in units:
            if unit.id in processed:
                continue
            
            if unit.must_pair_with:
                paired_unit = next((u for u in units if u.id == unit.must_pair_with), None)
                if paired_unit:
                    pairs.append([unit, paired_unit])
                    processed.add(unit.id)
                    processed.add(paired_unit.id)
        
        return pairs
    
    def _difficulty_weight(self, difficulty: str) -> int:
        """Get numeric weight for difficulty"""
        weights = {
            "Easy": 1,
            "Medium": 2,
            "Hard": 3
        }
        return weights.get(difficulty, 2)
    
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
        
        # Check prerequisite ordering
        for unit in term1.assigned_units:
            for prereq_id in unit.prerequisites:
                # Prerequisite should not be in term 2
                if any(u.id == prereq_id for u in term2.assigned_units):
                    issues.append(f"Prerequisite order violation: {unit.id} in T1 but {prereq_id} in T2")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'workload_balance': {
                'term1_hours': term1.total_weekly_hours,
                'term2_hours': term2.total_weekly_hours,
                'difference': hours_diff
            }
        }