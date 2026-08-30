from unittest.mock import MagicMock
from context_compiler.llm.orchestrator import ContextCompilerAgent
from context_compiler.models.entities import CodeEntity, EntityType

def test_agent_orchestration():
    mock_retriever = MagicMock()
    
    # Mocking retrieval to return 1 entity
    entity = CodeEntity(
        id="file.py::func", file_path="file.py", entity_type=EntityType.FUNCTION,
        name="func", start_line=1, end_line=2, language="python",
        source_code="def func(): pass", docstring="Does a thing."
    )
    mock_retriever.retrieve.return_value = [entity]
    
    # Using dummy API key to avoid initialization errors
    agent = ContextCompilerAgent(retriever=mock_retriever, api_key="dummy_key")
    
    # Mock the Gemini client response
    mock_response = MagicMock()
    mock_response.text = "This is a mocked response based on the code."
    agent.client.models.generate_content = MagicMock(return_value=mock_response)
    
    response_text = agent.ask("How does this function work?")
    
    assert response_text == "This is a mocked response based on the code."
    
    # Check memory state
    assert len(agent.memory.history) == 2
    assert agent.memory.history[0].role == "user"
    assert agent.memory.history[0].parts[0].text == "How does this function work?"
    assert agent.memory.history[1].role == "model"
    assert agent.memory.history[1].parts[0].text == "This is a mocked response based on the code."
    
    # Verify the context builder
    context_str = agent._build_context_prompt("fake query")
    assert "def func(): pass" in context_str
    assert "Does a thing." in context_str
    assert "file.py" in context_str
