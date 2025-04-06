
from repos import user_repo
from repos.user_repo import UserRepository 
from schemas.auth_schema import LoginSchema
from schemas.user_schema import *
from shared.error_handlers import *
from shared.security import SecurityUtils
from shared.exceptions import *
from db.dummy_db import dummy_db_instance  


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
        
        # Use centralized refresh
        raw_token = self.refresh_token(user.id)
        
        return {
            "user": user.to_api_response(),
            "token": raw_token,
            "expiry": user.token_expiry
        }
    
    
    def logout(self, user):
        """Secure logout with cryptographic token invalidation"""
        with dummy_db_instance.get_collection_lock('users'):   
            user.token_hash = None
            user.token_expiry = None
            self.user_repo.update(user)
              
        
    def get_all_users(self):
        """Admin-only user listing"""
        return self.user_repo.find_all()
    
    
    #==================================================
    def refresh_token(user_id: str) -> str:
        """Centralized token refresh usable anywhere"""
        
        user = user_repo.find_by_id(user_id)
            
        if not user:
            raise NotFoundError(f"User {user_id} does not exist")
                
        raw_token, hashed_token, expiry = SecurityUtils.generate_auth_token()
            
        with dummy_db_instance.get_collection_lock('users'):    
            # Automatically invalidates old token by replacement
            user.token_hash = hashed_token
            user.token_expiry = expiry
            user_repo.update(user)  # Auto-handles indexes
            
            return raw_token



    

        
        
        
        
        