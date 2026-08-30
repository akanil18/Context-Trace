from pathlib import Path
from context_compiler.retrieval.vector_store import VectorStore
from context_compiler.graph.builder import GraphBuilder
from context_compiler.models.entities import CodeEntity, EntityType, Relationship, RelationshipType
from context_compiler.retrieval.hybrid import HybridRetriever

def test_hybrid_retriever(tmp_path):
    vector_store = VectorStore(tmp_path / "lancedb", model_name="all-MiniLM-L6-v2")
    graph_builder = GraphBuilder()
    
    # Entity 1: login (seed)
    entity1 = CodeEntity(
        id="auth.py::login", file_path="auth.py", entity_type=EntityType.FUNCTION,
        name="login", start_line=1, end_line=5, language="python",
        source_code="def login():\n    check_db()", docstring="Authenticates user."
    )
    
    # Entity 2: check_db (related via graph)
    entity2 = CodeEntity(
        id="db.py::check_db", file_path="db.py", entity_type=EntityType.FUNCTION,
        name="check_db", start_line=1, end_line=2, language="python",
        source_code="def check_db():\n    pass", docstring="Database check."
    )
    
    # Entity 3: unrelated
    entity3 = CodeEntity(
        id="ui.py::render", file_path="ui.py", entity_type=EntityType.FUNCTION,
        name="render", start_line=1, end_line=2, language="python",
        source_code="def render():\n    pass", docstring="Renders UI."
    )
    
    vector_store.add_entities([entity1, entity2, entity3])
    graph_builder.add_entity(entity1)
    graph_builder.add_entity(entity2)
    graph_builder.add_entity(entity3)
    
    rel = Relationship(
        source_id="auth.py::login", target_id="db.py::check_db", 
        relationship_type=RelationshipType.CALLS
    )
    graph_builder.add_relationship(rel)
    
    retriever = HybridRetriever(vector_store, graph_builder, token_budget=4000)
    
    # "authentication" should find login semantically, and pull in check_db via graph
    results = retriever.retrieve("authentication", semantic_limit=1)
    
    print(f"DEBUG SEEDS: {vector_store.search('authentication', limit=3)}")
    print(f"DEBUG RESULTS: {results}")
    
    ids = [r.id for r in results]
    assert "auth.py::login" in ids
    assert "db.py::check_db" in ids
    assert "ui.py::render" not in ids
    
    # Test token budgeting (10 tokens = ~40 chars max)
    # entity1 source code is 27 chars = 6 tokens
    # entity2 source code is 24 chars = 6 tokens
    # Total = 12 tokens. With 10 tokens limit, entity2 should be skipped!
    retriever_small = HybridRetriever(vector_store, graph_builder, token_budget=10)
    results_small = retriever_small.retrieve("authentication", semantic_limit=1)
    
    ids_small = [r.id for r in results_small]
    assert len(ids_small) == 1
    assert "auth.py::login" in ids_small
