from datetime import datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
import secrets
from typing import Optional
from uuid import uuid4

class Transaction:
    def __init__(self, 
                 transaction_type:str,
                 amount: Decimal, 
                #  from_balance_before: float
                #  from_balance_after: float
                #  to_balance_before: float
                #  to_balance_after: float
                 from_account_id: Optional[str]=None, 
                 to_account_id: Optional[str]=None, 
                 description:str = ""):
        """
        Banking transaction model with strict validation
        
        Args:
            transaction_type: One of ['deposit', 'withdrawal', 'transfer']
            amount: Positive decimal value
            from_account_id: Required for withdrawals/transfers
            to_account_id: Required for transfers/deposits
            description: Transaction memo (max 255 chars)
        """
        # Transaction identifiers
        self.id = str(uuid4()) # Internal UUID Primary Key
        self.public_id = f"TX-{secrets.token_urlsafe(12)}"  # Public-facing ID
        
        # Financial details
        self.transaction_type = transaction_type
        self.amount = amount
        self.from_account_id = from_account_id #FK
        self.to_account_id = to_account_id  #FK
        self.description = description[:255]
        
        
        self.created_at = datetime.now().isoformat(timespec='milliseconds') + 'Z'
        self.updated_at = self.created_at  # Initialize with creation time
        
        # Transaction lifecycle
        self.status = "pending"
        self._verification_token = secrets.token_urlsafe(32) # For sensitive operations
        self.token_expiry = datetime.now() + timedelta(minutes=15)  # Short-lived token
        
        # Validate after assignment
        self._validate_initial_state()

    def _validate_initial_state(self):
        """Validate core business rules during initialization"""
        if self.amount <= Decimal('0'):
            raise ValueError("Transaction amount must be positive")
            
        if self.transaction_type == 'transfer'and not all([self.from_account_id, self.to_account_id]):
            raise ValueError("Transfer requires both accounts")
        if self.from_account_id == self.to_account_id:
            raise ValueError("Cannot transfer to same account")
        if self.transaction_type == 'withdrawal' and not self.from_account_id:
            raise ValueError("Withdrawals require source account")
        
    def to_api_response(self) -> dict:
        """Safe serialization for API responses"""
        return {
            "transaction_id": self.public_id,
            "type": self.transaction_type,
            "amount": str(self.amount),
            # float(self.amount.quantize(Decimal('0.00'), ROUND_HALF_UP)),
            "from_account": self.from_account_id,
            "to_account": self.to_account_id,
            "status": self.status,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.created_at
        }

    def update_status(self, new_status: str):
        """Update transaction status with timestamp"""
        self.status = new_status.lower()
        self.updated_at = datetime.now().isoformat(timespec='milliseconds') + 'Z'

    def validate_token(self, token: str) -> bool:
        """Constant-time verification token check"""
        return secrets.compare_digest(token, self._verification_token)
        
        