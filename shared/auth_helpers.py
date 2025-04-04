from datetime import datetime
from functools import wraps
import secrets
from flask import request, jsonify, g
from models.user_model import User
from repos.account_repo import AccountRepository
from repos.user_repo import UserRepository
from services.auth_service import AuthService
from shared.security import SecurityUtils
from .exceptions import *
from .error_handlers import *

# def refresh_token_expiry(user):
#     """Refresh token expiration on activity"""
#     user.token_expiry = datetime.utcnow() + current_app.config['TOKEN_EXPIRY']
#     UserRepository().update(user)
    
#Authentication decorator
def authenticate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Extract token from headers,token validation
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            raise InvalidTokenError("Invalid authorization format")
            
        raw_token = auth_header[len('Bearer '):].strip()
        
        #Secure token lookup with constant-time comparison
        hashed_token = SecurityUtils.hash_token(raw_token)
        user = UserRepository().find_by_token(hashed_token)
          
        # Validate token existence and expiry    
        if not user or not _valid_token(user):
            raise InvalidTokenError("Invalid or expired token")
            
        # Store user in request context
        g.current_user = user 
        # g.token = token   
        _refresh_token_expiry(user)
        
        return func(*args, **kwargs)
    return wrapper


def _valid_token(user: User) -> bool:
    """Constant-time token of token expiry"""
    return datetime.utcnow() < user.token_expiry

def _refresh_token_expiry(user: User):
    """Reset token expiration on activity"""
    user.token_expiry = datetime.utcnow() + current_app.config['TOKEN_EXPIRY']
    UserRepository().update(user)


# Authorization Decorators

def account_owner_required(f):
    @wraps(f)
    def decorated(account_id, *args, **kwargs):
        account = AccountRepository.find_by_id(account_id)
        
        if not account or account.user_id != g.current_user.id:
            raise ForbiddenError("Account ownership verification failed")
       
        return f(account_id, *args, **kwargs)
    return decorated


def admin_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user.role != 'admin':
            raise ForbiddenError("Administrator privileges required")  
        return func(*args, **kwargs)
    return decorated


def require_role(required_role: str):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user = get_current_user()
            
            if user.role != required_role:
                raise ForbiddenError(
                    f"{required_role.capitalize()} role required")
           
            return f(*args, **kwargs)
        return wrapper
    return decorator


# Context Helpers
def get_current_user() -> User:
    """Retrieve authenticated user from request context"""
    user = getattr(g, 'current_user', None)
    
    if not user or not isinstance(user, User):
        raise InvalidCredentialsError("Authentication required")
    
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








