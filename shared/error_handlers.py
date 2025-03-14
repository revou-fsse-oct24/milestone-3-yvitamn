from flask import jsonify
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException
from .exceptions import *

def register_error_handlers(app):  
    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        return jsonify({"error": "Validation failed", "details": e.messages}), 400

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return jsonify({"error": e.description}), e.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        return jsonify({"error": "Unexpected server error"}), 500
    
   
   # InvalidTokenError() 