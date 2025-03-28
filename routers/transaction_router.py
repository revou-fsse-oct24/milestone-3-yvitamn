
from flask import Flask, Blueprint, request, jsonify
from models.user_model import Transaction
from services.transaction_service import TransactionService
from shared.auth_helpers import *
from shared.exceptions import *
from shared.error_handlers import *
from datetime import datetime


transaction_router = Blueprint('transaction', __name__)

#===========================Transaction Endpoints===================
@transaction_router.route('/transactions', methods=["GET","POST"])
@transaction_router.route('/transactions/<transaction_id>', methods=["GET","POST","PUT","DELETE"])
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
            
            
            
  