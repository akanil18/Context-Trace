from .models import UserRepository
from .utils import generate_token

def authenticate_user(username: str, password: str) -> str | None:
    """Authenticates a user and returns a token if successful."""
    repo = UserRepository()
    user = repo.find_by_username(username)
    if user and user.verify_password(password):
        return generate_token(user.id)
    return None

def validate_token(token: str) -> bool:
    """Validates an authentication token."""
    return len(token) > 10 and token.startswith("jwt_")
