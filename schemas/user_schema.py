import re
from marshmallow import Schema, fields, validate, validates_schema
from uuid import UUID
from shared.error_handlers import *

# Helper function for UUID validation
def validate_uuid(uuid_str):
    try:
        UUID(uuid_str)
    except ValueError:
        raise ValidationError("Invalid UUID format")
    
    
#=============validation schemas===========
class UserSchema(Schema):
    id = fields.Str(
        validate=validate_uuid,
        error_messages={"validator_failed": "Invalid UUID format"}
    )
    username = fields.Str(
        required=True,
        validate=[
            validate.Length(min=4, max=20),
            validate.Regexp(r'^[a-zA-Z0-9_]+$',
                            error="Username can only contain letters, numbers, and underscores")
        ],
        error_messages={
            "required": "Username is required",
            "invalid": "Invalid username format"
        }
    )
    email = fields.Email(
        required=True,
        error_messages={
            "required": "Email is required",
            "invalid": "Invalid email format"
        }
    )
    pin = fields.Str(
        required=True,
        validate=[
            validate.Length(min=8, max=8),
            validate.Regexp(r'^\d+$', error="PIN must contain only numbers")
        ],
        error_messages={
            "required": "PIN is required",
            "invalid": "Invalid PIN format"
        }
    )
    first_name = fields.Str(
        validate=validate.Length(max=50),
        error_messages={"invalid": "First name must be a string"}
    )
    last_name = fields.Str(
        validate=validate.Length(max=50),
        error_messages={"invalid": "Last name must be a string"}
    )
    # Add this new field
    role = fields.Str(
        dump_only=True,  # Prevent role from being set via input
        validate=validate.OneOf(['user', 'admin']),
        error_messages={
            "validator_failed": "Invalid role specified"
        }
    )
    
   

    @validates_schema('pin')
    def validate_pin_format(self, value):
        """Additional PIN validation"""
        if len(value) != 8 or not value.isdigit():
            raise ValidationError("PIN must be 8 digits")
        if len(set(value)) == 1:
            raise ValidationError("PIN cannot be all identical digits", field_name="pin")
    
    @validates_schema('email')
    def validate_email_format(self, value):
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", value):
            raise ValidationError("Invalid email format")

    @validates_schema('username')
    def validate_username_format(self, value):
        if len(value) < 4:
            raise ValidationError("Username too short (min 4 chars)")
        if not value.isalnum():
            raise ValidationError("Username must be alphanumeric")

    
class LoginSchema(Schema):
    username = fields.Str(required=True)
    pin = fields.Str(
        required=True, 
        error_messages={"required": "Username is required"}
    )
    pin = fields.Str(
        required=True,
        validate=validate.Length(
            min=8, 
            max=8,
            error="PIN must be 8 digits"
        ),
        error_messages={"required": "PIN is required"}
    )
    @validates_schema
    def validate_pin_format(self, data, **kwargs):
        if not data['pin'].isdigit():
            raise ValidationError("PIN must contain only numbers", field_name="pin")

user_schema = UserSchema()
 