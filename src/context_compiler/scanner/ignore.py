import fnmatch
from pathlib import Path

class IgnorePatterns:
    """Handles ignore pattern matching for file scanning."""
    
    def __init__(self, additional_ignores: list[str] = None):
        self.patterns = [
            ".git", "node_modules", "__pycache__", ".venv", "venv", 
            "env", "build", "dist", "*.egg-info"
        ]
        if additional_ignores:
            self.patterns.extend(additional_ignores)

    def load_gitignore(self, root_path: Path):
        """Loads patterns from a .gitignore file if it exists."""
        gitignore_path = root_path / ".gitignore"
        if gitignore_path.exists():
            with open(gitignore_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        self.patterns.append(line)

    def is_ignored(self, path: Path, root_path: Path) -> bool:
        """Checks if a path matches any ignore pattern."""
        try:
            rel_path = path.relative_to(root_path)
        except ValueError:
            rel_path = path

        rel_str = str(rel_path)
        
        for pattern in self.patterns:
            clean_pattern = pattern.rstrip("/")
            
            # Match exactly the name of the file/folder or wildcard match
            if path.name == clean_pattern or fnmatch.fnmatch(path.name, clean_pattern):
                return True
                
            # Match the relative path
            if (fnmatch.fnmatch(rel_str, clean_pattern) or 
                fnmatch.fnmatch(rel_str, f"*/{clean_pattern}") or 
                fnmatch.fnmatch(rel_str, f"{clean_pattern}/*") or 
                fnmatch.fnmatch(rel_str, f"*/{clean_pattern}/*")):
                return True
                
        return False
