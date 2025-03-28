from datetime import datetime
from functools import wraps
import secrets
from flask import request, jsonify, g
from models.user_model import User
from repos.user_repo import UserRepository
from services.auth_service import AuthService
from .exceptions import *
from .error_handlers import *


#Token required decorator
def authenticate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        
        # Skip authentication for registration/login routes
        if request.path in ['/register', '/login']:
            return func(*args, **kwargs)
        
        # Extract token from headers,token validation
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            raise InvalidTokenError("Invalid authorization format")
            
        token = auth_header[7:].strip()
        if not token or len(token) != 43: 
            raise InvalidTokenError("Malformed token")
           
        #Secure token lookup with constant-time comparison
        user_repo = UserRepository()
        user = user_repo.find_by_token(token)
            
        if not user or not _valid_token(user, token):
            raise InvalidTokenError("Invalid or expired token")
            
        # Store user in request context
        g.user = user 
        # g.token = token   
        return func(*args, **kwargs)
    return wrapper

def _valid_token(user, token: str) -> bool:
    """Constant-time token validation with expiration check"""
    return (
        secrets.compare_digest(user.token, token) and 
        user.token_expiry > datetime.utcnow()
    )

#for admin auth
def admin_required(func):
    @wraps(func)
    def wrapper(user, *args, **kwargs):
        user = getattr(g, 'current_user', None)
        
        # Defense against invalid user objects
        if not user or not isinstance(user, User):
            raise AuthenticationError("Authentication required")
            
        if user.role != 'admin':
            raise ForbiddenError("Admin privileges required")  
        return func(user, *args, **kwargs)
    return wrapper


def get_current_user() -> User:
    """Retrieve authenticated user from request context"""
    user = getattr(g, 'current_user', None)
    if not user or not isinstance(user, User):
        raise AuthenticationError("Not authenticated")
    return user




# def pin_protected(func):
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         user = get_current_user()
#         pin_attempt = request.json.get('pin')
        
#         try:
#             AuthService.validate_pin(user, pin_attempt)
#             return func(*args, **kwargs)
#         except InvalidPinError as e:
#             return jsonify({"error": str(e)}), e.code          
#     return wrapper








