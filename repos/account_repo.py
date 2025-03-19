
from models.model import Account
from .base_repo import DummyBaseRepository
from shared.error_handlers import *
from datetime import datetime


class AccountRepository(DummyBaseRepository):
    def __init__(self):
        super().__init__(model=Account, collection_name='accounts')
        self._next_account_number = 100000000000
        
    def create_account(self, account):
        # Assign consecutive account number
        account.account_number = str(self._next_account_number).zfill(12)
        self._next_account_number += 1
        self.collection[account.id] = account
        return account
    
    def find_by_user(self, user_id):
        return [
            acc for acc in self.collection.values() 
            if acc.user_id == user_id
        ]

    def find_by_account_number(self, account_number: str) -> Account:
        return next(
            (acc for acc in self.collection.values() 
             if acc.account_number == account_number),
            None
        )

    def update_balance(self, account_id: str, amount: float) -> Account:
        account = self.find_by_id(account_id)
        if not account:
            raise NotFoundError("Account not found")
        account.balance += amount
        account.updated_at = datetime.now()
        return account

    def transfer_funds(self, from_id: str, to_id: str, amount: float) -> tuple[Account, Account]:
        from_acc = self.find_by_id(from_id)
        to_acc = self.find_by_id(to_id)
        
        if not from_acc or not to_acc:
            raise NotFoundError("One or both accounts not found")
            
        if from_acc.balance < amount:
            raise BusinessRuleViolation("Insufficient funds")
            
        from_acc.balance -= amount
        to_acc.balance += amount
        from_acc.updated_at = to_acc.updated_at = datetime.now()
        
        return from_acc, to_acc