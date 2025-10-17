
import json
from tool_pattern_agent.tool_agent import ToolAgent
from tool_pattern_agent.tools import search_tool

# --- Mock Helper Classes ---
class MockChoice:
    def __init__(self, content):
        self.message = MockMessage(content)

class MockMessage:
    def __init__(self, content):
        self.content = content

class MockCompletion:
    def __init__(self, content):
        self.choices = [MockChoice(content)]


def test_run_with_tool_call_and_synthesis(mocker):
    """
    Tests the primary execution path where the agent:
    1. Decides to use a tool.
    2. Executes the tool.
    3. Synthesizes a final answer.
    """
    # Arrange: Set up mock responses for the two LLM calls
    # Response 1: The "Router" decides to use the search tool.
    router_response_content = json.dumps({
        "action": "search",
        "action_input": "latest trends in AI"
    })
    mock_router_response = MockCompletion(router_response_content)

    # Response 2: The "Synthesizer" provides the final answer.
    synthesizer_response_content = "Based on my search, the latest trends in AI include multi-modal models and agentic architectures."
    mock_synthesizer_response = MockCompletion(synthesizer_response_content)

    # Mock the API to return different responses on subsequent calls.
    # 'side_effect' is a powerful mocker feature for testing multi-step interactions.
    mock_api_call = mocker.patch(
        "openai.resources.chat.completions.Completions.create",
        side_effect=[mock_router_response, mock_synthesizer_response]
    )

    agent = ToolAgent(tools=[search_tool])
    user_prompt = "What are the latest trends in AI?"

    # Act: Run the agent's full logic
    final_answer = agent.run(user_prompt)

    # Assert: Verify the outcome
    assert final_answer == synthesizer_response_content
    assert mock_api_call.call_count == 2 # Crucially, verify that both the router and synthesizer were called.


def test_run_with_direct_answer(mocker):
    """
    Tests the simpler execution path where the agent knows the answer
    and does not need to use a tool.
    """
    # Arrange: Set up a single, direct response from the LLM
    direct_answer_content = "Paris is the capital of France."
    mock_direct_response = MockCompletion(direct_answer_content)

    # Here we only need one response, so 'return_value' is sufficient.
    mock_api_call = mocker.patch(
        "openai.resources.chat.completions.Completions.create",
        return_value=mock_direct_response
    )

    agent = ToolAgent(tools=[search_tool])
    user_prompt = "What is the capital of France?"

    # Act: Run the agent's logic
    final_answer = agent.run(user_prompt)

    # Assert: Verify the outcome
    assert final_answer == direct_answer_content
    assert mock_api_call.call_count == 1 # Verify that only the router was called.