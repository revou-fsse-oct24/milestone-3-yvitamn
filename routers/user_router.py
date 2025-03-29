import os
from flask import Flask, Blueprint, request, jsonify
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
    current_user = get_current_user()
    return jsonify({
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "created_at": current_user.created_at.isoformat()
    })


@user_router.route('/users', methods=["GET"])
@authenticate
def get_all_users_route(): 

        users = UserService().get_all_users()
        return jsonify([u.to_dict() for u in users])       
    # raise ForbiddenError("Access restricted in production")

    
    # service = UserService()
       
    # users = service.get_all_users()
    # return jsonify([{
    #             "id": u.id,
    #             "username": u.username,
    #             "email": u.email
    #             "created_at": u.created_at.isoformat()
    # } for u in users])
            
@user_router.route('/register', methods=["POST"])
def register_user_route():
    try:    
        data = request.get_json()
        
        #validate input 
        errors = user_schema.validate(data)
        if errors:
            return jsonify({"success": False, "error": "Validation failed"}), 400
        
        data.pop('role', None)  #prevent unauthorized role assignment     
        user = UserService().register_user(data)   
        
        return jsonify({
                    "success": True,
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

def update_current_user():
    current_user = get_current_user()
    data = request.get_json()
    
    updated_user = service.update_user(
        user_id=current_user.id,
        email=data.get('email'),
        pin=data.get('pin'),
        first_name=data.get('first_name'),
        last_name=data.get('last_name')
    )
    
    return jsonify({
        "id": updated_user.id,
        "username": updated_user.username,
        "email": updated_user.email
    })
    
@user_router.route('/users/<user_id>', methods=["PUT","DELETE"])
@authenticate
def handle_users(user_id):
    
    match request.method.lower():           
        case "put":
            data = request.get_json()
           
            try:
                updated_user = service.update_user(
                    user_id,
                    data.get('username'),
                    data.get('email'),
                    data.get('pin')
                )
                return jsonify({
                    "success": True,
                    "data": {
                        "id": updated_user.id,
                        "username": updated_user.username,
                        "email": updated_user.email
                    }
                })
            except BusinessRuleViolation as e:
                return jsonify({"success": False, "error": str(e)}), 400
                
        # case "delete":
        #     try:
        #         service.delete_user(user_id)
        #         return jsonify({
        #             "success": True,
        #             "message": "User deleted successfully"
        #         })
        #     except BusinessRuleViolation as e:
        #         return jsonify({"success": False, "error": str(e)}), 400


# routes.py (TEMPORARY FOR TESTING ONLY)
# @router.route('/users', methods=['GET'])
# @authenticate
# def get_all_users():
#     service = UserService()
#     return jsonify([user.to_dict()
#         for user in service.user_repo.find_all()
#     ])
    
