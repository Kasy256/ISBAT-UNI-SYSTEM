"""Authentication endpoints."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash

from app.middleware.auth import AuthError, AuthMiddleware
from app.models.user import User
from app import get_db

bp = Blueprint("auth", __name__, url_prefix="/auth")
auth_middleware = AuthMiddleware()


@bp.post("/login")
def login():
    """Login endpoint using email and password from MongoDB"""
    try:
        data = request.get_json(force=True)
        email = data.get("email") or data.get("username")  # Support both for backward compatibility
        password = data.get("password", "")
        
        if not email or not password:
            raise AuthError("Email and password are required")
        
        # Get database
        db = get_db()
        if db is None:
            raise AuthError("Database connection unavailable")
        
        # Find user by email
        user_doc = db.users.find_one({"email": email})
        
        if not user_doc:
            raise AuthError("Invalid credentials")
        
        # Check if user is active
        if not user_doc.get("is_active", True):
            raise AuthError("Account is inactive")
        
        # Convert MongoDB document to dict (handle _id and datetime)
        # MongoDB datetime objects are already datetime, so we can use them directly
        user_dict = {
            'id': user_doc.get('id'),
            'email': user_doc.get('email'),
            'password_hash': user_doc.get('password_hash'),
            'full_name': user_doc.get('full_name', ''),
            'role': user_doc.get('role', 'viewer'),
            'department': user_doc.get('department'),
            'is_active': user_doc.get('is_active', True),
            'created_at': user_doc.get('created_at'),  # Already datetime from MongoDB
            'last_login': user_doc.get('last_login')    # Already datetime from MongoDB
        }
        
        # Validate required fields
        if not user_dict['id'] or not user_dict['email'] or not user_dict['password_hash']:
            raise AuthError("Invalid user data in database")
        
        # Create User object from database document
        user = User.from_dict(user_dict)
        
        # Verify password
        if not user.check_password(password):
            raise AuthError("Invalid credentials")
        
        # Update last login
        db.users.update_one(
            {"email": email},
            {"$set": {"last_login": datetime.now(timezone.utc)}}
        )
        
        # Generate token using AuthMiddleware
        token = auth_middleware.generate_access_token(
            user_id=user.id,
            role=user.role,
            email=user.email
        )
        
        return jsonify({
            "access_token": token,
            "roles": [user.role],  # Return as list for consistency
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role
            }
        }), 200
        
    except AuthError as e:
        return jsonify({"error": e.message}), e.status_code
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        # Log the full error for debugging (in production, use proper logging)
        print(f"Login error: {str(e)}")
        print(f"Traceback: {error_details}")
        return jsonify({"error": f"Login failed: {str(e)}"}), 500


@bp.post("/register")
def register_user():
    """Register a new user"""
    try:
        data = request.get_json(force=True)
        email = data.get("email")
        password = data.get("password")
        full_name = data.get("full_name", "")
        role = data.get("role", "viewer")
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        # Get database
        db = get_db()
        if db is None:
            return jsonify({"error": "Database connection unavailable"}), 500
        
        # Check if user already exists
        existing_user = db.users.find_one({"email": email})
        if existing_user:
            return jsonify({"error": "User with this email already exists"}), 400
        
        # Create new user
        import uuid
        user_id = str(uuid.uuid4())
        password_hash = generate_password_hash(password)
        
        new_user = {
            "id": user_id,
            "email": email,
            "password_hash": password_hash,
            "full_name": full_name,
            "role": role,
            "department": data.get("department"),
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "last_login": None
        }
        
        db.users.insert_one(new_user)
        
        return jsonify({
            "id": user_id,
            "email": email,
            "full_name": full_name,
            "role": role
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
