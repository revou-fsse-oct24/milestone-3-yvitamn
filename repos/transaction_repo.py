
from decimal import Decimal
from typing import List, Optional
from models.user_model import Transaction
from db.base_repo import DummyBaseRepository
from .account_repo import AccountRepository
from shared.error_handlers import *
from datetime import datetime, timedelta


class TransactionRepository(DummyBaseRepository):
    def __init__(self):
        super().__init__(Transaction, 'transactions')
        
    
    def create(self, entity: Transaction) -> Transaction:
        """without business logic"""
        with self.db.atomic_update():
            if entity.amount <= Decimal('0'):
                raise BusinessRuleViolation("Amount must be positive")

            if entity.from_account_id:
                account = self.account_repo.find_by_id(entity.from_account_id)
                if not account:
                    raise InvalidAccountError("Source account not found")

        return super().create(entity)
            

    def find_by_id(self, tx_id: str) -> Optional[Transaction]:
        """Find transaction base repository method"""
        # tx_ids = self.db._indexes['transactions']['transaction_id'].get(tx_id, set())
        # return self.find_by_id(next(iter(tx_ids))) if tx_ids else None
        return super().find_by_id(tx_id)

    def update_status(self, tx_id: str, new_status: str) -> Transaction:
        valid_transitions = {
            'pending': ['completed', 'failed'],
            'failed': ['retrying'],
            'completed': ['reversed']
        }
        
        with self.db.atomic_update():
            tx = self.find_by_id(tx_id)
            current_status = tx.status
        
        if new_status not in valid_transitions.get(current_status, []):
            raise BusinessRuleViolation(f"Invalid status: {current_status} -> {new_status}")
        
        # # Update through base class to handle indexes
        # transaction.status = new_status
        # return self.update(transaction)
        """Status update without validation"""
        tx.status = new_status
        tx.updated_at = datetime.utcnow().isoformat() + 'Z'
        return super().update(tx)

    def find_by_status(self, status: str) -> List[Transaction]:
        """Status-based lookup using index"""
        tx_ids = self.db._indexes['transactions']['status'].get(status, set())
        return [self.find_by_id(tid) for tid in tx_ids]

    def find_by_account(self, account_id: str) -> List[Transaction]:
        """Index-based account transaction history"""
        from_txns = self.db._indexes['transactions']['from_account'].get(account_id, set())
        to_txns = self.db._indexes['transactions']['to_account'].get(account_id, set())
        return [self.find_by_id(tid) for tid in from_txns.union(to_txns)]
    
    
    def find_recent(self, days: int = 7) -> list[Transaction]:
        """Date-based lookup (consider adding created_at index)"""
        cutoff = datetime.now() - timedelta(days=days)
        return [
            t for t in self.collection.values() if t.created_at > cutoff]

   
    