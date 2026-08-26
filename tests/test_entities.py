from context_compiler.models.entities import CodeEntity, EntityType, Relationship, RelationshipType

def test_code_entity_serialization():
    entity = CodeEntity(
        id="auth.py::authenticate_user",
        file_path="auth.py",
        entity_type=EntityType.FUNCTION,
        name="authenticate_user",
        start_line=10,
        end_line=20,
        language="python",
        source_code="def authenticate_user():\n    pass",
        signature="def authenticate_user():",
        docstring="Authenticates the user."
    )
    
    data = entity.model_dump()
    assert data["id"] == "auth.py::authenticate_user"
    assert data["entity_type"] == "function"
    
    reloaded = CodeEntity(**data)
    assert reloaded.id == entity.id
    assert reloaded.entity_type == EntityType.FUNCTION
    assert reloaded.start_line == 10

def test_relationship_serialization():
    rel = Relationship(
        source_id="auth.py::authenticate_user",
        target_id="models.py::User.find",
        relationship_type=RelationshipType.CALLS
    )
    
    data = rel.model_dump()
    assert data["relationship_type"] == "calls"
    
    reloaded = Relationship(**data)
    assert reloaded.source_id == rel.source_id
    assert reloaded.target_id == "models.py::User.find"
