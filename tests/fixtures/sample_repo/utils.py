import hashlib
import time

def hash_password(password: str) -> str:
    """Hashes a password for storage."""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token(user_id: str) -> str:
    """Generates a new JWT-like token."""
    timestamp = int(time.time())
    return f"jwt_{user_id}_{timestamp}"
