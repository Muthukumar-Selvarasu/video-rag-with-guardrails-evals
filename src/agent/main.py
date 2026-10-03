"""Main entrypoint initializing the Google ADK LlmAgent for Video RAG."""

import os
import sys
import logging
from typing import Any, Dict, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configure logging for CI/CD and observability
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
)
logger = logging.getLogger("video_rag_agent")

try:
    from google.adk.agents import LlmAgent
except ImportError:
    # Graceful fallback placeholder for pre-install / linting environments
    logger.warning("google-adk not found in current environment. Using placeholder LlmAgent.")

    class LlmAgent:  # type: ignore
        def __init__(self, name: str, model: str, description: str, instruction: str, tools: list):
            self.name = name
            self.model = model
            self.description = description
            self.instruction = instruction
            self.tools = tools

        def run(self, query: str) -> str:
            return f"[Agent: {self.name} | Model: {self.model}] Simulated response to: {query}"


from src.agent.tools import search_transcripts
from src.guardrails.router import GuardrailRouter


def create_video_rag_agent(
    model: Optional[str] = None,
    instructions: Optional[str] = None,
) -> LlmAgent:
    """Initialize and configure the production Google ADK Video RAG Agent.

    Args:
        model: Gemini model identifier (defaults to GEMINI_MODEL env var or gemini-2.0-flash-exp).
        instructions: System instructions for the agent.

    Returns:
        Configured LlmAgent instance.
    """
    model_name = model or os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
    default_instructions = (
        "You are an expert video transcript retrieval assistant. "
        "Your task is to answer user queries with high factual accuracy based on video transcripts. "
        "Strict Guidelines:\n"
        "1. Always invoke `search_transcripts` before answering questions.\n"
        "2. Ground your answers strictly in the retrieved transcript context.\n"
        "3. Include video titles, timestamps, or segment IDs when available.\n"
        "4. If the retrieved transcripts do not contain the answer, explicitly state "
        "'Based on the available video transcripts, I cannot find information to answer this question.'"
    )

    logger.info(f"Initializing Google ADK LlmAgent with model: {model_name}")

    agent = LlmAgent(
        name="video_transcript_rag_agent",
        model=model_name,
        description="Autonomous RAG agent specialized in searching and answering queries from video transcripts.",
        instruction=instructions or default_instructions,
        tools=[search_transcripts],
    )
    return agent


def run_pipeline(query: str, agent: Optional[LlmAgent] = None) -> Dict[str, Any]:
    """Execute the full query pipeline protected by runtime guardrails.

    Args:
        query: User input query.
        agent: Optional pre-configured LlmAgent instance.

    Returns:
        Structured result dictionary with execution status and response text.
    """
    active_agent = agent or create_video_rag_agent()
    router = GuardrailRouter()

    def agent_executor(prompt: str) -> str:
        if hasattr(active_agent, "run"):
            return active_agent.run(prompt)
        return str(active_agent)

    return router.process(query=query, agent_executor=agent_executor)


if __name__ == "__main__":
    test_query = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "What key topics were discussed in the machine learning keynote?"
    )
    print(f"Running Video RAG pipeline with query: '{test_query}'\n")

    result = run_pipeline(test_query)
    print(f"Pipeline Result Status: {result.get('success')}")
    print(f"Pipeline Response:\n{result.get('response')}")
