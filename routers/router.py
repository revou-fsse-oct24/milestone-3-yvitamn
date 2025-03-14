from flask import Blueprint, request, jsonify
from models.model import User, Account, Transaction
from services.service import (
    TransactionService,
    UserService,
    AuthService,
    AccountService,    
)    
from repos.repo import (
    
    UserRepository
)    
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

router = Blueprint('router', __name__)

#Token required decorator
def authenticate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            raise UnAuthorizedError("Missing authentication token")
            
        user = UserRepository().find_by_token(token)
        if not user:
            raise InvalidTokenError("Invalid authentication token")
            
        return func(user, *args, **kwargs)
    return wrapper
    
    
#User endpoints
@router.route('/users', methods=['POST'])
def register():
    data = request.get_json()
    service = UserService()
    
    try:
        user = service.register_user(data)
        return jsonify({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at.isoformat()}), 201    
    except BusinessRuleViolation as e:
        return jsonify({"error": str(e)}), 400

@router.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    service = AuthService()
    
    try:
        user = service.login(data['username'], data['pin'])
        return jsonify({
            "access_token": user.token,
            "user_id": user.id
        })
    except AuthenticationError as e:
        return jsonify({"error": str(e)}), 401

@router.route('/users/me', methods=['GET'])
@authenticate
def get_profile(user):
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "created_at": user.created_at.isoformat()
    })



# Account Endpoints
@router.route('/accounts', methods=['POST'])
@authenticate
def create_account(user):
    data = request.get_json()
    service = AccountService()
    
    try:
        account = service.create_account(user.id, data.get('account_type', 'checking'))
        return jsonify({
            "id": account.id,
            "account_number": account.account_number,
            "account_type": account.account_type,
            "balance": account.balance,
            "created_at": account.created_at.isoformat()
        }), 201
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400


@router.route('/accounts', methods=['GET'])
@authenticate
def get_accounts(user):
    service = AccountService()
    accounts = service.get_user_accounts(user.id)   
    return jsonify([{
        "id": acc.id,
        "account_number": acc.account_number,
        "account_type": acc.account_type,
        "balance": acc.balance,
        "created_at": acc.created_at.isoformat()
    } for acc in accounts])


@router.route('/accounts/<account_id>', methods=['GET'])
@authenticate
def get_account(user, account_id):
    service = AccountService()
    accounts = service.get_user_accounts(user.id)  
     
    try:
        # Get specific account with ownership validation
        account = service.get_account_by_id(user.id, account_id)
        return jsonify({
            "id": account.id,
            "account_number": account.account_number,
            "account_type": account.account_type,
            "balance": account.balance,
            "created_at": account.created_at.isoformat(),
            "updated_at": account.updated_at.isoformat()
        })
    except NotFoundError:
        return jsonify({"error": "Account not found"}), 404


# Transaction Endpoints
@router.route('/transactions', methods=['POST'])
@authenticate 
#pinprotected should be here
def create_transaction(user):
    data = request.get_json()
    service = TransactionService()
    
    try:
        transaction = service.create_transaction(user, data)
        return jsonify({
            "transaction_id": transaction.id,
            "status": transaction.status,
            "amount": transaction.amount,
            "type": transaction.transaction_type,
            "timestamp": transaction.created_at.isoformat()
        }), 201
    except (ValidationError, InsufficientBalanceException, InvalidAccountError) as e:
        return jsonify({"error": str(e)}), 400
  

@router.route('/transactions', methods=['GET'])
@authenticate
def get_transactions(user):
    service = TransactionService()
    transactions = service.get_user_transaction(user.id)
    
    return jsonify([{
        "id": t.id,
        "type": t.transaction_type,
        "amount": t.amount,
        "from_account": t.from_account_id,
        "to_account": t.to_account_id,
        "status": t.status,
        "timestamp": t.created_at.isoformat()
    } for t in transactions])
       
