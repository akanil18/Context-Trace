from pathlib import Path
import tree_sitter_python as tspython
from tree_sitter import Language, Parser

from .base import BaseParser
from context_compiler.models.entities import CodeEntity, EntityType

class PythonParser(BaseParser):
    def __init__(self):
        self.language = Language(tspython.language())
        self.parser = Parser(self.language)
        
        query_path = Path(__file__).parent / "queries" / "python.scm"
        with open(query_path, "r", encoding="utf-8") as f:
            self.query_string = f.read()
            
        from tree_sitter import Query
        self.query = Query(self.language, self.query_string)

    def parse(self, file_path: Path) -> list[CodeEntity]:
        with open(file_path, "rb") as f:
            source_bytes = f.read()
            
        tree = self.parser.parse(source_bytes)
        entities = []
        
        from tree_sitter import QueryCursor
        cursor = QueryCursor(self.query)
        
        for match in cursor.matches(tree.root_node):
            captures_dict = match[1]
            
            if "function.def" in captures_dict and "function.name" in captures_dict:
                def_node = captures_dict["function.def"][0]
                name_node = captures_dict["function.name"][0]
                
                name = source_bytes[name_node.start_byte:name_node.end_byte].decode("utf-8")
                
                docstring = None
                if "function.body" in captures_dict:
                    body_node = captures_dict["function.body"][0]
                    if body_node.named_children:
                        first_stmt = body_node.named_children[0]
                        if first_stmt.type == "expression_statement":
                            expr = first_stmt.named_children[0]
                            if expr.type == "string":
                                docstring = source_bytes[expr.start_byte:expr.end_byte].decode("utf-8").strip('\'"')

                signature = ""
                if "function.body" in captures_dict:
                    sig_bytes = source_bytes[def_node.start_byte:captures_dict["function.body"][0].start_byte]
                    signature = sig_bytes.decode("utf-8").strip()
                    if signature.endswith(":"):
                        signature = signature[:-1].strip()

                entity = CodeEntity(
                    id=f"{file_path.name}::{name}",
                    file_path=str(file_path),
                    entity_type=EntityType.FUNCTION,
                    name=name,
                    start_line=def_node.start_point[0] + 1,
                    end_line=def_node.end_point[0] + 1,
                    language="python",
                    source_code=source_bytes[def_node.start_byte:def_node.end_byte].decode("utf-8"),
                    signature=signature,
                    docstring=docstring
                )
                
                # Prevent duplicates (query matches can sometimes yield overlapping captures)
                if not any(e.id == entity.id for e in entities):
                    entities.append(entity)
                
        return entities
