from marshmallow import Schema, fields, validate

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(
        required=True, 
        validate=validate.Length(min=4, max=6)
        )
    
class TransactionSchema(Schema):
    account_id = fields.Str(required=True)
    amount = fields.Float(
        required=True,
        validate=validate.Range(min=0.01)
        )
    password = fields.Str(
        required=True,
        validate=validate.Length(min=4, max=6)
    )