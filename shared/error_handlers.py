from flask import jsonify
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException
from shared.exception import AccountLockedError, WrongCredentialException, UserNotFoundException, InsufficientBalanceException, TransactionRetryException

def error_handlers(app):
    @app.errorhandler(400)
    def handle_bad_request(error):
        return jsonify({"error": "Bad request", "details": str(error)}), 400

    @app.errorhandler(401)
    def handle_unauthorized(error):
        return jsonify({"error": "Unauthorized", "details": "Authentication failed or token expired"}), 401

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({"error": "Resource not found","details": str(error)}), 404

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        return jsonify({"error": "Validation failed", "details": error.messages}), 400

    @app.errorhandler(Exception)
    def handle_generic_error(error):
        return jsonify({"error": "Internal server error","details": str(error)}), 500

    @app.errorhandler(UserNotFoundException)
    def handle_user_not_found_error(error):
            return jsonify({"error": f"User {error.email} not found", "code": "USER_NOT_FOUND"}), 404
  
    #during login
    @app.errorhandler(WrongCredentialException)
    def handle_wrong_credentials_error(error):
        return jsonify({"error": f"Invalid credentials for {error.email}", "code": "INVALID_CREDENTIALS"}), 401
    
    # @app.errorhandler(AccountLockedError)
    # def handle_lockout(e):
    #     return jsonify(
    #         {"error": "Account locked", 
    #          "retry_after": 3600,
    #          "code": "ACCOUNT_LOCKED"
    #     }), 429 
        
    @app.errorhandler(InsufficientBalanceException)
    def handle_insufficient_balance_error(error):
        return jsonify({
            "error": f"Insufficient balance in account {error.account_id}. Current balance: {error.balance}",
            "code": "INSUFFICIENT_BALANCE"
        }), 402
        
    # @app.errorhandler(TransactionRetryException)
    # def handle_transaction_retry_exceeded_error(error):
    #     return jsonify({
    #         "error": f"Transaction {error.transaction_id} retry limit exceeded",
    #         "code": "TRANSACTION_RETRY_LIMIT_EXCEEDED"
    #     }), 409
    
   