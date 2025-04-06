
from decimal import Decimal, InvalidOperation
import uuid
from marshmallow.validate import Length
from marshmallow import Schema, fields, ValidationError, validates, validate

# def validate_uuid(value):
#     try:
#         uuid.UUID(value)
#     except ValueError:
#         raise ValidationError("Invalid UUID format")
    
class TransactionSchema(Schema):
    amount = fields.Decimal(
        required=True,
        places=2,
        validate=[
            validate.Range(min=Decimal('0.01'), max=Decimal('1000000.00'))
        ],
        error_messages={
            "invalid": "Invalid amount format. Use up to 2 decimal places",
            "required": "Amount is required",
            "min": "Minimum transaction amount is 0.01",
            "max": "Maximum transaction amount is 1,000,000.00"
        }
    )
    transaction_type = fields.Str(
        required=True,
        data_key="type",
        validate=validate.OneOf(
            ['deposit', 'withdrawal', 'transfer'],
            error="Invalid transaction type. Valid values: deposit, withdrawal, transfer"
        )
        # error_messages={
        #     "required": "Transaction type is required",
        #     "null": "Transaction type cannot be empty"
        # }
    )
    
    from_account_id = fields.Str(
        validate=[
            # validate_uuid,
            validate.Regexp(
               r'^ACCT-[a-f0-9]{12}$',
        error="Invalid source account ID format"
            )
        ]    
    )
    
    to_account_id = fields.Str(
        validate=[
            # validate_uuid,
      validate.Regexp(
               r'^ACCT-[a-f0-9]{12}$',
        error="Invalid destination account ID format"
            )
        ]    
    )
    
    description = fields.Str(
        validate=Length(max=255),
        error_messages={
            # "invalid": "Description must be a string",
            "too_long": "Description cannot exceed 255 characters"
        }
    )
    
    created_at = fields.DateTime(
        required=True,
        format='iso',
        error_messages={"invalid": "Invalid ISO timestamp"}
    )
     
    updated_at = fields.DateTime(
        format='iso',
        error_messages={"invalid": "Invalid ISO timestamp"}
    )
    
    @validates
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
            
            
    @validates
    def validate_amount_precision(self, data, **kwargs):
        """Strict decimal validation"""
        try:
            amount = Decimal(str(data['amount'])).normalize()
            if abs(amount.as_tuple().exponent) != 2:
                raise ValidationError(
                    "Must have exactly 2 decimal places", 
                    field_name="amount"
                )
        except (TypeError, InvalidOperation):
            raise ValidationError(
                "Invalid amount format", 
                field_name="amount"
            )