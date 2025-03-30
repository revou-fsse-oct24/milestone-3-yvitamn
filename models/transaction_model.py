from datetime import datetime, timedelta
from decimal import Decimal
import secrets
from uuid import uuid4

class Transaction:
    def __init__(self, 
                 transaction_type:str,
                 amount: float, 
                 from_account_id: str=None, 
                 to_account_id:str=None, 
                 description:str = ""):
        
        self.id = str(uuid4()) # PK & Auto-generated UUID & for internal use
        self.transaction_id = secrets.token_urlsafe(16)  # Public-facing ID
        
        self.transaction_type = transaction_type
        
        # Convert Decimal to float for storage
        self.amount = float(amount) if isinstance(amount, Decimal) else amount
        self.from_account_id = from_account_id #FK
        self.to_account_id = to_account_id  #FK
        self.description = description
        
        self.status = "pending"
        self.created_at = datetime.now()
        self.updated_at = self.created_at  # Initialize with creation time
        
        self.verification_token = secrets.token_urlsafe(32)
        self.token_expiry = datetime.now() + timedelta(hours=24)
        
        # Validate after assignment
        self._validate_initial_state()

    def _validate_initial_state(self):
        """Validate core business rules during initialization"""
        if self.amount <= 0:
            raise ValueError("Transaction amount must be positive")
            
        if self.transaction_type == 'transfer':
            if not self.from_account_id:
                raise ValueError("Transfer requires source account")
            if self.from_account_id == self.to_account_id:
                raise ValueError("Cannot transfer to same account")
        
    def to_dict(self) -> dict:
        """Safe serialization for API responses"""
        return {
            "transaction_id": self.transaction_id,
            "type": self.transaction_type,
            "amount": round(self.amount, 2), # Format amount to 2 decimal places
            "from_account": self.from_account_id,
            "to_account": self.to_account_id,
            "status": self.status,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.created_at.isoformat()   
        }

    def update_status(self, new_status: str):
        """Update transaction status with timestamp"""
        self.status = new_status
        self.updated_at = datetime.now()

    def generate_new_token(self) -> None:
        """Refresh security token"""
        self.verification_token = secrets.token_urlsafe(32)
        self.token_expiry = datetime.now() + timedelta(hours=24)
        
        
        