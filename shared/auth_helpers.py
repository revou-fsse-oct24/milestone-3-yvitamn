# from functools import wraps
# from flask import request, jsonify
# from repos.repo import UserRepository, TokenRepository
# from services.service import AuthService
# from .exceptions import *

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








