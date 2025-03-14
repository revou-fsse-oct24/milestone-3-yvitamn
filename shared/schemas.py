from marshmallow import Schema, fields, validate


#=============validation===========

class UserSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=4))
    email = fields.Email(required=True)
    pin = fields.Str(required=True, validate=validate.Length(min=8))
    first_name = fields.Str()
    last_name = fields.Str()
    
class LoginSchema(Schema):
    email = fields.Email(required=True)
    pin = fields.Str(
        required=True, 
        validate=validate.Length(min=4, max=6)
        )
    
class TransactionSchema(Schema):
    amount = fields.Decimal(required=True, gt=0)
    type = fields.Str(required=True, validate=validate.OneOf(['deposit', 'withdrawal', 'transfer']))
    from_account_id = fields.Str()
    to_account_id = fields.Str()