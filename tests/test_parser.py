from pathlib import Path
from context_compiler.parser.python_parser import PythonParser
from context_compiler.models.entities import EntityType

def test_python_parser_extracts_functions(sample_repo_path):
    parser = PythonParser()
    auth_file = sample_repo_path / "auth.py"
    
    entities = parser.parse(auth_file)
    
    # We expect 2 functions: authenticate_user, validate_token
    assert len(entities) == 2
    
    # Check authenticate_user
    auth_func = next((e for e in entities if e.name == "authenticate_user"), None)
    assert auth_func is not None
    assert auth_func.entity_type == EntityType.FUNCTION
    assert auth_func.id == "auth.py::authenticate_user"
    assert "Authenticates a user" in auth_func.docstring
    assert auth_func.start_line > 0
    assert auth_func.end_line > auth_func.start_line
    assert auth_func.signature.startswith("def authenticate_user")
    
    # Check validate_token
    val_func = next((e for e in entities if e.name == "validate_token"), None)
    assert val_func is not None
    
def test_python_parser_extracts_classes(sample_repo_path):
    parser = PythonParser()
    models_file = sample_repo_path / "models.py"
    
    entities = parser.parse(models_file)
    
    # User class, UserRepository class, and their methods:
    # __init__, verify_password, find_by_username
    
    user_class = next((e for e in entities if e.name == "User"), None)
    assert user_class is not None
    assert user_class.entity_type == EntityType.CLASS
    assert "Domain model for a user" in user_class.docstring
    
    repo_class = next((e for e in entities if e.name == "UserRepository"), None)
    assert repo_class is not None
    assert repo_class.entity_type == EntityType.CLASS
    
    verify_method = next((e for e in entities if e.name == "verify_password"), None)
    assert verify_method is not None
    assert verify_method.entity_type == EntityType.METHOD

