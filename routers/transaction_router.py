
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
@transaction_router.route('/transactions', methods=["GET"])
@authenticate 
# @pinprotected should be here
def get_user_transactions(user):
    """Get all transactions for the authenticated user"""
    try:
        transactions = service.get_user_transactions(user.id)
        return format_response({
            "data": [{
                "id": t.id,
                "amount": float(t.amount),
                "type": t.transaction_type,
                "status": t.status,
                "created_at": t.created_at.isoformat()
            } for t in transactions]
        })
    
    except NotFoundError as e:
        return handle_error(str(e), 404)
    except Exception as e:
        return handle_error("Internal server error", 500)            
                
                
@transaction_router.route('/transactions/<string:transaction_id>', methods=["GET"])            
@authenticate
def get_transaction(user, transaction_id):            
    """Get specific transaction details"""  
    try:
        transaction = service.get_user_transaction(user.id, transaction_id)
        return format_response({
            "data": {
                "id": transaction.id,
                "amount": float(transaction.amount),
                "type": transaction.transaction_type,
                "status": transaction.status,
                "from_account": transaction.from_account_id,
                "to_account": transaction.to_account_id,
                "created_at": transaction.created_at.isoformat()     
            } 
        })
    
    except NotFoundError as e:
        return handle_error(f"Transaction {transaction_id} not found", 404)
    except ForbiddenError as e:
        return handle_error("Access to transaction denied", 403)
    except Exception as e:
        return handle_error("Internal server error", 500)       
  
           
@transaction_router.route('/transactions', methods=['POST'])
@authenticate           
def create_transaction(user):
    """Create a new transaction"""  
    try:           
        data = transaction_schema.load(request.get_json())
                
        transaction = service.create_transaction(user.id, data)
        #     user_id=user.id,
        #     transaction_type=data['type'],
        #     amount=data['amount'],
        #     from_account=data.get('from_account'),
        #     to_account=data.get('to_account'),
        #     description=data.get('description', '')
        # )
      
        return format_response({ 
            "data": {
                "transaction_id": transaction.id,
                "status": transaction.status,
                "message": "Transaction created successfully"
            }
        }), 201
            
    except ValidationError as e:
        return handle_error({
            "message": "Validation failed",
            "errors": e.messages
        }, 400)
    except BusinessRuleViolation as e:
        return handle_error(str(e), 400)
    except Exception as e:
        return handle_error("Transaction creation failed", 500)            
        
                
@transaction_router.route('/transactions/<string:transaction_id>', methods=["PUT"])            
@authenticate
def update_transaction_status(user, transaction_id):
    """Update transaction status"""  
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        transaction = service.update_transaction_status(user.id, transaction_id, data)
        #     user_id=user.id,
        #     transaction_id=transaction_id,
        #     new_status=new_status
        # )
        return format_response({
            "data": {
                "id": transaction.id,
                "status": transaction.status
            }
        })
    
    except NotFoundError as e:
        return handle_error(f"Transaction {transaction_id} not found", 404)
    except ForbiddenError as e:
        return handle_error("Update not allowed", 403)
    except Exception as e:
        return handle_error("Update failed", 500)    
    


@transaction_router.route('/transactions/<string:transaction_id>', methods=["DELETE"])            
@authenticate
def delete_transaction(user, transaction_id):
    """Delete a transaction"""
    try:        
        service.delete_user_transaction(user.id, transaction_id)        
        return format_response({
            "message": f"Transaction {transaction_id} deleted successfully"
        }), 204
    
    except NotFoundError as e:
        return handle_error(f"Transaction {transaction_id} not found", 404)
    except ForbiddenError as e:
        return handle_error("Deletion not allowed", 403)
    except Exception as e:
        return handle_error("Deletion failed", 500)
            
  