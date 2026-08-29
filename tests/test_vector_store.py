from pathlib import Path
from context_compiler.retrieval.vector_store import VectorStore
from context_compiler.models.entities import CodeEntity, EntityType

def test_vector_store(tmp_path):
    # Use a small/fast model for testing purposes
    store = VectorStore(tmp_path / "lancedb", model_name="all-MiniLM-L6-v2")
    
    entity1 = CodeEntity(
        id="auth.py::login",
        file_path="auth.py",
        entity_type=EntityType.FUNCTION,
        name="login",
        start_line=1,
        end_line=5,
        language="python",
        source_code="def login():\n    pass",
        docstring="Handles user authentication securely."
    )
    
    entity2 = CodeEntity(
        id="db.py::connect",
        file_path="db.py",
        entity_type=EntityType.FUNCTION,
        name="connect",
        start_line=1,
        end_line=2,
        language="python",
        source_code="def connect():\n    pass",
        docstring="Connects to the PostgreSQL database cluster."
    )
    
    store.add_entities([entity1, entity2])
    
    # Semantic search for authentication concepts
    results = store.search("authentication", limit=1)
    assert len(results) == 1
    assert results[0].name == "login"
    
    # Semantic search for database concepts
    results = store.search("database", limit=1)
    assert len(results) == 1
    assert results[0].name == "connect"
    
    # Reinitialize to test persistence
    store2 = VectorStore(tmp_path / "lancedb", model_name="all-MiniLM-L6-v2")
    results2 = store2.search("authentication", limit=1)
    assert len(results2) == 1
    assert results2[0].name == "login"
