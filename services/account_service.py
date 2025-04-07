from decimal import Decimal
from typing import Optional

from flask import current_app
from models.account_model import Account
from models.transaction_model import Transaction
from repos.account_repo import AccountRepository  
import uuid
from schemas.account_schema import AccountSchema
from schemas.user_schema import *
from shared.error_handlers import *


#=================================Account Service====================
class AccountService:
    def __init__(self):
        self.account_repo = AccountRepository()
        self.schema = AccountSchema()
        
    def create_account(self, user_id: str, data: dict) -> Account:
        # Validate input
        validated = self.schema.load(data) 
        # Generate account
        return self.account_repo.create(Account(
            user_id=user_id,
            balance=Decimal(validated['initial_balance']),
            account_type=validated['account_type']
        ))
        
    
    def validate_account_ownership(self, account_id: str, user_id: str):
        account = self.account_repo.find_by_id(account_id)
        if not account or account.user_id != user_id:
            raise ForbiddenError("Account access denied")
    
    def _verify_account(self, 
                        account_id: str, 
                        user_id: Optional[str],
                        amount: Optional[Decimal] = None,
                        txn_type: Optional[str] = None
                        )-> Account:
        account = self.account_repo.find_by_id(account_id)
        if not account:
            current_app.logger.warning(f"Account not found: {account_id}")
            raise InvalidAccountError("Account not found")
            
        # if not allow_third_party and account.user_id != user_id:
        #     raise ForbiddenError("Account ownership verification failed")
        if user_id and account.user_id != user_id:
            current_app.logger.warning(
                f"Ownership violation: User {user_id} tried accessing account {account_id}"
            )
            raise ForbiddenError("You don't own this account")
            
        if txn_type in ['withdrawal', 'transfer'] and account.balance < amount:
            raise InsufficientBalanceException(
                account_id=account.id, 
                current_balance=account.balance, 
                required_amount=amount)           
        
        return account
    
    
    def get_account_transactions(self, account_id: str) -> list[Transaction]:
        """Get transactions for specific account"""
        return self.transaction_repo.find_by_account(account_id)
    
    
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
        
    
    def _execute_update_balances(self, txn_type: str,
                                 from_account: Optional[Account],  
                                 to_account: Optional[Account],  
                                 amount: Decimal):
        """Atomic balance operations"""
        try:
            # with self.account_repo.atomic_update():
                if txn_type == 'deposit':
                    self.account_repo.update_balance(
                    to_account.id, 
                    amount
                )
                elif txn_type == 'withdrawal':
                    self.account_repo.update_balance(
                    from_account.id, 
                    -amount
                )
                elif txn_type == 'transfer':
                    self.account_repo.transfer_funds(
                    from_account.id, 
                    to_account.id, 
                    amount
                )
                          
        except InsufficientBalanceException as e:
            e.details = {
                'transaction_type': txn_type,
                'from_account': from_account.id if from_account else None,
                'amount': float(amount)
            }
            raise
        
        
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
        
    # def deactivate_account(self, account_id: str, user_id: str) -> Account:
    #     account = self.get_account(account_id, user_id)
    #     if account.balance != Decimal('0'):
    #         raise BusinessRuleViolation("Cannot deactivate account with balance")
    #     account.is_active = False
    #     return self.account_repo.update(account)
    
    # def delete_account(self, account_id: str, user_id: str) -> bool:
    #     account = self.get_account(account_id, user_id)
    #     if account.balance > 0:
    #         raise BusinessRuleViolation("Cannot delete account with balance")
    #     return self.repo.delete(account_id)