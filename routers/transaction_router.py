
from flask import Flask, Blueprint, request, jsonify
from models.user_model import Transaction
from schemas.transaction_schema import TransactionSchema
from services.transaction_service import TransactionService
from shared.auth_helpers import *
from shared.exceptions import *
from shared.error_handlers import *
from datetime import datetime


transaction_router = Blueprint('transaction', __name__)
service = TransactionService()
transaction_schema = TransactionSchema()

#===========================Transaction Endpoints===================
@transaction_router.route('/transactions', methods=["GET","POST"])
@authenticate 
# @pinprotected should be here
def get_user_transactions(user):
    """Get all transactions for the authenticated user"""
    transactions = service.get_user_transactions(user.id)
    return jsonify({
        "data": [{
            "id": t.id,
            "amount": float(t.amount),
            "type": t.transaction_type,
            "status": t.status,
            "created_at": t.created_at.isoformat()
        } for t in transactions]
    })
                
                
                
   @transaction_router.route('/transactions/<transaction_id>', methods=["GET",             
                
                
                
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
            
            
            
  