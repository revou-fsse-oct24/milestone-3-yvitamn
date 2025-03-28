





class AccountSchema(Schema):
    account_type = fields.Str(
        required=True,
        validate=validate.OneOf(
            ['checking', 'savings', 'business'],
            error="Invalid account type. Allowed values: checking, savings, business"
        )
    )

    