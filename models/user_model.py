from datetime import datetime, timedelta
import secrets
from uuid import uuid4
import uuid
import bcrypt




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
    ) -> None:
        
        self.id = str(uuid.uuid4()) #PK
        self.username = username.strip().lower()
        self.email = email
        self.pin_hash = self._hash_pin(pin) #hash in real implementation
        self.first_name = first_name
        self.last_name = last_name
        self.role = role
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.token = None 
        self.token_expiry = None
 
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()   
    
    def refresh_token(self):
        """Generates new auth token"""
        self.token = secrets.token_urlsafe(64)
        self.token_expiry = datetime.now() + timedelta(hours=1)
        
    def _hash_pin(self, pin: str) -> str:
        """Hash the PIN using bcrypt with salt."""
        # print(f"Hashing PIN: {pin} (Type: {type(pin)})")
        hashed = bcrypt.hashpw(pin.encode('utf-8'), bcrypt.gensalt())
        # print(f"Generated hash: {hashed.decode()}")
        return hashed.decode('utf-8')

    def verify_pin(self, pin: str) -> bool:
        """Verify if the provided PIN matches the hash."""
        # print(f"Verifying PIN: {pin} against {self.pin_hash}")
        return bcrypt.checkpw(
            pin.encode('utf-8'), 
            self.pin_hash.encode('utf-8')
        )
    
    
    def to_dict(self) -> dict:
        """Safe serialization (excludes sensitive fields)"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
            
        }    
    

        
 