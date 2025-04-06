from flask import jsonify
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException
from .exceptions import *


def format_response(data=None, success=True, status_code=200):
    """Standard response formatter for all endpoints"""
    if data is None:
        data = {}
        
    return jsonify({
        "data": data,
        "success": success
    }), status_code

def handle_error(message, status_code):
    """Error response formatter"""
    return jsonify({
        "data": {
            "message": message
        },
        "success": False
    }), status_code


def register_error_handlers(app):  
    @app.errorhandler(APIException)
    def handle_api_exception(e):
        return jsonify({
            "error": e.description,
            "code": e.code,
            "details": getattr(e, 'details', None)
        }), e.code
        
    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        return jsonify({
            "error": "Validation Error",
            "details": e.messages,
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
            
    @app.errorhandler(404)
    def handle_not_found(e):
        return jsonify({
            "error": "Resource not found",
            "code": 404
        }), 404
            

   
    # @app.errorhandler(InvalidCredentialsError)
    # def handle_invalid_creds(e):
    #     SecurityUtils.handle_failed_login(request.email)  # If implementing lockouts
    #     return format_response({"message": str(e)}, False, 401)
    
   
    