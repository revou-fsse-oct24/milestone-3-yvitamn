from repos.transaction_repo import TransactionRepository   
from repos.account_repo import AccountRepository    
import uuid
from models.user_model import Transaction
from schemas.transaction_schema import TransactionSchema
from schemas.user_schema import *
from shared.error_handlers import *


    
#=================================Transaction Service====================    
class TransactionService:
    def __init__(self):
        self.transaction_repo = TransactionRepository()
        self.account_repo = AccountRepository()
        self.schema = TransactionSchema()
        
    def create_transaction(self, user_id: str, data: dict) -> Transaction:
        try:
            # Validate and deserialize input
            validated_data = self.schema.load(data)
            transaction_type = validated_data['type']
            amount = Decimal(validated_data['amount']).quantize(Decimal('0.01'))
        
            #Get related accounts & validate
            from_account = self._validate_source_account(self._validate_source_account(user_id, validated_data))
            to_account = self._validate_destination_account(self._validate_destination_account(user_id, validated_data))
                 
            #Create transaction record first
            transaction = Transaction(
                transaction_type = transaction_type,
                amount=float(amount),
                from_account_id=from_account.id if from_account else None,
                to_account_id=to_account.id if to_account else None,
                description=validated_data.get('description', '')
            )
            
            #Process transaction
            self._update_balances(transaction_type, from_account, to_account, amount)
            
            # Update transaction status
            transaction.status = 'completed'
            return self.transaction_repo.create(transaction)
            
        except ValidationError as e:
            raise BusinessRuleViolation(f"Validation error: {e.messages}")
        except Exception as e:
            # Create failed transaction
            transaction.status = 'failed'
            self.transaction_repo.create(transaction)
            raise TransactionFailedError(f"Transaction failed: {str(e)}")      
        
    def _validate_source_account(self, user_id: str, data: dict):
        if data['type'] in ['withdrawal', 'transfer']:
            account = self.account_repo.find_by_id(data['from_account_id'])
            if not account or account.user_id != user_id:
                raise InvalidAccountError("Invalid source account")
            if account.balance < Decimal(data['amount']):
                raise InsufficientBalanceError(account.id, account.balance)
            return account
        return None    
        
    def _validate_destination_account(self, user_id: str, data: dict):
        if data['type'] in ['deposit', 'transfer']:
            account = self.account_repo.find_by_id(data['to_account_id'])
            if not account:
                raise InvalidAccountError("Destination account not found")
            if data['type'] == 'deposit' and account.user_id != user_id:
                raise InvalidAccountError("Cannot deposit to another user's account")
            return account
        return None   
        
    def _update_balances(self, transaction_type: str, from_account, to_account, amount: Decimal):
        try:
            with self.account_repo.atomic_update():
                if transaction_type == 'deposit':
                    to_account.balance += amount
                    self.account_repo.update(to_account)
                elif transaction_type == 'withdrawal':
                    from_account.balance -= amount
                    self.account_repo.update(from_account)
                elif transaction_type == 'transfer':
                    from_account.balance -= amount
                    to_account.balance += amount
                    self.account_repo.update(from_account)
                    self.account_repo.update(to_account)
                          
        except Exception as e:
            raise TransactionFailedError(f"Balance update failed: {str(e)}")     
        