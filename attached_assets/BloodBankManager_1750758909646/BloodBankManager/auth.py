from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from dynamodb_models import User, UserRole

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.get_by_id(current_user_id)
        
        if not user or user.role != UserRole.ADMIN:
            return jsonify({
                'success': False,
                'message': 'Admin access required'
            }), 403
            
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get current authenticated user"""
    try:
        current_user_id = get_jwt_identity()
        if current_user_id:
            return User.get_by_id(current_user_id)
        return None
    except:
        return None

def create_user_token(user):
    """Create JWT token for user"""
    return create_access_token(
        identity=user.user_id,
        additional_claims={
            'role': user.role,
            'name': user.name,
            'email': user.email or user.username
        }
    )
