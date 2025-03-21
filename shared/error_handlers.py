from flask import jsonify
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException
from .exceptions import *

def register_error_handlers(app):    
    @app.errorhandler(ValidationError)
    @app.errorhandler(UnauthorizedError)
    @app.errorhandler(ForbiddenError)
    @app.errorhandler(AuthenticationError)
    @app.errorhandler(InvalidTokenError)
    @app.errorhandler(InvalidPinError)
    @app.errorhandler(BusinessRuleViolation)
    @app.errorhandler(NotFoundError)
    @app.errorhandler(InvalidAccountError)
    @app.errorhandler(HTTPException)
    def handle_auth_error(e):
        if isinstance(e, HTTPException):
            return jsonify({
                "error": e.description,
                "code": e.code
                }), e.code
        # For custom exceptions
        return jsonify({
            "error": e.description,
            "code": e.code
        }), e.code
        
    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        return jsonify({"error": "Unexpected server error"}), 500
    
   
    