from dataclasses import dataclass
from typing import List, Optional
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

@dataclass
class User:
    """User model for authentication"""
    id: str
    email: str
    password_hash: str
    full_name: str
    role: str  # admin, scheduler, viewer
    department: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    def set_password(self, password: str):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_sensitive: bool = False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'department': self.department,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        
        if include_sensitive:
            data['password_hash'] = self.password_hash
        
        return data
    
    @staticmethod
    def from_dict(data: dict) -> 'User':
        """Create User from dictionary"""
        return User(
            id=data['id'],
            email=data['email'],
            password_hash=data['password_hash'],
            full_name=data['full_name'],
            role=data['role'],
            department=data.get('department'),
            is_active=data.get('is_active', True),
            created_at=data.get('created_at'),
            last_login=data.get('last_login')
        )
    
    def has_permission(self, required_role: str) -> bool:
        """Check if user has required permission level"""
        role_hierarchy = {
            'viewer': 1,
            'scheduler': 2,
            'admin': 3
        }
        
        user_level = role_hierarchy.get(self.role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        return user_level >= required_level