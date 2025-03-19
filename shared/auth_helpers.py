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
            return f(*args, **kwargs)
        
        token = request.headers.get('Authorization')
        if not token:
            raise UnauthorizedError("Missing authentication token")
        
        # Extract the token value 
        token = token.replace('Bearer ', '', 1)
        # print(f"Cleaned token: {token}")     

        user_repo = UserRepository()
        user = user_repo.find_by_token(token)
        # print(f"Found user: {user}") 
        if not user:
            raise InvalidTokenError("Invalid authentication token")
            
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








