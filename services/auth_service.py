from repos.user_repo import UserRepository 
 
import uuid
from models.model import User
from shared.schemas import *
from shared.error_handlers import *



#=================================Auth Service====================   
class AuthService:
    #make limit for pin attemps
    # MAX_PIN_RETRIES = 3

    def __init__(self):
        self.user_repo = UserRepository()
        self.schemas = LoginSchema()
        
    def login(self, data: dict) -> User:
        #validate input
        errors = self.schemas.validate(data)
        if errors:
            raise ValidationError("Invalid login data", errors)
        
        # Sanitize and normalize inputs
        username = data['username'].strip().lower()
        pin = str(data['pin']).strip()

        # Debug logging
        print(f"Attempting login for: {username}")
        
        user = self.user_repo.find_by_username(username)
        if not user:
            print(f"User {username} not found")
            raise AuthenticationError("Invalid credentials")
        
        # PIN verification with debugging
        print(f"Verifying PIN for user {user.id}")
        print(f"Stored hash: {user.pin_hash}")
        if not user.verify_pin(pin):
            print(f"PIN mismatch for user {user.id}")
            raise AuthenticationError("Invalid credentials")
        
        # Generate and store new token 
        user.token = str(uuid.uuid4()) #Generate UUID token
        self.user_repo.update(user)
        print(f"Generated new token: {user.token}")
        
        return user
             
        
    # def _validate_pin(self, user, pin_attempt):
    #     if user.pin_retries >= self.MAX_PIN_RETRIES:
    #         raise RetryExceededError("Account locked")
            
    #     if user.pin != pin_attempt:
    #         user.pin_retries += 1
    #         self.repo.update(user)
    #         return False
            
    #     user.pin_retries = 0
    #     self.repo.update(user)
    #     return True



    

        
        
        
        
        