
import uuid
from marshmallow.validate import Range, Length, OneOf
from marshmallow import Schema, fields, ValidationError, validates_schema, validate

def validate_uuid(value):
    try:
        uuid.UUID(value)
    except ValueError:
        raise ValidationError("Invalid UUID format")
    
class TransactionSchema(Schema):
    amount = fields.Decimal(
        required=True,
        gt=0,
        places=2,
        validate=[
            validate.Range(min=0.01, max=1000000, 
                         error="Amount must be between $0.01 and $1,000,000")
        ],
        error_messages={
            "invalid": "Invalid amount format. Must be a number with up to 2 decimal places",
            "required": "Amount is required"
        }
    )
    transaction_type = fields.Str(
        required=True,
        data_key="type",
        validate=validate.OneOf(
            ['deposit', 'withdrawal', 'transfer'],
            error="Invalid transaction type. Allowed values: deposit, withdrawal, transfer"
        ),
        error_messages={
            "required": "Transaction type is required",
            "null": "Transaction type cannot be empty"
        }
    )
    
    from_account_id = fields.Str(
        validate=[
            validate_uuid,
            validate.Length(equal=36, error="Invalid account ID length")
        ],
        error_messages={
            "invalid_uuid": "Invalid source account ID format"
        }
    )
    
    to_account_id = fields.Str(
        validate=[
            validate_uuid,
            validate.Length(equal=36, error="Invalid account ID length")
        ],
        error_messages={
            "invalid_uuid": "Invalid destination account ID format"
        }
    )
    
    description = fields.Str(
        validate=Length(max=255),
        error_messages={
            "invalid": "Description must be a string",
            "too_long": "Description cannot exceed 255 characters"
        }
    )
    
    @validates_schema
    def validate_transaction_structure(self, data, **kwargs):
        tx_type = data.get('transaction_type')
        
        match tx_type:
            case 'transfer':
                if not data.get('from_account_id') or not data.get('to_account_id'):
                    raise ValidationError("Both from_account and to_account required for transfers")
                if data.get('from_account_id') == data.get('to_account_id'):
                    raise ValidationError("Cannot transfer to the same account")
                    
            case 'withdrawal':
                if not data.get('from_account_id'):
                    raise ValidationError("from_account required for withdrawals")
                if data.get('to_account_id'):
                    raise ValidationError("Withdrawals cannot have to_account")
                    
            case 'deposit':
                if not data.get('to_account_id'):
                    raise ValidationError("to_account required for deposits")
                if data.get('from_account_id'):
                    raise ValidationError("Deposits cannot have from_account")
            
            
    @validates_schema
    def validate_amount_precision(self, data, **kwargs):
        """Ensure exactly 2 decimal places"""
        amount = data.get('amount')
        if amount is not None:
            if abs(amount.as_tuple().exponent) != 2:
                raise ValidationError(
                    "Must have exactly 2 decimal places")