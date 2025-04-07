import bcrypt
import secrets
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Tuple
from flask import current_app
import redis
from .exceptions import *
from models.user_model import User


# Configure Redis connection (You can modify the host, port as needed)
r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)


class SecurityUtils:
    @staticmethod
    def validate_pin_complexity(plain_pin: str) -> Tuple[bool, str]:
        """Enforce PIN complexity rules for banking applications"""
        if len(plain_pin) < 8:
            return False, "PIN must be exactly 8 digits"
        # if not plain_pin.isdigit():
        #     return False, "PIN must contain only numbers"
        # if len(set(plain_pin)) < 4:
        #     return False, "PIN must contain at least 4 unique digits"
        # if plain_pin in ['12345678', '00000000']:
        #     return False, "Common PINs are not allowed"
        return True, "PIN is valid"

    @staticmethod
    def hash_pin(plain_pin: str) -> str:
        """Hash the PIN using bcrypt with salt.""" 
        valid, message = SecurityUtils.validate_pin_complexity(plain_pin)
        if not valid:
            raise SecurityValidationError(message)
        # print(f"Hashing PIN: {pin} (Type: {type(pin)})")
        hashed = bcrypt.hashpw(plain_pin.encode('utf-8'), bcrypt.gensalt())
        # print(f"Generated hash: {hashed.decode()}")
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_pin(plain_pin: str, pin_hash: str) -> bool:
        """Verify if the provided PIN matches the hash."""
        # print(f"Verifying PIN: {pin} against {self.pin_hash}")
        try:
            return bcrypt.checkpw(
                plain_pin.encode('utf-8'), 
                pin_hash.encode('utf-8')
            )
        except (TypeError, ValueError) as e:
            # Handle invalid hash formats or empty values
            current_app.logger.error(f"PIN verification error: {str(e)}")
            return False
    
    
    # @staticmethod
    # def check_pin_attempt_limit(user: User):
    #     if user.failed_pin_attempts >= 3:
    #         lock_time = datetime.utcnow() + timedelta(minutes=15)
    #         user.pin_locked_until = lock_time
    #         UserRepository().update(user)
    #         raise AccountLockedError()
      
    #token related==========================
    # revoked_tokens_hashes = set()  # Stores hashed tokens ,Use Redis in production
    
        
    @staticmethod
    def generate_auth_token() -> Tuple[str, datetime]:
        """Generate secure auth token with expiry"""
        raw_token = secrets.token_urlsafe(64)
        token_hash = bcrypt.hashpw(raw_token.encode(), bcrypt.gensalt()).decode()
        expiry = datetime.now() + timedelta(hours=1)
        return raw_token, token_hash, expiry
    
    
    @staticmethod
    def validate_token(raw_token: str, user: User) -> bool:
        """Only validate token hash and expiry"""
        return (
            bcrypt.checkpw(raw_token.encode(), user.token_hash.encode()) and 
            user.token_expiry >= datetime.utcnow()
        )
        
        # if user.token_hash in SecurityUtils.revoked_tokens_hashes:
        #     return False
        # # Check if the token is valid and not expired   
        # if user.token_expiry < datetime.utcnow():
        #     return False

        # return bcrypt.checkpw(raw_token.encode(), user.token_hash.encode())
    
    
    # @staticmethod
    # def invalidate_token(token_hash: str) -> None:
    #     SecurityUtils.revoked_tokens.add(token_hash)
    
    
    @staticmethod
    def hash_token(raw_token: str) -> str:
        return bcrypt.hashpw(raw_token.encode(), bcrypt.gensalt()).decode()

     
    @staticmethod
    def generate_transaction_id(prefix: str = "TX") -> str:
        """Generate unique transaction IDs with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random = secrets.token_hex(4)
        return f"{prefix}-{timestamp}-{random}"

    #redis implementation
    @staticmethod
    def store_token_in_cache(user_id: str, token_hash: str, expiry: timedelta):
        """Store token hash and expiry time in Redis cache"""
        r.setex(f"user_token:{user_id}", token_hash, expiry)

    @staticmethod
    def validate_token_from_cache(user_id: str, raw_token: str) -> bool:
        """Validate token using cached token hash"""
        token_hash = r.get(f"user_token:{user_id}")
        if not token_hash:
            return False
        return bcrypt.checkpw(raw_token.encode(), token_hash)
    
    @staticmethod
    def invalidate_token_in_cache(user_id: str):
        """Invalidate (delete) the token from the cache"""
        r.delete(f"user_token:{user_id}")  # Delete the token hash from Redis

    # @staticmethod
    # def handle_failed_login(user):
    #     """Track failed login attempts"""
    #     user.failed_attempts += 1
    #     if user.failed_attempts >= 3:
    #         user.locked_until = datetime.now() + timedelta(minutes=15)
    #     UserRepository().update(user)    
    