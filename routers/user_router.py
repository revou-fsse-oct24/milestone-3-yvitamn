from flask import Flask, Blueprint, request, jsonify
from models.model import User
from repos.user_repo import UserRepository
from services.user_service import UserService
from shared.auth_helpers import *
from shared.exceptions import *
from shared.error_handlers import *
from shared.schemas import *
from datetime import datetime



app = Flask(__name__)
user_router = Blueprint('user', __name__)

service = UserService()
 
#==========================User Endpoints===================

@user_router.route('/users', methods=["GET"])
@authenticate
def get_all_users_route():
       
        users = service.get_all_users()
        return jsonify([{
                "id": u.id,
                "username": u.username,
                "email": u.email
        } for u in users])
            
@user_router.route('/register', methods=["POST"])
# @authenticate
def register_user_route():
    try:    
        data = request.get_json()
        if not data:
            return jsonify({"error": "Empty request body"}), 400
        
        # schema = UserSchema()
        # errors = schema.validate(data)
        # if errors:
        #     return jsonify({"success": False, "error": "Validation failed", "details": errors}), 400
        
        user = UserService().register_user(data)   
        return jsonify({
                    "success": True,
                    "data": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name
                    }
            }), 201     
    except ValidationError as e:
        return jsonify({"success": False, "error": str(e)}), 400

    except BusinessRuleViolation as e:
        return jsonify({"success": False, "error": str(e)}), 400

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


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
                
        case "delete":
            try:
                service.delete_user(user_id)
                return jsonify({
                    "success": True,
                    "message": "User deleted successfully"
                })
            except BusinessRuleViolation as e:
                return jsonify({"success": False, "error": str(e)}), 400


# routes.py (TEMPORARY FOR TESTING ONLY)
# @router.route('/users', methods=['GET'])
# @authenticate
# def get_all_users():
#     service = UserService()
#     return jsonify([user.to_dict()
#         for user in service.user_repo.find_all()
#     ])
    
           
if __name__ == "__main__":
    # Run with watchdog and deep file monitoring
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=True,
        reloader_type='watchdog',
        extra_files=[
            './services/**/*.py',
            './models/**/*.py', 
            './repos/**/*.py',
            './shared/*.py'
        ]
    )