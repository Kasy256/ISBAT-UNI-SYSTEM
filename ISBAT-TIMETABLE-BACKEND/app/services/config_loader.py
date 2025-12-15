"""Helper functions to load configurable values from database."""

from typing import List, Dict, Optional

# Fallback days (not configurable yet, but kept for consistency)
FALLBACK_DAYS = ['MON', 'TUE', 'WED', 'THU', 'FRI']


# Cache for database connection to avoid creating multiple connections
_cached_db_connection = None
_cached_client = None

# Cache for config data to avoid repeated database queries
_cached_time_slots = None
_cached_room_specializations = None
_cached_time_slots_for_config = None

def _get_db_connection():
    """Get database connection - works with or without Flask app context"""
    global _cached_db_connection, _cached_client
    
    try:
        # Try Flask app context first
        from app import get_db
        db = get_db()
        if db is not None:
            return db
    except:
        pass
    
    # Fallback: Direct MongoDB connection (for standalone scripts)
    # Reuse cached connection if available
    if _cached_db_connection is not None:
        try:
            # Test if connection is still alive
            _cached_client.server_info()
            return _cached_db_connection
        except:
            # Connection is dead, reset cache
            _cached_db_connection = None
            _cached_client = None
    
    try:
        from app.config import Config
        from pymongo import MongoClient
        
        # Increased timeout for MongoDB Atlas connections (30 seconds)
        # Added connection pool settings for better reliability
        client = MongoClient(
            Config.MONGO_URI,
            serverSelectionTimeoutMS=30000,  # 30 seconds instead of 5
            connectTimeoutMS=30000,
            socketTimeoutMS=30000,
            maxPoolSize=10,
            retryWrites=True,
            retryReads=True
        )
        
        # Test the connection
        client.server_info()
        
        db = client[Config.MONGO_DB_NAME]
        
        # Cache the connection for reuse
        _cached_client = client
        _cached_db_connection = db
        
        return db
    except Exception as e:
        print(f"Warning: Failed to connect to MongoDB: {e}")
        return None


def invalidate_config_cache():
    """Invalidate cached config data (call this when data is updated)"""
    global _cached_time_slots, _cached_room_specializations, _cached_time_slots_for_config
    _cached_time_slots = None
    _cached_room_specializations = None
    _cached_time_slots_for_config = None


def get_room_specializations(use_cache: bool = True) -> List[Dict]:
    """Get room specializations from database (with caching)
    
    Args:
        use_cache: If True, use cached data if available. If False, force reload from database.
    """
    global _cached_room_specializations
    
    # Return cached data if available and cache is enabled
    if use_cache and _cached_room_specializations is not None:
        return _cached_room_specializations
    
    try:
        db = _get_db_connection()
        if db is None:
            return []
        
        specializations = list(db.room_specializations.find().sort('name', 1))
        
        # Convert to list of dicts (remove _id)
        result = []
        for spec in specializations:
            spec_dict = {k: v for k, v in spec.items() if k != '_id'}
            result.append(spec_dict)
        
        # Cache the result
        _cached_room_specializations = result
        return result
    except Exception as e:
        print(f"Error loading room specializations: {e}")
        return []


def get_time_slots(use_cache: bool = True) -> List[Dict]:
    """Get time slots from database with retry logic and caching
    
    Args:
        use_cache: If True, use cached data if available. If False, force reload from database.
    """
    global _cached_time_slots
    
    # Return cached data if available and cache is enabled
    if use_cache and _cached_time_slots is not None:
        return _cached_time_slots
    
    import time
    
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            db = _get_db_connection()
            if db is None:
                if attempt < max_retries - 1:
                    print(f"Warning: Database connection failed, retrying in {retry_delay}s... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    continue
                return []
            
            time_slots = list(db.time_slots.find().sort('order', 1))
            
            # Convert to list of dicts (remove _id)
            result = []
            for slot in time_slots:
                slot_dict = {k: v for k, v in slot.items() if k != '_id'}
                result.append(slot_dict)
            
            # Cache the result
            _cached_time_slots = result
            return result
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Warning: Error loading time slots (attempt {attempt + 1}/{max_retries}): {e}")
                print(f"Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                # Reset cached connection on error to force reconnection
                global _cached_db_connection, _cached_client
                _cached_db_connection = None
                _cached_client = None
            else:
                print(f"Error loading time slots after {max_retries} attempts: {e}")
                return []
    
    return []


def get_days() -> List[str]:
    """Get days from database, with fallback to defaults"""
    # For now, days are not configurable, but this function allows for future expansion
    return FALLBACK_DAYS.copy()


def get_time_slots_for_config(use_cache: bool = True) -> List[Dict]:
    """Get time slots in format expected by Config class (with caching)
    
    Args:
        use_cache: If True, use cached data if available. If False, force reload from database.
    """
    global _cached_time_slots_for_config
    
    # Return cached formatted data if available and cache is enabled
    if use_cache and _cached_time_slots_for_config is not None:
        return _cached_time_slots_for_config
    
    slots = get_time_slots(use_cache=use_cache)
    result = [
        {
            'period': slot['period'],
            'start': slot['start'],
            'end': slot['end'],
            'is_afternoon': slot.get('is_afternoon', False)
        }
        for slot in slots
    ]
    
    # Cache the formatted result
    _cached_time_slots_for_config = result
    return result


def format_time_for_display(start: str, end: str) -> str:
    """Format time slot for display (e.g., '09:00 AM - 11:00 AM')"""
    def format_single_time(time_str: str) -> str:
        """Convert 24-hour time to 12-hour format"""
        try:
            hours, minutes = time_str.split(':')
            hour = int(hours)
            ampm = 'PM' if hour >= 12 else 'AM'
            hour12 = hour % 12 or 12
            return f"{hour12}:{minutes} {ampm}"
        except:
            return time_str
    
    start_formatted = format_single_time(start)
    end_formatted = format_single_time(end)
    return f"{start_formatted} - {end_formatted}"

