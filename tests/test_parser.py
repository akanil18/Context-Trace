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
    assert val_func.id == "auth.py::validate_token"
    assert "Validates an authentication token." in val_func.docstring
