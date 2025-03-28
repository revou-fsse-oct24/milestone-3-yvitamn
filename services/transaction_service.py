from repos.transaction_repo import TransactionRepository   
from repos.account_repo import AccountRepository    
import uuid
from models.user_model import Transaction
from schemas.user_schema import *
from shared.error_handlers import *


    
#=================================Transaction Service====================    
class TransactionService:
    def __init__(self):
        self.transaction_repo = TransactionRepository()
        self.account_repo = AccountRepository()
        self.schema = TransactionSchema()
        
    def create_transaction(self, user, transaction_data):
        #Validate input using schema
        errors = self.schema.validate(transaction_data)
        if errors:
            raise ValidationError(errors)
        
        transaction_type = transaction_data['type']
        amount = float(transaction_data['amount'])
        
        # Generate UUID for transaction
        # transaction_id = str(uuid.uuid4())
        
        #Get related accounts & validate
        from_account = self._validate_source_account(user, transaction_data)
        to_account = self._validate_destination_account(user, transaction_data)
        
        # Check balance
        if from_account.balance < transaction_data['amount']:
            raise InsufficientBalanceException("Insufficient funds")
        
        # Process transaction
        try:
            self._update_balances(
                    transaction_type,
                    from_account,
                    to_account,
                    amount
                )
            
            #Create transaction record
            transaction = Transaction(
                # id=transaction_id,
                transaction_type = transaction_type,
                amount=amount,
                from_account_id=from_account.id,
                to_account_id=to_account.id if to_account else None,
                description=transaction_data.get('description', '')
            )
            transaction.status = 'completed'
            
            self.transaction_repo.create(transaction)
            return transaction
    
        except Exception as e:
             # Create failed transaction record
                transaction = Transaction(
                    # id=transaction_id,
                    transaction_type = transaction_type,
                    amount=amount,
                    status='failed',
                    description=str(e)
                )
                self.repo.create(transaction)
                raise TransactionFailedError(str(e))       
        
    def _validate_source_account(self, user, data):
        if data['type'] in ['withdrawal', 'transfer']:
            account = self.transaction_repo.find_by_id(data['from_account_id'])
            if not account or account.user_id != user.id:
                raise InvalidAccountError("Invalid source account")
            return account
        return None    
        
    def _validate_destination_account(self, user, data):
        if data['type'] in ['deposit', 'transfer']:
            account = self.transaction_repo.find_by_id(data['to_account_id'])
            if not account:
                raise InvalidAccountError("Destination account not found")
            if data['type'] == 'deposit' and account.user_id != user.id:
                raise InvalidAccountError("Cannot deposit to another user's account")
            return account
        return None   
        
    def _update_balances(self, transaction_type, from_account, to_account, amount):
        try:
            if transaction_type == 'deposit':
                to_account.balance += amount
                self.repo.update(to_account)
            elif transaction_type == 'withdrawal':
                from_account.balance -= amount
                self.transaction_repo.update(from_account)
            elif transaction_type == 'transfer':
                from_account.balance -= amount
                to_account.balance += amount
                self.transaction_repo.update(from_account)
                self.transaction_repo.update(to_account)
                          
        except Exception as e:
            raise TransactionFailedError(f"Balance update failed: {str(e)}")     
        