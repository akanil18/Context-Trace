from .auth import validate_token

def auth_middleware(request, next_handler):
    """Middleware to enforce authentication."""
    token = request.headers.get("Authorization", "")
    if token.startswith("Bearer "):
        token = token.split(" ")[1]
        
    if not validate_token(token):
        return {"status": 401, "message": "Unauthorized"}
        
    return next_handler(request)
