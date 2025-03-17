from repos.transaction_repo import UserRepository
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
        
    def register_user(self, user_data):
        #Validate input
        errors = self.schema.validate(user_data)
        if errors:
            raise ValidationError(errors)
        
        #Business logic validation
        #check username 
        if self.user_repo.find_by_username(user_data['username']):
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
        return self.user_repo.create(user)
    
    
    def get_user_by_id(self, user_id):
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        return user

    def get_all_users(self):
        return self.user_repoo.find_all()

    def update_user(self, user_id, update_data):
        user = self.get_user_by_id(user_id)
        
        # Example update logic
        if 'email' in update_data:
            if self.user_repo.email_exists(update_data['email'], exclude_user=user):
                raise BusinessRuleViolation("Email already registered")
            user.email = update_data['email']
        
        # Add other fields as needed
        user.updated_at = datetime.now()
        return self.user_repo.update(user)

    def delete_user(self, user_id):
        user = self.get_user_by_id(user_id)
        
        # Delete related accounts
        accounts = self.user_repo.find_by_user(user_id)
        for account in accounts:
            self.user_repo.delete(account.id)
            
        self.repo.delete(user_id)