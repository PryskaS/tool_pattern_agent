import os
import json
from openai import OpenAI
from typing import List
from .tool import Tool

class ToolAgent:
    """An agent that can use tools to answer questions."""

    def __init__(self, tools: List[Tool], model: str = "gpt-3.5-turbo"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model
        # Use a dictionary for fast tool lookup by name
        self.tools = {tool.name: tool for tool in tools}
        self.system_prompt = self._create_system_prompt()

    # Creates a system prompt for the agent
    def _create_system_prompt(self) -> str:
        """Creates a dynamic system prompt based on the available tools."""
        tool_descriptions = json.dumps(
            [tool.to_dict() for tool in self.tools.values()],
            indent=2
        )

        return f"""
        You are a helpful assistant with access to the following tools.
        Your task is to answer the user's question.
        You must decide if a tool is necessary to answer the question.

        If a tool is needed, respond with a single JSON object with two keys:
        "action": the name of the tool to use (e.g., "search")
        "action_input": the query or input for the tool.

        If no tool is needed, just respond with the answer directly.

        Here are the available tools:
        {tool_descriptions}
        """

    # Runs the agent with the given user prompt
    def run(self, user_prompt: str) -> str:
        """
        Orchestrates the agent's execution loop.
        1. Decides if a tool is needed.
        2. If so, executes the tool.
        3. Synthesizes the final answer based on the tool's output.
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        # === Step 1: First call to the LLM to act as the "Router" ===
        print("--- Agent thinking... (Router Call) ---")
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0, # Use low temperature for deterministic tool selection
            )
            response_message = response.choices[0].message
            response_content = response_message.content.strip()
            messages.append(response_message) # Add LLM's decision to history

        except Exception as e:
            return f"An error occurred during the first API call: {e}"

        # === Step 2: Parse the Router's response to see if it's a tool call ===
        tool_call = None
        try:
            # Expect a JSON object for tool calls.
            # If it's not valid JSON, we assume it's a direct answer.
            tool_call = json.loads(response_content)
            print(f"--- Tool call detected: {tool_call} ---")
        except json.JSONDecodeError:
            # No valid JSON found, so it's a direct answer from the LLM.
            print("--- No tool call detected. Returning direct answer. ---")
            return response_content

        # === Step 3: Execute the tool if the call is valid ===
        if tool_call and "action" in tool_call and "action_input" in tool_call:
            action_name = tool_call["action"]
            action_input = tool_call["action_input"]

            if action_name not in self.tools:
                return f"Error: The model tried to use a tool named '{action_name}' which does not exist."

            tool = self.tools[action_name]
            
            try:
                tool_output = tool.execute(action_input)
            except Exception as e:
                return f"An error occurred while executing the tool '{action_name}': {e}"
            
            # Add the tool's output to the conversation history for the next step
            messages.append(
                {"role": "user", "content": f"The tool '{action_name}' returned the following result:\n{tool_output}"}
            )
        else:
            return "Error: The model's response was not a valid tool call JSON object."

        # === Step 4: Second call to the LLM to act as the "Synthesizer" ===
        print("--- Agent thinking... (Synthesizer Call) ---")
        try:
            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7, # Higher temperature for more natural language
            )
            return final_response.choices[0].message.content

        except Exception as e:
            return f"An error occurred during the final API call: {e}"