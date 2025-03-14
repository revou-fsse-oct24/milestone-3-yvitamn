from db.dummy_db import dummy_db
from models.model import Transaction, User, Account
from repos.base_repo import DummyBaseRepository

class UserRepository(DummyBaseRepository):
    def __init__(self):
        super().__init__(model=User, collection_name='users')
      
    
    def find_by_username(self, username):
        return next((u for u in self.users.values() if u.username == username), None)


class AccountRepository(DummyBaseRepository):
    def __init__(self):
        super().__init__(model=Account, collection_name='accounts')
        
    
    def find_by_user(self, user_id):
        return [acc for acc in self.accounts.values() if acc.user_id == user_id]


class TransactionRepository(DummyBaseRepository):
    def __init__(self):
        super().__init__(model=Transaction, collection_name='transactions')
        
      
    def find_by_user(self, user_id):
        #Get account ID's with access AccountRepository through instance
        account_repo = AccountRepository()
        user_accounts = [acc.id for acc in self.accounts.values() if acc.user_id == user_id]
        
        return [
            t for t in self.transactions.values() 
            if t.from_account_id in user_accounts 
            or t.to_account_id in user_accounts
        ]
    
    def find_by_account(self, account_id):
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