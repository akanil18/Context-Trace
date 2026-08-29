from pathlib import Path
import tree_sitter_python as tspython
from tree_sitter import Language, Parser
from context_compiler.models.entities import CodeEntity, Relationship, RelationshipType

class PythonAnalyzer:
    """Analyzes Python files using Tree-sitter to extract cross-entity relationships (e.g. CALLS)."""
    
    def __init__(self, entities: list[CodeEntity], workspace_root: Path):
        self.entities = {e.id: e for e in entities}
        self.workspace_root = workspace_root
        self.language = Language(tspython.language())
        self.parser = Parser(self.language)

    def analyze_file(self, file_path: Path) -> list[Relationship]:
        with open(file_path, "rb") as f:
            source_bytes = f.read()
            
        tree = self.parser.parse(source_bytes)
        
        symbol_table = {}
        relationships = []
        
        def get_text(node):
            return source_bytes[node.start_byte:node.end_byte].decode("utf-8")
            
        # First pass: find imports
        def find_imports(node):
            if node.type == "import_from_statement":
                module_name = ""
                names = []
                for child in node.named_children:
                    # In newer tree-sitter bindings, a relative import comes as 'relative_import'
                    if child.type == "dotted_name" and not module_name:
                        # Only take the first dotted_name as module_name if not already set by relative_import
                        module_name = get_text(child)
                    elif child.type == "relative_import":
                        module_name = get_text(child)
                    elif child.type == "aliased_import":
                        names.append(get_text(child.named_children[0]))
                    elif child.type == "dotted_name" or child.type == "identifier":
                        names.append(get_text(child))
                
                if module_name.startswith("."):
                    target_file = module_name.strip(".") + ".py"
                else:
                    target_file = module_name.replace(".", "/") + ".py"
                    
                for name in names:
                    if name != module_name:
                        symbol_table[name] = f"{Path(target_file).name}::{name}"
                        
            for child in node.children:
                find_imports(child)
                
        find_imports(tree.root_node)
        
        # Second pass: find function definitions and their calls
        def find_calls(node, current_func_id=None):
            if node.type == "function_definition":
                name_node = next((c for c in node.named_children if c.type == "identifier"), None)
                if name_node:
                    func_name = get_text(name_node)
                    current_func_id = f"{file_path.name}::{func_name}"
                    
            if node.type == "call" and current_func_id:
                func_node = node.child_by_field_name("function")
                if func_node:
                    if func_node.type == "identifier":
                        call_name = get_text(func_node)
                        if call_name in symbol_table:
                            target_id = symbol_table[call_name]
                            if target_id in self.entities:
                                relationships.append(Relationship(
                                    source_id=current_func_id,
                                    target_id=target_id,
                                    relationship_type=RelationshipType.CALLS
                                ))
                        else:
                            local_id = f"{file_path.name}::{call_name}"
                            if local_id in self.entities:
                                relationships.append(Relationship(
                                    source_id=current_func_id,
                                    target_id=local_id,
                                    relationship_type=RelationshipType.CALLS
                                ))
                    elif func_node.type == "attribute":
                        attr_node = func_node.child_by_field_name("attribute")
                        if attr_node:
                            method_name = get_text(attr_node)
                            # Match unambiguously named methods globally
                            matches = [e_id for e_id, e in self.entities.items() 
                                      if e.name == method_name and e.entity_type.value == "method"]
                            if len(matches) == 1:
                                relationships.append(Relationship(
                                    source_id=current_func_id,
                                    target_id=matches[0],
                                    relationship_type=RelationshipType.CALLS
                                ))
                                
            for child in node.children:
                find_calls(child, current_func_id)
                
        find_calls(tree.root_node)
        
        return relationships
