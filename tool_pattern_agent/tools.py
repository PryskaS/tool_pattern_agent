from .tool import Tool

def simulated_search(query: str) -> str:
    """
    A simulated search function. In a real-world scenario, this would
    call a search engine API (e.g., Google, Bing, Tavily).
    """
    print(f"--- SIMULATING SEARCH for query: '{query}' ---")
    
    # Simulate finding different results based on the query
    if "latest trends in AI" in query.lower():
        return """
        Recent AI trends include the rise of multi-modal models like GPT-4o,
        the development of smaller, more efficient open-source models (SLMs),
        and a strong focus on AI agent architectures for autonomous task execution.
        """
    elif "who is the ceo of openai" in query.lower():
        return "Sam Altman is the CEO of OpenAI."
    else:
        return "Sorry, I couldn't find any information on that topic. Try asking about 'latest trends in AI' or 'who is the CEO of OpenAI'."

# Create an instance of the Tool for our agent to use
search_tool = Tool(
    name="search",
    description="Searches for up-to-date information on a given topic. Use this to answer questions about current events or specific facts.",
    function=simulated_search
)