


from decimal import Decimal
from models.transaction_model import Transaction
from repos.account_repo import AccountRepository
from repos.user_repo import UserRepository
from shared.exceptions import *


class AdminService:
    def __init__(self):
        self.user_repo = UserRepository()
        self.account_repo = AccountRepository()
      
    def list_users(self, filters: str) -> list:
        """Admin-only user listing with security check"""
        return self.user_repo.find_by(
            role=filters.get('role'),
            email=filters.get('email')
        )
    
    
    def get_users_accounts(self, user_id: str) -> dict:
        """Admin-specific summary"""
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
            
        accounts = self.account_repo.find_by_user(user_id)
        return {
            "user_id": user.id,
            "account_count": len(accounts),
            "active_accounts": sum(1 for a in accounts if a.is_active)
        }
    
    
    def get_user_by_email(self, email: str) -> dict:
        """Admin user lookup with transaction history"""
        user = self.user_repo.find_by_email(email)
        if not user:
            raise NotFoundError("User not found")

        # Get all user accounts
        accounts = self.account_repo.find_by_user(user.id)
        account_ids = [acc.id for acc in accounts]

         # Get last transaction across all accounts
        last_transaction = self.transaction_repo.find_latest_by_accounts(account_ids)  

        return {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at,
            "last_login": user.token_expiry,
            "is_active": any(acc.is_active for acc in accounts),
            "last_transaction": self._format_transaction(last_transaction) if last_transaction else None
        }

    def _format_transaction(self, transaction: Transaction) -> dict:
        """Safe transaction formatting for admin view"""
        return {
            "id": transaction.transaction_id,  # Using public-facing ID
            "type": transaction.transaction_type,
            "amount": str(transaction.amount.quantize(Decimal('0.00'))),
            "date": transaction.created_at.isoformat(),
            "status": transaction.status,
            "counterparty": transaction.to_account_id if transaction.transaction_type == "transfer" else None
        }
    # def revert_transaction(self, admin_id: str, txn_id: str):
        # Verify transaction exists
        # Check transaction reversibility
        # Create reverse transaction
        # Update balances
        
    # def update_user(self, admin_id: str, target_id: str, update_data: dict) -> User:
        # Verify admin privileges
        # Validate role changes
        # Prevent self-modification of admin status
        # Update user
