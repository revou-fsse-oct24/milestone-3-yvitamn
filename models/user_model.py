from datetime import datetime, timedelta
import secrets
from uuid import uuid4
import uuid
import bcrypt
import logging
from shared.exceptions import *

logging.setLevel(logging.DEBUG)
#=============Models=========================    
class User:
    def __init__(
        self,
        username: str, 
        email: str, 
        pin: str, 
        first_name: str, 
        last_name: str, 
        role: str = 'user'
    ):
        
        self.id = str(uuid.uuid4()) #Primary Key
        self.username = username.lower().strip()
        self.email = email.lower().strip()
        self.first_name = first_name
        self.last_name = last_name
        self.role = role
        self.created_at = datetime.now().isoformat() + 'Z'
        self.updated_at = datetime.now()
        self.token_hash = None 
        self.token_expiry = None
        logging.debug(f"Setting PIN for user {self.username}")
        self.pin = pin
        
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()   
    
    #pin related====================
    @property
    def pin(self):
        raise AttributeError("PIN access denied - use verify_pin() instead")
    
    @pin.setter
    def pin(self, value: str):
        """Automatically hash PIN when set"""
        logging.debug(f"Hashing PIN for {self.username}")
        from shared.security import SecurityUtils
        logging.debug(f"Hashing PIN: {value}")
        valid, msg = SecurityUtils.validate_pin_complexity(value)
        if not valid:
            logging.debug(f"Invalid PIN complexity: {msg}")
            raise SecurityValidationError(msg)
        self.pin_hash = SecurityUtils.hash_pin(value)  # Requires hash_pin()
       
    def verify_pin(self, plain_pin: str) -> bool:
        from shared.security import SecurityUtils
        return SecurityUtils.verify_pin(plain_pin, self.pin_hash)
    
    # token related==========================
    def refresh_token(self):
        """Generates new auth token""" 
        from shared.security import SecurityUtils
         # Invalidate previous token first
        if self.token_hash:
            SecurityUtils.invalidate_token(self.token_hash)
        
        # Generate both raw and hashed tokens
        raw_token, hashed_token, expiry = SecurityUtils.generate_auth_token()
        
        # Store ONLY the hash
        self.token_hash = hashed_token
        self.token_expiry = expiry
        
        return raw_token
    
    
    def logout(self):
        self.token_hash = None
        self.token_expiry = None
        
    
    def to_api_response(self) -> dict:
        """Safe serialization (excludes sensitive fields)"""
        return {
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat(),
        }    

