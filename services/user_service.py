import os
from repos.user_repo import UserRepository
import uuid
from models.user_model import User
from schemas.user_schema import *
from shared.error_handlers import *
from datetime import datetime

        
#=============User Service==================================
class UserService:
    def __init__(self):
        self.user_repo = UserRepository()
        self.schema = UserSchema()
   
        
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
            pin=pin, #hash pin later in real implementation
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', '')
        )  
        #generate auth token
        user.refresh_token()
        #Create user
        return self.user_repo.create(user)
  
    
    def create_initial_admin(self):
        """Create admin user with secure defaults"""
        admin_data = {
            'username': 'admin',
            'email': 'admin@revobank.dprk',
            'pin': '202503',  # Should be from env in production
            'first_name': 'System',
            'last_name': 'Administrator',
            'role': 'admin'
        }
        if not self.user_repo.find_by_username(admin_data['username']):
            admin = User(**admin_data)
            admin.refresh_token()
            self.repo.create(admin)
  
    
    def authenticate_user(self, identifier: str, pin: str) -> User:
        """Authenticate by username/email with PIN"""
        user = (self.repo.find_by_email(identifier) 
                or self.repo.find_by_username(identifier))
        
        if not user or not user.verify_pin(pin):
            raise InvalidCredentialsError("Invalid credentials")
            
        if user.token_expiry < datetime.now():
            raise InvalidTokenError("Session expired")
            
        return user
   
        
    #get user by id
    def get_current_user_profile(self, user_id: str) -> dict:
        user = self.repo.find_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
            
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'created_at': user.created_at.isoformat()
        }        


    def list_users(self, requester_id: str) -> list:
        """Admin-only user listing with security check"""
        requester = self.repo.find_by_id(requester_id)
        if not requester or requester.role != 'admin':
            raise ForbiddenError("Admin privileges required")
            
        return [u.to_dict() for u in self.repo.find_all()]


    def update_user(self, user_id: str, update_data: dict) -> User:
        user = self.repo.find_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        # Email update handling
        if 'email' in update_data:
            new_email = update_data['email'].lower().strip()
            if new_email != user.email:
                if self.repo.email_exists(new_email):
                    raise BusinessRuleViolation("Email already registered")
                user.email = new_email

        # Name updates
        if 'first_name' in update_data:
            user.first_name = update_data['first_name'].strip()
        if 'last_name' in update_data:
            user.last_name = update_data['last_name'].strip()

        user.updated_at = datetime.now()
        return self.repo.update(user)

    
    def change_pin(self, user_id: str, old_pin: str, new_pin: str) -> User:
        user = self.repo.find_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
            
        if not user.verify_pin(old_pin):
            raise InvalidCredentialsError("Invalid current PIN")
            
        self._validate_pin(new_pin)
        user.pin_hash = user._hash_pin(new_pin)
        user.updated_at = datetime.now()
        return self.repo.update(user)
    
    
    # def delete_user(self, user_id):
    #     user = self.get_user_by_id(user_id)
        
    #     # Delete related accounts
    #     accounts = self.user_repo.find_by_user(user_id)
    #     for account in accounts:
    #         self.user_repo.delete(account.id)
            
    #     self.user_repo.delete(user_id)