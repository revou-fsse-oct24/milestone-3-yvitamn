from db.dummy_db import dummy_db
from repos.repo import UserRepository, AccountRepository, TransactionRepository       
import uuid
from models.model import User, Account, Transaction
from shared.schemas import *
from shared.error_handlers import *
from shared.exceptions import *
        
#=============Services==================================
class UserService:
    def __init__(self):
        self.repo = UserRepository()
        self.schema = UserSchema()
        
    def register_user(self, user_data):
        #Validate input
        errors = self.schema.validate(user_data)
        if errors:
            raise ValidationError(errors)
        
        #Business logic validation
        #check username 
        if self.repo.find_by_username(user_data['username']):
            raise BusinessRuleViolation("Username already exists")
        
        #Create user entity
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            pin=user_data['pin'], #hash pin later in real implementation
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', '')
        )  
        #Create user
        return self.repo.create(user)
    
class AuthService:
    #make limit for pin attemps
    MAX_PIN_RETRIES = 3

    def __init__(self):
        self.repo = UserRepository()
        
    def login(self, username, pin):
        user = self.repo.find_by_username(username)   
        
        if not user or not self.validate_pin(user, pin):
            raise InvalidPinError("Invalid credentials")
            
        user.token = str(uuid.uuid4())
        return user
        
        
    def validate_pin(self, user, pin_attempt):
        if user.pin_retries >= self.MAX_PIN_RETRIES:
            raise RetryExceededError("Account locked")
            
        if user.pin != pin_attempt:
            user.pin_retries += 1
            self.repo.update(user)
            return False
            
        user.pin_retries = 0
        self.repo.update(user)
        return True

class AccountService:
    @staticmethod
    def create_account(user_id, account_type):
        account = Account(user_id, account_type)
        return AccountRepository.create_account(account)
    
class TransactionService:
    def __init__(self):
        self.repo = TransactionRepository()
        self.repo = AccountRepository()
        self.schema = TransactionSchema()
        
    def create_transaction(self, user, transaction_data):
        #Validate input
        errors = self.schema.validate(transaction_data)
        if errors:
            raise ValidationError(errors)
        
        transaction_type = 
        
        
        
        
        
        
        
        
        
        
        
        
        transaction_type = transaction_data.get('type')
        if transaction_type not in ['deposit', 'withdrawal', 'transfer']:
            return None, "Invalid transaction type"
   
        amount = float(transaction_data.get('amount',0))
        from_account_id = transaction_data.get('from_account_id')
        to_account_id = transaction_data.get('to_account_id')
        
        #Get relevant accounts
        from_account = dummy_db['accounts'].get(from_account_id)
        to_account = dummy_db['accounts'].get(to_account_id)
        
        #Transaction validation
        if transaction_type == 'withdrawal' or transaction_type == 'transfer':
            if not from_account or from_account.user_id != user.id:
                return None, "Invalid source account"
            if from_account.balance < amount:
                return None, "Insufficient funds"
            
        if transaction_type == 'deposit':
            if not to_account or to_account.user_id != user.id:
                return None, "Invalid destination account"
            
        #Execute transaction
        try:
            if transaction_type == 'deposit':
                to_account.balance += amount
            elif transaction_type == 'withdrawal':
                to_account.balance -=amount
            elif transaction_type == 'transfer':
                from_account.balance -= amount
                to_account.balance += amount
                
            transaction = Transaction(
                transaction_type=transaction_type,
                amount=amount,
                from_account_id=from_account_id,
                to_account_id=to_account_id,
                description=transaction_data.get('description', '')
            )
            transaction.status = "completed"
            
            dummy_db['transactions'][transaction.id] = transaction
            return transaction, None
        
        except Exception as e:
            return None, str(e)