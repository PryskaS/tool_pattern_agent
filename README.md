# Tool Agent Service 🤖🛠️

[![Code Quality and Tests](https://github.com/PRYSKAS/TOOL_PATTERN_AGENT/actions/workflows/ci.yml/badge.svg)](https://github.com/PRYSKAS/TOOL_PATTERN_AGENT/actions)

An AI microservice that implements the **Tool Use Pattern**. This agent can analyze a user's question, select the appropriate tool from an available set, execute it to fetch external information, and then synthesize an informed final answer.

This project demonstrates how to give an LLM "arms and hands," enabling it to interact with external systems and access real-time data—a critical capability for building business-oriented AI applications.

## 🧠 Core Concept: The "Router & Synthesizer" Agent

A standalone LLM is a brain with static knowledge. The Tool Use Pattern transforms it into a dynamic agent through a two-step reasoning loop:

1.  **Routing:** In the first LLM call, the model acts as a "router." It analyzes the user's prompt and the list of available tools, then decides if a tool is necessary. If so, it returns a structured JSON object with the `action` to perform and the `action_input` for that tool.
2.  **Synthesis:** After the tool is executed, the LLM is called a second time. Now acting as a "synthesizer," it receives the original prompt, the tool that was used, and the raw output from the tool. Its task is to synthesize all this information into a final, cohesive, natural-language response for the user.

This **Decide -> Act -> Synthesize** loop is the foundation for creating capable and autonomous AI agents.

## 🚀 Engineering & MLOps Highlights

This project builds upon the engineering foundation of the previous service, proving the efficiency of a reusable architecture.

* **Extensible Architecture:** The agent is designed to receive a list of tools via dependency injection, making it trivial to add new capabilities without altering the agent's core logic.
* **Microservice API:** The logic is served via **FastAPI**, with robust data validation enforced by **Pydantic**.
* **Docker Containerization:** Ensures a 100% reproducible and isolated deployment environment.
* **Unit Testing:** The agent's decision-making flow (with and without tool use) is validated with **Pytest** and **pytest-mock**, ensuring the orchestrator's logic is robust.
* **Automated CI/CD:** The **GitHub Actions** pipeline validates code quality (`Ruff`) and correctness (`Pytest`) on every push, guaranteeing continuous project integrity.

## 🏗️ Service Architecture

```mermaid
graph TD
    A[User] -->|HTTP Request| B(FastAPI Service);
    B -->|prompt| C{ToolAgent};
    C -->|1. Which tool to use? (Router Call)| D[OpenAI API];
    D -->|Action JSON| C;
    C -->|2. Execute Tool| E(Search Tool);
    E -->|Search Result| C;
    C -->|3. Synthesize answer (Synthesizer Call)| D;
    D -->|Final Answer| C;
    C -->|Complete Response| B;
    B -->|JSON Response| A;
```

## 🏁 Getting Started

### Prerequisites
* Git
* Python 3.9+
* Docker Desktop (running)

### 1. Running Locally (for Development)

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/PRYSKAS/TOOL_PATTERN_AGENT.git](https://github.com/PRYSKAS/TOOL_PATTERN_AGENT.git)
    cd TOOL_PATTERN_AGENT
    ```

2.  **Set up the environment:**
    * Create a `.env` file from the example: `copy .env.example .env` (on Windows) or `cp .env.example .env` (on Unix/macOS).
    * Add your `OPENAI_API_KEY` to the new `.env` file.

3.  **Install dependencies and the package:**
    ```bash
    pip install -r requirements.txt
    pip install -e .
    ```

4.  **Run tests:**
    ```bash
    pytest
    ```

5.  **Start the API server:**
    ```bash
    uvicorn main:app --reload --port 8001
    ```
    Access the interactive documentation at `http://127.0.0.1:8001/docs`.

### 2. Running with Docker (Production Mode)

1.  **Build the Docker image:**
    ```bash
    docker build -t tool-agent-service .
    ```

2.  **Run the container:**
    ```bash
    docker run -d -p 8001:8001 --env-file .env --name tool-agent tool-agent-service
    ```
    Access the API at `http://127.0.0.1:8001/docs`.

## 📡 API Endpoint

### `POST /run`

Executes the agent's full reasoning cycle to answer a question.

**Request Body:**
```json
{
  "prompt": "What are the latest trends in AI?"
}
```

**Success Response (200 OK):**
```json
{
  "original_prompt": "What are the latest trends in AI?",
  "final_answer": "Recent AI trends include the rise of multi-modal models like GPT-4o, the development of smaller, more efficient open-source models (SLMs), and a strong focus on AI agent architectures for autonomous task execution."
}
```