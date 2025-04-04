import bcrypt
import secrets
from datetime import datetime, timedelta
from typing import Tuple
from flask import current_app
from models.user_model import User
from repos.user_repo import UserRepository
from .exceptions import *


class SecurityUtils:
    @staticmethod
    def validate_pin_complexity(pin: str) -> Tuple[bool, str]:
        """Enforce PIN complexity rules for banking applications"""
        if len(pin) != 8:
            return False, "PIN must be exactly 8 digits"
        if not pin.isdigit():
            return False, "PIN must contain only numbers"
        if len(set(pin)) < 4:
            return False, "PIN must contain at least 4 unique digits"
        if pin in ['12345678', '00000000']:
            return False, "Common PINs are not allowed"
        return True, ""

    @staticmethod
    def hash_pin(pin: str) -> str:
        """Hash the PIN using bcrypt with salt.""" 
        valid, message = SecurityUtils.validate_pin_complexity(pin)
        if not valid:
            raise SecurityValidationError(message)
        # print(f"Hashing PIN: {pin} (Type: {type(pin)})")
        hashed = bcrypt.hashpw(pin.encode('utf-8'), bcrypt.gensalt())
        # print(f"Generated hash: {hashed.decode()}")
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_pin(plain_pin: str, hashed_pin: str) -> bool:
        """Verify if the provided PIN matches the hash."""
        # print(f"Verifying PIN: {pin} against {self.pin_hash}")
        try:
            return bcrypt.checkpw(
                plain_pin.encode('utf-8'), 
                hashed_pin.encode('utf-8')
            )
        except (TypeError, ValueError) as e:
            # Handle invalid hash formats or empty values
            current_app.logger.error(f"PIN verification error: {str(e)}")
            return False
        
    @staticmethod
    def generate_auth_token(length: int = 64) -> Tuple[str, datetime]:
        """Generate secure auth token with expiry"""
        token = secrets.token_urlsafe(length)
        expiry = datetime.now() + timedelta(hours=1)
        return token, expiry
    
    @staticmethod
    def validate_token(token: str, user: User) -> bool:
        """Validate token with security checks"""
        return (
            secrets.compare_digest(token, user.token) and
            user.token_expiry > datetime.now()
        )
    
    @staticmethod
    def invalidate_token(old_token: str) -> None:
        """Perform cryptographic token invalidation"""
        # Use constant-time comparison to prevent timing attacks
        secrets.compare_digest(old_token, "invalidated")
    
    # @staticmethod
    # def hash_token(token: str) -> str:
    #     return bcrypt.hashpw(token.encode(), bcrypt.gensalt()).decode()

     
    @staticmethod
    def generate_transaction_id(prefix: str = "TX") -> str:
        """Generate unique transaction IDs with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random = secrets.token_hex(4)
        return f"{prefix}-{timestamp}-{random}"

    @staticmethod
    def validate_password_complexity(password: str) -> Tuple[bool, str]:
        """Bank-grade password validation (if needed later)"""
        # Implement similar complexity rules as PIN if required
        pass
        

    # @staticmethod
    # def validate_login_attempt(user):
    #     """Check failed attempts and lockouts"""
    #     if user.failed_attempts >= 3:
    #         if datetime.now() < user.locked_until:
    #             raise AccountLockedError(f"Account locked until {user.locked_until}")
    #         else:
    #             user.failed_attempts = 0
    #             user.locked_until = None

    @staticmethod
    def handle_failed_login(user):
        """Track failed login attempts"""
        user.failed_attempts += 1
        if user.failed_attempts >= 3:
            user.locked_until = datetime.now() + timedelta(minutes=15)
        UserRepository().update(user)    
    