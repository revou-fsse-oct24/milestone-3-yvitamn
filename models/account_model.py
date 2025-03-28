






class Account:
    def __init__(self, user_id, account_type):
        self.id = str(uuid.uuid4()) #PK for account_id
        self.account_number = None # will be set by repo
        self.user_id = user_id # UUID from User model & FK
        self.account_type = account_type  #checking,savings,credit
        self.balance = 0.0
        self.is_active = True
        self.created_at = datetime.now()
        self.updated_at = datetime.now()