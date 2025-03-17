from repos.user_repo import UserRepository   
import uuid
from models.model import Account
from shared.schemas import *
from shared.error_handlers import *



#=================================Auth Service====================   
class AuthService:
    #make limit for pin attemps
    # MAX_PIN_RETRIES = 3

    def __init__(self):
        self.user_repo = UserRepository()
        
    def login(self, username, pin):
        user = self.user_repo.find_by_username(username)       
        if not user or user.pin != pin:
            raise AuthenticationError("Invalid credentials")
          
        # if user and user.pin == pin: 
        # Generate and store new token 
        user.token = str(uuid.uuid4()) #Generate UUID token
        self.user_repo.update(user)
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



    

        
        
        
        
        