
from decimal import Decimal
from typing import List, Optional
from models.transaction_model import Transaction
from db.base_repo import DummyBaseRepository
from .account_repo import AccountRepository
from shared.error_handlers import *
from datetime import datetime, timedelta


class TransactionRepository(DummyBaseRepository[Transaction]):
    def __init__(self):
        super().__init__(
            model=Transaction,
            collection_name='transactions',
            unique_fields=['public_id', 'verification_token_hash']
        )
        
    
    def create(self, entity_data: dict) -> Transaction:
        """""Create transaction with validation"""
        # with self.db.get_collection_lock('transactions'):
        if Decimal(entity_data['amount']) <= Decimal('0'):
            raise BusinessRuleViolation("Amount must be positive")
        return super().create(entity_data)
            

    def find_by_id(self, tx_id: str) -> Optional[Transaction]:
        """Find transaction by ID"""
        return super().find_by_id(tx_id)


    def update_status(self, tx_id: str, new_status: str) -> Transaction:
        """Update transaction status with validation"""
        valid_transitions = {
            'pending': ['completed', 'failed'],
            'failed': ['retrying'],
            'completed': ['reversed']
        }
        def update_fn(tx: Transaction):
            if new_status not in valid_transitions.get(tx.status, []):
                raise BusinessRuleViolation(f"Invalid status: {tx.status} -> {new_status}")

            tx.status = new_status
            tx.updated_at = datetime.utcnow().isoformat() + 'Z'
            return tx
        return self.atomic_update(tx_id, update_fn)


    def find_by_status(self, status: str) -> List[Transaction]:
        """Status-based lookup using index"""
        return self.find_by_field('status', status)

    def find_by_account(self, account_id: str) -> List[Transaction]:
        """Index-based account transaction history"""
        from_txns = self.find_by_field('from_account', account_id)
        to_txns = self.find_by_field('to_account', account_id)
        return from_txns + to_txns
    
    
    def find_recent(self, days: int = 7) -> list[Transaction]:
        """Date-based lookup (consider adding created_at index)"""
        cutoff = datetime.now() - timedelta(days=days)
        # If created_at is indexed in DummyDB:
        return self.find_by_field('created_at', cutoff, operator='gt')
        # Otherwise use base implementation:
        # return [t for t in self.find_all() if t.created_at > cutoff]
    
    