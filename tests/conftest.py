import pytest
from pathlib import Path

@pytest.fixture
def sample_repo_path() -> Path:
    """Returns the absolute path to the sample_repo fixture directory."""
    return Path(__file__).parent / "fixtures" / "sample_repo"
