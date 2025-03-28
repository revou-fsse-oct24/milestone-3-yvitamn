from flask import app, jsonify
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException
from .exceptions import *

def register_error_handlers(app):    
    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        return jsonify({
            "error": e.description,
            "details": getattr(e, 'details', None),
            "code": 400
        }), 400
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
            return jsonify({
                "error": e.description,
                "code": e.code
            }), e.code
    
    @app.errorhandler(Exception)
    def handle_generic_error(e):
            if isinstance(e, (BusinessRuleViolation, 
                            InvalidCredentialsError,
                            InvalidTokenError,
                            ForbiddenError)):
                return jsonify({
                    "error": str(e),
                    "code": e.code if hasattr(e, 'code') else 400
                }), e.code if hasattr(e, 'code') else 400
                
            # Log unexpected errors here
            app.logger.error(f"Unexpected error: {str(e)}")
            return jsonify({
                "error": "An unexpected error occurred",
                "code": 500
            }), 500
        

    
   
    