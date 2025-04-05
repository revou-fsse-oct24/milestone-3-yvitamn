
from email_validator import EmailNotValidError, ValidatedEmail
from marshmallow import Schema, ValidationError, fields, pre_load, validate, validates

class AdminUserQuerySchema(Schema):
    role = fields.Str(validate=validate.OneOf(['user', 'admin']))
    email = fields.Email()
#     locked = fields.Bool()


class AdminEmailFilterSchema(Schema):
    email = fields.Str(required=True)
    
    @pre_load
    def normalize_email(self, data, **kwargs):
        """Pre-process email before validation"""
        if 'email' in data:
            try:
                validated = ValidatedEmail(data['email'], check_deliverability=False)
                data['email'] = validated.normalized
            except EmailNotValidError:
                pass  # Validation will catch this
        return data
    
    @validates('email')
    def validate_email_format(self, value):
        try:
            # Validate and normalize email
            result = ValidatedEmail(value, check_deliverability=False)
            return result.normalized  # Returns normalized email
        except EmailNotValidError as e:
            raise ValidationError(str(e))
        
# class AdminTransactionQuerySchema(Schema):
#     start_date = fields.Date()
#     end_date = fields.Date()
#     min_amount = fields.Float()
#     transaction_type = fields.Str(validate=validate.OneOf(['deposit', 'withdrawal', 'transfer']))