from pathlib import Path
from context_compiler.server import compile_workspace, ask_compiler

def test_compile_workspace(tmp_path, monkeypatch):
    # Setup dummy workspace
    workspace = tmp_path / "dummy_workspace"
    workspace.mkdir()
    
    (workspace / "main.py").write_text("def hello():\n    pass")
    
    # Mock GOOGLE_API_KEY so orchestration initializes without crashing
    monkeypatch.setenv("GOOGLE_API_KEY", "dummy_key")
    
    # Compile
    result = compile_workspace(str(workspace))
    assert "Success" in result
    assert "1 entities" in result
    
    # We won't test ask_compiler since that makes a network call, but we can verify agent state
    from context_compiler.server import agent, compiled
    assert compiled is True
    assert agent is not None
