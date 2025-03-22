import os
from repos.user_repo import UserRepository
import uuid
from models.model import User
from shared.schemas import *
from shared.error_handlers import *
from datetime import datetime

        
#=============User Service==================================
class UserService:
    def __init__(self):
        self.user_repo = UserRepository()
        self.schema = UserSchema()
        
    def register_user(self, user_data: dict) -> User:
        #Validate input
        errors = self.schema.validate(user_data)
        if errors:
            raise ValidationError(errors)
        
        username = user_data['username'].strip().lower()
        
        #Business logic validation
        #check existence
        if self.user_repo.find_by_username(username):
            raise BusinessRuleViolation("Username already exists")
        
        #Create user entity
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            #model auto hash this pin
            pin=user_data['pin'], #hash pin later in real implementation
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', '')
        )  
        #Create user
        return self.user_repo.create(user)
    
    def create_initial_admin(self):
        """One-time admin setup (call during app initialization)"""
        admin_username = 'admin'
        if not self.user_repo.find_by_username(admin_username):
            admin = User(
                username=admin_username,
                email=os.getenv('ADMIN_EMAIL', 'admin@system.dprk'),
                pin=os.getenv('ADMIN_PIN', 'secure_admin_pin'),
                first_name='System',
                last_name='Administrator',
                role='admin'
            )
            self.user_repo.create(admin)
            print("People's Admin created successfully!")
    
    def authenticate_user(self, username, pin):
        """
        Authenticate user with username and PIN
        Returns user if authentication succeeds
        """
        user = self.user_repo.find_by_username(username)
        
        if not user:
            raise AuthenticationError("Invalid credentials")
            
        if not user.verify_pin(pin):
            raise AuthenticationError("Invalid credentials")         
        
        return user
    
    
    def get_user_by_id(self, user_id):
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        return user

    def get_all_users(self) -> list[User]:
        return self.user_repo.find_all()

    def update_user(self, user_id, update_data):
        user = self.get_user_by_id(user_id)
        
        if 'email' in update_data:
            if self.user_repo.email_exists(update_data['email'], exclude_user=user):
                raise BusinessRuleViolation("Email already registered")
            user.email = update_data['email']
        
        user.updated_at = datetime.now()
        return self.user_repo.update(user)
    
    def update_pin(self, user_id, old_pin, new_pin):
        user = self.get_user_by_id(user_id)
        
        if not user.verify_pin(old_pin):
            raise AuthenticationError("Invalid current PIN")
        
        user.pin_hash = user._hash_pin(new_pin)
        user.updated_at = datetime.now()
        return self.user_repo.update(user)
    
    
    def delete_user(self, user_id):
        user = self.get_user_by_id(user_id)
        
        # Delete related accounts
        accounts = self.user_repo.find_by_user(user_id)
        for account in accounts:
            self.user_repo.delete(account.id)
            
        self.user_repo.delete(user_id)