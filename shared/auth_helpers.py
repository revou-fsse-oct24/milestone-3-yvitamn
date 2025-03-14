from functools import wraps
from flask import request, jsonify
from repos.repo import UserRepository, TokenRepository
from services.service import AuthService
from .exceptions import *

def get_current_user():
    token = request.headers.get('Authorization')
    user = UserRepository().find_by_token(token)
    if not user:
        raise InvalidTokenError()
    return user

def pin_protected(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = get_current_user()
        pin_attempt = request.json.get('pin')
        
        try:
            AuthService.validate_pin(user, pin_attempt)
            return func(*args, **kwargs)
        except InvalidPinError as e:
            return jsonify({"error": str(e)}), e.code          
    return wrapper



















# def get_current_user():
#     """Retrieve current user from Authorization header"""
#     token = request.headers.get('Authorization')
#     if not token:
#         return None
#     if not TokenRepository().validate_token(token):
#         return None
    
#     token_data = TokenRepository().get_token_data(token)
#     return UserRepository().get_user_by_id(token_data['user_id'])
    
    
# def token_required(f):
#     """Decorator for endpoints requiring authentication"""
#     def wrapper(*args, **kwargs):
#         user = get_current_user()
#         if not user:
#             return jsonify({'message': 'Unauthorized'}), 401
#         return f(user, *args, **kwargs)
#     return wrapper

# def validate_transaction_password(user_id, password):
#     """Reusable password checker for critical transactions"""
#     user = UserRepository().get_user_by_id(user_id)
#     if not user:
#         return False
#     return check_password_hash(user['password_hash'], password)
    