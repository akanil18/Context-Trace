import pytest
from pathlib import Path
from context_compiler.scanner.file_scanner import FileScanner
from context_compiler.scanner.ignore import IgnorePatterns

def test_ignore_patterns():
    ignore = IgnorePatterns([".custom_ignore"])
    root = Path("/fake/root")
    
    # Should ignore standard directories
    assert ignore.is_ignored(root / ".git", root)
    assert ignore.is_ignored(root / "__pycache__", root)
    assert ignore.is_ignored(root / ".venv", root)
    
    # Should ignore custom
    assert ignore.is_ignored(root / ".custom_ignore", root)
    
    # Should not ignore normal files
    assert not ignore.is_ignored(root / "main.py", root)
    assert not ignore.is_ignored(root / "src", root)

def test_file_scanner(sample_repo_path, tmp_path):
    # Test scanning the sample repo
    scanner = FileScanner()
    files = scanner.scan(sample_repo_path)
    
    # Verify we found the expected files
    file_names = [f.name for f in files]
    assert "auth.py" in file_names
    assert "middleware.py" in file_names
    assert "models.py" in file_names
    assert "utils.py" in file_names
    
    # Test ignore logic with a temporary structure
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").touch()
    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv" / "bad.py").touch()
    (tmp_path / "build").mkdir()
    (tmp_path / "build" / "out.py").touch()
    
    # Create a gitignore
    with open(tmp_path / ".gitignore", "w") as f:
        f.write("src/ignore_me.py\n")
        
    (tmp_path / "src" / "ignore_me.py").touch()
    
    scanned = scanner.scan(tmp_path)
    scanned_names = [f.name for f in scanned]
    
    assert "main.py" in scanned_names
    assert "bad.py" not in scanned_names
    assert "out.py" not in scanned_names
    assert "ignore_me.py" not in scanned_names
