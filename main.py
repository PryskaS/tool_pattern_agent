# in main.py
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# --- Import our new agent's core logic and tools ---
from tool_pattern_agent.tool_agent import ToolAgent
from tool_pattern_agent.tools import search_tool

# --- Load Environment Variables ---
load_dotenv()

# --- Configure Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- API Contract (Pydantic Models) ---
class RunRequest(BaseModel):
    prompt: str = Field(
        ...,
        description="The user's question for the agent.",
        example="What are the latest trends in AI?"
    )

class RunResponse(BaseModel):
    original_prompt: str
    final_answer: str

# --- FastAPI Application Setup ---
app = FastAPI(
    title="Tool Agent Service",
    description="An API to access an AI agent that can use tools to answer questions.",
    version="1.0.0"
)

# --- API Endpoints ---
@app.get("/health", tags=["Monitoring"])
def health_check():
    """Checks if the service is running."""
    return {"status": "ok"}

@app.post("/run", response_model=RunResponse, tags=["Agent Logic"])
def execute_agent_run(request: RunRequest):
    """
    Executes the ToolAgent to get an answer, potentially using tools.
    """
    try:
        logger.info(f"Received request for prompt: '{request.prompt[:50]}...'")
        
        # Instantiate the agent and inject its dependencies (the tools).
        agent = ToolAgent(tools=[search_tool])
        
        final_answer = agent.run(request.prompt)

        logger.info("Successfully completed agent run.")
        return RunResponse(
            original_prompt=request.prompt,
            final_answer=final_answer
        )
    except Exception as e:
        logger.exception("An unhandled exception occurred during agent run.")
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")