import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DEBUG = os.getenv('FLASK_DEBUG', 'True') == 'True'
    
    # MongoDB
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'timetable_scheduler')
    
    # CSP Configuration
    CSP_MAX_ITERATIONS = int(os.getenv('CSP_MAX_ITERATIONS', 10000))
    CSP_TIMEOUT_SECONDS = int(os.getenv('CSP_TIMEOUT_SECONDS', 300))
    
    # GGA Configuration
    GGA_POPULATION_SIZE = int(os.getenv('GGA_POPULATION_SIZE', 100))
    GGA_MAX_GENERATIONS = int(os.getenv('GGA_MAX_GENERATIONS', 500))
    GGA_MUTATION_RATE = float(os.getenv('GGA_MUTATION_RATE', 0.15))
    GGA_CROSSOVER_RATE = float(os.getenv('GGA_CROSSOVER_RATE', 0.80))
    GGA_TARGET_FITNESS = float(os.getenv('GGA_TARGET_FITNESS', 0.90))
    GGA_STALL_LIMIT = 100
    GGA_ELITE_SIZE = 10
    
    # Time Slots
    TIME_SLOTS = [
        {'period': 'SLOT_1', 'start': '09:00', 'end': '11:00', 'is_afternoon': False},
        {'period': 'SLOT_2', 'start': '11:00', 'end': '13:00', 'is_afternoon': False},
        {'period': 'SLOT_3', 'start': '14:00', 'end': '16:00', 'is_afternoon': True},
        {'period': 'SLOT_4', 'start': '16:00', 'end': '18:00', 'is_afternoon': True}
    ]
    
    DAYS = ['MON', 'TUE', 'WED', 'THU', 'FRI']
    
    # Validation Thresholds
    SOFT_CONSTRAINT_MINIMUM = 0.75
    DEPLOYMENT_THRESHOLD = 0.80
    EXCELLENCE_THRESHOLD = 0.90
    
    # Fitness Weights
    FITNESS_WEIGHTS = {
        'student_idle_time': 0.35,
        'lecturer_workload_balance': 0.30,
        'room_utilization': 0.20,
        'weekday_distribution': 0.15
    }