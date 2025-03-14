from db.dummy_db import dummy_db
from repos.repo import UserRepository, AccountRepository, TransactionRepository       
import uuid
from models.model import User, Account, Transaction
        
        
#=============Services==================================
class UserService:
    @staticmethod
    def register_user(user_data):
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password'],
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', '')
        )
        return UserRepository.create_user(user)
    
class AuthService:
    @staticmethod
    def login(username, pin):
        for user in dummy_db['users'].values():
            if user.username == username and user.pin == pin:
                user.token = str(uuid.uuid4())
                return user
            return None

class AccountService:
    @staticmethod
    def create_account(user_id, account_type):
        account = Account(user_id, account_type)
        return AccountRepository.create_account(account)
    
class TransactionService:
    @staticmethod
    def create_transaction(user, transaction_data):
        #Validation transaction type
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