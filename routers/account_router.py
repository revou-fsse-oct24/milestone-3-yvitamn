from typing import TYPE_CHECKING
from flask import Blueprint, Flask, request
from schemas.account_schema import AccountSchema

from services.account_service import AccountService
from shared.auth_helpers import *
from shared.exceptions import *
from shared.error_handlers import *


app = Flask(__name__)
account_router = Blueprint('account', __name__)
service = AccountService()

#===========================Account Endpoints===================
@account_router.route('/accounts', methods=["GET"])
@authenticate
def get_accounts():
    try:
        service.set_current_user()
        accounts = service.get_user_accounts(service.user.id)
        return format_response({
            "data": [account.to_api_response() for account in accounts]
        })
    except Exception as e:
        return handle_error("Failed to retrieve accounts", 500)
        
            
            
@account_router.route('/accounts', methods=['POST'])
@authenticate
def create_account():      
    try:
        service.set_current_user()
        data = AccountSchema().load(request.get_json())
        account = service.create_account(service.user.id, data)
        return format_response({"data":account.to_api_response()}, 201)  
    except ValidationError as e:
        return handle_error(e.messages, 400)    
    except BusinessRuleViolation as e:
        return handle_error(str(e), 400)
    except Exception as e:
        return handle_error("Account creation failed", 500)
               
                           
@account_router.route('/accounts/<account_id>', methods=['GET'])
@authenticate
def get_account(account_id):
    try:
        service.set_current_user() 
        account = service.get_account(account_id, service.current_user.id)
        return format_response(account.to_api_response())
    except ForbiddenError as e:
        return handle_error(str(e), 403)
    except NotFoundError as e:
        return handle_error(str(e), 404)             
               
               
# @account_router.route('/accounts/<account_id>', methods=['PUT'])
# @authenticate
# def update_account(account_id):
#     try:
#         current_user = get_current_user()
#         updated_account = service.update_account(
#             account_id, 
#             current_user.id,
#             request.get_json()
#         )
#         return format_response({    
#             "data": {
#                 "id": updated_account.id,
#                 "account_type": updated_account.account_type,
#                 "balance": updated_account.balance
#             }
#         })
#     except BusinessRuleViolation as e:
#        return handle_error(str(e), 400)
#     except Exception as e:
#         return handle_error("Update failed", 500)
#Balance can't be modified directly through account update endpoint
    
# @account_router.route('/accounts/<account_id>', methods=['DELETE'])
# @authenticate
# #owner
# def delete_account(account_id):
#     try:
#         current_user = get_current_user()
#         service.delete_account(account_id, current_user.id)
#         return format_response(None, 204)
#     except BusinessRuleViolation as e:
#         return handle_error(str(e), 400)
#     except Exception as e:
#         return handle_error("Deletion failed", 500)


