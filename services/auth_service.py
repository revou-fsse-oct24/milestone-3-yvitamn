from repos.user_repo import UserRepository 
import secrets
import uuid
from models.user_model import User
from schemas.auth_schema import LoginSchema
from schemas.user_schema import *
from shared.error_handlers import *
from shared.security import SecurityUtils


#=================================Auth Service====================   
class AuthService:
    #make limit for pin attemps
    # MAX_PIN_RETRIES = 3

    def __init__(self):
        self.user_repo = UserRepository()
        self.schema = LoginSchema()
        
    def login(self, credentials: dict):
        """Secure login with PIN validation and token generation"""
        #validate input
        validated = self.schema.load(credentials)
        user = self.user_repo.find_by_username(validated['username'].lower())
        # print(f"Attempting login for: {username}")
       
        if not user or not SecurityUtils.verify_pin(validated['pin'], user.pin_hash):
            raise InvalidCredentialsError("Invalid username or PIN")
        
        token, expiry = SecurityUtils.generate_auth_token()
        user.token = SecurityUtils.hash_token(token)
        user.token_expiry = expiry
        self.user_repo.update(user)
        # print(f"Generated new token: {user.token}")
  
        return {
            "user": user,
            "token": token,
            "expiry": expiry
        }
    
    
    def logout(self, user):
        """Secure logout with cryptographic token invalidation"""
        user.token = None
        user.token_expiry = None
        self.user_repo.update(user)
        SecurityUtils.invalidate_token(user.token)
        # print(f"Token invalidated for user {user.id}")    
        
    def get_all_users(self):
        """Admin-only user listing"""
        return self.user_repo.find_all()



    

        
        
        
        
        