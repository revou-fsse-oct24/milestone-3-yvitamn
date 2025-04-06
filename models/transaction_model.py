from datetime import datetime, timedelta
from decimal import Decimal
import secrets
from typing import Optional
from uuid import uuid4
from flask import current_app



class Transaction:
    def __init__(self, 
                 transaction_type:str,
                 amount: Decimal, 
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
        
        # Transaction security - NOW HASHED
        self.status = "pending"
        self.verification_token_hash = None
        self.token_expiry = None
        
        # Generate secure verification token
        self._generate_verification_token()
        
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
            "amount": str(self.amount.quantize(Decimal('0.00'))),
            # float(self.amount.quantize(Decimal('0.00'), ROUND_HALF_UP)),
            "from_account": self.from_account_id,
            "to_account": self.to_account_id,
            "status": self.status,
            "description": self.description,
            "created_at": self.created_at,
            # Excluded fields:
            # - id (internal UUID) 
            # - verification_token_hash
            # - token_expiry
            # - updated_at (if not needed by frontend)
        }


    def update_status(self, new_status: str):
        """Update transaction status with timestamp"""
        self.status = new_status.lower()
        self.updated_at = datetime.now().isoformat(timespec='milliseconds') + 'Z'


    def _generate_verification_token(self):
        """Secure token generation and storage"""
        from shared.security import SecurityUtils
        current_app.logger.info(f"Generated verification token for TX-{self.public_id}")
        raw_token = secrets.token_urlsafe(32)
        self.verification_token_hash = SecurityUtils.hash_token(raw_token)
        self.token_expiry = datetime.now() + timedelta(minutes=15)
        return raw_token


    def validate_token(self, token: str) -> bool:
        """Constant-time verification token check"""
        from shared.security import SecurityUtils
        return SecurityUtils.validate_token(
            raw_token=token,
            hashed_token=self.verification_token_hash
        )
        
        