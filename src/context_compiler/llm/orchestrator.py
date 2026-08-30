import os
from google import genai
from google.genai import types
from context_compiler.retrieval.hybrid import HybridRetriever

class ConversationMemory:
    """Manages the multi-turn conversational history for the agent."""
    def __init__(self):
        self.history = []
        
    def add_user_message(self, message: str):
        self.history.append(types.Content(role="user", parts=[types.Part.from_text(text=message)]))
        
    def add_model_message(self, message: str):
        self.history.append(types.Content(role="model", parts=[types.Part.from_text(text=message)]))
        
    def get_history(self) -> list[types.Content]:
        return self.history

class ContextCompilerAgent:
    """Orchestrates code context retrieval and multi-turn LLM interactions."""
    def __init__(self, retriever: HybridRetriever, model_name: str = "gemini-2.5-flash", api_key: str | None = None):
        self.retriever = retriever
        self.model_name = model_name
        self.memory = ConversationMemory()
        # Initialize GenAI Client (requires GOOGLE_API_KEY environment variable if api_key is None)
        self.client = genai.Client(api_key=api_key)
        
    def _build_context_prompt(self, query: str) -> str:
        entities = self.retriever.retrieve(query)
        if not entities:
            return "No relevant code context found."
            
        context_parts = ["Here is the relevant code context:\n"]
        for entity in entities:
            context_parts.append(f"--- File: {entity.file_path} | Entity: {entity.name} ---")
            if entity.docstring:
                context_parts.append(f"Docstring: {entity.docstring}")
            context_parts.append(f"Code:\n```python\n{entity.source_code}\n```\n")
            
        return "\n".join(context_parts)
        
    def ask(self, query: str) -> str:
        """Processes a user query by retrieving context and calling the LLM."""
        context_str = self._build_context_prompt(query)
        
        system_instruction = (
            "You are an expert autonomous coding assistant. Use the provided code context to answer the user's question accurately."
        )
        
        # We append the giant context payload to the query only for the LLM call, but we 
        # don't save it to the memory history to avoid blowing up the context window in multi-turn.
        full_prompt = f"{context_str}\n\nUser Question:\n{query}"
        
        # Build contents array
        current_message = types.Content(role="user", parts=[types.Part.from_text(text=full_prompt)])
        contents = self.memory.get_history() + [current_message]
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.0
            )
        )
        
        # Save pure query to memory, not the huge context payload
        self.memory.add_user_message(query)
        self.memory.add_model_message(response.text)
        
        return response.text
