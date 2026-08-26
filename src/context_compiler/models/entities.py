from enum import Enum
from pydantic import BaseModel, Field

class EntityType(str, Enum):
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    IMPORT = "import"

class CodeEntity(BaseModel):
    id: str = Field(description="Unique identifier, e.g. auth.py::authenticate_user")
    file_path: str
    entity_type: EntityType
    name: str
    start_line: int
    end_line: int
    language: str = "python"
    source_code: str
    signature: str = ""
    docstring: str | None = None

class RelationshipType(str, Enum):
    CALLS = "calls"
    IMPORTS = "imports"
    DEFINES = "defines"
    INHERITS = "inherits"
    REFERENCES = "references"

class Relationship(BaseModel):
    source_id: str
    target_id: str
    relationship_type: RelationshipType
