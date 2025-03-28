import bcrypt
import secrets
from datetime import datetime


def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

def generate_token():
    return secrets.token_urlsafe(32)

def generate_transaction_id():
    return f"TX-{datetime.now().strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(4)}"