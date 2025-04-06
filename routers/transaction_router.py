
from flask import Blueprint, Flask, request
from schemas import transaction_schema
from schemas.transaction_schema import TransactionSchema
from services.transaction_service import TransactionService
from shared.auth_helpers import *
from shared.exceptions import *
from shared.error_handlers import *
from datetime import datetime

app = Flask(__name__)
transaction_router = Blueprint('transaction', __name__)
service = TransactionService()
transaction_schema = TransactionSchema()

#===========================Transaction Endpoints===================
@transaction_router.route('/transactions', methods=["GET"])
@authenticate 
# @pinprotected should be here
def get_transactions():
    """Get all transactions with optional filters"""
    try:
        service.set_current_user() 
        
        # Parse query parameters
        account_id = request.args.get('account_id')
        start_date = request.args.get('start')
        end_date = request.args.get('end')
        # data = transaction_schema.load(request.get_json())
        
        # Validate date format
        filters = {}
        if start_date:
            try:
                filters['start_date'] = datetime.fromisoformat(start_date)
            except ValueError:
                return handle_error("Invalid start_date format. Use ISO 8601", 400)
        
        if end_date:
            try:
                filters['end_date'] = datetime.fromisoformat(end_date)
            except ValueError:
                return handle_error("Invalid end_date format. Use ISO 8601", 400)
        
        transactions = service.get_user_transactions(
            service.current_user.id, 
            account_id=account_id,
            filters=filters
        )
        return format_response({
            "data": [
                transaction_schema.dump(t) for t in transactions]     
        }), 200
    
    except ValidationError as e:
        return handle_error({
            "message": "Validation failed",
            "errors": e.normalized_messages()
        }, 400)
    except BusinessRuleViolation as e:
        return handle_error(str(e), 403)
    except Exception as e:
        return handle_error("Failed to retrieve transactions", 500)            
                

@transaction_router.route('/transactions/<string:transaction_id>', methods=["GET"])
@authenticate
@account_owner_required
def get_transactions_details(transaction_id):
    """Get detailed transaction"""
    try:
        service.set_current_user()
        transaction = service.get_transaction_details(service.current_user.id, transaction_id)
        return format_response({
            "data": transaction_schema.dump(transaction) 
        })
    except NotFoundError as e:
        return handle_error(str(e), 404)
    except ForbiddenError as e:
        return handle_error(str(e), 403)
    except Exception as e:
        return handle_error("Failed to retrieve transaction", 500)    
  
           
@transaction_router.route('/transactions', methods=['POST'])
@authenticate           
def create_transaction():
    """Create a new transaction"""  
    try:   
        service.set_current_user()
        data = transaction_schema.load(request.get_json())        
        transaction = service.create_transaction(service.current_user.id, data)
        
        return format_response({ 
            "data": {
                "transaction_id": transaction.public_id,
                "status": transaction.status,
                "message": "Transaction created successfully",
                "verification_required": transaction.status == 'pending'
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
        
 
 
# ====================== Security Endpoints ======================
@transaction_router.route('/transactions/<string:txn_id>/verify', methods=['POST'])
@authenticate
def verify_transaction(txn_id):
    """Verify pending transaction"""
    try:
        service.set_current_user()
        token = request.json.get('verification_token')
        transaction = service.verify_transaction(
            service.current_user.id,
            txn_id,
            token
        )
        
        return format_response({
            "status": transaction.status,
            "message": "Transaction verified successfully"
        })
        
    except InvalidTokenError as e:
        return handle_error(str(e), 401)
    except NotFoundError as e:
        return handle_error(str(e), 404)
    except ForbiddenError as e:
        return handle_error(str(e), 403)
    except Exception as e:
        return handle_error("Verification failed", 500)
  
#   GET /transactions?account_id=acc_123:
#   self.find_by_field('from_account', 'acc_123') 