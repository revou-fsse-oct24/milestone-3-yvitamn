from flask import Blueprint, request, jsonify
from models.model import User, Account, Transaction
import uuid
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

#Token required
def authenticate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({"message": "Unauthorized"}), 401
            
            user = next((u for u in dummy_db['users'].values() if u.token == token), None)
            if not user:
                return jsonify({"message": "Invalid token"}), 401
            
            return func(user, *args, **kwargs)
    return wrapper
    
    
#User endpoints
@router.route('/users', methods=['POST'])
def register():
    data = request.get_json()
    user = User(
        username=data['username'],
        email=data['email'],
        password=data['password'],
        first_name=data.get('first_name', ''),
        last_name=data.get('last_name', '')
    )
    dummy_db['users'][user.id] = user
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email
    }), 201

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
    account = Account(
        user_id=user.id,
        account_type=data.get('account_type', 'checking')
    )
    dummy_db['accounts'][account.id] = account
    return jsonify({
        "id": account.id,
        "account_number": account.account_number,
        "balance": account.balance,
        "account_type": account.account_type
    }), 201

@router.route('/accounts', methods=['GET'])
@authenticate
def get_accounts(user):
    return jsonify([{
        "id": acc.id,
        "account_number": acc.account_number,
        "balance": acc.balance,
        "account_type": acc.account_type,
        "created_at": acc.created_at.isoformat()
    } for acc in dummy_db['accounts'].values() if acc.user_id == user.id])

@router.route('/accounts/<account_id>', methods=['GET'])
@authenticate
def get_account(user, account_id):
    account = dummy_db['accounts'].get(account_id)
    if not account or account.user_id != user.id:
        return jsonify({"error": "Account not found"}), 404
    return jsonify({
        "id": account.id,
        "account_number": account.account_number,
        "balance": account.balance,
        "account_type": account.account_type,
        "created_at": account.created_at.isoformat()
    })

# Transaction Endpoints
@router.route('/transactions', methods=['POST'])
@authenticate
def create_transaction(user):
    data = request.get_json()
    transaction, error = TransactionService.create_transaction(user, data)
    
    if error:
        return jsonify({"error": error}), 400
        
    return jsonify({
        "id": transaction.id,
        "type": transaction.transaction_type,
        "amount": transaction.amount,
        "status": transaction.status,
        "from_account": transaction.from_account_id,
        "to_account": transaction.to_account_id,
        "timestamp": transaction.created_at.isoformat()
    }), 201

@router.route('/transactions', methods=['GET'])
@authenticate
def get_transactions(user):
    user_account_ids = [acc.id for acc in dummy_db['accounts'].values() if acc.user_id == user.id]
    
    return jsonify([{
        "id": t.id,
        "type": t.transaction_type,
        "amount": t.amount,
        "from_account": t.from_account_id,
        "to_account": t.to_account_id,
        "status": t.status,
        "timestamp": t.created_at.isoformat()
    } for t in dummy_db['transactions'].values() 
       if t.from_account_id in user_account_ids or t.to_account_id in user_account_ids])

# if __name__ == '__main__':
#     app.run(port=5000, debug=True)