from pathlib import Path
from context_compiler.config import CompilerConfig

def test_config_defaults():
    """Test that the configuration defaults are set properly."""
    config = CompilerConfig()
    assert config.token_budget == 4000
    assert config.embedding_model == "BAAI/bge-small-en-v1.5"
    assert ".git" in config.ignored_directories
    assert ".venv" in config.ignored_directories
    assert config.workspace_path == Path.cwd()

def test_config_overrides():
    """Test that configuration parameters can be overridden."""
    custom_path = Path("/tmp/test")
    config = CompilerConfig(
        workspace_path=custom_path,
        token_budget=8000,
        ignored_directories=[".custom_ignore"],
        embedding_model="openai/text-embedding-3-small"
    )
    assert config.token_budget == 8000
    assert config.embedding_model == "openai/text-embedding-3-small"
    assert config.ignored_directories == [".custom_ignore"]
    assert config.workspace_path == custom_path
