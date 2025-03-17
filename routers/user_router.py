from flask import Flask, Blueprint, request, jsonify
from models.model import User
from repos.transaction_repo import UserRepository
from services.auth_service import UserService
from shared.exceptions import *
from shared.error_handlers import *
from datetime import datetime
from functools import wraps


app = Flask(__name__)
router = Blueprint('router', __name__)

#==========================User Endpoints===================
@router.route('/users', methods=["GET","POST","PUT","DELETE"])
@authenticate
def handle_users():
    # data = request.get_json()
    service = UserService()
    
    match request.method.lower():
        case "get":
            users = service.get_all_users()
            return jsonify([{
                "id": u.id,
                "username": u.username,
                "email": u.email
            } for u in users])
            
        case "post":
            data = request.get_json()
            try:
                user = service.register_user(data)
                return jsonify({
                    "success": True,
                    "data": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "full_name": user.full_name
                    }
                }), 201
            except BusinessRuleViolation as e:
                return jsonify({"success": False, "error": str(e)}), 400
                
        case "put":
            data = request.get_json()
            try:
                updated_user = service.update_user(
                    user.id,
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
                service.delete_user(user.id)
                return jsonify({
                    "success": True,
                    "message": "User deleted successfully"
                })
            except BusinessRuleViolation as e:
                return jsonify({"success": False, "error": str(e)}), 400



           
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