from db.dummy_db import dummy_db
from repos.repo import UserRepository, AccountRepository, TransactionRepository       
import uuid
from models.model import User, Account, Transaction
from shared.schemas import *
from shared.error_handlers import *

        
#=============User Service==================================
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
    
    def get_user_by_id(self, user_id):
        user = self.repo.find_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        return user

    def get_all_users(self):
        return self.repo.find_all()

    def update_user(self, user_id, update_data):
        user = self.get_user_by_id(user_id)
        
        # Example update logic
        if 'email' in update_data:
            if self.repo.email_exists(update_data['email'], exclude_user=user):
                raise BusinessRuleViolation("Email already registered")
            user.email = update_data['email']
        
        # Add other fields as needed
        user.updated_at = datetime.now()
        return self.repo.update(user)

    def delete_user(self, user_id):
        user = self.get_user_by_id(user_id)
        
        # Delete related accounts
        accounts = self.account_repo.find_by_user(user_id)
        for account in accounts:
            self.account_repo.delete(account.id)
            
        self.repo.delete(user_id)

#=================================Auth Service====================   
class AuthService:
    #make limit for pin attemps
    # MAX_PIN_RETRIES = 3

    def __init__(self):
        self.repo = UserRepository()
        
    def login(self, username, pin):
        user = self.repo.find_by_username(username)       
        if not user or user.pin != pin:
            raise AuthenticationError("Invalid credentials")
          
        # if user and user.pin == pin: 
        # Generate and store new token 
        user.token = str(uuid.uuid4()) #Generate UUID token
        self.repo.update(user)
        return user
             
        
    # def _validate_pin(self, user, pin_attempt):
    #     if user.pin_retries >= self.MAX_PIN_RETRIES:
    #         raise RetryExceededError("Account locked")
            
    #     if user.pin != pin_attempt:
    #         user.pin_retries += 1
    #         self.repo.update(user)
    #         return False
            
    #     user.pin_retries = 0
    #     self.repo.update(user)
    #     return True


#=================================Account Service====================
class AccountService:
    def __init__(self):
        self.repo = AccountRepository()
        self.repo = UserRepository()
        
    def create_account(self, user_id, account_type):
        # Validate user exists
        if not self.repo.find_by_id(user_id):
            raise NotFoundError("User not found")
    
        # Validate account type
        valid_account_types = ['checking', 'savings', 'credit']  # Example types
        if account_type not in valid_account_types:
            raise BusinessRuleViolation(
                description=f"Invalid account type: {account_type}. Valid types are: {', '.join(valid_account_types)}",
                code=400
            )
        
    # Create account with consecutive account_number
        account = Account(
            user_id=user_id, # UUID from authenticated user
            account_type=account_type,
        )
        return self.repo.create(account)
    
    def get_user_accounts(self, user_id):
        return self.repo.find_by_user(user_id)
    
    def get_account_by_id(self, user_id, account_id):
        # Verify account exists and belongs to user
        account = self.repo.find_by_id(account_id)
        if not account:
            raise NotFoundError("Account not found")
        if account.user_id != user_id:
            raise InvalidAccountError("Account doesn't belong to user")
    
    
#=================================Transaction Service====================    
class TransactionService:
    def __init__(self):
        self.repo = TransactionRepository()
        self.repo = AccountRepository()
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
            
            self.repo.create(transaction)
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
            account = self.repo.find_by_id(data['from_account_id'])
            if not account or account.user_id != user.id:
                raise InvalidAccountError("Invalid source account")
            return account
        return None    
        
    def _validate_destination_account(self, user, data):
        if data['type'] in ['deposit', 'transfer']:
            account = self.repo.find_by_id(data['to_account_id'])
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
                self.repo.update(from_account)
            elif transaction_type == 'transfer':
                from_account.balance -= amount
                to_account.balance += amount
                self.repo.update(from_account)
                self.repo.update(to_account)
                          
        except Exception as e:
            raise TransactionFailedError(f"Balance update failed: {str(e)}")     
        
        
        
        
        
        