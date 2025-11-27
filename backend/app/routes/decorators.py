"""Shared decorators for route protection."""

from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..models import User

def role_required(*roles):
    """Decorator to check if the current user has one of the required roles."""
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            if not user or user.role not in roles:
                return jsonify({'message': 'Access forbidden: insufficient permissions'}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper