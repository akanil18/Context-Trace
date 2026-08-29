from pathlib import Path
from context_compiler.parser.python_parser import PythonParser
from context_compiler.parser.python_analyzer import PythonAnalyzer

def test_python_analyzer(sample_repo_path):
    parser = PythonParser()
    
    auth_file = sample_repo_path / "auth.py"
    models_file = sample_repo_path / "models.py"
    utils_file = sample_repo_path / "utils.py"
    
    all_entities = []
    all_entities.extend(parser.parse(auth_file))
    all_entities.extend(parser.parse(models_file))
    all_entities.extend(parser.parse(utils_file))
    
    analyzer = PythonAnalyzer(all_entities, sample_repo_path)
    
    auth_rels = analyzer.analyze_file(auth_file)
    
    # authenticate_user calls generate_token (imported from utils)
    calls_generate_token = any(
        r.source_id == "auth.py::authenticate_user" and r.target_id == "utils.py::generate_token" 
        for r in auth_rels
    )
    
    # authenticate_user calls verify_password (method matched globally)
    calls_verify_password = any(
        r.source_id == "auth.py::authenticate_user" and r.target_id == "models.py::verify_password" 
        for r in auth_rels
    )
                                
    assert calls_generate_token is True
    assert calls_verify_password is True
