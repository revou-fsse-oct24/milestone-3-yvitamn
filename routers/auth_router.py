from flask import Flask, Blueprint, request, jsonify
from db.dummy_db import DummyDB
from models.user_model import *
from schemas.user_schema import LoginSchema
from services.auth_service import AuthService
from services.user_service import UserService
from shared.exceptions import *
from shared.error_handlers import *
from shared.auth_helpers import *
from datetime import datetime

#contoh
# @router.route('/transactions', methods=['POST'])
# @authenticate
# @pin_protected
# def create_transaction(user):
#     data = TransactionSchema().load(request.json)
#     # ... rest of the code
     

auth_router = Blueprint('auth', __name__)
# login_schema = LoginSchema()
service = AuthService()

#==============================Auth endpoint=========================
@auth_router.route('/login', methods=['POST'])
def handle_login():
    """User login"""
    try:
        auth_data = service.login(request.get_json())
        # print(f"DEBUG: Generated token {auth_data.token} for user {auth_data.id}")
        return format_response({
            "access_token": auth_data.token, #token generated during login
            "expires_at": auth_data.token_expiry.isoformat(),
            "user_id": auth_data.user.id,
        }), 200
        
    except ValidationError as e:
        return handle_error({
            "message": "Validation failed", 
            "errors": e.messages
        }, 400)
    except InvalidCredentialsError as e:
        return handle_error(str(e), 401)
    except Exception as e:
        return handle_error("Login failed", 500)
 
 
@auth_router.route('/logout', methods=['POST'])
@authenticate
def handle_logout():
    """User logout"""
    try:
        service.logout(user)
        return format_response({"message": "Successfully logged out"})
    except Exception as e:
        return handle_error("Logout failed", 500) 
 
   
@auth_router.route('/users/me', methods=['GET'])
@authenticate
def get_current_user_profile(user):
    return format_response({
            "id": g.user.id,
            "username": g.user.username,
            "email": g.user.email,
            "full_name": g.user.full_name,
            "role": user.role,
            "accounts": [acc.account_number for acc in user.accounts] 
    })

@auth_router.route('/admin/users', methods=['GET'])
@authenticate  
@admin_required  
def get_all_users(user):
    """Admin-only user listing"""
    try:
        users = service.get_all_users()
        return format_response([{
            "id": u.id,
            "username": u.username,
            "email": u.email
        } for u in users])
    except ForbiddenError as e:
        return handle_error(str(e), 403)
    
# @auth_router.route('/debug/users', methods=["GET"])
# def handle_debug_users():
#     return jsonify({
#         "users": [
#             {"id": u.id, "username": u.username} 
#             for u in DummyDB.users.values()
#         ]
#     })



