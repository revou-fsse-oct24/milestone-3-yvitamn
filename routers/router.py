from flask import Flask, Blueprint, request, jsonify
from models.model import User, Account, Transaction
from services.service import (
    TransactionService,
    UserService,
    AuthService,
    AccountService,    
)    
from repos.repo import UserRepository
from shared.exceptions import *
from shared.error_handlers import *
from datetime import datetime
from db.dummy_db import dummy_db
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
        print(f"Cleaned token: {token}")     

        user_repo = UserRepository()
        user = user_repo.find_by_token(token)
        print(f"Found user: {user}") 
        if not user:
            raise InvalidTokenError("Invalid authentication token")
            
        return func(user, *args, **kwargs)
    return wrapper
    
    
#==========================User Endpoints===================
@router.route('/users', methods=["GET","POST","PUT","DELETE"])
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
                
        case "put" | "delete":
            return jsonify({"success": False, "error": "Method not implemented"}), 501
            
        case _:
            return jsonify({"success": False, "error": "Method not allowed"}), 405


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


#===========================Account Endpoints===================
@router.route('/accounts', methods=["GET","POST","PUT","DELETE"])
@authenticate
def handle_accounts(user):
    # data = request.get_json()
    service = AccountService()
    match request.method.lower():
        case "get":
            accounts = service.get_user_accounts(user.id)
            return jsonify({
                "success": True,
                "data": [{
                    "id": acc.id,
                    "account_number": acc.account_number,
                    # "account_type": acc.account_type,
                    "balance": acc.balance,
                    # "created_at": acc.created_at.isoformat()
                } for acc in accounts]
            })
            
        case "post":
            data = request.get_json()
            try:
                account = service.create_account(user.id, data.get('account_type', 'checking'))
                return jsonify({
                    "success": True,
                    "data": {
                        "id": account.id,
                        "account_number": account.account_number
                    }
                }), 201
            except (BusinessRuleViolation, InvalidAccountError) as e:
                return jsonify({"success": False, "error": str(e)}), 400
                
        case "put" | "delete":
            return jsonify({"success": False, "error": "Method not implemented"}), 501
            
        case _:
            return jsonify({"success": False, "error": "Method not allowed"}), 405


@router.route('/accounts/<account_id>', methods=['GET'])
@authenticate
def get_an_account(user, account_id):
    service = AccountService()
    accounts = service.get_user_accounts(user.id)  
     
    try:
        # Get specific account with ownership validation
        account = service.get_account_by_id(user.id, account_id)
        return jsonify({
            "success": True,
            "message": "Account details retrieved",
            "data": {
                "id": account.id,
                "account_number": account.account_number,
                "account_type": account.account_type,
                "balance": account.balance,
                "created_at": account.created_at.isoformat(),
                "updated_at": account.updated_at.isoformat()
            }
        })
    except NotFoundError as e:
        return jsonify({"success": False, "error": e.description}), 404
    except InvalidAccountError as e:
        return jsonify({"success": False, "error": e.description}), 403



#===========================Transaction Endpoints===================
@router.route('/transactions', methods=["GET","POST","PUT","DELETE"])
@authenticate 
# @pinprotected should be here
def handle_transactions(user):
    # data = request.get_json()
    service = TransactionService()
    match request.method.lower():
        case "get":
            transactions = service.get_user_transaction(user.id)
            return jsonify({
                "success": True,
                "data": [{
                    "id": t.id,
                    "amount": t.amount,
                    "type": t.transaction_type
                } for t in transactions]
            })
            
        case "post":
            data = request.get_json()
            try:
                transaction = service.create_transaction(user, data)
                return jsonify({
                    "success": True,
                    "data": {
                        "transaction_id": transaction.id,
                        "status": transaction.status
                    }
                }), 201
            except BusinessRuleViolation as e:
                return jsonify({"success": False, "error": str(e)}), 400
                
        case "put" | "delete":
            return jsonify({"success": False, "error": "Method not implemented"}), 501
            
        case _:
            return jsonify({"success": False, "error": "Method not allowed"}), 405
  

# @router.route('/transactions', methods=['GET'])
# @authenticate
# def get_transactions(user):
#     service = TransactionService()
#     transactions = service.get_user_transaction(user.id)
    
#     return jsonify({
#         "success": True,
#         "message": f"Found {len(transactions)} transaction(s)",
#         "data": [{
#             "id": t.id,
#             "type": t.transaction_type,
#             "amount": t.amount,
#             "from_account": t.from_account_id,
#             "to_account": t.to_account_id,
#             "status": t.status,
#             "timestamp": t.created_at.isoformat()
#     } for t in transactions]
# })


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