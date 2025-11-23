"""Genetic operators for Guided Genetic Algorithm."""

from typing import Dict, List, Any, Tuple
import random
import copy


class GeneticOperators:
    """Genetic operators for chromosome manipulation"""
    
    def __init__(self, constraint_checker=None, lecturers: Dict = None, rooms: Dict = None,
                 course_units: Dict = None, student_groups: Dict = None, config: Dict[str, float] = None,
                 variable_pairs: Dict[str, List[str]] = None,
                 canonical_course_groups: Dict[str, Dict[int, List[str]]] = None):
        """
        Initialize genetic operators
        
        Args:
            constraint_checker: ConstraintChecker instance
            lecturers: Dictionary of lecturers by ID
            rooms: Dictionary of rooms by ID
            course_units: Dictionary of course units by ID
            student_groups: Dictionary of student groups by ID
            config: Configuration with mutation and crossover rates
            variable_pairs: Theory/practical pairs (gene_id -> list of paired gene_ids)
            canonical_course_groups: Canonical course groups (canonical_id -> {session_number: [gene_ids]})
        """
        self.constraint_checker = constraint_checker
        self.lecturers = lecturers or {}
        self.rooms = rooms or {}
        self.course_units = course_units or {}
        self.student_groups = student_groups or {}
        self.variable_pairs = variable_pairs or {}
        self.canonical_course_groups = canonical_course_groups or {}
        
        self.config = config or {
            'mutation_rate': 0.15,
            'crossover_rate': 0.80
        }
    
    def mutate(self, chromosome: Dict[str, Any], 
               problem_areas: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Apply guided mutation to chromosome
        
        Args:
            chromosome: Timetable chromosome to mutate
            problem_areas: Identified problem areas for guided mutation
            
        Returns:
            Mutated chromosome
        """
        mutated = copy.deepcopy(chromosome)
        sessions = mutated.get('sessions', [])
        
        if not sessions:
            return mutated
        
        # Determine mutation strategy based on problem areas
        if problem_areas and random.random() < 0.7:
            # Guided mutation targeting problem areas
            self._guided_mutation(mutated, problem_areas)
        else:
            # Random mutation for diversity
            self._random_mutation(mutated)
        
        return mutated
    
    def crossover(self, parent1: Dict[str, Any], parent2: Dict[str, Any],
                  strategy: str = 'uniform') -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Apply crossover to create offspring
        
        Args:
            parent1: First parent chromosome
            parent2: Second parent chromosome
            strategy: Crossover strategy ('uniform', 'day_based', 'lecturer_based')
            
        Returns:
            Tuple of two offspring chromosomes
        """
        if random.random() > self.config['crossover_rate']:
            # No crossover, return copies of parents
            return copy.deepcopy(parent1), copy.deepcopy(parent2)
        
        if strategy == 'day_based':
            return self._day_based_crossover(parent1, parent2)
        elif strategy == 'lecturer_based':
            return self._lecturer_based_crossover(parent1, parent2)
        else:
            return self._uniform_crossover(parent1, parent2)
    
    def _guided_mutation(self, chromosome: Dict[str, Any], 
                        problem_areas: List[Dict[str, Any]]):
        """Apply problem-specific mutations"""
        sessions = chromosome.get('sessions', [])
        
        for problem in problem_areas[:3]:  # Focus on top 3 problems
            problem_type = problem.get('type', '')
            
            if problem_type == 'STUDENT_LONG_GAP':
                self._compact_schedule_mutation(chromosome)
            elif problem_type == 'LECTURER_OVERLOAD':
                self._balance_lecturer_load_mutation(chromosome)
            elif problem_type == 'ROOM_UNDERUSE':
                self._consolidate_room_mutation(chromosome)
            elif problem_type == 'UNBALANCED_DAYS':
                self._redistribute_days_mutation(chromosome)
    
    def _random_mutation(self, chromosome: Dict[str, Any]):
        """Apply random mutations for diversity"""
        sessions = chromosome.get('sessions', [])
        
        if not sessions:
            return
        
        # Select random sessions to mutate
        num_mutations = max(1, int(len(sessions) * self.config['mutation_rate']))
        sessions_to_mutate = random.sample(sessions, min(num_mutations, len(sessions)))
        
        for session in sessions_to_mutate:
            mutation_type = random.choice(['time_slot', 'room', 'lecturer'])
            
            if mutation_type == 'time_slot':
                self._mutate_time_slot(session, chromosome)
            elif mutation_type == 'room':
                self._mutate_room(session, chromosome)
            elif mutation_type == 'lecturer':
                self._mutate_lecturer(session, chromosome)
    
    def _compact_schedule_mutation(self, chromosome):
        """Compact schedule to reduce gaps"""
        # Simply return the chromosome - compaction will happen naturally through other mutations
        return chromosome
        
        # Group by student group and day
        groups_by_day = {}
        for session in sessions:
            group_id = session.get('student_group_id', '')
            day = session.get('time_slot', {}).get('day', '')
            key = f"{group_id}_{day}"
            
            if key not in groups_by_day:
                groups_by_day[key] = []
            groups_by_day[key].append(session)
        
        # Try to compact sessions
        for key, day_sessions in groups_by_day.items():
            if len(day_sessions) < 2:
                continue
            
            # Sort by time
            day_sessions.sort(key=lambda s: s['time_slot']['start'])
            
            # Try to move sessions closer together
            time_slots = ['SLOT_1', 'SLOT_2', 'SLOT_3', 'SLOT_4']
            for i, session in enumerate(day_sessions):
                if i < len(time_slots):
                    session['time_slot']['period'] = time_slots[i]
                    self._update_time_slot_times(session, time_slots[i])
    
    def _balance_lecturer_load_mutation(self, chromosome: Dict[str, Any]):
        """Balance lecturer workload across days"""
        sessions = chromosome.get('sessions', [])
        
        # Group by lecturer
        lecturer_sessions = {}
        for session in sessions:
            lec_id = session.get('lecturer_id', '')
            if lec_id not in lecturer_sessions:
                lecturer_sessions[lec_id] = []
            lecturer_sessions[lec_id].append(session)
        
        # Find overloaded days and move sessions
        for lec_id, lec_sessions in lecturer_sessions.items():
            day_counts = {}
            for session in lec_sessions:
                day = session.get('time_slot', {}).get('day', '')
                day_counts[day] = day_counts.get(day, 0) + 1
            
            # Find heavy and light days
            if not day_counts:
                continue
            
            max_day = max(day_counts, key=day_counts.get)
            min_day = min(day_counts, key=day_counts.get)
            
            if day_counts[max_day] > day_counts[min_day] + 1:
                # Move one session from heavy to light day
                for session in lec_sessions:
                    if session.get('time_slot', {}).get('day') == max_day:
                        session['time_slot']['day'] = min_day
                        break
    
    def _consolidate_room_mutation(self, chromosome: Dict[str, Any]):
        """Consolidate sessions to fewer rooms"""
        sessions = chromosome.get('sessions', [])
        rooms = chromosome.get('rooms', {})
        
        if not rooms:
            return
        
        # Get most used rooms
        room_usage = {}
        for session in sessions:
            room_id = session.get('room_id', '')
            room_usage[room_id] = room_usage.get(room_id, 0) + 1
        
        if not room_usage:
            return
        
        # Find most used room
        most_used_room = max(room_usage, key=room_usage.get)
        
        # Try to move sessions to most used room
        for session in random.sample(sessions, min(5, len(sessions))):
            if session.get('room_id') != most_used_room:
                # Check if room is suitable
                room = rooms.get(most_used_room, {})
                if self._is_room_compatible(session, room):
                    session['room_id'] = most_used_room
    
    def _redistribute_days_mutation(self, chromosome: Dict[str, Any]):
        """Redistribute sessions for better weekday balance"""
        sessions = chromosome.get('sessions', [])
        
        # Count sessions per day
        day_counts = {}
        for session in sessions:
            day = session.get('time_slot', {}).get('day', '')
            day_counts[day] = day_counts.get(day, 0) + 1
        
        if not day_counts:
            return
        
        # Find heavy and light days
        max_day = max(day_counts, key=day_counts.get)
        min_day = min(day_counts, key=day_counts.get)
        
        if day_counts[max_day] > day_counts[min_day] + 2:
            # Move sessions from heavy to light day
            moved = 0
            for session in sessions:
                if session.get('time_slot', {}).get('day') == max_day and moved < 2:
                    session['time_slot']['day'] = min_day
                    moved += 1
    
    def _mutate_time_slot(self, session: Dict[str, Any], chromosome: Dict[str, Any]):
        """Mutate time slot of a session"""
        days = ['MON', 'TUE', 'WED', 'THU', 'FRI']
        periods = ['SLOT_1', 'SLOT_2', 'SLOT_3', 'SLOT_4']
        
        current_day = session.get('time_slot', {}).get('day', '')
        current_period = session.get('time_slot', {}).get('period', '')
        
        # Try adjacent time slot first
        if random.random() < 0.5 and current_period:
            period_idx = periods.index(current_period) if current_period in periods else 0
            new_period_idx = period_idx + random.choice([-1, 1])
            if 0 <= new_period_idx < len(periods):
                session['time_slot']['period'] = periods[new_period_idx]
                self._update_time_slot_times(session, periods[new_period_idx])
                return
        
        # Random day and period
        session['time_slot']['day'] = random.choice(days)
        new_period = random.choice(periods)
        session['time_slot']['period'] = new_period
        self._update_time_slot_times(session, new_period)
    
    def _mutate_room(self, gene):
        """Mutate room assignment of a gene"""
        if not self.rooms:
            return
        
        # Get compatible rooms
        compatible_rooms = []
        for room_id, room in self.rooms.items():
            # Handle both dict and object formats
            if hasattr(room, 'capacity'):
                room_dict = room.to_dict() if hasattr(room, 'to_dict') else {
                    'capacity': room.capacity,
                    'room_type': room.room_type
                }
            else:
                room_dict = room
            
            if self._is_room_compatible_gene(gene, room_dict):
                compatible_rooms.append(room_id)
        
        if compatible_rooms:
            gene.room_id = random.choice(compatible_rooms)
    
    def _mutate_lecturer(self, gene):
        """Mutate lecturer assignment of a gene"""
        if not self.lecturers:
            return
        
        course_id = gene.course_unit_id
        
        # Get qualified lecturers
        qualified = []
        for lec_id, lecturer in self.lecturers.items():
            # Handle both dict and object formats
            if hasattr(lecturer, 'specializations'):
                specializations = lecturer.specializations
            else:
                specializations = lecturer.get('specializations', [])
            
            if course_id in specializations:
                qualified.append(lec_id)
        
        if qualified:
            gene.lecturer_id = random.choice(qualified)
    
    def _uniform_crossover(self, parent1: Dict[str, Any], 
                          parent2: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Uniform crossover (gene-by-gene)"""
        child1 = copy.deepcopy(parent1)
        child2 = copy.deepcopy(parent2)
        
        sessions1 = child1.get('sessions', [])
        sessions2 = child2.get('sessions', [])
        
        # Swap genes with 50% probability
        for i in range(min(len(sessions1), len(sessions2))):
            if random.random() < 0.5:
                sessions1[i], sessions2[i] = sessions2[i], sessions1[i]
        
        return child1, child2
    
    def _day_based_crossover(self, parent1: Dict[str, Any],
                            parent2: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Day-based crossover (inherit complete days)"""
        child1 = copy.deepcopy(parent1)
        child2 = copy.deepcopy(parent2)
        
        days = ['MON', 'TUE', 'WED', 'THU', 'FRI']
        
        # Group sessions by day
        p1_by_day = self._group_by_day(parent1)
        p2_by_day = self._group_by_day(parent2)
        
        c1_sessions = []
        c2_sessions = []
        
        for day in days:
            if random.random() < 0.5:
                c1_sessions.extend(p1_by_day.get(day, []))
                c2_sessions.extend(p2_by_day.get(day, []))
            else:
                c1_sessions.extend(p2_by_day.get(day, []))
                c2_sessions.extend(p1_by_day.get(day, []))
        
        child1['sessions'] = c1_sessions
        child2['sessions'] = c2_sessions
        
        return child1, child2
    
    def _lecturer_based_crossover(self, parent1: Dict[str, Any],
                                  parent2: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Lecturer-based crossover (inherit complete lecturer schedules)"""
        child1 = copy.deepcopy(parent1)
        child2 = copy.deepcopy(parent2)
        
        # Group sessions by lecturer
        p1_by_lec = self._group_by_lecturer(parent1)
        p2_by_lec = self._group_by_lecturer(parent2)
        
        all_lecturers = set(p1_by_lec.keys()) | set(p2_by_lec.keys())
        
        c1_sessions = []
        c2_sessions = []
        
        for lec_id in all_lecturers:
            if random.random() < 0.5:
                c1_sessions.extend(p1_by_lec.get(lec_id, []))
                c2_sessions.extend(p2_by_lec.get(lec_id, []))
            else:
                c1_sessions.extend(p2_by_lec.get(lec_id, []))
                c2_sessions.extend(p1_by_lec.get(lec_id, []))
        
        child1['sessions'] = c1_sessions
        child2['sessions'] = c2_sessions
        
        return child1, child2
    
    @staticmethod
    def _group_by_day(chromosome: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Group sessions by day"""
        by_day = {}
        for session in chromosome.get('sessions', []):
            day = session.get('time_slot', {}).get('day', '')
            if day not in by_day:
                by_day[day] = []
            by_day[day].append(copy.deepcopy(session))
        return by_day
    
    @staticmethod
    def _group_by_lecturer(chromosome: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Group sessions by lecturer"""
        by_lecturer = {}
        for session in chromosome.get('sessions', []):
            lec_id = session.get('lecturer_id', '')
            if lec_id not in by_lecturer:
                by_lecturer[lec_id] = []
            by_lecturer[lec_id].append(copy.deepcopy(session))
        return by_lecturer
    
    def _is_room_compatible_gene(self, gene, room: Dict[str, Any]) -> bool:
        """Check if room is compatible with gene requirements"""
        # Get student group info
        student_group = self.student_groups.get(gene.student_group_id, {})
        if hasattr(student_group, 'size'):
            group_size = student_group.size
        else:
            group_size = student_group.get('size', 0) if isinstance(student_group, dict) else 0
        
        # Check capacity
        if room.get('capacity', 0) < group_size:
            return False
        
        # Get course info
        course_unit = self.course_units.get(gene.course_unit_id, {})
        if hasattr(course_unit, 'preferred_room_type'):
            preferred_room_type = course_unit.preferred_room_type
        else:
            preferred_room_type = course_unit.get('preferred_room_type', 'Theory') if isinstance(course_unit, dict) else 'Theory'
        
        # Check room type
        room_type = room.get('room_type', '')
        
        if preferred_room_type == 'Lab' and room_type != 'Lab':
            return False
        if preferred_room_type == 'Theory' and room_type == 'Lab':
            return False
        
        return True
    
    @staticmethod
    def _is_room_compatible(session: Dict[str, Any], room: Dict[str, Any]) -> bool:
        """Check if room is compatible with session requirements (legacy for dict-based)"""
        # Check capacity
        group_size = session.get('student_group_size', 0)
        if room.get('capacity', 0) < group_size:
            return False
        
        # Check room type
        course_preferred_room_type = session.get('course_preferred_room_type', 'Theory')
        room_type = room.get('room_type', '')
        
        if course_preferred_room_type == 'Lab' and room_type != 'Lab':
            return False
        if course_preferred_room_type == 'Theory' and room_type == 'Lab':
            return False
        
        return True
    
    @staticmethod
    def _update_time_slot_times(session: Dict[str, Any], period: str):
        """Update start and end times based on period"""
        time_mappings = {
            'SLOT_1': {'start': '09:00', 'end': '11:00', 'is_afternoon': False},
            'SLOT_2': {'start': '11:00', 'end': '13:00', 'is_afternoon': False},
            'SLOT_3': {'start': '14:00', 'end': '16:00', 'is_afternoon': True},
            'SLOT_4': {'start': '16:00', 'end': '18:00', 'is_afternoon': True}
        }
        
        if period in time_mappings:
            session['time_slot'].update(time_mappings[period])


def mutate_chromosome(chromosome, constraint_checker=None, lecturers: Dict = None,
                     rooms: Dict = None, course_units: Dict = None, student_groups: Dict = None,
                     config: Dict[str, float] = None,
                     problem_areas: List[Dict[str, Any]] = None):
    """
    Convenience function to mutate a chromosome
    
    Args:
        chromosome: Chromosome to mutate
        constraint_checker: ConstraintChecker instance
        lecturers: Dictionary of lecturers
        rooms: Dictionary of rooms
        course_units: Dictionary of course units
        student_groups: Dictionary of student groups
        config: Optional configuration
        problem_areas: Optional problem areas for guided mutation
        
    Returns:
        Mutated chromosome
    """
    operators = GeneticOperators(constraint_checker, lecturers, rooms, course_units, student_groups, config)
    return operators.mutate(chromosome, problem_areas)


def crossover_chromosomes(parent1, parent2, strategy: str = 'uniform',
                         constraint_checker=None, lecturers: Dict = None, rooms: Dict = None,
                         course_units: Dict = None, student_groups: Dict = None,
                         config: Dict[str, float] = None):
    """
    Convenience function to perform crossover
    
    Args:
        parent1: First parent
        parent2: Second parent
        strategy: Crossover strategy
        constraint_checker: ConstraintChecker instance
        lecturers: Dictionary of lecturers
        rooms: Dictionary of rooms
        course_units: Dictionary of course units
        student_groups: Dictionary of student groups
        config: Optional configuration
        
    Returns:
        Tuple of two offspring
    """
    operators = GeneticOperators(constraint_checker, lecturers, rooms, course_units, student_groups, config)
    return operators.crossover(parent1, parent2, strategy)
