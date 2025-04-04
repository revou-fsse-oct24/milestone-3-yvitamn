
# from marshmallow import Schema, fields, validate

# class AdminUserUpdateSchema(Schema):
#     role = fields.Str(validate=validate.OneOf(['user', 'admin']))
#     email = fields.Email()
#     locked = fields.Bool()

# class AdminTransactionQuerySchema(Schema):
#     start_date = fields.Date()
#     end_date = fields.Date()
#     min_amount = fields.Float()
#     transaction_type = fields.Str(validate=validate.OneOf(['deposit', 'withdrawal', 'transfer']))