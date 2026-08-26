from pathlib import Path

def test_sample_repo_exists(sample_repo_path: Path):
    """Test that the sample_repo fixture provides a valid path with the expected files."""
    assert sample_repo_path.exists()
    assert sample_repo_path.is_dir()
    
    expected_files = ["auth.py", "middleware.py", "models.py", "utils.py"]
    for file_name in expected_files:
        assert (sample_repo_path / file_name).exists()
