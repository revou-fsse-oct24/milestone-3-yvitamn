from decimal import Decimal
from repos.account_repo import AccountRepository
from repos.transaction_repo import TransactionRepository
from repos.user_repo import UserRepository       
import uuid
from models.user_model import Account
from schemas.account_schema import AccountSchema
from schemas.user_schema import *
from shared.error_handlers import *


#=================================Account Service====================
class AccountService:
    def __init__(self):
        self.account_repo = AccountRepository()
        # self.user_repo = UserRepository()
        # self.transaction_repo = TransactionRepository()
        self.schema = AccountSchema()
        
    def create_account(self, user_id: str, data: dict) -> Account:
        # Validate input
        validated = self.schema.load(data) 
        # Generate account
        return self.repo.create(Account(
            user_id=user_id,
            balance=Decimal(validated['initial_balance']),
            account_type=validated['account_type']
        ))
        
    
    def validate_account_ownership(self, account_id: str, user_id: str):
        account = self.account_repo.find_by_id(account_id)
        if not account or account.user_id != user_id:
            raise ForbiddenError("Account access denied")
    
    
    def get_user_accounts(self, user_id: str) -> list[Account]:
        return self.account_repo.find_by_user(user_id)
    
    
    def get_account(self, account_id: str, user_id: str) -> Account:
        account = self.account_repo.find_by_id(account_id)
        if not account or account.user_id != user_id:
            raise ForbiddenError("Account access denied")
        return account
    
    
    def get_account_by_id(self, user_id, account_id):
        # Verify account exists and belongs to user
        account = self.account_repo.find_by_id(account_id)
        if not account:
            raise NotFoundError("Account not found")
        if account.user_id != user_id:
            raise InvalidAccountError("Account doesn't belong to user")
        
        
    def get_account_summary(self, account_id: str) -> dict:
        """Get financial summary with transaction data"""
        account = self.account_repo.find_by_id(account_id)
        transactions = self.transaction_repo.find_by_account(account_id)
        return {
            "account_number": account.account_number,
            "current_balance": str(account.balance),
            "transaction_count": len(transactions),
            "last_transaction": max(t.created_at for t in transactions).isoformat() if transactions else None
        }
        
    def deactivate_account(self, account_id: str, user_id: str) -> Account:
        account = self.get_account(account_id, user_id)
        if account.balance != Decimal('0'):
            raise BusinessRuleViolation("Cannot deactivate account with balance")
        account.is_active = False
        return self.account_repo.update(account)
    
    # def delete_account(self, account_id: str, user_id: str) -> bool:
    #     account = self.get_account(account_id, user_id)
    #     if account.balance > 0:
    #         raise BusinessRuleViolation("Cannot delete account with balance")
    #     return self.repo.delete(account_id)