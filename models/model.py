from datetime import datetime
from uuid import uuid4
import uuid
import bcrypt

#=============Models=========================    
class User:
    def __init__(self, username, email, pin, first_name, last_name):
        self.id = str(uuid.uuid4()) #PK
        self.username = username
        self.email = email
        self.pin_hash = self._hash_pin(pin) #hash in real implementation
        self.first_name = first_name
        self.last_name = last_name
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.token = None
    
    def _hash_pin(self, pin):
        """Hash the PIN using bcrypt with salt."""
        if not isinstance(pin, str):
            raise ValueError("PIN must be string")
        return bcrypt.hashpw(
            pin.encode('utf-8'),
            bcrypt.gensalt()
            ).decode('utf-8')

    def verify_pin(self, pin):
        """Verify if the provided PIN matches the hash."""
        return bcrypt.checkpw(pin.encode('utf-8'), self.pin_hash.encode('utf-8'))
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
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
        