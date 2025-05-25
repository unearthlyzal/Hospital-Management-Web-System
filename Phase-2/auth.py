from functools import wraps
from flask import request, jsonify
import jwt
from datetime import datetime, timedelta
from models import User
from db import SessionLocal
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-here')  # In production, use environment variable
TOKEN_EXPIRATION = int(os.getenv('TOKEN_EXPIRATION_HOURS', '24'))  # hours

def generate_token(user_id, role):
    """Generate a JWT token for the user"""
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=TOKEN_EXPIRATION)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    """Verify and decode the JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_token_from_header():
    """Extract token from Authorization header"""
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.split(' ')[1]
    return None

def login_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_header()
        if not token:
            return {'message': 'Missing token'}, 401
        
        payload = verify_token(token)
        if not payload:
            return {'message': 'Invalid or expired token'}, 401
        
        # Add user info to request context
        request.user_id = payload['user_id']
        request.user_role = payload['role']
        return f(*args, **kwargs)
    return decorated

def role_required(allowed_roles):
    """Decorator to require specific roles"""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated(*args, **kwargs):
            if request.user_role not in allowed_roles:
                return {'message': 'Insufficient permissions'}, 403
            return f(*args, **kwargs)
        return decorated
    return decorator

def admin_required(f):
    """Decorator to require admin role"""
    return role_required(['Admin'])(f)

def get_current_user():
    """Get the current authenticated user"""
    token = get_token_from_header()
    if not token:
        return None
    
    payload = verify_token(token)
    if not payload:
        return None
    
    session = SessionLocal()
    user = session.query(User).get(payload['user_id'])
    session.close()
    return user

# Role-based access control permissions
PERMISSIONS = {
    'Admin': ['read:all', 'write:all', 'delete:all'],
    'Doctor': [
        'read:own_schedule', 'write:own_schedule',
        'read:own_appointments', 'write:medical_records',
        'read:patient_records'
    ],
    'Patient': [
        'read:own_appointments', 'write:own_appointments',
        'read:own_records', 'read:doctors'
    ]
}

def has_permission(permission):
    """Decorator to check specific permissions"""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated(*args, **kwargs):
            user_permissions = PERMISSIONS.get(request.user_role, [])
            if permission not in user_permissions:
                return {'message': 'Permission denied'}, 403
            return f(*args, **kwargs)
        return decorated
    return decorator 