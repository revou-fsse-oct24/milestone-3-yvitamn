import os
from typing import Optional
from flask import current_app
from db.dummy_db import AtomicOperation
from repos import *
from models.user_model import User
from repos.account_repo import AccountRepository
from repos.transaction_repo import TransactionRepository
from repos.user_repo import UserRepository
from schemas.user_schema import *
from shared.auth_helpers import *
from shared.error_handlers import *
from datetime import datetime
from shared.security import *
# from sqlalchemy.exc import SQLAlchemyError

# load_dotenv('.env')  # Load secrets
# load_dotenv('.flaskenv')  # Load Flask settings
# if os.getenv('FLASK_ENV') == 'testing':
#     load_dotenv('.env.test')
        
#=============User Service==================================
class UserService:
    def __init__(self, current_user: Optional[User] = None):
        self.user_repo = UserRepository()
        self.schema = UserSchema()
        self.current_user = current_user 
   
   
    def set_current_user(self):
        """Sets the current user using get_current_user()"""
        self.current_user = get_current_user()
        
        
    def register_user(self, user_data: dict) -> User:
        #Validate input format
        errors = self.schema.validate(user_data)
        if errors:
            raise ValidationError("Invalid user data", details=errors)
        
        #normalize inputs
        username = user_data['username'].lower().strip()
        email = user_data['email'].lower().strip()
        pin = str(user_data['pin'])
        
        #Business logic validation (require database access)
        # Validate PIN complexity
        is_valid, message = SecurityUtils.validate_pin_complexity(pin)
        if not is_valid:
            raise ValueError(message)
      
        #check existence
        if self.user_repo.email_exists(email):
            raise BusinessRuleViolation("Email already registered")
        if self.user_repo.find_by_username(username):
            raise BusinessRuleViolation("Username already exists")
        
        #Create user entity
        user = User(
            username=username,
            email=email,
            #model auto hash this pin
            pin=pin, #hashed pin 
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', '')
        )  
        #generate auth token
        user.refresh_token()
        #Create user
        return self.user_repo.create(user)
    
    
    
    # def create_initial_admin(self):
    #     """Create admin user with env variables"""
    #     # List of environment variables required for admin creation
    #     required_vars = ['ADMIN_USERNAME', 'ADMIN_EMAIL', 'ADMIN_INITIAL_PIN']

    #     # Check which required variables are missing from the environment
    #     missing = [var for var in required_vars if not os.getenv(var)]
    #     # ^ Security Impact: Ensures no silent failures for missing credentials

    #     # If any variables are missing...
    #     if missing:
    #         # Create error message listing missing variables
    #         msg = f"Missing admin env vars: {', '.join(missing)}"
    #         # ^ Audit Value: Helps track configuration issues
            
    #         # Production Environment: Fail hard and fast
    #         if os.getenv('FLASK_ENV') == 'production':
    #             raise RuntimeError(msg)
    #             # ^ Security Critical: Prevents deployment with incomplete security config
            
    #         # Development/Staging: Warn but continue
    #         else:
    #             current_app.logger.warning(f"{msg} - Using development defaults")
    #             # ^ Security Note: Tradeoff between security and development convenience
    #             # Risk: Could lead to default credentials in non-prod environments
        
    #     admin_data = {
    #         'username': os.getenv('ADMIN_USERNAME', 'dev_admin'),
    #         'email': os.getenv('ADMIN_EMAIL', 'admin@localhost'),
    #         'pin': SecurityUtils.hash_pin(os.getenv('ADMIN_INITIAL_PIN', '00000000')),
    #         'first_name': 'System',
    #         'last_name': 'Administrator',
    #         'role': 'admin'
    #     }
        
    #     if not self.user_repo.find_by_email(admin_data['email']):
    #         try:
    #             admin = User(**admin_data)
    #             admin.refresh_token()
    #             self.user_repo.create(admin)
    #         except Exception as e:
    #             current_app.logger.error(f"Admin creation failed: {str(e)}")
    #     else:
    #         current_app.logger.info("Admin already exists")
  
    
    def authenticate_user(self, identifier: str, plain_pin: str) -> User:
        """Authenticate by username/email with PIN"""
        user = (self.user_repo.find_by_email(identifier) 
                or self.user_repo.find_by_username(identifier))
        
        # Check account lock
        # if user.account_locked_until and user.account_locked_until > datetime.now():
        # raise AccountLockedError()
        
        if not user or not user.verify_pin(plain_pin):
            # user.failed_login_attempts += 1
            # if user.failed_login_attempts >= 3:
            #     user.account_locked_until = datetime.now() + timedelta(minutes=15)
            # self.user_repo.update(user)
            raise InvalidCredentialsError("Invalid credentials")
        
        # Session expiry check    
        if user.token_expiry and user.token_expiry < datetime.now():
            raise InvalidTokenError("Session expired")
        
        self.refresh_token()  
        
        self.user_repo.update(user)    
        return user
   
        
    #get user by id
    def get_current_user_profile(self, user_id: str) -> dict:
        if user_id != self.current_user.id:
            raise ForbiddenError("Access to other user profiles denied")
       
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'created_at': user.created_at.isoformat()
        }        


    def update_self(self, update_data: dict) -> User:
        """Update current user's profile"""
        current_user = get_current_user()  
        return self._update_user(current_user, update_data)


    def _update_user(self, user: User, update_data: dict) -> User:
        """Shared update logic"""  
        if 'role' in update_data:
            if user.role == 'superadmin':
                raise ForbiddenError("Cannot modify superadmin roles")
            if self.current_user.role != 'superadmin':
                raise ForbiddenError("Requires superadmin privileges")
        
        # Email update handling
        if 'email' in update_data:
            new_email = update_data['email'].lower().strip()
            if new_email != user.email:
                if self.user_repo.email_exists(new_email):
                    raise BusinessRuleViolation("Email already registered")
                user.email = new_email

        # Name updates(OUTSIDE email check)
        if 'first_name' in update_data:
            user.first_name = update_data['first_name'].strip()
        if 'last_name' in update_data:
            user.last_name = update_data['last_name'].strip()
                            
            user.role = update_data['role']

        user.updated_at = datetime.now()
        return self.user_repo.update(user)


    # def update_other_user(self, target_user_id: str, update_data: dict) -> User:
    #     """Admin-only user updates"""
    #     admin = get_current_user()
    #     if admin.role != 'admin':
    #         raise ForbiddenError("Admin privileges required")
            
    #     target_user = self.user_repo.find_by_id(target_user_id)
    #     return self._update_user(target_user, update_data)


    # def change_pin(self, old_pin: str, new_pin: str) -> User:
    #     user = get_current_user()
    #     # logger.info(f"PIN change initiated for user {user.id}")
        
    #     # Verify current PIN    
    #     if not SecurityUtils.verify_pin(old_pin, user.pin_hash):
    #         raise InvalidCredentialsError("Invalid current PIN")
        
    #     try:
    #         # Validate and hash new PIN
    #         user.pin = new_pin # Uses property setter, calls SecurityUtils.hash_pin internally
            
    #     except SecurityValidationError as e:
    #         raise ValidationError(str(e))
    #     except ValueError as e:
    #         raise ValidationError(str(e))

    #     user.updated_at = datetime.now()  
    #     # Security log
    #     # print(f"User {user.id} changed PIN at {datetime.now()}")
    #     self.user_repo.update(user)
    #      # Secure logging
    #     current_app.logger.info(
    #         f"PIN changed for user {user.id}",
    #         extra={
    #             'category': 'SECURITY',
    #             'user_id': user.id,
    #             'action': 'PIN_CHANGE'
    #             }
    #     )
    #     return user
    
    

    # def delete_user(self, user_id: str):
    #     """Atomic user deletion"""
    #     # try:
    #     with AtomicOperation(self.user_repo.db):  # Database transaction
    #             user = self.user_repo.find_by_id(user_id)
    #             if not user:
    #                 raise NotFoundError("User not found")
        
    #             # Delete related accounts
    #             account_repo = AccountRepository()
    #             transaction_repo = TransactionRepository()
                
    #             for acc in account_repo.find_by_user(user_id):
    #                 #transaction cleanup:
    #                 for txn in transaction_repo.find_by_account(acc.id):
    #                     transaction_repo.delete(txn.id)
    #                 # Then delete account
    #                 account_repo.delete(acc.id)
    #             # Delete user   
    #             self.user_repo.delete(user_id)
                
    #             current_app.logger.info(f"User {user_id} deleted successfully")
            # AuditLog.create(
            #     user_id=user_id,
            #     action="USER_DELETION",
            #     performer_id=self.current_user.id
            # )
        # except SQLAlchemyError as e:
        #     current_app.logger.error(f"User deletion failed: {str(e)}")
        #     raise TransactionFailedError("User deletion transaction failed")