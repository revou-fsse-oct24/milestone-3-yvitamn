
from typing import Optional
from models.user_model import Transaction
from .base_repo import DummyBaseRepository
from .account_repo import AccountRepository
from shared.error_handlers import *
from datetime import datetime, timedelta


class TransactionRepository(DummyBaseRepository):
    def __init__(self):
        super().__init__(Transaction, 'transactions')
        self.account_repo = AccountRepository()
    
    def create(self, entity: Transaction) -> Transaction:
        # Validate before creation
        if entity.amount <= 0:
            raise BusinessRuleViolation("Insufficient funds")
       # Now handle stateful business rules
        match entity.transaction_type:
            case 'transfer' | 'withdrawal':
                account = self.account_repo.find_by_id(entity.from_account_id)
                if not account:
                    raise BusinessRuleViolation("Source account not found")
                if account.balance < entity.amount:
                    raise BusinessRuleViolation("Insufficient funds")
                    
            case 'deposit':
                if not self.account_repo.find_by_id(entity.to_account_id):
                    raise BusinessRuleViolation("Destination account not found")
       
       #DummyDB handle indexing through base create
        return super().create(entity)
    

    def find_by_transaction_id(self, tx_id: str) -> Optional[Transaction]:
        """Find by public transaction ID using index"""
        tx_ids = self.db._indexes['transactions']['transaction_id'].get(tx_id, set())
        return self.find_by_id(next(iter(tx_ids))) if tx_ids else None


    def update_status(self, tx_id: str, new_status: str) -> Transaction:
        transaction = self.find_by_transaction_id(tx_id)
        if not transaction:
            raise NotFoundError("Transaction not found")
            
        # Update through base class to handle indexes
        transaction.status = new_status
        return self.update(transaction)

    def find_recent(self, days: int = 7) -> list[Transaction]:
        cutoff = datetime.now() - timedelta(days=days)
        return [t for t in self.collection.values() if t.created_at > cutoff]

    def get_summary(self, account_id: str) -> dict:
        transactions = [
            t for t in self.collection.values()
            if t.from_account_id == account_id or t.to_account_id == account_id
        ]
        return {
            "total_deposits": sum(t.amount for t in transactions if t.to_account_id == account_id),
            "total_withdrawals": sum(t.amount for t in transactions if t.from_account_id == account_id),
            "last_transaction": max((t.created_at for t in transactions), default=None)
        }

    #undoing a previous transaction
    # def revert_transaction(self, transaction_id: str) -> Transaction:
    #     transaction = self.find_by_id(transaction_id)
    #     if not transaction:
    #         raise NotFoundError("Transaction not found")
            
    #     account_repo = AccountRepository()
        
    #     # Reverse the transaction
    #     if transaction.from_account_id:
    #         account_repo.update_balance(
    #             transaction.from_account_id,
    #             transaction.amount
    #         )
    #     if transaction.to_account_id:
    #         account_repo.update_balance(
    #             transaction.to_account_id,
    #             -transaction.amount
    #         )
            
    #     transaction.status = "reverted"
    #     return transaction