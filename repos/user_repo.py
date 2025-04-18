from dataclasses import fields
from typing import Optional
from models.user_model import User
from db.base_repo import DummyBaseRepository
from db.dummy_db import dummy_db_instance
from .account_repo import AccountRepository
from shared.error_handlers import *
from datetime import datetime

class UserRepository(DummyBaseRepository[User]):
    def __init__(self):
        
        super().__init__(
            model=User,
            collection_name='users',
            # unique_fields=['email', 'username', 'token_hash']
        )
                      
                      
    def create(self, entity_data: dict) -> User:
        # Call the parent class's create method to store the user
        created_user_data = super().create(entity_data)

        # Return a new User object initialized with only the fields expected by the User model
        # Sensitive fields like pin_hash and token_hash are not exposed here
        new_user = User(
            username=created_user_data["username"],
            email=created_user_data["email"],
            pin="dummy_pin",  # Use a placeholder since the actual PIN is hashed
            first_name=created_user_data["first_name"],
            last_name=created_user_data["last_name"],
            role=created_user_data.role.get('role', "user") # Default to "user" if not provided
        )
            
        return new_user
        
        
    
    def update(self, user: User) -> User:
        """Update user with index management"""
        return super().update(user)


    #search
    #Function to get user IDs associated with a given email
    # def _get_user_ids_by_email(self, email: str) -> set[str]:
    #     """Get user IDs associated with a given email"""
    #     normalized_email = email.strip().lower()
    #     return self.db._indexes['users']['email'].get(normalized_email, set())
    
    #find user by username
    def find_by_username(self, username: str) -> Optional[User]:  
        """Find user by username"""
        users = self.find_by_field('username', username)
        return users[0] if users else None


    def find_by_token(self, token_hash: str) -> Optional[User]:
        """Find user by hashed token"""
        users = self.find_by_field('token_hash', token_hash)
        return users[0] if users else None

    
    #find user by email
    def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email"""
        users = self.db.find_by_field('email', email)
        return users[0] if users else None


    #find all registered users
    def find_all(self) -> list[User]:
       """Get all users in the database"""
       return super().find_all()
    
    
    def email_exists(self, email: str, exclude_user: User = None)-> bool:
        """Check if email exists in the database, excluding a specific user"""
        users = self.find_by_field('email', email)
        
        if not users:
            return False  # Email doesn't exist
            # Check if any ID in the set is NOT the excluded user's ID
        return any(user.id != getattr(exclude_user, 'id', None) for user in users)
        
        
    def get_users_with_balance(self, min_balance: float) -> list[User]:
        """Get users with total balance above a certain threshold"""
        account_repoo = AccountRepository()
        return[
            user for user in self.find_all()
            if sum(
                acc.balance for acc in account_repoo.find_by_user(user.id)
            ) >= min_balance
        ]
            

    def delete(self, user_id: str) -> bool:
        """Delete user and associated accounts"""
        return super().delete(user_id)