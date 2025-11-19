"""Authentication and authorization middleware."""

import jwt
import os
from functools import wraps
from flask import request, jsonify
from datetime import datetime, timedelta
from typing import Optional, Callable, Any


class AuthError(Exception):
    """Authentication error exception"""
    def __init__(self, message: str, status_code: int = 401):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AuthMiddleware:
    """Handles JWT verification and role checks"""
    
    def __init__(self):
        self.secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
        self.algorithm = 'HS256'
        self.access_token_expires = timedelta(hours=24)
        self.refresh_token_expires = timedelta(days=30)
    
    def generate_access_token(self, user_id: str, role: str, email: str) -> str:
        """Generate JWT access token"""
        payload = {
            'user_id': user_id,
            'role': role,
            'email': email,
            'type': 'access',
            'exp': datetime.utcnow() + self.access_token_expires,
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def generate_refresh_token(self, user_id: str) -> str:
        """Generate JWT refresh token"""
        payload = {
            'user_id': user_id,
            'type': 'refresh',
            'exp': datetime.utcnow() + self.refresh_token_expires,
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> dict:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthError('Token has expired', 401)
        except jwt.InvalidTokenError:
            raise AuthError('Invalid token', 401)
    
    def get_token_from_header(self) -> Optional[str]:
        """Extract token from Authorization header"""
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header:
            return None
        
        parts = auth_header.split()
        
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            raise AuthError('Invalid authorization header format. Expected: Bearer <token>')
        
        return parts[1]
    
    def get_current_user(self) -> dict:
        """Get current authenticated user from token"""
        token = self.get_token_from_header()
        
        if not token:
            raise AuthError('No authentication token provided')
        
        payload = self.verify_token(token)
        
        if payload.get('type') != 'access':
            raise AuthError('Invalid token type')
        
        return {
            'user_id': payload['user_id'],
            'role': payload['role'],
            'email': payload['email']
        }
    
    def require_auth(self, f: Callable) -> Callable:
        """Decorator to require authentication"""
        @wraps(f)
        def decorated_function(*args: Any, **kwargs: Any) -> Any:
            try:
                user = self.get_current_user()
                request.current_user = user
                return f(*args, **kwargs)
            except AuthError as e:
                return jsonify({'error': e.message}), e.status_code
            except Exception as e:
                return jsonify({'error': 'Authentication failed'}), 401
        
        return decorated_function
    
    def require_role(self, required_role: str) -> Callable:
        """Decorator to require specific role"""
        def decorator(f: Callable) -> Callable:
            @wraps(f)
            def decorated_function(*args: Any, **kwargs: Any) -> Any:
                try:
                    user = self.get_current_user()
                    request.current_user = user
                    
                    # Role hierarchy: viewer < scheduler < admin
                    role_hierarchy = {
                        'viewer': 1,
                        'scheduler': 2,
                        'admin': 3
                    }
                    
                    user_level = role_hierarchy.get(user['role'], 0)
                    required_level = role_hierarchy.get(required_role, 0)
                    
                    if user_level < required_level:
                        return jsonify({
                            'error': 'Insufficient permissions',
                            'required_role': required_role,
                            'user_role': user['role']
                        }), 403
                    
                    return f(*args, **kwargs)
                    
                except AuthError as e:
                    return jsonify({'error': e.message}), e.status_code
                except Exception as e:
                    return jsonify({'error': 'Authorization failed'}), 403
            
            return decorated_function
        return decorator
    
    def refresh_access_token(self, refresh_token: str, user_id: str, role: str, email: str) -> str:
        """Generate new access token using refresh token"""
        try:
            payload = self.verify_token(refresh_token)
            
            if payload.get('type') != 'refresh':
                raise AuthError('Invalid token type for refresh')
            
            if payload.get('user_id') != user_id:
                raise AuthError('Token user mismatch')
            
            return self.generate_access_token(user_id, role, email)
            
        except AuthError:
            raise
        except Exception:
            raise AuthError('Token refresh failed')


# Global auth middleware instance
auth_middleware = AuthMiddleware()


# Decorator shortcuts
def require_auth(f: Callable) -> Callable:
    """Require authentication decorator"""
    return auth_middleware.require_auth(f)


def require_role(role: str) -> Callable:
    """Require specific role decorator"""
    return auth_middleware.require_role(role)


def require_admin(f: Callable) -> Callable:
    """Require admin role decorator"""
    return auth_middleware.require_role('admin')(f)


def require_scheduler(f: Callable) -> Callable:
    """Require scheduler role or higher decorator"""
    return auth_middleware.require_role('scheduler')(f)


def require_viewer(f: Callable) -> Callable:
    """Require viewer role or higher decorator"""
    return auth_middleware.require_role('viewer')(f)
