from pathlib import Path
from .ignore import IgnorePatterns

class FileScanner:
    """Scans directories for supported source files."""
    
    def __init__(self, supported_extensions: list[str] = None, ignore_patterns: list[str] = None):
        self.supported_extensions = supported_extensions or [".py"]
        self.ignore = IgnorePatterns(ignore_patterns)

    def scan(self, root_path: Path) -> list[Path]:
        """Scans the root path for supported files, respecting ignore patterns."""
        root_path = Path(root_path).resolve()
        self.ignore.load_gitignore(root_path)
        
        found_files = []
        
        def walk(current_dir: Path):
            if self.ignore.is_ignored(current_dir, root_path):
                return
                
            try:
                for item in current_dir.iterdir():
                    if self.ignore.is_ignored(item, root_path):
                        continue
                        
                    if item.is_dir():
                        walk(item)
                    elif item.is_file() and item.suffix in self.supported_extensions:
                        found_files.append(item)
            except PermissionError:
                pass # Skip directories we lack permissions for
                
        walk(root_path)
        return sorted(found_files)
