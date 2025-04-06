from functools import wraps
from typing import Optional
from flask import current_app, request, g
from models.user_model import User
from repos.account_repo import AccountRepository
from repos.user_repo import UserRepository
from shared.security import SecurityUtils
from .exceptions import *
from .error_handlers import *


def get_token_from_header() -> Optional[str]:
    """Helper to extract raw token from Authorization header"""
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header[len('Bearer '):].strip()
    return None
    
#Authentication decorator
def authenticate(func):
    """Decorator to authenticate user using token"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Extract token from headers,token validation
        raw_token = get_token_from_header()
         
        if not raw_token:
            raise InvalidTokenError("Missing authentication token") 
        
        try:
            # Secure token validation
            user = UserRepository().find_by_field(
                'token_hash', SecurityUtils.hash_token(raw_token)
            )    
            # Validate token existence and expiry    
            if not user or not SecurityUtils.validate_token(raw_token, user):
                raise InvalidTokenError("Invalid or expired token")
        
            # Refresh expiry on each request
            # with dummy_db_instance.get_collection_lock('users'):
            #     user.token_expiry = datetime.utcnow() + timedelta(hours=1)  # Simple 1hr extension
            #     UserRepository().update(user)
            
            g.current_user = user
            return func(*args, **kwargs)
        
        except Exception as e:
            current_app.logger.error(f"Authentication error: {str(e)}")
            raise InvalidTokenError("Authentication failed")
    
    return wrapper


# Authorization Decorators
def account_owner_required(f):
    """Decorator to ensure the user is the owner of the account"""
    @wraps(f)
    def decorated(account_id, *args, **kwargs):
        account = AccountRepository.find_by_id(account_id)
        
        if not account or account.user_id != g.current_user.id:
            raise ForbiddenError("Account ownership verification failed")
       
        return f(account_id, *args, **kwargs)
    return decorated


# def admin_required(func):
#     """Decorator admin privileges"""
#     @wraps(func)
#     def decorated(*args, **kwargs):
#         user = get_current_user()
#         if not user.role != 'admin':
#             raise ForbiddenError("Administrator access required")  
#         return func(*args, **kwargs)
#     return decorated


def get_current_user() -> User:
    """Retrieve authenticated user from request context"""
    
    user = getattr(g, 'current_user', None) 
    if not user or not isinstance(user, User):
        raise InvalidCredentialsError("Authentication required")
    return user










