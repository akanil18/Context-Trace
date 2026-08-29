from abc import ABC, abstractmethod
from pathlib import Path
from context_compiler.models.entities import CodeEntity

class BaseParser(ABC):
    """Abstract base class for language parsers."""
    
    @abstractmethod
    def parse(self, file_path: Path) -> list[CodeEntity]:
        """Parses a file and extracts code entities."""
        pass
