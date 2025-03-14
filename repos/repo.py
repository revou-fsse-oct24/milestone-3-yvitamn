from db.dummy_db import dummy_db
from models.model import Transaction, User, Account
from repos.base_repo import DummyBaseRepository

class UserRepository(DummyBaseRepository):
    def __init__(self):
        super().__init__(model=User, collection_name='users')
      
    def find_by_token(self, token):
        return next((u for u in self.collection.values() if u.token == token), None)

    def find_by_username(self, username):
        return next((u for u in self.collection.values() if u.username == username), None)


class AccountRepository(DummyBaseRepository):
    def __init__(self):
        super().__init__(model=Account, collection_name='accounts')
        self._next_account_number = 100000000000
        
    def create(self, account):
        # Assign consecutive account number
        account.account_number = str(self._next_account_number).zfill(12)
        self._next_account_number += 1
        self.collection[account.id] = account
        return account
    
    def find_by_user(self, user_id):
        return [acc for acc in self.collection.values() if acc.user_id == user_id]


class TransactionRepository(DummyBaseRepository):
    def __init__(self):
        super().__init__(model=Transaction, collection_name='transactions')
        
      
    def find_by_user(self, user_id):
        #Get account ID's with access AccountRepository through instance
        account_repo = AccountRepository()
        user_accounts = [acc.id for acc in self.collection.values() if acc.user_id == user_id]
        
        return [
            t for t in self.transactions.values() 
            if t.from_account_id in user_accounts 
            or t.to_account_id in user_accounts
        ]
    
    def find_by_account(self, account_id: str) -> list[Transaction]:
        return [
            t for t in self.collection.values()
            if t.from_account_id == account_id
            or t.to_account_id == account_id
        ]   
    
    def find_by_type(self, transaction_type):
        """Find transactions by type"""
        return [t for t in self.collection.values() if t.transaction_type == transaction_type]

    # Update method implementation
    def update(self, transaction_id, update_data):
        transaction = self.find_by_id(transaction_id)
        if transaction:
            for key, value in update_data.items():
                if hasattr(transaction, key):
                    setattr(transaction, key, value)
            return transaction
        return None

    # Delete method implementation
    def delete(self, transaction_id):
        transaction = self.find_by_id(transaction_id)
        if transaction:
            del self.collection[transaction_id]
            return True
        return False