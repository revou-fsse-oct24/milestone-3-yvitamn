from datetime import datetime
from uuid import uuid4
import uuid


#=============Models=========================    
class User:
    def __init__(self, username, email, pin, first_name, last_name):
        self.id = str(uuid.uuid4())
        self.username = username
        self.email = email
        self.pin = pin
        self.first_name = first_name
        self.last_name = last_name
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.token = None
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
class Account:
    def __init__(self, user_id, account_type):
        self.id = str(uuid.uuid4())
        self.account_number = self._generate_account_number()
        self.user_id = user_id
        self.account_type = account_type
        self.balance = 0.0
        self.is_active = True
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
    def _generate_account_number(self):
        return str(uuid.uuid4().int)[:12]
    
class Transaction:
    def __init__(self, transaction_type, amount, from_account_id=None, to_account_id=None, description=""):
        self.id = str(uuid.uuid4()) # Auto-generated UUID
        self.transaction_type = transaction_type #deposit, withdrawal, transfer
        self.amount = amount
        self.from_account_id = from_account_id
        self.to_account_id = to_account_id
        self.description = description
        self.status = "pending"
        self.created_at = datetime.now()
        