



       
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