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
        # print(f"Cleaned token: {token}")     

        user_repo = UserRepository()
        user = user_repo.find_by_token(token)
        # print(f"Found user: {user}") 
        if not user:
            raise InvalidTokenError("Invalid authentication token")
            
        return func(user, *args, **kwargs)
    return wrapper
    
    
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
@router.route('/accounts', methods=["GET","POST"])
@router.route('/accounts/<account_id>', methods=["GET","POST","PUT","DELETE"])
@authenticate
def handle_accounts(user, account_id=None):
    # data = request.get_json()
    service = AccountService()
    match request.method.lower():
        case "get":
            if account_id:
                account = service.get_account_by_id(user.id, account_id)
                return jsonify({
                    "success": True,
                    "data": {
                        "id": account.id,
                        "account_number": account.account_number,
                        "balance": account.balance,
                        "account_type": account.account_type
                    }
                })
            else:
                accounts = service.get_user_accounts(user.id)
                return jsonify({
                    "success": True,
                    "data": [{
                        "id": acc.id,
                        "account_number": acc.account_number,
                        "balance": acc.balance
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
            except BusinessRuleViolation as e:
                return jsonify({"success": False, "error": str(e)}), 400
                
        case "put":
            data = request.get_json()
            try:
                updated_account = service.update_account(
                    user.id,
                    account_id,
                    data.get('account_type'),
                    data.get('balance')
                )
                return jsonify({
                    "success": True,
                    "data": {
                        "id": updated_account.id,
                        "account_type": updated_account.account_type,
                        "balance": updated_account.balance
                    }
                })
            except BusinessRuleViolation as e:
                return jsonify({"success": False, "error": str(e)}), 400
                
        case "delete":
            try:
                service.delete_account(user.id, account_id)
                return jsonify({
                    "success": True,
                    "message": "Account deleted successfully"
                })
            except BusinessRuleViolation as e:
                return jsonify({"success": False, "error": str(e)}), 400




#===========================Transaction Endpoints===================
@router.route('/transactions', methods=["GET","POST"])
@router.route('/transactions/<transaction_id>', methods=["GET","POST","PUT","DELETE"])
@authenticate 
# @pinprotected should be here
def handle_transactions(user, transaction_id=None):
    # data = request.get_json()
    service = TransactionService()
    match request.method.lower():
        case "get":
            if transaction_id:
                transaction = service.get_transaction_by_id(user.id, transaction_id)
                return jsonify({
                    "success": True,
                    "data": {
                        "id": transaction.id,
                        "amount": transaction.amount,
                        "type": transaction.transaction_type,
                        "status": transaction.status
                    }
                })
            else:
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
                
        case "put":
            data = request.get_json()
            try:
                updated_transaction = service.update_transaction(
                    user.id,
                    transaction_id,
                    data.get('status')
                )
                return jsonify({
                    "success": True,
                    "data": {
                        "id": updated_transaction.id,
                        "status": updated_transaction.status
                    }
                })
            except BusinessRuleViolation as e:
                return jsonify({"success": False, "error": str(e)}), 400
                
        case "delete":
            try:
                service.delete_transaction(user.id, transaction_id)
                return jsonify({
                    "success": True,
                    "message": "Transaction deleted successfully"
                })
            except BusinessRuleViolation as e:
                return jsonify({"success": False, "error": str(e)}), 400


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