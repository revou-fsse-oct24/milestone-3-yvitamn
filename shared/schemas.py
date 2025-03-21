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
            validate.Length(min=4, max=6),
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

    @validates_schema
    def validate_pin_complexity(self, data, **kwargs):
        """Additional PIN validation"""
        pin = data.get('pin', '')
        if len(set(pin)) == 1:
            raise ValidationError("PIN cannot be all identical digits", field_name="pin")
    
    
class LoginSchema(Schema):
    username = fields.Str(required=True)
    pin = fields.Str(
        required=True, 
        error_messages={"required": "Username is required"}
    )
    pin = fields.Str(
        required=True,
        validate=validate.Length(
            min=4, 
            max=6,
            error="PIN must be 4-6 digits"
        ),
        error_messages={"required": "PIN is required"}
    )
    @validates_schema
    def validate_pin_format(self, data, **kwargs):
        if not data['pin'].isdigit():
            raise ValidationError("PIN must contain only numbers", field_name="pin")
        
class TransactionSchema(Schema):
    amount = fields.Decimal(
        required=True,
        gt=0,
        places=2,
        error_messages={
            "invalid": "Amount must be a valid number",
            "gt": "Amount must be greater than 0"
        }
    )
    type = fields.Str(
        required=True,
        validate=validate.OneOf(
            ['deposit', 'withdrawal', 'transfer'],
            error="Invalid transaction type. Allowed values: deposit, withdrawal, transfer"
        )
    )
    from_account_id = fields.Str(validate=validate_uuid)
    to_account_id = fields.Str(validate=validate_uuid)
    description = fields.Str(validate=validate.Length(max=255))
    
    @validates_schema
    def validate_account_ids(self, data, **kwargs):
        transaction_type = data.get('type')
        
        if transaction_type == 'transfer':
            if not data.get('from_account_id') or not data.get('to_account_id'):
                raise ValidationError("Both from_account_id and to_account_id are required for transfers")
                
        elif transaction_type == 'withdrawal':
            if not data.get('from_account_id'):
                raise ValidationError("from_account_id is required for withdrawals")
                
        elif transaction_type == 'deposit':
            if not data.get('to_account_id'):
                raise ValidationError("to_account_id is required for deposits")


class AccountSchema(Schema):
    account_type = fields.Str(
        required=True,
        validate=validate.OneOf(
            ['checking', 'savings', 'business'],
            error="Invalid account type. Allowed values: checking, savings, business"
        )
    )

    