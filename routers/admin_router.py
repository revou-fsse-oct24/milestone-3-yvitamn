

from flask import Blueprint, request
from marshmallow import ValidationError

from schemas import transaction_schema
from schemas.admin_schema import AdminEmailFilterSchema, AdminTransactionQuerySchema, AdminUserQuerySchema, AdminUserUpdateSchema
from shared.auth_helpers import *
from shared.error_handlers import *
from shared.exceptions import *


admin_router = Blueprint('admin', __name__, url_prefix='/admin')
admin_service = AdminService()


# ================== Admin-only User Management ==================
# @admin_router.route('/users/<string:user_id>', methods=["PUT"])
# @authenticate
# @admin_required
# def admin_update_user(user_id):
#     """Admin updates any user's profile(including role)"""
#     try:
#         data = update_schema.load(request.get_json)
        
#         # Admin can update role - add role validation if needed
#         updated_user = admin_service.update_user(
#             admin_id=request.current_user.id,
#             target_id=user_id,
#             update_data=data
#         )
#         return format_response({
#             "id": updated_user.id,
#             "username": updated_user.username,
#             "email": updated_user.email,
#             "role": updated_user.role,
#             "message": "User updated successfully"
#         })
#     except ValidationError as e:
#         return handle_error({
#             "message": "Validation failed", 
#             "errors": e.messages
#         }, 400)
        
#     except BusinessRuleViolation as e:
#         return handle_error(str(e), 400)
#     except NotFoundError as e:
#         return handle_error(str(e), 404)
#     except Exception as e:
#         return handle_error("Admin update failed", 500)

# @admin_router.route('/users/<string:user_id>', methods=["DELETE"])
# @authenticate
# @admin_required
# def admin_delete_user(user_id):
#     """Deletes a user & associated data permanently"""
#     try:
#         admin_service.delete_user(
#             admin_id=request.current_user.id,
#             target_id=user_id
#         )
#         return format_response(
#             {"message": "User deleted successfully"}, 
#             status_code=204
#         )
#     except NotFoundError as e:
#         return handle_error(str(e), 404)
#     except ForbiddenError as e:
#         return handle_error(str(e), 403)
#     except Exception as e:
#         return handle_error("Deletion failed", 500)
    
    
@admin_router.route('/users', methods=['GET'])
@authenticate
@admin_required
def list_all_users():
    """List all users (admin only)"""
    try:
        schema = AdminUserQuerySchema()
        filters = schema.load(request.args)
        
        users = admin_service.list_users(filters)
        return format_response([u.to_admin_dict() for u in users])
    
    except ValidationError as e:
        return handle_error({"errors": e.messages}, 400)
    except Exception as e:
        return handle_error("Failed to fetch users", 500)


@admin_router.route('/users/<user_id>', methods=['GET'])
@authenticate
@admin_required
def get_users_accounts(user_id):
    """Get detailed user accounts summary"""
    try:
        summary = admin_service.get_user_summary(user_id)
        return format_response(summary)
    except NotFoundError as e:
        return handle_error(str(e), 404)


@admin_router.route('/users/email', methods=['GET'])
@authenticate
@admin_required
def get_user_by_email():
    """Get user details by exact email match (admin only)"""
    try:
        schema = AdminEmailFilterSchema()
        data = schema.load(request.args)  # Get email from query params
        
        user_data = admin_service.get_user_by_email(data['email'])
        return format_response(user_data)
        
    except ValidationError as e:
        return handle_error({"errors": e.messages}, 400)
    except NotFoundError as e:
        return handle_error(str(e), 404)
    except Exception as e:
        return handle_error("Failed to fetch user", 500)

# @admin_router.route('/accounts/<account_id>', methods=['DELETE'])
# @authenticate
# @admin_required
# def admin_delete_account(account_id):
#     """Admin can force-delete accounts with balance"""
#     try:
#         service.force_delete_account(account_id)
#         return format_response(None, 204)
#     except Exception as e:
#         return handle_error("Admin deletion failed", 500)
    
    
    #admin transaction management
# @admin_router.route('/transactions', methods=['GET'])
# @authenticate
# @admin_required
# def list_all_transactions():
#     """View all transactions in the system"""
#     try:
#         filters = transaction_schema.load(request.args)
#         transactions = admin_service.list_transactions(filters)
#         return format_response([t.to_admin_dict() for t in transactions])
    
#     except ValidationError as e:
#         return handle_error({"errors": e.messages}, 400)
#     except Exception as e:
#         return handle_error("Failed to fetch transactions", 500)
