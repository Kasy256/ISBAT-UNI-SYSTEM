"""Fitness evaluation for Guided Genetic Algorithm."""

from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import statistics


@dataclass
class FitnessScore:
    """Complete fitness score with breakdown"""
    overall_fitness: float
    student_idle_time: float
    lecturer_workload_balance: float
    room_utilization: float
    weekday_distribution: float
    breakdown: 'FitnessBreakdown'
    violation_penalty: float = 0.0  # Penalty for hard constraint violations
    violation_count: int = 0  # Number of hard constraint violations


@dataclass
class FitnessBreakdown:
    """Detailed fitness metrics"""
    # Student metrics
    avg_gap_length: float = 0.0
    max_gap_length: float = 0.0
    students_with_long_gaps: int = 0
    avg_daily_span: float = 0.0
    
    # Lecturer metrics
    workload_std_dev: float = 0.0
    overloaded_days: int = 0
    
    # Room metrics
    avg_room_occupancy: float = 0.0
    underutilized_rooms: int = 0
    room_waste: float = 0.0
    
    # Distribution metrics
    day_loads: List[int] = None
    day_load_variance: float = 0.0
    empty_days: int = 0
    back_to_back_long_days: int = 0
    
    def __post_init__(self):
        if self.day_loads is None:
            self.day_loads = [0, 0, 0, 0, 0]


class FitnessEvaluator:
    """Evaluates fitness of timetable chromosomes"""
    
    def __init__(self, course_units: Dict = None, student_groups: Dict = None,
                 lecturers: Dict = None, rooms: Dict = None, config: Dict[str, float] = None):
        """
        Initialize fitness evaluator
        
        Args:
            course_units: Dictionary of course units by ID
            student_groups: Dictionary of student groups by ID
            lecturers: Dictionary of lecturers by ID
            rooms: Dictionary of rooms by ID
            config: Fitness weights configuration
        """
        self.course_units = course_units or {}
        self.student_groups = student_groups or {}
        self.lecturers = lecturers or {}
        self.rooms = rooms or {}
        
        self.weights = config or {
            'student_idle_time': 0.30,
            'lecturer_workload_balance': 0.25,
            'room_utilization': 0.15,
            'weekday_distribution': 0.30  # Increased from 0.15 to 0.30 for better balance
        }
    
    def evaluate(self, chromosome) -> FitnessScore:
        """
        Evaluate overall fitness of chromosome
        
        Args:
            chromosome: Chromosome object with genes
            
        Returns:
            FitnessScore with overall and component scores
        """
        breakdown = FitnessBreakdown()
        
        # Convert chromosome to dict format for evaluation
        if hasattr(chromosome, 'genes'):
            # It's a Chromosome object - convert it
            sessions = []
            for gene in chromosome.genes:
                time_slot_dict = gene.time_slot.to_dict() if hasattr(gene.time_slot, 'to_dict') else gene.time_slot
                sessions.append({
                    'id': gene.session_id,
                    'student_group_id': gene.student_group_id,
                    'course_unit_id': gene.course_unit_id,
                    'lecturer_id': gene.lecturer_id,
                    'room_id': gene.room_id,
                    'time_slot': time_slot_dict,
                    'term': gene.term,
                    'session_number': gene.session_number
                })
            chromosome_dict = {'sessions': sessions}
        else:
            # Already a dict
            chromosome_dict = chromosome if 'sessions' in chromosome else {'sessions': []}
        
        # Evaluate each component
        student_score = self._evaluate_student_idle_time(chromosome_dict, breakdown)
        lecturer_score = self._evaluate_lecturer_workload_balance(chromosome_dict, breakdown)
        room_score = self._evaluate_room_utilization(chromosome_dict, breakdown)
        distribution_score = self._evaluate_weekday_distribution(chromosome_dict, breakdown)
        
        # Calculate violation penalty (CRITICAL: Heavily penalize hard constraint violations)
        violation_penalty, violation_count = self._evaluate_violations(chromosome)
        
        # Calculate weighted overall fitness (subtract violation penalty)
        soft_constraint_fitness = (
            self.weights['student_idle_time'] * student_score +
            self.weights['lecturer_workload_balance'] * lecturer_score +
            self.weights['room_utilization'] * room_score +
            self.weights['weekday_distribution'] * distribution_score
        )
        
        # Apply violation penalty (can make fitness negative if too many violations)
        overall = max(0.0, soft_constraint_fitness - violation_penalty)
        
        return FitnessScore(
            overall_fitness=overall,
            student_idle_time=student_score,
            lecturer_workload_balance=lecturer_score,
            room_utilization=room_score,
            weekday_distribution=distribution_score,
            breakdown=breakdown,
            violation_penalty=violation_penalty,
            violation_count=violation_count
        )
    
    def _evaluate_student_idle_time(self, chromosome: Dict[str, Any], 
                                   breakdown: FitnessBreakdown) -> float:
        """
        Evaluate student idle time (minimize gaps between classes)
        
        Higher score = less idle time (better)
        """
        sessions = chromosome.get('sessions', [])
        
        # Group sessions by student group and day
        student_schedules = {}
        for session in sessions:
            group_id = session.get('student_group_id', '')
            day = session.get('time_slot', {}).get('day', '')
            
            if group_id not in student_schedules:
                student_schedules[group_id] = {}
            if day not in student_schedules[group_id]:
                student_schedules[group_id][day] = []
            
            student_schedules[group_id][day].append(session)
        
        total_idle_score = 0.0
        total_days = 0
        all_gaps = []
        
        for group_id, day_schedules in student_schedules.items():
            for day, day_sessions in day_schedules.items():
                if len(day_sessions) < 2:
                    total_idle_score += 1.0
                    total_days += 1
                    continue
                
                # Sort sessions by time
                sorted_sessions = sorted(
                    day_sessions,
                    key=lambda s: self._time_to_minutes(s['time_slot']['start'])
                )
                
                # Calculate gaps between sessions
                gaps = []
                for i in range(len(sorted_sessions) - 1):
                    end_time = self._time_to_minutes(sorted_sessions[i]['time_slot']['end'])
                    start_time = self._time_to_minutes(sorted_sessions[i + 1]['time_slot']['start'])
                    gap = (start_time - end_time) / 60.0  # Convert to hours
                    gaps.append(gap)
                    all_gaps.append(gap)
                
                # Calculate day score based on gaps
                day_score = 1.0
                for gap in gaps:
                    if gap == 0:  # Back-to-back (ideal)
                        day_score *= 1.0
                    elif gap <= 1:  # Small gap (acceptable)
                        day_score *= 0.95
                    elif gap <= 2:  # Medium gap (not ideal)
                        day_score *= 0.85
                    else:  # Long gap (bad)
                        day_score *= 0.65
                        breakdown.students_with_long_gaps += 1
                
                # Calculate daily span efficiency
                first_start = self._time_to_minutes(sorted_sessions[0]['time_slot']['start'])
                last_end = self._time_to_minutes(sorted_sessions[-1]['time_slot']['end'])
                span = (last_end - first_start) / 60.0
                
                actual_hours = len(sorted_sessions) * 2  # Each session is 2 hours
                efficiency = actual_hours / span if span > 0 else 1.0
                day_score *= (0.7 + 0.3 * efficiency)
                
                total_idle_score += day_score
                total_days += 1
                breakdown.avg_daily_span += span
        
        # Calculate breakdown metrics
        if all_gaps:
            breakdown.avg_gap_length = statistics.mean(all_gaps)
            breakdown.max_gap_length = max(all_gaps)
        
        if total_days > 0:
            breakdown.avg_daily_span /= total_days
        
        return total_idle_score / max(total_days, 1)
    
    def _evaluate_lecturer_workload_balance(self, chromosome: Dict[str, Any],
                                           breakdown: FitnessBreakdown) -> float:
        """
        Evaluate lecturer workload balance (even distribution across week)
        
        Higher score = more balanced (better)
        """
        sessions = chromosome.get('sessions', [])
        
        # Group sessions by lecturer
        lecturer_schedules = {}
        for session in sessions:
            lecturer_id = session.get('lecturer_id', '')
            if lecturer_id not in lecturer_schedules:
                lecturer_schedules[lecturer_id] = []
            lecturer_schedules[lecturer_id].append(session)
        
        total_balance_score = 0.0
        all_std_devs = []
        
        for lecturer_id, lec_sessions in lecturer_schedules.items():
            # Calculate hours per day
            week_schedule = {'MON': 0, 'TUE': 0, 'WED': 0, 'THU': 0, 'FRI': 0}
            
            for session in lec_sessions:
                day = session.get('time_slot', {}).get('day', '')
                if day in week_schedule:
                    week_schedule[day] += 2  # Each session is 2 hours
            
            # Calculate balance metrics
            daily_loads = list(week_schedule.values())
            non_zero_loads = [load for load in daily_loads if load > 0]
            
            if not non_zero_loads:
                continue
            
            # Calculate standard deviation
            avg_load = statistics.mean(daily_loads)
            std_dev = statistics.stdev(daily_loads) if len(daily_loads) > 1 else 0
            all_std_devs.append(std_dev)
            
            # Score based on ideal distribution (3-5 hours per day)
            balance_score = 1.0
            
            for day_load in daily_loads:
                if day_load == 0:
                    balance_score *= 0.95  # Slightly prefer using all days
                elif day_load <= 2:
                    balance_score *= 0.90  # Too light
                elif day_load <= 6:
                    balance_score *= 1.0  # Ideal range
                else:
                    balance_score *= 0.70  # Overloaded
                    breakdown.overloaded_days += 1
            
            # Penalize high variance
            if std_dev > 2.0:
                balance_score *= (1.0 - 0.1 * min(std_dev - 2.0, 1.0))
            
            total_balance_score += balance_score
        
        # Calculate breakdown metrics
        if all_std_devs:
            breakdown.workload_std_dev = statistics.mean(all_std_devs)
        
        return total_balance_score / max(len(lecturer_schedules), 1)
    
    def _evaluate_room_utilization(self, chromosome: Dict[str, Any],
                                   breakdown: FitnessBreakdown) -> float:
        """
        Evaluate room utilization efficiency
        
        Higher score = better utilization (better)
        """
        sessions = chromosome.get('sessions', [])
        rooms_data = chromosome.get('rooms', {})
        
        # Group sessions by room
        room_usage = {}
        for session in sessions:
            room_id = session.get('room_id', '')
            if room_id not in room_usage:
                room_usage[room_id] = []
            room_usage[room_id].append(session)
        
        total_utilization_score = 0.0
        total_occupancy = 0.0
        
        for room_id, room_sessions in room_usage.items():
            room = rooms_data.get(room_id, {})
            room_capacity = room.get('capacity', 1)
            
            # Calculate occupancy rate (slots used / total slots)
            total_slots = 20  # 5 days × 4 slots
            used_slots = len(room_sessions)
            occupancy_rate = used_slots / total_slots
            
            total_occupancy += occupancy_rate
            
            # Ideal occupancy: 40-80%
            utilization_score = 1.0
            if occupancy_rate < 0.4:
                utilization_score = occupancy_rate / 0.4
                breakdown.underutilized_rooms += 1
            elif occupancy_rate > 0.8:
                utilization_score = 1.0 - 0.3 * (occupancy_rate - 0.8) / 0.2
            
            # Calculate capacity efficiency
            for session in room_sessions:
                group_size = session.get('student_group_size', 0)
                waste_ratio = (room_capacity - group_size) / room_capacity if room_capacity > 0 else 0
                
                if waste_ratio > 0.5:  # Room more than 50% oversized
                    utilization_score *= 0.85
                    breakdown.room_waste += waste_ratio
            
            total_utilization_score += utilization_score
        
        # Calculate breakdown metrics
        if room_usage:
            breakdown.avg_room_occupancy = total_occupancy / len(room_usage)
        
        return total_utilization_score / max(len(room_usage), 1)
    
    def _evaluate_weekday_distribution(self, chromosome: Dict[str, Any],
                                       breakdown: FitnessBreakdown) -> float:
        """
        Evaluate weekday distribution (even spread across days)
        
        Higher score = more even distribution (better)
        """
        sessions = chromosome.get('sessions', [])
        
        # Count sessions per day
        day_loads = {'MON': 0, 'TUE': 0, 'WED': 0, 'THU': 0, 'FRI': 0}
        
        for session in sessions:
            day = session.get('time_slot', {}).get('day', '')
            if day in day_loads:
                day_loads[day] += 1
        
        loads_list = list(day_loads.values())
        breakdown.day_loads = loads_list
        
        # Calculate metrics
        avg_load = statistics.mean(loads_list)
        variance = statistics.variance(loads_list) if len(loads_list) > 1 else 0
        breakdown.day_load_variance = variance
        
        empty_days = sum(1 for load in loads_list if load == 0)
        breakdown.empty_days = empty_days
        
        # Score calculation - stronger penalties for imbalance
        if avg_load == 0:
            return 0.0
        
        # Calculate coefficient of variation (CV) - normalized standard deviation
        cv = (variance ** 0.5) / avg_load if avg_load > 0 else 1.0
        
        # Base score from CV (lower CV = better distribution)
        # Perfect distribution (CV=0) = 1.0, Poor distribution (CV>0.5) = <0.5
        distribution_score = 1.0 / (1.0 + cv * 2.0)
        
        # Strong penalty for empty days
        if empty_days > 0:
            distribution_score *= (1.0 - 0.25 * empty_days)  # Increased from 0.15
        
        # Strong penalty for high variance
        if variance > avg_load:  # Variance > average means very uneven
            excess_variance = variance - avg_load
            penalty = min(excess_variance / (avg_load * 2), 0.5)  # Max 50% penalty
            distribution_score *= (1.0 - penalty)
        
        # Check for consecutive heavy days (back-to-back overload)
        day_order = ['MON', 'TUE', 'WED', 'THU', 'FRI']
        for i in range(len(day_order) - 1):
            day1_load = day_loads[day_order[i]]
            day2_load = day_loads[day_order[i + 1]]
            if day1_load > avg_load * 1.3 and day2_load > avg_load * 1.3:
                breakdown.back_to_back_long_days += 1
                distribution_score *= 0.85  # Increased penalty from 0.90
        
        # Additional penalty for extreme imbalance (one day has >40% of sessions)
        max_day_load = max(loads_list)
        if max_day_load > avg_load * 1.8:  # More than 80% above average
            distribution_score *= 0.80
        
        return max(distribution_score, 0.0)
    
    def _chromosome_to_dict(self, chromosome) -> Dict[str, Any]:
        """
        Convert Chromosome object to dictionary format for evaluation
        
        Args:
            chromosome: Chromosome object
            
        Returns:
            Dictionary with sessions and resource data
        """
        sessions = []
        
        for gene in chromosome.genes:
            # Get additional data from resources
            student_group = self.student_groups.get(gene.student_group_id, {})
            course_unit = self.course_units.get(gene.course_unit_id, {})
            
            # Handle both dict and object formats
            if hasattr(student_group, 'size'):
                group_size = student_group.size
            else:
                group_size = student_group.get('size', 0) if isinstance(student_group, dict) else 0
            
            if hasattr(course_unit, 'is_lab'):
                is_lab = course_unit.is_lab
            else:
                is_lab = course_unit.get('is_lab', False) if isinstance(course_unit, dict) else False
            
            session = {
                'session_id': gene.session_id,
                'course_unit_id': gene.course_unit_id,
                'student_group_id': gene.student_group_id,
                'lecturer_id': gene.lecturer_id,
                'room_id': gene.room_id,
                'time_slot': gene.time_slot,
                'term': gene.term,
                'session_number': gene.session_number,
                'student_group_size': group_size,
                'course_is_lab': is_lab
            }
            sessions.append(session)
        
        return {
            'sessions': sessions,
            'rooms': self.rooms,
            'lecturers': self.lecturers,
            'course_units': self.course_units,
            'student_groups': self.student_groups
        }
    
    def _evaluate_violations(self, chromosome) -> Tuple[float, int]:
        """
        Evaluate hard constraint violations and calculate penalty
        
        Returns:
            (penalty, violation_count) tuple
        """
        from app.services.csp.constraints import ConstraintContext, ConstraintChecker, ConstraintType
        from app.services.gga.chromosome import Gene
        
        # Build constraint context
        context = ConstraintContext()
        context.lecturers = {lid: self._lecturer_to_dict(l) for lid, l in self.lecturers.items()}
        context.rooms = {rid: self._room_to_dict(r) for rid, r in self.rooms.items()}
        context.course_units = {cid: self._course_to_dict(c) for cid, c in self.course_units.items()}
        context.student_groups = {gid: self._group_to_dict(g) for gid, g in self.student_groups.items()}
        
        constraint_checker = ConstraintChecker()
        total_violations = 0
        critical_violations = 0  # Double-booking, capacity
        
        # Check each assignment
        for gene in chromosome.genes:
            assignment = gene.to_assignment()
            is_valid, violations = constraint_checker.check_all(assignment, context)
            
            if not is_valid:
                total_violations += len(violations)
                
                # Check for critical violations (double-booking, capacity)
                if not constraint_checker.check_constraint(ConstraintType.NO_DOUBLE_BOOKING, assignment, context):
                    critical_violations += 1
                if not constraint_checker.check_constraint(ConstraintType.ROOM_CAPACITY, assignment, context):
                    critical_violations += 1
            
            context.add_assignment(assignment)
        
        # Calculate penalty: Penalty that allows evolution but strongly encourages fixing violations
        # Critical violations: -0.5 each (double-booking, capacity) - very bad, should never happen
        # Limit violations: -0.02 each (weekly/daily limits) - bad but fixable
        # Penalty is subtracted from soft constraint fitness (typically 0.6-0.8)
        # With 25 violations: 25 * 0.02 = 0.5 penalty, leaving room for fitness > 0
        # This ensures GGA prioritizes fixing violations while still allowing exploration
        penalty = (critical_violations * 0.5) + ((total_violations - critical_violations) * 0.02)
        
        return penalty, total_violations
    
    def _lecturer_to_dict(self, lecturer) -> dict:
        """Convert lecturer to dict for constraint context"""
        if hasattr(lecturer, 'to_dict'):
            return lecturer.to_dict()
        elif isinstance(lecturer, dict):
            return lecturer
        else:
            return {
                'id': getattr(lecturer, 'id', ''),
                'name': getattr(lecturer, 'name', ''),
                'role': getattr(lecturer, 'role', 'Full-Time'),
                'max_weekly_hours': getattr(lecturer, 'max_weekly_hours', 22),
                'specializations': getattr(lecturer, 'specializations', [])
            }
    
    def _room_to_dict(self, room) -> dict:
        """Convert room to dict for constraint context"""
        if hasattr(room, 'to_dict'):
            return room.to_dict()
        elif isinstance(room, dict):
            return room
        else:
            return {
                'id': getattr(room, 'id', ''),
                'capacity': getattr(room, 'capacity', 0),
                'room_type': getattr(room, 'room_type', 'Classroom')
            }
    
    def _course_to_dict(self, course) -> dict:
        """Convert course to dict for constraint context"""
        if hasattr(course, 'to_dict'):
            return course.to_dict()
        elif isinstance(course, dict):
            return course
        else:
            return {
                'id': getattr(course, 'id', ''),
                'is_lab': getattr(course, 'is_lab', False)
            }
    
    def _group_to_dict(self, group) -> dict:
        """Convert student group to dict for constraint context"""
        if hasattr(group, 'to_dict'):
            return group.to_dict()
        elif isinstance(group, dict):
            return group
        else:
            return {
                'id': getattr(group, 'id', ''),
                'size': getattr(group, 'size', 0)
            }
    
    @staticmethod
    def _time_to_minutes(time_str: str) -> int:
        """Convert time string (HH:MM) to minutes since midnight"""
        try:
            hours, minutes = map(int, time_str.split(':'))
            return hours * 60 + minutes
        except:
            return 0


def evaluate_chromosome(chromosome, course_units: Dict = None, 
                       student_groups: Dict = None, lecturers: Dict = None,
                       rooms: Dict = None, config: Dict[str, float] = None) -> FitnessScore:
    """
    Convenience function to evaluate chromosome fitness
    
    Args:
        chromosome: Timetable chromosome
        course_units: Dictionary of course units
        student_groups: Dictionary of student groups
        lecturers: Dictionary of lecturers
        rooms: Dictionary of rooms
        config: Optional fitness weights configuration
        
    Returns:
        FitnessScore with overall and component scores
    """
    evaluator = FitnessEvaluator(course_units, student_groups, lecturers, rooms, config)
    return evaluator.evaluate(chromosome)


def compare_fitness(fitness1: FitnessScore, fitness2: FitnessScore) -> int:
    """
    Compare two fitness scores
    
    Returns:
        1 if fitness1 is better, -1 if fitness2 is better, 0 if equal
    """
    if fitness1.overall_fitness > fitness2.overall_fitness:
        return 1
    elif fitness1.overall_fitness < fitness2.overall_fitness:
        return -1
    return 0
