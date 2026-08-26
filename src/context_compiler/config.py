from pathlib import Path
from pydantic import BaseModel, Field

class CompilerConfig(BaseModel):
    """Configuration for the ContextCompiler system."""
    
    workspace_path: Path = Field(
        default_factory=Path.cwd, 
        description="Root directory of the workspace"
    )
    ignored_directories: list[str] = Field(
        default_factory=lambda: [".git", "node_modules", "__pycache__", ".venv", "build", "dist"],
        description="Directories to ignore during scanning"
    )
    token_budget: int = Field(
        default=4000, 
        description="Max token budget for LLM context"
    )
    embedding_model: str = Field(
        default="BAAI/bge-small-en-v1.5", 
        description="Model name for embeddings"
    )
