from datetime import datetime
from decimal import Decimal
import secrets
import uuid


class Account:
    def __init__(self, user_id: str, balance: Decimal, account_type: str):
        self.id = str(uuid.uuid4()) #PK for account_id
        self.account_number = self._generate_account_number()
        self.user_id = user_id # UUID from user_model & Foreign Key
        self.account_type = account_type.lower()  #checking,savings,credit
        self.balance = balance
        self.is_active = True
        self.created_at = datetime.now().isoformat() + 'Z'
        self.updated_at = self.created_at
        
    def _generate_account_number(self):
        timestamp_part = datetime.now().strftime("%y%m%d")
        random_part = secrets.token_hex(3).upper()  # 6 chars
        check_digit = secrets.choice("ABCDE")
        return f"RV{timestamp_part}{random_part}{check_digit}"
        
    def to_api_response(self):
        return {
            "id": self.id,
            "account_number": self.account_number,
            "type": self.account_type,
            "balance": str(self.balance.quantize(Decimal('0.00'))),
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }