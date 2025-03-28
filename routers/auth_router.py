from flask import Flask, Blueprint, request, jsonify
from db.dummy_db import DummyDB
from models.user_model import *
from services.auth_service import AuthService
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
     
app = Flask(__name__)
auth_router = Blueprint('auth', __name__)



#==============================Auth endpoint=========================
@auth_router.route('/login', methods=['POST'])
def handle_login():
    service = AuthService()
    data = request.get_json()   
    
    try:
        # Required data check
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        user = service.login(data)
        print(f"DEBUG: Generated token {user.token} for user {user.id}")
        return jsonify({
            "success": True,
            "user_id": user.id,
            "token": user.token #token generated during login
        }), 200
        
    except ValidationError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    
    except AuthenticationError as e:
        return jsonify({"success": False, "error": str(e)}), 401
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    
@auth_router.route('/users/me', methods=['GET'])
@authenticate
def handle_user_profile():
    return jsonify({
        "success": True,
        "message": "User profile retrieved successfully",
        "data": {
            "id": g.user.id,
            "username": g.user.username,
            "email": g.user.email,
            "full_name": g.user.full_name,
            "created_at": g.user.created_at.isoformat()
        }
    })

@auth_router.route('/admin', methods=['GET'])
@authenticate  
@admin_required  
def admin_dashboard(admin_user):
    return jsonify({
        "message": "Admin dashboard",
        "data": "Sensitive admin-only data"
    })
    
@auth_router.route('/debug/users', methods=["GET"])
def handle_debug_users():
    return jsonify({
        "users": [
            {"id": u.id, "username": u.username} 
            for u in DummyDB.users.values()
        ]
    })

# ======================== Debug Endpoints ======================

           
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