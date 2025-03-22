from functools import wraps
from flask import request, jsonify
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
        
        # Extract token from headers
        token = request.headers.get('Authorization')
        if not token:
            raise UnauthorizedError("Missing authentication token")
        
        # Clean token format
        if token.startswith('Bearer '):
            token = token[7:]
        # print(f"Cleaned token: {token}")     

        # Validate token against users
        user_repo = UserRepository()
        user = user_repo.find_by_token(token)
            
        if not user:
            raise InvalidTokenError("Invalid or expired token")
            
        return func(user, *args, **kwargs)
    return wrapper


#for admin auth
def admin_required(func):
    @wraps(func)
    def wrapper(user, *args, **kwargs):
        if not hasattr(user, 'role') or user.role != 'admin':
            raise ForbiddenError("Admin privileges required")
        return func(user, *args, **kwargs)
    return wrapper


# def get_current_user():
#     token = request.headers.get('Authorization')
#     user = UserRepository().find_by_token(token)
#     if not user:
#         raise InvalidTokenError()
#     return user

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








