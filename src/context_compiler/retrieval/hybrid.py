from context_compiler.retrieval.vector_store import VectorStore
from context_compiler.graph.builder import GraphBuilder
from context_compiler.models.entities import CodeEntity

class HybridRetriever:
    """Combines semantic search with graph traversal to retrieve contextual code snippets."""
    
    def __init__(self, vector_store: VectorStore, graph_builder: GraphBuilder, token_budget: int = 4000):
        self.vector_store = vector_store
        self.graph = graph_builder.graph
        self.token_budget = token_budget
        
    def _estimate_tokens(self, text: str) -> int:
        """Rough estimation: 4 characters per token."""
        return len(text) // 4
        
    def retrieve(self, query: str, semantic_limit: int = 5) -> list[CodeEntity]:
        """
        1. Perform semantic search to find seed entities.
        2. Traverse graph to find related entities (callers/callees).
        3. Assemble results until token budget is hit.
        """
        seeds = self.vector_store.search(query, limit=semantic_limit)
        
        selected_entities = {}
        current_tokens = 0
        
        # Phase 1: Add semantic seeds
        for entity in seeds:
            tokens = self._estimate_tokens(entity.source_code)
            # If a seed alone exceeds budget, include it anyway if it's the very first one
            if current_tokens > 0 and current_tokens + tokens > self.token_budget:
                continue
            
            selected_entities[entity.id] = entity
            current_tokens += tokens
            
        # Phase 2: Add graph relationships (1st degree)
        new_candidates = []
        for seed in seeds:
            if seed.id in self.graph:
                # Outgoing edges (e.g., seed calls X)
                for target_id in self.graph.successors(seed.id):
                    if target_id not in selected_entities:
                        new_candidates.append(target_id)
                        
                # Incoming edges (e.g., Y calls seed)
                for source_id in self.graph.predecessors(seed.id):
                    if source_id not in selected_entities:
                        new_candidates.append(source_id)
                        
        # Phase 3: Budgeted addition of graph neighbors
        # (Could use pagerank or weight here, for now arbitrary order)
        for entity_id in set(new_candidates):
            if entity_id in self.graph.nodes:
                node_data = dict(self.graph.nodes[entity_id])
                if "id" not in node_data:
                    node_data["id"] = entity_id
                entity = CodeEntity(**node_data)
                
                tokens = self._estimate_tokens(entity.source_code)
                if current_tokens + tokens <= self.token_budget:
                    selected_entities[entity.id] = entity
                    current_tokens += tokens
                else:
                    break # Stop if budget exhausted
                    
        return list(selected_entities.values())
