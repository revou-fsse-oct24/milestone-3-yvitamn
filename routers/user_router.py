import os
from flask import Flask, Blueprint, request
from models.user_model import User
from repos.user_repo import UserRepository
from services.user_service import UserService
from shared.auth_helpers import *
from shared.exceptions import *
from shared.error_handlers import *
from schemas.user_schema import *
from datetime import datetime


user_router = Blueprint('user', __name__)
service = UserService()
user_schema = UserSchema()
 
#==========================User Endpoints===================

@user_router.route('/users/me', methods=['GET'])
@authenticate
def get_current_user_profile():
    try:
        current_user = get_current_user()
        return format_response({
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "role": current_user.role,
            "created_at": current_user.created_at.isoformat()
    })
    except Exception as e:
        return handle_error("Failed to fetch user profile", 500)


@user_router.route('/users', methods=["GET"])
@authenticate
@admin_required
def get_all_users_route(): 
    try:
        users = service.get_all_users()
        return format_response({
            "users": [u.to_dict() for u in users],
            "count": len(users)
        })       
    except ForbiddenError as e:
        return handle_error(str(e), 403)
    except Exception as e:
        return handle_error("Failed to fetch users", 500)
        
            
@user_router.route('/register', methods=["POST"])
def register_user_route():
    try:    
        data = user_schema.load(request.get_json())
        data.pop('role', None)  #prevent unauthorized role assignment 
        
        #validate input 
        user = service.register_user(data)
        return format_response({
                    "data": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role
                    }
            }), 201     
    except ValidationError as e:
        return jsonify({"success": False, "error": str(e)}), 400

    except BusinessRuleViolation as e:
        return jsonify({"success": False, "error": str(e)}), 400

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@user_router.route('/users/me', methods=['PUT'])
@authenticate
def update_current_user():
    try:
        current_user = get_current_user()
        data = request.get_json()
        
        updated_user = service.update_user(
            user_id=current_user.id,
            email=data.get('email'),
            # pin=data.get('pin'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name')
        )
        
        return format_response({
            "id": updated_user.id,
            "username": updated_user.username,
            "email": updated_user.email,
            "message": "User successfully updated"
        })
    except ValidationError as e:
        return handle_error({
            "message": "Validation failed", 
            "errors": e.messages
        }, 400)
    except BusinessRuleViolation as e:
        return handle_error(str(e), 400)
    except Exception as e:
        return handle_error("Update failed", 500)

    
@user_router.route('/users/<string:user_id>', methods=["PUT","DELETE"])
@authenticate
@admin_required
def delete_user(user_id):
    try:
        service.delete_user(user_id)
        return format_response({"message": "User deleted successfully"}, status_code=204)
    except NotFoundError as e:
        return handle_error(str(e), 404)
    except ForbiddenError as e:
        return handle_error(str(e), 403)
    except Exception as e:
        return handle_error("Deletion failed", 500)
                
      
@user_router.route('/users/me/pin', methods=['PUT'])
@authenticate
def update_pin():
    try:
        current_user = get_current_user()
        data = request.get_json()
        service.update_pin(
            user_id=current_user.id,
            old_pin=data['old_pin'],
            new_pin=data['new_pin']
        )
        return format_response({"message": "PIN updated successfully"})
    except ValidationError as e:
        return handle_error({"message": "Validation failed", "errors": e.messages}, 400)
    except InvalidCredentialsError as e:
        return handle_error(str(e), 401)
    except Exception as e:
        return handle_error("PIN update failed", 500)