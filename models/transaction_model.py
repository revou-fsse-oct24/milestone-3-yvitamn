
from datetime import datetime, timedelta
import secrets
from uuid import uuid4


class Transaction:
    def __init__(self, 
                 transaction_type,
                 amount, 
                 from_account_id=None, 
                 to_account_id=None, 
                 description=""):
        
        
        
        self.id = str(uuid4()) # PK & Auto-generated UUID & for internal use
        self.transaction_id = secrets.token_urlsafe(16)  # Public-facing ID
        
        self.transaction_type = transaction_type #deposit, withdrawal, transfer
        
        self.amount = amount
        self.from_account_id = from_account_id #FK
        self.to_account_id = to_account_id  #FK
        self.description = description
        
        self.status = "pending"
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
        self.verification_token = secrets.token_urlsafe(32)
        self.token_expiry = datetime.now() + timedelta(hours=24)
        
        
    def to_dict(self) -> dict:
        """Safe serialization for API responses"""
        return {
            "transaction_id": self.transaction_id,
            "type": self.transaction_type,
            "amount": self.amount,
            "from_account": self.from_account_id,
            "to_account": self.to_account_id,
            "status": self.status,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            
        }

    def validate_transaction(self) -> bool:
        """Check basic transaction validity"""
        if self.amount <= 0:
            raise ValueError("Transaction amount must be positive")
            
        if self.transaction_type == "transfer" and not self.from_account_id:
            raise ValueError("Transfer requires source account")
            
        return True

    def generate_new_token(self) -> None:
        """Refresh security token"""
        self.verification_token = secrets.token_urlsafe(32)
        self.token_expiry = datetime.now() + timedelta(hours=24)
        
        
        