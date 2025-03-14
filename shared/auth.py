
from flask import request, jsonify
from repos.repo import TokenRepository, UserRepository

def get_current_user():
    """Retrieve current user from Authorization header"""
    token = request.headers.get('Authorization')
    if not token:
        return None
    if not TokenRepository().validate_token(token):
        return None
    
    token_data = TokenRepository().get_token_data(token)
    return UserRepository().get_user_by_id(token_data['user_id'])
    
    
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
    