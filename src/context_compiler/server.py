import os
from pathlib import Path
from fastmcp import FastMCP

from context_compiler.config import CompilerConfig
from context_compiler.scanner.file_scanner import FileScanner
from context_compiler.scanner.ignore import IgnorePatterns
from context_compiler.parser.python_parser import PythonParser
from context_compiler.parser.python_analyzer import PythonAnalyzer
from context_compiler.retrieval.vector_store import VectorStore
from context_compiler.graph.builder import GraphBuilder
from context_compiler.retrieval.hybrid import HybridRetriever
from context_compiler.llm.orchestrator import ContextCompilerAgent

mcp = FastMCP("ContextCompiler")

# Global state
agent: ContextCompilerAgent | None = None
compiled = False

@mcp.tool()
def ping() -> str:
    """A simple ping tool to verify the MCP server is running."""
    return "pong"

@mcp.tool()
def compile_workspace(workspace_path: str) -> str:
    """
    Scans, parses, and indexes a local workspace directory into the Context Compiler's memory.
    Must be called before ask_compiler().
    """
    global agent, compiled
    
    workspace_root = Path(workspace_path).expanduser().resolve()
    if not workspace_root.is_dir():
        return f"Error: Directory {workspace_root} does not exist."
        
    config = CompilerConfig(workspace_root=workspace_root)
    scanner = FileScanner(ignore_patterns=config.ignored_directories)
    
    files = scanner.scan(workspace_root)
    
    # Pass 1: Parse entities
    parser = PythonParser()
    all_entities = []
    
    for f in files:
        if f.suffix == ".py":
            all_entities.extend(parser.parse(f))
            
    # Pass 2: Analyze relationships
    analyzer = PythonAnalyzer(all_entities, workspace_root)
    all_relationships = []
    for f in files:
        if f.suffix == ".py":
            all_relationships.extend(analyzer.analyze_file(f))
            
    # Build Storage
    lancedb_path = workspace_root / ".context_compiler" / "lancedb"
    lancedb_path.parent.mkdir(parents=True, exist_ok=True)
    
    import shutil
    # Clean previous vector store for fresh compile
    shutil.rmtree(lancedb_path, ignore_errors=True)
    
    vector_store = VectorStore(lancedb_path)
    vector_store.add_entities(all_entities)
    
    graph_builder = GraphBuilder()
    for e in all_entities:
        graph_builder.add_entity(e)
    for r in all_relationships:
        graph_builder.add_relationship(r)
        
    # Serialize graph
    graph_path = workspace_root / ".context_compiler" / "graph.json"
    graph_builder.save(graph_path)
    
    # Setup Orchestrator
    retriever = HybridRetriever(vector_store, graph_builder)
    
    # We rely on GOOGLE_API_KEY being set in the environment
    if "GOOGLE_API_KEY" not in os.environ:
        return f"Workspace compiled successfully with {len(all_entities)} entities. However, GOOGLE_API_KEY is not set in the environment. LLM orchestration will fail."
        
    agent = ContextCompilerAgent(retriever)
    compiled = True
    
    return f"Success! Compiled {len(all_entities)} entities and {len(all_relationships)} relationships across {len(files)} files in {workspace_root}."

@mcp.tool()
def ask_compiler(query: str) -> str:
    """
    Asks the Context Compiler agent a question about the compiled workspace. 
    It will use the hybrid retriever to gather relevant code snippets before answering.
    """
    global agent, compiled
    if not compiled or agent is None:
        return "Error: Workspace has not been compiled yet. Please run compile_workspace() first."
        
    try:
        response = agent.ask(query)
        return response
    except Exception as e:
        import traceback
        return f"Error during LLM orchestration:\n{traceback.format_exc()}"

if __name__ == "__main__":
    mcp.run()
