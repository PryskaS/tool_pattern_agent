from dataclasses import dataclass
from typing import Callable, Dict, Any

@dataclass
class Tool:
    """A dataclass to represent a tool the agent can use."""
    name: str
    description: str
    function: Callable[[str], str]

    def to_dict(self) -> Dict[str, Any]:
        """
        Returns a dictionary representation of the tool,
        formatted for the LLM to understand.
        """
        return {"name": self.name, "description": self.description}

    def execute(self, action_input: str) -> str:
        """Executes the tool's function with the given input."""
        return self.function(action_input)