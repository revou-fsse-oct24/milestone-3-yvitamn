from flask import Flask, Blueprint, request, jsonify
from models.model import User, Account, Transaction
from services.auth_service import AuthService
from shared.exceptions import *
from shared.error_handlers import *
from datetime import datetime
from functools import wraps


#contoh
# @router.route('/transactions', methods=['POST'])
# @authenticate
# @pin_protected
# def create_transaction(user):
#     data = TransactionSchema().load(request.json)
#     # ... rest of the code
     
#========================API Endpoints===========================
app = Flask(__name__)
router = Blueprint('router', __name__)

#Token required decorator
def authenticate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
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
    


#==============================Auth endpoint=========================
@router.route('/login', methods=['POST'])
def handle_login():
    service = AuthService()
    data = request.get_json()   
    
    try:
        user = service.login(data['username'], data['pin'])
        # print(f"DEBUG: Generated token {user.token} for user {user.id}")
        return jsonify({
            "success": True,
            "message": "Login successful",
            "data": {
                "access_token": user.token,
                "user_id": user.id
            }
        })
    except AuthenticationError as e:
        return jsonify({"success": False, "error": str(e)}), 401

@router.route('/users/me', methods=['GET'])
@authenticate
def handle_user_profile(user):
    return jsonify({
        "success": True,
        "message": "User profile retrieved successfully",
        "data": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name
            # "first_name": user.first_name,
            # "last_name": user.last_name,
            # "created_at": user.created_at.isoformat()
        }
    })




# ======================== Debug Endpoints ======================
@router.route('/debug/users', methods=["GET"])
def handle_debug_users():
    users = UserRepository().collection.values()
    return jsonify([{
        "id": u.id,
        "token": u.token
    } for u in users])
    
           
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