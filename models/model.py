from datetime import datetime
from uuid import uuid4
import uuid
import bcrypt

#=============Models=========================    
class User:
    def __init__(self, username, email, pin, first_name, last_name, role='user'):        
        
        self.id = str(uuid.uuid4()) #PK
        self.username = username.strip().lower()
        self.email = email
        self.pin_hash = self._hash_pin(pin) #hash in real implementation
        self.first_name = first_name
        self.last_name = last_name
        self.role = role
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.token = None
    
    
    # Add PIN validation before hashing
        if not isinstance(pin, str):
            raise ValueError("PIN must be string type")
            
        self.pin_hash = self._hash_pin(str(pin)) #string conversion
        
    def _hash_pin(self, pin: str) -> str:
        """Hash the PIN using bcrypt with salt."""
        print(f"Hashing PIN: {pin} (Type: {type(pin)})")
        hashed = bcrypt.hashpw(pin.encode('utf-8'), bcrypt.gensalt())
        print(f"Generated hash: {hashed.decode()}")
        return hashed.decode('utf-8')

    def verify_pin(self, pin: str) -> bool:
        """Verify if the provided PIN matches the hash."""
        print(f"Verifying PIN: {pin} against {self.pin_hash}")
        return bcrypt.checkpw(
            pin.encode('utf-8'), 
            self.pin_hash.encode('utf-8')
        )
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def to_dict(self):
        """Safe serialization (excludes sensitive fields)"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
            "role": self.role
        }    
    
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
        