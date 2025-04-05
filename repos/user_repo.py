
from dataclasses import fields
from typing import Optional
from models.user_model import User
from db.base_repo import DummyBaseRepository
from .account_repo import AccountRepository
from shared.error_handlers import *
from datetime import datetime

class UserRepository(DummyBaseRepository):
    def __init__(self):
        super().__init__(User, 'users')
                      
                      
    def create(self, entity: User) -> User:
        #  with self.db.get_collection_lock('users'):
            # Check for existing username/email before creation
            if self.find_by_username(entity.username):
                raise ValueError(f"Username {entity.username} already exists")
            if self.find_by_email(entity.email):
                raise ValueError(f"Email {entity.email} already registered")

            # Call parent create (handles ID generation and storage)
            created_user = super().create(entity)

            # Update indexes
            # self._add_to_index('email', entity.email, entity.id)
            # self._add_to_index('username', entity.username, entity.id)
            return created_user           
    
    def update(self, entity: User) -> User:
        # Get existing user data before update
        existing_user = self.find_by_id(entity.id)
        if not existing_user:
            raise NotFoundError("User not found")
        
        old_entity = self.find_by_id(entity.id)
        if old_entity.token != entity.token:
            self.db.remove_from_index('users', 'token', old_entity.token, entity.id)
            self.db.add_to_index('users', 'token', entity.token, entity.id)

        # Check for email/username changes
        if existing_user.email != entity.email:
            if self.find_by_email(entity.email):
                raise ValueError("New email already registered")
            self._remove_from_index('email', existing_user.email, entity.id)
            self._add_to_index('email', entity.email, entity.id)

        if existing_user.username != entity.username:
            if self.find_by_username(entity.username):
                raise ValueError("New username already taken")
            self._remove_from_index('username', existing_user.username, entity.id)
            self._add_to_index('username', entity.username, entity.id)

        return super().update(entity)


    #search
    #Function to get user IDs associated with a given email
    def _get_user_ids_by_email(self, email: str) -> set[str]:
        normalized_email = email.strip().lower()
        return self.db._indexes['users']['email'].get(normalized_email, set())
    
    #find user by username
    def find_by_username(self, username: str) -> Optional[User]:
        search_username = username.strip().lower()
        user_ids = self.db._indexes['users']['username'].get(search_username, set())
        if user_ids:
            return self.find_by_id(next(iter(user_ids)))
        return None


    def find_by_token(self, token: str) -> Optional[User]:
        user_ids = self.db._indexes['users']['token'].get(token, set())
        return self.find_by_id(next(iter(user_ids))) if user_ids else None

    # def update_token(self, user: User) -> User:
    #     return self.update(user)
    
    #find user by email
    def find_by_email(self, email: str) -> Optional[User]:
        users = self.db.find_by('users', 'email', email)
        return users[0] if users else None


    #find all registered users
    def find_all(self) -> list[User]:
        # , fields: list[str] = None)
        """Get all users with specified fields"""  
        # default_fields = ["email", "username", "created_at"]
        # selected_fields = fields or default_fields  
        return [
            {
                "email": user.email,
                "username": user.username
                # field: getattr(user, field, None)
                # for field in selected_fields
                # if hasattr(user, field)
            }
            for user in self.collection.values()
        ]
    
    
    def email_exists(self, email: str, exclude_user: User = None)-> bool:
        normalized_email = email.strip().lower()
        user_ids = self.db._indexes['users']['email'].get(normalized_email, set())
        
        if not user_ids:
            return False  # Email doesn't exist
        
        if exclude_user:
            # Check if any ID in the set is NOT the excluded user's ID
            return any(uid != exclude_user.id for uid in user_ids)
        
        return True
    
    
    def get_users_with_balance(self, min_balance: float) -> list[User]:
        account_repoo = AccountRepository()
        users = []
        for user in self.collection.values():
            total = sum(
                acc.balance 
                for acc in account_repoo.find_by_user(user.id)
            )
            if total >= min_balance:
                users.append(user)
        return users

    def delete(self, user_id: str) -> bool:
        user = self.find_by_id(user_id)
        if not user:
            return False

        # Clean up indexes
        # self._remove_from_index('email', user.email, user_id)
        # self._remove_from_index('username', user.username, user_id)
        
        return super().delete(user_id)