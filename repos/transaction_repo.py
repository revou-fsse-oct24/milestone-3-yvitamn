
from typing import Optional
from models.user_model import Transaction
from .base_repo import DummyBaseRepository
from .account_repo import AccountRepository
from shared.error_handlers import *
from datetime import datetime, timedelta


class TransactionRepository(DummyBaseRepository):
    def __init__(self):
        super().__init__(Transaction, 'transactions')
        # self.account_repo = AccountRepository()
    
    def create(self, entity: Transaction) -> Transaction:
        """Atomic transaction creation"""
        try:
            
            # Final validation before persistence
            if entity.amount <= 0:
                raise BusinessRuleViolation("Invalid transaction amount")

            return super().create(entity)
        except Exception as e:
                entity.status = 'failed'
                super().create(entity)
                raise
            

    def find_by_transaction_id(self, tx_id: str) -> Optional[Transaction]:
        """Find by public transaction ID using index"""
        tx_ids = self.db._indexes['transactions']['transaction_id'].get(tx_id, set())
        return self.find_by_id(next(iter(tx_ids))) if tx_ids else None


    def update_status(self, transaction_id: str, new_status: str) -> Transaction:
        transaction = self.find_by_transaction_id(transaction_id)
        if not transaction:
            raise NotFoundError("Transaction not found")    
             
        # Validate status transition
        valid_transitions = {
            'pending': ['completed', 'failed'],
            'failed': ['retrying'],
            'completed': ['reverted']
        }
        
        if new_status not in valid_transitions.get(transaction.status, []):
            raise BusinessRuleViolation(f"Invalid status transition: {transaction.status} -> {new_status}")
        
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