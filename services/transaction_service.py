from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Optional
from flask import current_app
from models.account_model import Account
from repos import account_repo
from repos import transaction_repo
from repos.transaction_repo import TransactionRepository   
from repos.account_repo import AccountRepository    
import uuid
from models.transaction_model import Transaction 
from models.user_model import User
from schemas.transaction_schema import TransactionSchema
from shared.error_handlers import *
from shared.exceptions import *


    
#=================================Transaction Service====================    
class TransactionService:
    def __init__(self):
        self.transaction_repo = TransactionRepository()
        self.account_repo = AccountRepository()
        self.schema = TransactionSchema()
     
        
    def create_transaction(self, user_id: str, data: dict) -> Transaction:
        
        
        # Validate and deserialize input
        validated_data = self.schema.load(data)
        transaction_type = validated_data['type']
        amount = self._validate_amount(validated_data['amount'])
        
        try:
            with self.account_repo.atomic_update(), self.transaction_repo.atomic_update():
                # Ownership verification
                from_account = self._validate_source_account(
                    user_id, transaction_type, validated_data, amount
                )
                to_account = self._validate_destination_account(
                    user_id,transaction_type, validated_data
                )
                # , allow_third_party=True)
                   
                # create transaction
                transaction = self.transaction_repo.create(
                    Transaction(
                    transaction_type=transaction_type,
                    amount=amount,
                    from_account_id=from_account.id if from_account else None,
                    to_account_id=to_account.id if to_account else None,
                    description=validated_data.get('description', ''),
                    status='pending'
                    )
                )
                
                # Update balances
                self._execute_update_balances(
                    transaction_type,
                    from_account,
                    to_account,
                    amount
                )
                
                # Finalize successful transaction
                return self._finalize_transaction(transaction, 'completed') 
            
        except Exception as e:
            current_app.logger.error(f"Transaction failed: {str(e)}")
            return self._fail_transaction(
                transaction if 'transaction' in locals() else None,
                str(e)
            )
    
    
    def _validate_amount(self, value: str) -> Decimal:
        """Validate and normalize currency amount"""
        try:
            amount = Decimal(value) if isinstance(value, str) else value
            return amount.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
        except Exception as e:
            current_app.logger.error(f"Invalid amount: {value} | Error: {str(e)}")
            raise ValidationError("Invalid amount format. Use positive decimal values with up to 2 decimal places")


    def _process_transaction(self, user_id: str, txn_type: str, 
                           amount: Decimal, data: dict) -> tuple[Optional[Account], Optional[Account]]:
        """Core transaction processing logic"""
        with self.account_repo.atomic_update():
            from_account = self._validate_source_account(user_id, txn_type, data)
            to_account = self._validate_destination_account(user_id, txn_type, data)

            if txn_type == 'deposit':
                self._update_balance(to_account, amount)
            elif txn_type == 'withdrawal':
                self._update_balance(from_account, -amount)
            elif txn_type == 'transfer':
                self._update_balance(from_account, -amount)
                self._update_balance(to_account, amount)

            return from_account, to_account
    
    
    def _finalize_transaction(self, transaction: Transaction, status: str) -> Transaction:
        """Update transaction status after successful processing"""
        transaction.status = status
        return self.transaction_repo.update(transaction)
        
        
    def _validate_source_account(self, user_id: str, txn_type: str, 
                               data: dict, amount: Decimal) -> Optional[Account]:
        if txn_type not in ['withdrawal', 'transfer']:
            return None

        account_id = data.get('from_account_id')
        if not account_id:
            raise ValidationError("Source account required for this transaction type")

        account = self.account_repo.find_by_id(account_id)
        if not account:
            current_app.logger.warning(f"Source account not found: {account_id}")
            raise InvalidAccountError("Invalid source account")

        # Ownership verification
        if account.user_id != user_id:
            current_app.logger.warning(
                f"Unauthorized access attempt: User {user_id} tried accessing account {account_id}"
            )
            raise ForbiddenError("You don't own this source account")

        # Balance check
        if account.balance < amount:
            raise InsufficientBalanceException(
                account_id=account.id,
                current_balance=account.balance,
                required_amount=amount
            )
        
        return account
            
      
    def _validate_destination_account(self, user_id: str, data: dict):
        if data['type'] in ['deposit', 'transfer']:
            account = self.account_repo.find_by_id(data['to_account_id'])
            if not account:
                raise InvalidAccountError("Destination account not found")
            if data['type'] == 'deposit' and account.user_id != user_id:
                raise InvalidAccountError("Cannot deposit to another user's account")
            # if account.status != 'active':
            #     raise BusinessRuleViolation("Destination account is not active")
            # if account.currency != from_account.currency:  # Add currency check
            #     raise BusinessRuleViolation("Currency mismatch")
            
            return account
        return None   
                                   

    def _fail_transaction(self, transaction: Optional[Transaction], reason: str) -> Transaction:
        if transaction:
            transaction.status = f'failed: {reason}'
            self.transaction_repo.update(transaction)
        raise TransactionFailedError(reason)
    
    
    def verify_transaction(self, user_id: str, txn_id: str, token: str) -> Transaction:
        txn = self.get_transaction_details(user_id, txn_id)
        if not txn.validate_token(token):
            raise InvalidTokenError("Invalid verification token")
        if datetime.now() > txn.token_expiry:
            raise InvalidTokenError("Verification token expired")
        return self.transaction_repo.update_status(txn.id, 'completed')
    
    
    def get_transaction_details(self, user_id: str, transaction_id: str) -> Transaction:
        """Get detailed transaction with ownership validation"""
        transaction = self.transaction_repo.find_by_id(transaction_id)
        if not transaction:
            raise NotFoundError("Transaction not found")
        
        # Verify user owns either source or destination account
        from_owner = self.account_repo.is_owner(transaction.from_account_id, user_id)
        to_owner = self.account_repo.is_owner(transaction.to_account_id, user_id)
        
        if not from_owner and not to_owner:
            raise ForbiddenError("Transaction access denied")
            
        return transaction
    
    
    
    
    
    def get_user_transactions(self, user_id, filters=None):
        """Get transactions with filters"""
        #date range support
        if filters and 'start_date' in filters:
            return self.transaction_repo.find_by_date_range(
                user_id, 
                filters['start_date'], 
                filters['end_date']
            ) 
        account_ids = [a.id for a in self.account_repo.find_by_user(user_id)]
        return self.transaction_repo.find_by_accounts(account_ids, filters)


    def is_transaction_owner(self, user_id, txn_id):
        """Check if user owns related accounts"""
        txn = self.transaction_repo.find_by_id(txn_id)
        from_owner = self.account_repo.is_owner(txn.from_account_id, user_id)
        to_owner = self.account_repo.is_owner(txn.to_account_id, user_id)
        return from_owner or to_owner
    
    
 
    
    
    
    
    
    
   
