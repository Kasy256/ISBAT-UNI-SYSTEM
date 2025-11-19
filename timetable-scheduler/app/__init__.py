from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
from app.config import Config

# Global database client
mongo_client = None
db = None

def create_app(config_class=Config):
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS
    CORS(app)
    
    # Initialize MongoDB
    global mongo_client, db
    mongo_client = MongoClient(app.config['MONGO_URI'])
    db = mongo_client[app.config['MONGO_DB_NAME']]
    
    # Create indexes for performance
    db.users.create_index('email', unique=True)
    db.lecturers.create_index('id', unique=True)
    db.rooms.create_index('id', unique=True)
    db.course_units.create_index('id', unique=True)
    db.student_groups.create_index('id', unique=True)
    db.timetables.create_index('created_at')
    
    # Register blueprints
    from app.api.routes import lecturers, rooms, courses, students, timetable, auth, validation
    
    app.register_blueprint(auth.bp)
    app.register_blueprint(lecturers.bp)
    app.register_blueprint(rooms.bp)
    app.register_blueprint(courses.bp)
    app.register_blueprint(students.bp)
    app.register_blueprint(timetable.bp)
    app.register_blueprint(validation.bp)
    
    # Health check endpoint
    @app.route('/health')
    def health():
        try:
            # Check MongoDB connection
            mongo_client.admin.command('ping')
            return {
                'status': 'healthy',
                'database': 'connected',
                'version': '1.0.0'
            }, 200
        except Exception as e:
            return {
                'status': 'unhealthy',
                'database': 'disconnected',
                'error': str(e)
            }, 503
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal server error'}, 500
    
    return app

def get_db():
    """Get database instance"""
    return db