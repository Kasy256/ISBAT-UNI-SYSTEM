from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.read_preferences import ReadPreference
from app.config import Config

# Global database client
mongo_client = None
db = None

def create_app(config_class=Config):
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS for all routes (development mode)
    # This ensures /auth/* and /api/* routes work properly
    CORS(app, 
         origins="*",  # Allow all origins for development
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         supports_credentials=True)
    
    # Initialize MongoDB with error handling
    global mongo_client, db
    try:
        # Set connection timeout and read preferences to handle replica set issues
        # readPreference=secondaryPreferred allows reading from secondaries when primary is unavailable
        mongo_uri = app.config['MONGO_URI']
        
        # Add read preference to URI if not already present
        if 'readPreference' not in mongo_uri:
            separator = '&' if '?' in mongo_uri else '?'
            mongo_uri = f"{mongo_uri}{separator}readPreference=secondaryPreferred"
        
        mongo_client = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=10000,  # 10 second timeout (increased from 5)
            connectTimeoutMS=10000,  # 10 second timeout (increased from 5)
            socketTimeoutMS=30000,  # 30 second timeout for operations
            retryWrites=True,
            retryReads=True,
            read_preference=ReadPreference.SECONDARY_PREFERRED  # Allow reading from secondaries
        )
        # Test connection with a more lenient approach
        try:
            mongo_client.admin.command('ping')
        except Exception as ping_error:
            # If ping fails, try to connect anyway - might be a replica set issue
            print(f"Warning: Initial ping failed: {ping_error}")
            print("Attempting to continue with connection...")
        
        db = mongo_client[app.config['MONGO_DB_NAME']]
        
        # Create indexes for performance (handle errors gracefully)
        try:
            db.users.create_index('email', unique=True)
        except Exception as e:
            print(f"Warning: Could not create index on users.email: {e}")
        
        try:
            db.lecturers.create_index('id', unique=True)
        except Exception as e:
            print(f"Warning: Could not create index on lecturers.id: {e}")
        
        try:
            # Drop old 'id' index if it exists (rooms now use room_number as primary key)
            try:
                # Try to drop the index by name
                db.rooms.drop_index('id_1')
            except:
                try:
                    # Try to find and drop any index on 'id' field
                    indexes = list(db.rooms.list_indexes())
                    for idx in indexes:
                        if 'id' in idx.get('key', {}) and idx['name'] != '_id_':
                            db.rooms.drop_index(idx['name'])
                            break
                except:
                    pass  # Index doesn't exist or couldn't be dropped, that's fine
            # Create unique index on room_number instead
            db.rooms.create_index('room_number', unique=True)
        except Exception as e:
            print(f"Warning: Could not create index on rooms.room_number: {e}")
        
        try:
            db.course_units.create_index('id', unique=True)
        except Exception as e:
            print(f"Warning: Could not create index on course_units.id: {e}")
        
        try:
            db.programs.create_index('id', unique=True)
        except Exception as e:
            print(f"Warning: Could not create index on programs.id: {e}")
        
        try:
            db.timetables.create_index('created_at')
        except Exception as e:
            print(f"Warning: Could not create index on timetables.created_at: {e}")
        
        try:
            db.canonical_course_groups.create_index('canonical_id', unique=True)
        except Exception as e:
            print(f"Warning: Could not create index on canonical_course_groups.canonical_id: {e}")
            
        print("✓ MongoDB connected successfully")
    except Exception as e:
        print(f"✗ MongoDB connection failed: {e}")
        print("\nTroubleshooting steps:")
        print("1. Check your internet connection")
        print("2. Verify MongoDB Atlas cluster is running and not paused")
        print("3. Check IP whitelist in MongoDB Atlas (Network Access)")
        print("4. Verify MONGO_URI in .env file is correct")
        print("5. Try using '0.0.0.0/0' in IP whitelist for testing (not recommended for production)")
        print("\nThe application will start but database operations will fail until connection is established.")
        # Set db to None so we can handle it gracefully
        db = None
        mongo_client = None
    
    # Register blueprints
    from app.api.routes import lecturers, rooms, subjects, programs, timetable, auth, validation, canonical_groups, reports, imports, room_specializations, time_slots
    
    app.register_blueprint(auth.bp)
    app.register_blueprint(lecturers.bp)
    app.register_blueprint(rooms.bp)
    app.register_blueprint(subjects.bp)
    app.register_blueprint(programs.bp)
    app.register_blueprint(timetable.bp)
    app.register_blueprint(validation.bp)
    app.register_blueprint(canonical_groups.bp)
    app.register_blueprint(reports.bp)
    app.register_blueprint(imports.bp)
    app.register_blueprint(room_specializations.bp)
    app.register_blueprint(time_slots.bp)
    
    # Health check endpoint
    @app.route('/health')
    def health():
        try:
            # Check MongoDB connection with read preference
            if mongo_client is None:
                return {
                    'status': 'unhealthy',
                    'database': 'disconnected',
                    'error': 'MongoDB client not initialized'
                }, 503
            
            # Try to ping, but allow secondary reads
            try:
                mongo_client.admin.command('ping')
            except Exception:
                # If ping fails, try a simple read operation instead
                # This will work even if primary is unavailable
                db.list_collection_names()
            
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
    if db is None:
        raise ConnectionError(
            "MongoDB connection not available. Please check your connection settings and ensure MongoDB is accessible."
        )
    return db