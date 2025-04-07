
from decimal import Decimal
from typing import List, Optional
from db.dummy_db import AtomicOperation
from models.transaction_model import Transaction
from models.account_model import Account
from db.base_repo import DummyBaseRepository
from shared.error_handlers import *
from datetime import datetime


class AccountRepository(DummyBaseRepository[Account]):
    def __init__(self):
        super().__init__(
            model=Account, 
            collection_name='accounts',
            # unique_fields=['account_number', 'user_id'] 
            )
        
    def create(self, entity_data: dict) -> Account:
        """Create account with validation"""
        existing_accounts = self.find_by_field('account_number', entity_data['account_number'])
    
        if any(a.user_id == entity_data['user_id'] for a in existing_accounts):
            raise BusinessRuleViolation("Account number already exists for this user")
    
        return super().create(entity_data)
        
    
    def find_by_user(self, user_id: str) -> list[Account]:
        """Find accounts by user ID"""
        return self.find_by_field('user_id', user_id)


    def find_by_account_number(self, number: str) -> Optional[Account]:
        """Find account by account number"""
        accounts = self.find_by_field('account_number', number)
        return accounts[0] if accounts else None
       
    
    def update_balance(self, account_id: str, delta: Decimal) -> Account:
        """Atomic balance update"""
        def update_fn(account: Account):
            # if account.account_type == 'credit':
            #     # Allow negative balances for credit accounts
            #     new_balance = account.balance + delta
            # else:
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
        # with AtomicOperation(self.db): 
        sender = self.update_balance(from_id, -amount),
        receiver = self.update_balance(to_id, amount)
        return sender, receiver
       
    
    def is_account_owner(self, account_id: str, user_id: str) -> bool:
        """Check if user owns the account"""
        account = self.find_by_id(account_id)
        return bool(account and account.user_id == user_id)
    
    
    def find_by_account_number(self, number: str) -> bool:
        """Check if account number exists"""
        return any(a.account_number == number 
                for a in self.collection.values())
    
    
    def get_user_accounts(self, account_id: str, user_id: str) -> List[Account]:
        """Get all accounts for a user"""
        return self.find_by_field('user_id', user_id)
    
    
    def find_by_user(self, user_id: str) -> List[Account]:
        
        return self.find_by_field('user_id', user_id)
    
    
    
    
