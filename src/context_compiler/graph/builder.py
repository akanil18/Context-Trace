import networkx as nx
import json
from pathlib import Path
from context_compiler.models.entities import CodeEntity, Relationship

class GraphBuilder:
    """Builds and serializes a directed graph of code entities and relationships."""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        
    def add_entity(self, entity: CodeEntity):
        """Adds a code entity as a node in the graph."""
        self.graph.add_node(entity.id, **entity.model_dump())
        
    def add_relationship(self, relationship: Relationship):
        """Adds a relationship as a directed edge in the graph."""
        self.graph.add_edge(
            relationship.source_id, 
            relationship.target_id, 
            type=relationship.relationship_type.value
        )
        
    def get_entity(self, entity_id: str) -> CodeEntity | None:
        """Retrieves a code entity from the graph by its ID."""
        if entity_id in self.graph:
            node_data = dict(self.graph.nodes[entity_id])
            if "id" not in node_data:
                node_data["id"] = entity_id
            return CodeEntity(**node_data)
        return None
        
    def save(self, path: Path):
        """Serializes the graph to a JSON file."""
        data = nx.node_link_data(self.graph)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            
    def load(self, path: Path):
        """Loads the graph from a JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.graph = nx.node_link_graph(data)
