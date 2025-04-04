from decimal import Decimal
from marshmallow import Schema, ValidationError, validates, fields, validate


class AccountSchema(Schema):
    account_type = fields.Str(
        required=True,
        validate=validate.OneOf(
            ['checking', 'savings', 'business'],
            error="Invalid account type"
        ),
        error_messages={"required": "Account type is required"}
    )

    initial_balance = fields.Decimal(
        required=True,
        places=2,
        validate=validate.Range(min=Decimal('0')),
        error_messages={
            "invalid": "Invalid balance format",
            "required": "Initial balance is required",
            # "min": "Minimum opening balance is 0.00"
        }
    )

    @validates('initial_balance')
    def validate_business_account(self, value, data, **kwargs):
        if data.get('account_type') == 'business' and value < Decimal('1000'):
            raise ValidationError(
                "Business accounts require minimum $1,000 balance",
                field_name="initial_balance"
            )
    