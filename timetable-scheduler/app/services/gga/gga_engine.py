import random
import time
from typing import List, Dict, Optional
from collections import defaultdict
from app.services.gga.chromosome import Chromosome, FitnessScore
from app.services.gga.fitness import FitnessEvaluator
from app.services.gga.operators import GeneticOperators
from app.services.csp.constraints import ConstraintChecker
from app.config import Config

class GGAEngine:
    """Guided Genetic Algorithm engine for timetable optimization"""
    
    def __init__(self, course_units: Dict, student_groups: Dict, 
                 lecturers: Dict, rooms: Dict):
        self.course_units = course_units
        self.student_groups = student_groups
        self.lecturers = lecturers
        self.rooms = rooms
        
        self.fitness_evaluator = FitnessEvaluator(
            course_units, student_groups, lecturers, rooms
        )
        
        self.constraint_checker = ConstraintChecker()
        
        self.operators = GeneticOperators(
            self.constraint_checker, lecturers, rooms, 
            course_units, student_groups
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
        print(f"Starting GGA optimization with population size {self.population_size}")
        
        # Initialize population
        self.population = self._initialize_population(initial_chromosome)
        
        # Evaluate initial population
        for chromosome in self.population:
            chromosome.fitness = self.fitness_evaluator.evaluate(chromosome)
        
        self._sort_population()
        self.best_ever = self.population[0].clone()
        initial_fitness = self.best_ever.fitness.overall_fitness
        
        print(f"Initial fitness: {initial_fitness:.4f}")
        
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
            for child in offspring:
                child.fitness = self.fitness_evaluator.evaluate(child)
            
            # Replacement
            self.population = self._replace(offspring)
            
            # Track progress
            current_best = self.population[0]
            if current_best.fitness.overall_fitness > self.best_ever.fitness.overall_fitness:
                self.best_ever = current_best.clone()
                self.stall_count = 0
                print(f"Gen {self.generation}: New best fitness: {self.best_ever.fitness.overall_fitness:.4f}")
            else:
                self.stall_count += 1
            
            self.fitness_history.append(self.best_ever.fitness.overall_fitness)
            
            # Progress update
            if self.generation % 10 == 0:
                elapsed = time.time() - self.start_time
                print(f"Gen {self.generation}/{self.max_generations}: "
                      f"Best={self.best_ever.fitness.overall_fitness:.4f}, "
                      f"Avg={sum(c.fitness.overall_fitness for c in self.population) / len(self.population):.4f}, "
                      f"Stall={self.stall_count}, Time={elapsed:.1f}s")
            
            # Adaptive parameter adjustment
            if self.generation % 50 == 0:
                self._adjust_parameters()
        
        final_fitness = self.best_ever.fitness.overall_fitness
        improvement = ((final_fitness - initial_fitness) / initial_fitness) * 100
        elapsed = time.time() - self.start_time
        
        print(f"\nOptimization complete:")
        print(f"  Generations: {self.generation}")
        print(f"  Initial fitness: {initial_fitness:.4f}")
        print(f"  Final fitness: {final_fitness:.4f}")
        print(f"  Improvement: {improvement:.2f}%")
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
                if self._validate_chromosome(child1):
                    offspring.append(child1)
                else:
                    # Use parent if child is invalid
                    offspring.append(parents[i].clone())
                
                if self._validate_chromosome(child2):
                    offspring.append(child2)
                else:
                    # Use parent if child is invalid
                    offspring.append(parents[i + 1].clone())
            else:
                # No crossover, just clone
                offspring.extend([parents[i].clone(), parents[i + 1].clone()])
        
        return offspring
    
    def _mutate(self, offspring: List[Chromosome]) -> List[Chromosome]:
        """Apply mutation to offspring with comprehensive constraint checking"""
        mutated = []
        
        for child in offspring:
            if random.random() < self.mutation_rate:
                # Try mutation up to 20 times to find a valid one (increased for better exploration)
                max_attempts = 20
                valid_mutant = None
                
                for attempt in range(max_attempts):
                    mutant = child.clone()
                    
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
                                
                                # Swap time slots (keeping period, changing day)
                                from app.services.csp.domain import TimeSlot
                                
                                # Handle both dict and TimeSlot objects
                                old_time = mutant.genes[idx1].time_slot
                                new_day = mutant.genes[idx2].time_slot['day'] if isinstance(mutant.genes[idx2].time_slot, dict) else mutant.genes[idx2].time_slot.day
                                
                                if isinstance(old_time, dict):
                                    # Create new time slot dict
                                    new_time = old_time.copy()
                                    new_time['day'] = new_day
                                else:
                                    # Create new TimeSlot object
                                    new_time = TimeSlot(
                                        day=new_day,
                                        period=old_time.period,
                                        start=old_time.start,
                                        end=old_time.end,
                                        is_afternoon=old_time.is_afternoon
                                    )
                                
                                mutant.genes[idx1].time_slot = new_time
                                
                                # Validate
                                if self._validate_chromosome(mutant):
                                    valid_mutant = mutant
                                    break
                    
                    # 50% chance: Regular time slot swap mutation (if weekday balancing didn't work)
                    if valid_mutant is None and len(mutant.genes) >= 2:
                        idx1, idx2 = random.sample(range(len(mutant.genes)), 2)
                        
                        # Only swap if genes are for different time slots originally
                        gene1_time = mutant.genes[idx1].time_slot
                        gene2_time = mutant.genes[idx2].time_slot
                        
                        # Handle both dict and TimeSlot objects
                        day1 = gene1_time['day'] if isinstance(gene1_time, dict) else gene1_time.day
                        day2 = gene2_time['day'] if isinstance(gene2_time, dict) else gene2_time.day
                        period1 = gene1_time['period'] if isinstance(gene1_time, dict) else gene1_time.period
                        period2 = gene2_time['period'] if isinstance(gene2_time, dict) else gene2_time.period
                        
                        # Check if swapping would create conflicts
                        if (day1 != day2 or period1 != period2):
                            # Swap time slots
                            if isinstance(gene1_time, dict):
                                mutant.genes[idx1].time_slot = gene2_time.copy()
                                mutant.genes[idx2].time_slot = gene1_time.copy()
                            else:
                                mutant.genes[idx1].time_slot = gene2_time.copy()
                                mutant.genes[idx2].time_slot = gene1_time.copy()
                            
                            # Comprehensive validation
                            if self._validate_chromosome(mutant):
                                valid_mutant = mutant
                                break
                
                # Use valid mutant if found, otherwise keep original
                mutated.append(valid_mutant if valid_mutant else child)
            else:
                mutated.append(child)
        
        return mutated
    
    def _validate_chromosome(self, chromosome: Chromosome) -> bool:
        """
        Comprehensive validation of chromosome against ALL hard constraints
        
        Returns True if valid, False otherwise
        Uses the full ConstraintChecker to ensure industry-standard validation
        """
        from app.services.csp.constraints import ConstraintContext
        
        # Build constraint context from chromosome
        context = ConstraintContext()
        
        # Load resource data into context
        context.lecturers = {lid: self._lecturer_to_dict(l) for lid, l in self.lecturers.items()}
        context.rooms = {rid: self._room_to_dict(r) for rid, r in self.rooms.items()}
        context.course_units = {cid: self._course_to_dict(c) for cid, c in self.course_units.items()}
        context.student_groups = {gid: self._group_to_dict(g) for gid, g in self.student_groups.items()}
        
        # Convert genes to assignments and validate each
        for gene in chromosome.genes:
            assignment = gene.to_assignment()
            
            # Check all constraints before adding
            is_valid, violations = self.constraint_checker.check_all(assignment, context)
            
            if not is_valid:
                # Constraint violation detected
                return False
            
            # Add assignment to context (updates tracking)
            context.add_assignment(assignment)
        
        return True  # All constraints satisfied
    
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
            'room_type': room.room_type if hasattr(room, 'room_type') else room.get('room_type', 'Classroom')
        }
    
    def _course_to_dict(self, course) -> dict:
        """Convert course object to dict for constraint context"""
        if isinstance(course, dict):
            return course
        return {
            'id': course.id if hasattr(course, 'id') else course.get('id'),
            'is_lab': course.is_lab if hasattr(course, 'is_lab') else course.get('is_lab', False)
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