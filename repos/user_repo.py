
from typing import Optional
from models.model import User
from .base_repo import DummyBaseRepository
from .account_repo import AccountRepository
from shared.error_handlers import *
from datetime import datetime

class UserRepository(DummyBaseRepository):
    def __init__(self):
        super().__init__(model=User, collection_name='users')
      
    def find_by_token(self, token):
        return next(
            (u for u in self.collection.values() if u.token == token)
            , None)

    def find_by_username(self, username: str) -> Optional[User]:
        """Case-insensitive search with debug logging"""
        search_username = username.strip().lower()
        print(f"Searching for username: '{search_username}'")
        print(f"Existing users: {[u.username for u in self.collection.values()]}")
        
        return next(
            (u for u in self.collection.values()
             if u.username == search_username),
            None
        )

    def find_all(self):
        return list(self.collection.values())
    
    def email_exists(self, email, exclude_user=None):
        return any(
            user.email == email 
            for user in self.collection.values()
            if not exclude_user or user.id != exclude_user.id
        )
    
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

    def delete(self, user_id):
        if user_id not in self.collection:
            raise NotFoundError("User not found")
        del self.collection[user_id]