






   
class Transaction:
    def __init__(self, transaction_type, amount, from_account_id=None, to_account_id=None, description=""):
        self.id = str(uuid.uuid4()) # PK & Auto-generated UUID
        self.transaction_type = transaction_type #deposit, withdrawal, transfer
        self.amount = amount
        self.from_account_id = from_account_id #FK
        self.to_account_id = to_account_id  #FK
        self.description = description
        self.status = "pending"
        self.created_at = datetime.now()
        