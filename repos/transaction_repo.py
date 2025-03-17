
from models.model import Transaction
from repos.base_repo import DummyBaseRepository
from shared.error_handlers import *
from datetime import datetime




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