
from decimal import Decimal
from typing import List, Optional
from db.dummy_db import AtomicOperation
from models.transaction_model import Transaction
from models.user_model import Account
from db.base_repo import DummyBaseRepository
from shared.error_handlers import *
from datetime import datetime


class AccountRepository(DummyBaseRepository):
    def __init__(self):
        super().__init__(Account, 'accounts')
        
        
    def create(self, entity: Account) -> Account:
       # Check for duplicate account number
        with AtomicOperation(self.db):
            if self.find_by_account_number(entity.account_number):
                raise BusinessRuleViolation("Account number already exists")
        return super().create(entity)
        
    
    def find_by_user(self, user_id: str) -> list[Account]:
        """Get all accounts for a user using index"""
        return self.find_by_field('user_id', user_id)


    def find_by_account_number(self, number: str) -> Optional[Account]:
        account_ids = self.db._indexes['accounts']['account_number'].get(number, set())
        return self.find_by_id(next(iter(account_ids))) if account_ids else None


    def update_balance(self, account_id: str, delta: Decimal) -> Account:
        """Atomic balance update"""
        def update_fn(account: Account):
            new_balance = account.balance + delta
            if new_balance < Decimal('0'):
                raise InsufficientBalanceException(
                    account_id=account.id,
                    current_balance=account.balance,
                    required_amount=abs(delta)
                )
            
            account.balance = new_balance
            account.updated_at = datetime.now().isoformat() + 'Z'
            return account
        
        return self.atomic_update(account_id, update_fn)


    def transfer_funds(self, from_id: str, to_id: str, amount: Decimal) -> tuple[Account, Account]:
        """Atomic funds transfer between accounts"""
        with AtomicOperation(self.db): 
            return(
            self.update_balance(from_id, -amount),
            self.update_balance(to_id, amount)
            )
       
    
    def is_account_owner(self, account_id: str, user_id: str) -> bool:
        """Check if user owns the account"""
        account = self.find_by_id(account_id)
        return bool(account and account.user_id == user_id)
    
    
    def _account_number_exists(self, number: str) -> bool:
        return any(a.account_number == number 
                for a in self.collection.values())
    
    
    def get_user_accounts(self, user_id: str) -> List[Account]:
        return self.find_by_field('user_id', user_id)
    
    
    def find_by_user(self, user_id: str) -> List[Account]:
        """Index-based user account lookup"""
        return self.find_by_field('user_id', user_id)
    
    
    
    
