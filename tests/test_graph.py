from pathlib import Path
from context_compiler.graph.builder import GraphBuilder
from context_compiler.models.entities import CodeEntity, EntityType, Relationship, RelationshipType

def test_graph_builder(tmp_path):
    builder = GraphBuilder()
    
    entity = CodeEntity(
        id="file.py::func",
        file_path="file.py",
        entity_type=EntityType.FUNCTION,
        name="func",
        start_line=1,
        end_line=2,
        language="python",
        source_code="def func(): pass",
    )
    
    entity2 = CodeEntity(
        id="file.py::func2",
        file_path="file.py",
        entity_type=EntityType.FUNCTION,
        name="func2",
        start_line=4,
        end_line=5,
        language="python",
        source_code="def func2(): func()",
    )
    
    builder.add_entity(entity)
    builder.add_entity(entity2)
    
    rel = Relationship(
        source_id="file.py::func2",
        target_id="file.py::func",
        relationship_type=RelationshipType.CALLS
    )
    builder.add_relationship(rel)
    
    assert builder.graph.number_of_nodes() == 2
    assert builder.graph.number_of_edges() == 1
    
    # Test get_entity
    assert builder.get_entity("file.py::func").name == "func"
    assert builder.get_entity("missing") is None
    
    # Test serialization
    save_path = tmp_path / "graph.json"
    builder.save(save_path)
    
    builder2 = GraphBuilder()
    builder2.load(save_path)
    
    assert builder2.graph.number_of_nodes() == 2
    assert builder2.graph.number_of_edges() == 1
    loaded_entity = builder2.get_entity("file.py::func")
    assert loaded_entity.name == "func"
