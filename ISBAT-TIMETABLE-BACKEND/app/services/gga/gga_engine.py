import random
import time
from typing import List, Dict, Optional
from collections import defaultdict
from app.services.gga.chromosome import Chromosome, FitnessScore
from app.services.gga.fitness import FitnessEvaluator
from app.services.gga.operators import GeneticOperators
from app.services.csp.constraints import ConstraintChecker
from app.config import Config
from app.services.canonical_courses import CANONICAL_COURSE_MAPPING, get_canonical_id

class GGAEngine:
    """Guided Genetic Algorithm engine for timetable optimization"""
    
    def __init__(self, course_units: Dict, student_groups: Dict, 
                 lecturers: Dict, rooms: Dict, 
                 variable_pairs: Optional[Dict[str, List[str]]] = None,
                 canonical_course_groups: Optional[Dict[str, Dict[int, List[str]]]] = None):
        self.course_units = course_units
        self.student_groups = student_groups
        self.lecturers = lecturers
        self.rooms = rooms
        
        # Theory/practical pairs: gene_id -> list of paired gene_ids
        self.variable_pairs = variable_pairs or {}
        
        # Canonical course groups: canonical_course_id -> {session_number: [gene_ids]}
        # Ensures canonical merged courses are scheduled at same time
        self.canonical_course_groups = canonical_course_groups or {}
        
        self.fitness_evaluator = FitnessEvaluator(
            course_units, student_groups, lecturers, rooms
        )
        
        self.constraint_checker = ConstraintChecker()
        
        self.operators = GeneticOperators(
            self.constraint_checker, lecturers, rooms, 
            course_units, student_groups,
            variable_pairs=variable_pairs,
            canonical_course_groups=canonical_course_groups
        )
        
        # Configuration
        self.population_size = Config.GGA_POPULATION_SIZE
        self.max_generations = Config.GGA_MAX_GENERATIONS
        self.mutation_rate = Config.GGA_MUTATION_RATE
        self.crossover_rate = Config.GGA_CROSSOVER_RATE
        self.elite_size = Config.GGA_ELITE_SIZE
        self.target_fitness = Config.GGA_TARGET_FITNESS
        self.stall_limit = Config.GGA_STALL_LIMIT
        
        # State
        self.population: List[Chromosome] = []
        self.best_ever: Optional[Chromosome] = None
        self.generation = 0
        self.stall_count = 0
        self.start_time = None
        
        # History
        self.fitness_history = []
    
    def optimize(self, initial_chromosome: Chromosome) -> Chromosome:
        """Optimize timetable using GGA"""
        
        self.start_time = time.time()
        print(f"Starting GGA optimization with population size {self.population_size}", flush=True)
        
        # Initialize population
        print("  Initializing population...", flush=True)
        self.population = self._initialize_population(initial_chromosome)
        
        # Evaluate initial population
        print("  Evaluating initial population...", flush=True)
        for i, chromosome in enumerate(self.population):
            chromosome.fitness = self.fitness_evaluator.evaluate(chromosome)
            if (i + 1) % 50 == 0:
                print(f"    Evaluated {i + 1}/{len(self.population)} chromosomes...", flush=True)
        
        self._sort_population()
        self.best_ever = self.population[0].clone()
        initial_fitness = self.best_ever.fitness.overall_fitness
        initial_violations = self.best_ever.fitness.violation_count
        
        print(f"Initial fitness: {initial_fitness:.4f} (violations: {initial_violations})", flush=True)
        
        # Main evolution loop
        for gen in range(self.max_generations):
            self.generation = gen + 1
            
            # Check termination
            if self.best_ever.fitness.overall_fitness >= self.target_fitness:
                print(f"Target fitness reached at generation {self.generation}")
                break
            
            if self.stall_count >= self.stall_limit:
                print(f"Stalled for {self.stall_limit} generations")
                break
            
            # Selection
            parents = self._select_parents()
            
            # Crossover
            offspring = self._crossover(parents)
            
            # Mutation
            offspring = self._mutate(offspring)
            
            # Evaluate offspring
            eval_start = time.time()
            for i, child in enumerate(offspring):
                child.fitness = self.fitness_evaluator.evaluate(child)
                # Show progress for large populations
                if len(offspring) > 100 and (i + 1) % 100 == 0:
                    print(f"    Evaluating offspring {i + 1}/{len(offspring)}...", flush=True)
            
            eval_time = time.time() - eval_start
            if eval_time > 5.0:  # If evaluation takes more than 5 seconds
                print(f"    Offspring evaluation took {eval_time:.1f}s", flush=True)
            
            # Replacement
            self.population = self._replace(offspring)
            
            # Track progress
            current_best = self.population[0]
            if current_best.fitness.overall_fitness > self.best_ever.fitness.overall_fitness:
                self.best_ever = current_best.clone()
                self.stall_count = 0
                print(f"Gen {self.generation}: New best fitness: {self.best_ever.fitness.overall_fitness:.4f}", flush=True)
            else:
                self.stall_count += 1
            
            self.fitness_history.append(self.best_ever.fitness.overall_fitness)
            
            # Progress update (every 10 generations, or every generation after 100 if stalled)
            should_print = (self.generation % 10 == 0) or (self.generation > 100 and self.stall_count > 5)
            if should_print:
                elapsed = time.time() - self.start_time
                avg_violations = sum(c.fitness.violation_count for c in self.population) / len(self.population)
                best_violations = self.best_ever.fitness.violation_count
                print(f"Gen {self.generation}/{self.max_generations}: "
                      f"Best={self.best_ever.fitness.overall_fitness:.4f} "
                      f"(violations={best_violations}), "
                      f"Avg={sum(c.fitness.overall_fitness for c in self.population) / len(self.population):.4f} "
                      f"(avg_viol={avg_violations:.1f}), "
                      f"Stall={self.stall_count}, Time={elapsed:.1f}s", flush=True)
            
            # Additional status every generation after 100 to show it's still running
            elif self.generation > 100:
                import sys
                print(".", end="", flush=True)
                if self.generation % 50 == 0:
                    print("", flush=True)  # New line every 50 dots
            
            # Adaptive parameter adjustment
            if self.generation % 50 == 0:
                self._adjust_parameters()
        
        final_fitness = self.best_ever.fitness.overall_fitness
        if initial_fitness > 0:
            improvement = ((final_fitness - initial_fitness) / initial_fitness) * 100
        else:
            improvement = 0.0 if final_fitness == 0 else float('inf')
        elapsed = time.time() - self.start_time
        
        final_violations = self.best_ever.fitness.violation_count
        print(f"\nOptimization complete:")
        print(f"  Generations: {self.generation}")
        print(f"  Initial fitness: {initial_fitness:.4f} (violations: {initial_violations})")
        print(f"  Final fitness: {final_fitness:.4f} (violations: {final_violations})")
        print(f"  Improvement: {improvement:.2f}%")
        print(f"  Violations reduced: {initial_violations - final_violations}")
        print(f"  Time: {elapsed:.2f}s")
        
        return self.best_ever
    
    def _initialize_population(self, base_chromosome: Chromosome) -> List[Chromosome]:
        """Initialize population with diversity"""
        population = []
        
        # Add base chromosome
        base = base_chromosome.clone()
        base.id = "BASE_0"
        population.append(base)
        
        # Generate diverse variants
        for i in range(1, self.population_size):
            variant = base_chromosome.clone()
            variant.id = f"INIT_{i}"
            
            # Apply random mutations for diversity
            strategy = i % 5
            
            if strategy == 0:  # Time slot permutation (skip for initialization)
                # Don't swap during initialization to maintain CSP validity
                pass
            
            elif strategy == 1:  # Room reallocation
                for gene in random.sample(variant.genes, min(10, len(variant.genes))):
                    self.operators._mutate_room(gene)
            
            elif strategy == 2:  # Lecturer swapping
                for gene in random.sample(variant.genes, min(10, len(variant.genes))):
                    self.operators._mutate_lecturer(gene)
            
            elif strategy == 3:  # Day compaction
                variant = self.operators._compact_schedule_mutation(variant)
            
            else:  # Keep base solution (no random perturbation in init)
                # Maintain CSP validity during initialization
                pass
            
            population.append(variant)
        
        return population
    
    def _select_parents(self) -> List[Chromosome]:
        """Select parents for reproduction"""
        parents = []
        
        # Elitism - keep best
        elite_count = self.elite_size
        parents.extend(self.population[:elite_count])
        
        # Tournament selection for rest
        remaining = (self.population_size * 7) // 10 - elite_count
        for _ in range(remaining):
            # Simple tournament selection
            tournament = random.sample(self.population, min(3, len(self.population)))
            parent = max(tournament, key=lambda x: x.fitness.overall_fitness if x.fitness else 0)
            parents.append(parent)
        
        return parents
    
    def _crossover(self, parents: List[Chromosome]) -> List[Chromosome]:
        """Apply crossover to create offspring"""
        offspring = []
        
        # Pair parents and apply simple crossover
        for i in range(0, len(parents) - 1, 2):
            if random.random() < self.crossover_rate:
                # Simple uniform crossover
                child1 = parents[i].clone()
                child2 = parents[i + 1].clone()
                
                # Swap some genes randomly
                for j in range(len(child1.genes)):
                    if random.random() < 0.5 and j < len(child2.genes):
                        child1.genes[j], child2.genes[j] = child2.genes[j], child1.genes[j]
                
                child1.generation = self.generation
                child2.generation = self.generation
                child1.id = f"GEN{self.generation}_OFF{len(offspring)}"
                child2.id = f"GEN{self.generation}_OFF{len(offspring)+1}"
                
                # Validate offspring - only add if valid
                # INDUSTRY-STANDARD: Allow violations but penalize in fitness
                # This allows GGA to evolve toward solutions with fewer violations
                offspring.append(child1)  # Accept even if has violations
                offspring.append(child2)  # Accept even if has violations
            else:
                # No crossover, just clone
                offspring.extend([parents[i].clone(), parents[i + 1].clone()])
        
        return offspring
    
    def _mutate(self, offspring: List[Chromosome]) -> List[Chromosome]:
        """Apply mutation to offspring with violation-prioritizing strategy"""
        mutated = []
        
        for child in offspring:
            if random.random() < self.mutation_rate:
                # PHASE 3: Violation-prioritizing mutation strategy
                # 1. Identify violations in current chromosome
                violations = self._identify_violations(child)
                
                # 2. Check if there are actual violations
                has_violations = (len(violations.get('weekly_limit', [])) > 0 or 
                                len(violations.get('daily_limit', [])) > 0 or
                                len(violations.get('unbalanced_days', [])) > 0)
                
                # 3. Prioritize violation-fixing mutations (70% chance if violations exist)
                if has_violations and random.random() < 0.7:
                    valid_mutant = self._apply_violation_fixing_mutation(child, violations)
                else:
                    # 4. Fall back to regular mutations (weekday balancing, swaps)
                    valid_mutant = self._apply_regular_mutation(child)
                
                mutated.append(valid_mutant if valid_mutant else child)
            else:
                mutated.append(child)
        
        return mutated
    
    def _identify_violations(self, chromosome: Chromosome) -> Dict[str, List]:
        """Identify violations in chromosome for targeted mutation"""
        from app.services.csp.constraints import ConstraintContext, ConstraintChecker, ConstraintType
        
        violations = {
            'weekly_limit': [],  # Lecturers exceeding weekly hours
            'daily_limit': [],   # Lecturers exceeding daily limits
            'unbalanced_days': []  # Days with too many/few sessions
        }
        
        # Build constraint context
        context = ConstraintContext()
        context.lecturers = {lid: self._lecturer_to_dict(l) for lid, l in self.lecturers.items()}
        context.rooms = {rid: self._room_to_dict(r) for rid, r in self.rooms.items()}
        context.course_units = {cid: self._course_to_dict(c) for cid, c in self.course_units.items()}
        context.student_groups = {gid: self._group_to_dict(g) for gid, g in self.student_groups.items()}
        
        constraint_checker = ConstraintChecker()
        
        # Track lecturer hours and daily counts
        lecturer_hours = defaultdict(int)
        lecturer_daily = defaultdict(lambda: defaultdict(int))
        day_counts = defaultdict(int)
        
        for gene in chromosome.genes:
            assignment = gene.to_assignment()
            day = assignment.time_slot.day if hasattr(assignment.time_slot, 'day') else assignment.time_slot['day']
            
            # Track hours
            lecturer_hours[assignment.lecturer_id] += 2
            lecturer_daily[assignment.lecturer_id][day] += 1
            day_counts[day] += 1
            
            # Check for violations
            is_valid, violation_list = constraint_checker.check_all(assignment, context)
            if not is_valid:
                for violation in violation_list:
                    if 'weekly limit' in violation.lower():
                        violations['weekly_limit'].append({
                            'lecturer_id': assignment.lecturer_id,
                            'gene_index': chromosome.genes.index(gene),
                            'gene': gene
                        })
                    elif 'daily limit' in violation.lower() or 'sessions on' in violation.lower():
                        violations['daily_limit'].append({
                            'lecturer_id': assignment.lecturer_id,
                            'day': day,
                            'gene_index': chromosome.genes.index(gene),
                            'gene': gene
                        })
            
            context.add_assignment(assignment)
        
        # Check for unbalanced days
        if day_counts:
            avg_load = len(chromosome.genes) / 5
            for day, count in day_counts.items():
                if count > avg_load * 1.3 or count < avg_load * 0.7:
                    violations['unbalanced_days'].append({
                        'day': day,
                        'count': count,
                        'avg': avg_load
                    })
        
        return violations
    
    def _apply_violation_fixing_mutation(self, chromosome: Chromosome, violations: Dict) -> Optional[Chromosome]:
        """Apply targeted mutations to fix violations - more aggressive approach"""
        max_attempts = 50  # Increased attempts for violation-fixing
        valid_mutant = None
        
        # Prioritize violations: always try to fix them if they exist
        has_weekly_violations = len(violations.get('weekly_limit', [])) > 0
        has_daily_violations = len(violations.get('daily_limit', [])) > 0
        has_unbalanced = len(violations.get('unbalanced_days', [])) > 0
        
        for attempt in range(max_attempts):
            mutant = chromosome.clone()
            fixed = False
            
            # Priority 1: Fix weekly limit violations (swap lecturer)
            if has_weekly_violations:
                violation = random.choice(violations['weekly_limit'])
                if self._fix_weekly_limit_violation(mutant, violation):
                    if self._validate_chromosome(mutant):
                        valid_mutant = mutant
                        fixed = True
                        break
            
            # Priority 2: Fix daily limit violations (move to different day)
            if not fixed and has_daily_violations:
                violation = random.choice(violations['daily_limit'])
                if self._fix_daily_limit_violation(mutant, violation):
                    if self._validate_chromosome(mutant):
                        valid_mutant = mutant
                        fixed = True
                        break
            
            # Priority 3: Fix unbalanced days (redistribute)
            if not fixed and has_unbalanced:
                if self._fix_unbalanced_days(mutant, violations['unbalanced_days']):
                    if self._validate_chromosome(mutant):
                        valid_mutant = mutant
                        fixed = True
                        break
        
        return valid_mutant
    
    def _fix_weekly_limit_violation(self, mutant: Chromosome, violation: Dict) -> bool:
        """Fix weekly limit violation by swapping lecturer"""
        gene = violation['gene']
        course_id = gene.course_unit_id
        
        # Find alternative lecturers for this course
        alternative_lecturers = []
        for lec_id, lecturer in self.lecturers.items():
            if lec_id == gene.lecturer_id:
                continue
            specializations = lecturer.specializations if hasattr(lecturer, 'specializations') else lecturer.get('specializations', [])
            if course_id in specializations:
                alternative_lecturers.append(lec_id)
        
        if alternative_lecturers:
            # Swap to alternative lecturer
            gene.lecturer_id = random.choice(alternative_lecturers)
            return True
        return False
    
    def _fix_daily_limit_violation(self, mutant: Chromosome, violation: Dict) -> bool:
        """Fix daily limit violation by moving session to different day"""
        gene = violation['gene']
        current_day = violation['day']
        
        # Find alternative days (prefer lighter days)
        from app.config import Config
        all_days = Config.DAYS
        alternative_days = [d for d in all_days if d != current_day]
        
        if alternative_days:
            new_day = random.choice(alternative_days)
            
            paired_genes = self._get_paired_genes(gene.session_id, mutant)
            genes_to_move = [gene] + paired_genes
            
            canonical_genes = []
            for canonical_id, session_map in self.canonical_course_groups.items():
                for session_num, gene_ids in session_map.items():
                    if gene.session_id in gene_ids:
                        canonical_genes.extend([g for g in mutant.genes 
                                               if g.session_id in gene_ids and g.session_number == gene.session_number])
            
            seen_ids = set()
            all_genes_to_move = []
            for g in genes_to_move + canonical_genes:
                if g.session_id not in seen_ids:
                    seen_ids.add(g.session_id)
                    all_genes_to_move.append(g)
            
            for g in all_genes_to_move:
                if isinstance(g.time_slot, dict):
                    g.time_slot = g.time_slot.copy()
                    g.time_slot['day'] = new_day
                else:
                    from app.services.csp.domain import TimeSlot
                    g.time_slot = TimeSlot(
                        day=new_day,
                        period=g.time_slot.period,
                        start=g.time_slot.start,
                        end=g.time_slot.end,
                        is_afternoon=g.time_slot.is_afternoon
                    )
            return True
        return False
    
    def _fix_unbalanced_days(self, mutant: Chromosome, unbalanced: List[Dict]) -> bool:
        """Fix unbalanced days by redistributing sessions"""
        if len(mutant.genes) < 2:
            return False
        
        # Find heavy and light days
        heavy_days = [v['day'] for v in unbalanced if v['count'] > v['avg'] * 1.3]
        light_days = [v['day'] for v in unbalanced if v['count'] < v['avg'] * 0.7]
        
        if not heavy_days or not light_days:
            return False
        
        # Find genes on heavy days
        heavy_genes = [i for i, g in enumerate(mutant.genes)
                      if (g.time_slot.day if hasattr(g.time_slot, 'day') else g.time_slot['day']) in heavy_days]
        light_genes = [i for i, g in enumerate(mutant.genes)
                      if (g.time_slot.day if hasattr(g.time_slot, 'day') else g.time_slot['day']) in light_days]
        
        if heavy_genes and light_genes:
            # Move a session from heavy day to light day
            idx = random.choice(heavy_genes)
            target_day = random.choice(light_days)
            gene = mutant.genes[idx]
            
            # Update time slot
            if isinstance(gene.time_slot, dict):
                gene.time_slot = gene.time_slot.copy()
                gene.time_slot['day'] = target_day
            else:
                from app.services.csp.domain import TimeSlot
                gene.time_slot = TimeSlot(
                    day=target_day,
                    period=gene.time_slot.period,
                    start=gene.time_slot.start,
                    end=gene.time_slot.end,
                    is_afternoon=gene.time_slot.is_afternoon
                )
            return True
        return False
    
    def _apply_regular_mutation(self, chromosome: Chromosome) -> Optional[Chromosome]:
        """Apply regular mutations (weekday balancing, swaps)"""
        max_attempts = 20
        valid_mutant = None
        
        for attempt in range(max_attempts):
            mutant = chromosome.clone()
            
            # 50% chance: Weekday-balancing mutation (move from heavy days to light days)
            if random.random() < 0.5 and len(mutant.genes) >= 2:
                # Calculate current day distribution
                day_counts = defaultdict(int)
                for gene in mutant.genes:
                    day = gene.time_slot['day'] if isinstance(gene.time_slot, dict) else gene.time_slot.day
                    day_counts[day] += 1
                
                # Find heavy and light days
                avg_load = len(mutant.genes) / 5
                heavy_days = [day for day, count in day_counts.items() if count > avg_load * 1.2]
                light_days = [day for day, count in day_counts.items() if count < avg_load * 0.8]
                
                if heavy_days and light_days:
                    # Find a gene on a heavy day
                    heavy_genes = [i for i, g in enumerate(mutant.genes) 
                                 if (g.time_slot['day'] if isinstance(g.time_slot, dict) else g.time_slot.day) in heavy_days]
                    light_genes = [i for i, g in enumerate(mutant.genes) 
                                 if (g.time_slot['day'] if isinstance(g.time_slot, dict) else g.time_slot.day) in light_days]
                    
                    if heavy_genes and light_genes:
                        idx1 = random.choice(heavy_genes)
                        idx2 = random.choice(light_genes)
                        
                        gene1 = mutant.genes[idx1]
                        gene2 = mutant.genes[idx2]
                        
                        # CRITICAL: Get all paired/canonical genes for gene1
                        paired_genes1 = self._get_paired_genes(gene1.session_id, mutant)
                        canonical_genes1 = []
                        for canonical_id, session_map in self.canonical_course_groups.items():
                            for session_num, gene_ids in session_map.items():
                                if gene1.session_id in gene_ids:
                                    canonical_genes1.extend([g for g in mutant.genes 
                                                           if g.session_id in gene_ids and g.session_number == gene1.session_number])
                        
                        seen_ids1 = set()
                        all_genes1 = []
                        for g in [gene1] + paired_genes1 + canonical_genes1:
                            if g.session_id not in seen_ids1:
                                seen_ids1.add(g.session_id)
                                all_genes1.append(g)
                        
                        from app.services.csp.domain import TimeSlot
                        
                        new_day = gene2.time_slot['day'] if isinstance(gene2.time_slot, dict) else gene2.time_slot.day
                        
                        for g in all_genes1:
                            if isinstance(g.time_slot, dict):
                                g.time_slot = g.time_slot.copy()
                                g.time_slot['day'] = new_day
                            else:
                                g.time_slot = TimeSlot(
                                    day=new_day,
                                    period=g.time_slot.period,
                                    start=g.time_slot.start,
                                    end=g.time_slot.end,
                                    is_afternoon=g.time_slot.is_afternoon
                                )
                        
                        if self._validate_chromosome(mutant):
                            valid_mutant = mutant
                            break
            
            # 50% chance: Regular time slot swap mutation (if weekday balancing didn't work)
            if valid_mutant is None and len(mutant.genes) >= 2:
                idx1, idx2 = random.sample(range(len(mutant.genes)), 2)
                
                gene1 = mutant.genes[idx1]
                gene2 = mutant.genes[idx2]
                
                # CRITICAL: Get all paired/canonical genes for both
                paired_genes1 = self._get_paired_genes(gene1.session_id, mutant)
                canonical_genes1 = []
                for canonical_id, session_map in self.canonical_course_groups.items():
                    for session_num, gene_ids in session_map.items():
                        if gene1.session_id in gene_ids:
                            canonical_genes1.extend([g for g in mutant.genes 
                                                   if g.session_id in gene_ids and g.session_number == gene1.session_number])
                # Deduplicate by session_id (Gene objects are not hashable)
                seen_ids1 = set()
                all_genes1 = []
                for g in [gene1] + paired_genes1 + canonical_genes1:
                    if g.session_id not in seen_ids1:
                        seen_ids1.add(g.session_id)
                        all_genes1.append(g)
                
                paired_genes2 = self._get_paired_genes(gene2.session_id, mutant)
                canonical_genes2 = []
                for canonical_id, session_map in self.canonical_course_groups.items():
                    for session_num, gene_ids in session_map.items():
                        if gene2.session_id in gene_ids:
                            canonical_genes2.extend([g for g in mutant.genes 
                                                   if g.session_id in gene_ids and g.session_number == gene2.session_number])
                # Deduplicate by session_id (Gene objects are not hashable)
                seen_ids2 = set()
                all_genes2 = []
                for g in [gene2] + paired_genes2 + canonical_genes2:
                    if g.session_id not in seen_ids2:
                        seen_ids2.add(g.session_id)
                        all_genes2.append(g)
                
                # Only swap if genes are for different time slots originally
                gene1_time = gene1.time_slot
                gene2_time = gene2.time_slot
                
                # Handle both dict and TimeSlot objects
                day1 = gene1_time['day'] if isinstance(gene1_time, dict) else gene1_time.day
                day2 = gene2_time['day'] if isinstance(gene2_time, dict) else gene2_time.day
                period1 = gene1_time['period'] if isinstance(gene1_time, dict) else gene1_time.period
                period2 = gene2_time['period'] if isinstance(gene2_time, dict) else gene2_time.period
                
                # Check if swapping would create conflicts
                if (day1 != day2 or period1 != period2):
                    # Swap time slots for all related genes
                    # CRITICAL: Create new time slot objects with correct day/period to preserve pairs
                    from app.services.csp.domain import TimeSlot
                    for g in all_genes1:
                        if isinstance(gene2_time, dict):
                            g.time_slot = gene2_time.copy()
                        else:
                            # Create new TimeSlot with gene2's day but preserve other properties
                            g.time_slot = TimeSlot(
                                day=gene2_time.day,
                                period=gene2_time.period,
                                start=gene2_time.start,
                                end=gene2_time.end,
                                is_afternoon=gene2_time.is_afternoon
                            )
                    
                    for g in all_genes2:
                        if isinstance(gene1_time, dict):
                            g.time_slot = gene1_time.copy()
                        else:
                            # Create new TimeSlot with gene1's day but preserve other properties
                            g.time_slot = TimeSlot(
                                day=gene1_time.day,
                                period=gene1_time.period,
                                start=gene1_time.start,
                                end=gene1_time.end,
                                is_afternoon=gene1_time.is_afternoon
                            )
                    
                    # Validate (allows limit violations, rejects critical ones)
                    if self._validate_chromosome(mutant):
                        valid_mutant = mutant
                        break
        
        return valid_mutant
    
    def _get_paired_genes(self, gene_id: str, chromosome: Chromosome) -> List:
        """Get all genes paired with the given gene (theory/practical pairs)"""
        paired_ids = self.variable_pairs.get(gene_id, [])
        return [g for g in chromosome.genes if g.session_id in paired_ids]
    
    def _get_canonical_group_genes(self, canonical_id: str, session_number: int, chromosome: Chromosome) -> List:
        """Get all genes for a canonical course group at a specific session number"""
        if canonical_id not in self.canonical_course_groups:
            return []
        session_genes = self.canonical_course_groups[canonical_id].get(session_number, [])
        return [g for g in chromosome.genes if g.session_id in session_genes]
    
    def _get_canonical_genes_for_gene(self, gene, chromosome: Chromosome) -> List:
        """Get all canonical group genes for a given gene using CANONICAL_COURSE_MAPPING"""
        canonical_genes = []
        # Get canonical ID for this gene's course
        gene_canonical_id = get_canonical_id(gene.course_unit_id) or gene.course_unit_id
        
        # Check if this course is in a canonical group
        if gene_canonical_id in self.canonical_course_groups:
            session_map = self.canonical_course_groups[gene_canonical_id]
            gene_ids = session_map.get(gene.session_number, [])
            canonical_genes = [g for g in chromosome.genes 
                             if g.session_id in gene_ids and g.session_number == gene.session_number]
        
        return canonical_genes
    
    def _validate_pairs_preserved(self, chromosome: Chromosome) -> bool:
        """Validate that theory/practical pairs are scheduled at same time"""
        for gene in chromosome.genes:
            paired_genes = self._get_paired_genes(gene.session_id, chromosome)
            if paired_genes:
                gene_day = gene.time_slot['day'] if isinstance(gene.time_slot, dict) else gene.time_slot.day
                gene_period = gene.time_slot['period'] if isinstance(gene.time_slot, dict) else gene.time_slot.period
                
                for paired in paired_genes:
                    paired_day = paired.time_slot['day'] if isinstance(paired.time_slot, dict) else paired.time_slot.day
                    paired_period = paired.time_slot['period'] if isinstance(paired.time_slot, dict) else paired.time_slot.period
                    
                    if gene_day != paired_day or gene_period != paired_period:
                        return False  # Pair broken!
        return True
    
    def _validate_canonical_groups_preserved(self, chromosome: Chromosome) -> bool:
        """Validate that canonical merged courses are scheduled at same time"""
        for canonical_id, session_map in self.canonical_course_groups.items():
            for session_num, gene_ids in session_map.items():
                canonical_genes = [g for g in chromosome.genes if g.session_id in gene_ids]
                if len(canonical_genes) > 1:
                    # All genes for this canonical course at this session should be at same time
                    first_gene = canonical_genes[0]
                    first_day = first_gene.time_slot['day'] if isinstance(first_gene.time_slot, dict) else first_gene.time_slot.day
                    first_period = first_gene.time_slot['period'] if isinstance(first_gene.time_slot, dict) else first_gene.time_slot.period
                    
                    for other_gene in canonical_genes[1:]:
                        other_day = other_gene.time_slot['day'] if isinstance(other_gene.time_slot, dict) else other_gene.time_slot.day
                        other_period = other_gene.time_slot['period'] if isinstance(other_gene.time_slot, dict) else other_gene.time_slot.period
                        
                        if first_day != other_day or first_period != other_period:
                            return False  # Canonical group broken!
        return True
    
    def _validate_chromosome(self, chromosome: Chromosome) -> bool:
        """
        Validate chromosome against CRITICAL constraints only
        
        Allows limit violations (weekly/daily hours) - these will be penalized in fitness
        Rejects only critical violations (double-booking, capacity, room type) - these can't be fixed
        Also validates that pairs and canonical groups are preserved
        
        Returns True if no critical violations, False otherwise
        """
        from app.services.csp.constraints import ConstraintContext, ConstraintType
        
        if not self._validate_pairs_preserved(chromosome):
            return False
        
        if not self._validate_canonical_groups_preserved(chromosome):
            return False
        
        context = ConstraintContext()
        context.lecturers = {lid: self._lecturer_to_dict(l) for lid, l in self.lecturers.items()}
        context.rooms = {rid: self._room_to_dict(r) for rid, r in self.rooms.items()}
        context.course_units = {cid: self._course_to_dict(c) for cid, c in self.course_units.items()}
        context.student_groups = {gid: self._group_to_dict(g) for gid, g in self.student_groups.items()}
        
        # Build variable_pairs mapping for constraint context (CRITICAL for proper conflict detection)
        context.variable_pairs = self.variable_pairs
        
        # Validate all genes in the chromosome
        for gene in chromosome.genes:
            assignment = gene.to_assignment()
            
            # CRITICAL: ALWAYS check double-booking FIRST - this is the most important constraint
            # The constraint correctly handles pairs (allows paired variables at same time)
            # but prevents conflicts with unrelated courses
            if not self.constraint_checker.check_constraint(
                ConstraintType.NO_DOUBLE_BOOKING, assignment, context
            ):
                return False
            
            # Check room capacity
            if not self.constraint_checker.check_constraint(
                ConstraintType.ROOM_CAPACITY, assignment, context
            ):
                return False
            
            # Check room type
            if not self.constraint_checker.check_constraint(
                ConstraintType.ROOM_TYPE, assignment, context
            ):
                return False
            
            # Check same-day repetition (HARD constraint - course can only be scheduled once per day)
            if not self.constraint_checker.check_constraint(
                ConstraintType.NO_SAME_DAY, assignment, context
            ):
                return False
            
            # Add assignment to context for next iteration's checks
            context.add_assignment(assignment)
        
        return True
    
    def _lecturer_to_dict(self, lecturer) -> dict:
        """Convert lecturer object to dict for constraint context"""
        if isinstance(lecturer, dict):
            return lecturer
        return {
            'id': lecturer.id if hasattr(lecturer, 'id') else lecturer.get('id'),
            'role': lecturer.role if hasattr(lecturer, 'role') else lecturer.get('role'),
            'max_weekly_hours': lecturer.max_weekly_hours if hasattr(lecturer, 'max_weekly_hours') else lecturer.get('max_weekly_hours', 22),
            'specializations': lecturer.specializations if hasattr(lecturer, 'specializations') else lecturer.get('specializations', [])
        }
    
    def _room_to_dict(self, room) -> dict:
        """Convert room object to dict for constraint context"""
        if isinstance(room, dict):
            return room
        return {
            'id': room.id if hasattr(room, 'id') else room.get('id'),
            'capacity': room.capacity if hasattr(room, 'capacity') else room.get('capacity'),
            'room_type': room.room_type if hasattr(room, 'room_type') else room.get('room_type', 'Theory')
        }
    
    def _course_to_dict(self, course) -> dict:
        """Convert course object to dict for constraint context"""
        if isinstance(course, dict):
            return course
        return {
            'id': course.id if hasattr(course, 'id') else course.get('id'),
            'preferred_room_type': course.preferred_room_type if hasattr(course, 'preferred_room_type') else course.get('preferred_room_type', 'Theory')
        }
    
    def _group_to_dict(self, group) -> dict:
        """Convert student group object to dict for constraint context"""
        if isinstance(group, dict):
            return group
        return {
            'id': group.id if hasattr(group, 'id') else group.get('id'),
            'size': group.size if hasattr(group, 'size') else group.get('size', 0)
        }
    
    def _replace(self, offspring: List[Chromosome]) -> List[Chromosome]:
        """Replace population using elitist strategy"""
        # Combine current population and offspring
        combined = self.population + offspring
        
        # Sort by fitness
        combined.sort(key=lambda c: c.fitness.overall_fitness if c.fitness else 0, 
                     reverse=True)
        
        # Age-based diversity preservation
        for chromosome in combined:
            chromosome.age += 1
        
        # Select new population
        new_population = []
        
        # Keep elites
        new_population.extend(combined[:self.elite_size])
        
        # Fill rest, avoiding very old chromosomes
        for chromosome in combined[self.elite_size:]:
            if len(new_population) >= self.population_size:
                break
            
            # Skip if too old (prevents premature convergence)
            if chromosome.age < 50:
                new_population.append(chromosome)
        
        # Fill remaining slots if needed
        while len(new_population) < self.population_size:
            new_population.append(combined[len(new_population)])
        
        return new_population[:self.population_size]
    
    def _sort_population(self):
        """Sort population by fitness"""
        self.population.sort(
            key=lambda c: c.fitness.overall_fitness if c.fitness else 0, 
            reverse=True
        )
    
    def _adjust_parameters(self):
        """Adaptively adjust GGA parameters"""
        # Calculate improvement rate
        if len(self.fitness_history) >= 50:
            recent = self.fitness_history[-50:]
            improvement_rate = (recent[-1] - recent[0]) / recent[0] if recent[0] > 0 else 0
            
            # Adjust mutation rate based on progress
            if improvement_rate < 0.01:  # Stagnation
                self.mutation_rate = min(self.mutation_rate * 1.2, 0.5)
                print(f"  Increased mutation rate to {self.mutation_rate:.3f}")
            elif improvement_rate > 0.05:  # Good progress
                self.mutation_rate = max(self.mutation_rate * 0.95, 0.05)
                print(f"  Decreased mutation rate to {self.mutation_rate:.3f}")
    
    def get_optimization_report(self) -> Dict:
        """Generate optimization report"""
        return {
            'success': True,
            'generations_run': self.generation,
            'final_fitness': self.best_ever.fitness.overall_fitness if self.best_ever else 0,
            'fitness_breakdown': {
                'student_idle_time': self.best_ever.fitness.student_idle_time,
                'lecturer_workload_balance': self.best_ever.fitness.lecturer_workload_balance,
                'room_utilization': self.best_ever.fitness.room_utilization,
                'weekday_distribution': self.best_ever.fitness.weekday_distribution
            } if self.best_ever and self.best_ever.fitness else {},
            'time_elapsed': time.time() - self.start_time if self.start_time else 0,
            'fitness_history': self.fitness_history,
            'population_size': self.population_size,
            'final_mutation_rate': self.mutation_rate
        }