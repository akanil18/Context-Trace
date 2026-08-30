from context_compiler.retrieval.vector_store import VectorStore
from context_compiler.models.entities import CodeEntity, EntityType
from pathlib import Path

p = Path('/tmp/debug_lancedb_3')
import shutil
shutil.rmtree(p, ignore_errors=True)
p.mkdir(exist_ok=True)

store = VectorStore(p, model_name='all-MiniLM-L6-v2')
e1 = CodeEntity(
    id='auth.py::login', 
    file_path='auth.py', 
    entity_type=EntityType.FUNCTION, 
    name='login', 
    start_line=1, 
    end_line=5, 
    language='python', 
    source_code='def login():\n    check_db()', 
    docstring='Authenticates user.'
)

try:
    store.add_entities([e1])
    print('add_entities succeeded!')
    print(f"table_names(): {store.db.table_names()}")
    
    t = store._get_or_create_table()
    if t:
        print(f"Table rows: {len(t.to_arrow())}")
        
    res = store.search("authentication", limit=1)
    print(f"Search results: {res}")
except Exception as e:
    import traceback
    traceback.print_exc()
