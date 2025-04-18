from marshmallow import Schema, fields, validate


class LoginSchema(Schema):
    username = fields.Str(
        required=True,
        validate=validate.Length(min=3),
        error_messages={"required": "Username is required"}
    )
    pin = fields.Str(
        required=True,
        validate=[
            validate.Length(min=8, max=8, error="PIN must be 8 digits"),
            validate.Regexp(r'^\d+$', error="PIN must contain only numbers")
        ],
        error_messages={"required": "PIN is required"}
    )