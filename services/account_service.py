from repos.account_repo import AccountRepository
from repos.user_repo import UserRepository       
import uuid
from models.model import Account
from shared.schemas import *
from shared.error_handlers import *


#=================================Account Service====================
class AccountService:
    def __init__(self):
        self.account_repo = AccountRepository()
        self.user_repo = UserRepository()
        
    def create_account(self, user_id, account_type):
        # Validate user exists
        if not self.account_repo.find_by_id(user_id):
            raise NotFoundError("User not found")
    
        # Validate account type
        valid_account_types = ['checking', 'savings', 'credit']  # Example types
        if account_type not in valid_account_types:
            raise BusinessRuleViolation(
                description=f"Invalid account type: {account_type}. Valid types are: {', '.join(valid_account_types)}",
                code=400
            )
        
    # Create account with consecutive account_number
        account = Account(
            user_id=user_id, # UUID from authenticated user
            account_type=account_type,
        )
        return self.account_repo.create(account)
    
    def get_user_accounts(self, user_id):
        return self.account_repo.find_by_user(user_id)
    
    def get_account_by_id(self, user_id, account_id):
        # Verify account exists and belongs to user
        account = self.account_repo.find_by_id(account_id)
        if not account:
            raise NotFoundError("Account not found")
        if account.user_id != user_id:
            raise InvalidAccountError("Account doesn't belong to user")