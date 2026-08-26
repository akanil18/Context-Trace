class User:
    """Domain model for a user."""
    
    def __init__(self, id: str, username: str, hashed_password: str):
        self.id = id
        self.username = username
        self.hashed_password = hashed_password
        
    def verify_password(self, password: str) -> bool:
        """Verifies if the provided password matches the hash."""
        from .utils import hash_password
        return hash_password(password) == self.hashed_password


class UserRepository:
    """Data access for users."""
    
    def find_by_username(self, username: str) -> User | None:
        """Finds a user by their username."""
        # Simulated database lookup
        if username == "admin":
            return User("1", "admin", "hashed_secret")
        return None
