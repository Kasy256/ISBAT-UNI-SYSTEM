from dataclasses import dataclass, field
from typing import List, Optional, Dict
import copy
from app.services.csp.domain import Assignment

@dataclass
class Gene:
    """Single gene representing a session assignment"""
    session_id: str
    course_unit_id: str
    program_id: str
    lecturer_id: str
    room_id: str
    time_slot: Dict
    term: str
    session_number: int
    
    # Metadata for guided operations
    flexibility: float = 0.5
    conflict_score: float = 0.0
    
    def to_assignment(self) -> Assignment:
        """Convert gene to Assignment object"""
        from app.services.csp.domain import TimeSlot
        
        time_slot_obj = TimeSlot(
            day=self.time_slot.day if hasattr(self.time_slot, 'day') else self.time_slot['day'],
            period=self.time_slot.period if hasattr(self.time_slot, 'period') else self.time_slot['period'],
            start=self.time_slot.start if hasattr(self.time_slot, 'start') else self.time_slot['start'],
            end=self.time_slot.end if hasattr(self.time_slot, 'end') else self.time_slot['end'],
            is_afternoon=self.time_slot.is_afternoon if hasattr(self.time_slot, 'is_afternoon') else self.time_slot['is_afternoon']
        )
        
        return Assignment(
            variable_id=self.session_id,
            course_unit_id=self.course_unit_id,
            program_id=self.program_id,
            lecturer_id=self.lecturer_id,
            room_number=self.room_id,  # Gene.room_id contains room_number value
            time_slot=time_slot_obj,
            term=self.term,
            session_number=self.session_number
        )
    
    def clone(self) -> 'Gene':
        """Create a deep copy of the gene"""
        return Gene(
            session_id=self.session_id,
            course_unit_id=self.course_unit_id,
            program_id=self.program_id,
            lecturer_id=self.lecturer_id,
            room_id=self.room_id,
            time_slot=self.time_slot.copy(),
            term=self.term,
            session_number=self.session_number,
            flexibility=self.flexibility,
            conflict_score=self.conflict_score
        )

@dataclass
class FitnessScore:
    """Fitness score breakdown"""
    student_idle_time: float = 0.0
    lecturer_workload_balance: float = 0.0
    room_utilization: float = 0.0
    weekday_distribution: float = 0.0
    overall_fitness: float = 0.0
    
    breakdown: Dict = field(default_factory=dict)

@dataclass
class Chromosome:
    """Chromosome representing a complete timetable"""
    id: str
    genes: List[Gene]
    fitness: Optional[FitnessScore] = None
    generation: int = 0
    age: int = 0
    
    def clone(self) -> 'Chromosome':
        """Create a deep copy of chromosome"""
        return Chromosome(
            id=f"{self.id}_clone",
            genes=[gene.clone() for gene in self.genes],
            fitness=copy.deepcopy(self.fitness) if self.fitness else None,
            generation=self.generation,
            age=self.age
        )
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'generation': self.generation,
            'age': self.age,
            'fitness': {
                'student_idle_time': self.fitness.student_idle_time if self.fitness else 0,
                'lecturer_workload_balance': self.fitness.lecturer_workload_balance if self.fitness else 0,
                'room_utilization': self.fitness.room_utilization if self.fitness else 0,
                'weekday_distribution': self.fitness.weekday_distribution if self.fitness else 0,
                'overall_fitness': self.fitness.overall_fitness if self.fitness else 0
            } if self.fitness else {},
            'genes_count': len(self.genes)
        }
    
    @staticmethod
    def from_csp_solution(assignments: List[Assignment], chromosome_id: str = "CSP_BASE") -> 'Chromosome':
        """Create chromosome from CSP solution"""
        genes = []
        
        for assignment in assignments:
            gene = Gene(
                session_id=assignment.variable_id,
                course_unit_id=assignment.course_unit_id,
                program_id=assignment.program_id,
                lecturer_id=assignment.lecturer_id,
                room_id=assignment.room_number,
                time_slot=assignment.time_slot.to_dict(),
                term=assignment.term,
                session_number=assignment.session_number
            )
            genes.append(gene)
        
        return Chromosome(
            id=chromosome_id,
            genes=genes,
            generation=0
        )
    
    def get_sessions_by_program(self) -> Dict[str, List[Gene]]:
        """Group genes by program"""
        from collections import defaultdict
        groups = defaultdict(list)
        for gene in self.genes:
            groups[gene.program_id].append(gene)
        return dict(groups)
    
    def get_sessions_by_lecturer(self) -> Dict[str, List[Gene]]:
        """Group genes by lecturer"""
        from collections import defaultdict
        lecturers = defaultdict(list)
        for gene in self.genes:
            lecturers[gene.lecturer_id].append(gene)
        return dict(lecturers)
    
    def get_sessions_by_room(self) -> Dict[str, List[Gene]]:
        """Group genes by room"""
        from collections import defaultdict
        rooms = defaultdict(list)
        for gene in self.genes:
            rooms[gene.room_id].append(gene)
        return dict(rooms)
    
    def get_sessions_by_day(self) -> Dict[str, List[Gene]]:
        """Group genes by day"""
        from collections import defaultdict
        days = defaultdict(list)
        for gene in self.genes:
            day = gene.time_slot.day if hasattr(gene.time_slot, 'day') else gene.time_slot['day']
            days[day].append(gene)
        return dict(days)