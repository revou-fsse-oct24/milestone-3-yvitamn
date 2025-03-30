from flask import Flask, Blueprint, request, jsonify
from models.user_model import Account
from services.account_service import AccountService
from repos.user_repo import UserRepository
from shared.auth_helpers import *
from shared.exceptions import *
from shared.error_handlers import *
from datetime import datetime


account_router = Blueprint('account', __name__)

#===========================Account Endpoints===================
@account_router.route('/accounts', methods=["GET","POST"])
@account_router.route('/accounts/<account_id>', methods=["GET","POST","PUT","DELETE"])
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



