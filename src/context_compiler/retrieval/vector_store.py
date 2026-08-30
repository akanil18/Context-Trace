import lancedb
from sentence_transformers import SentenceTransformer
from context_compiler.models.entities import CodeEntity
from pathlib import Path

class VectorStore:
    """Manages semantic embeddings and vector search for code entities."""
    
    def __init__(self, db_path: str | Path, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.db_path = str(db_path)
        self.db = lancedb.connect(self.db_path)
        self.model = SentenceTransformer(model_name)
        
    def _get_or_create_table(self):
        if "code_entities" in self.db.table_names():
            return self.db.open_table("code_entities")
        else:
            return None

    def add_entities(self, entities: list[CodeEntity]):
        """Embeds and stores a list of CodeEntity objects."""
        if not entities:
            return
            
        texts = []
        for e in entities:
            text = f"{e.name}\n{e.docstring or ''}\n{e.signature or e.source_code}"
            texts.append(text)
            
        vectors = self.model.encode(texts)
        
        data = []
        for i, entity in enumerate(entities):
            row = entity.model_dump()
            row["vector"] = vectors[i].tolist()
            row["entity_type"] = row["entity_type"].value
            data.append(row)
            
        table = self._get_or_create_table()
        if table is None:
            self.db.create_table("code_entities", data=data)
        else:
            table.add(data)
            
    def search(self, query: str, limit: int = 5) -> list[CodeEntity]:
        """Performs a semantic search for code entities."""
        table = self._get_or_create_table()
        if table is None:
            return []
            
        query_vector = self.model.encode([query])[0]
    
        results = table.search(query_vector).limit(limit).to_list()
        
        entities = []
        for res in results:
            # CodeEntity(**res) ignores extra fields like 'vector' and '_distance'
            entities.append(CodeEntity(**res))
            
        return entities
