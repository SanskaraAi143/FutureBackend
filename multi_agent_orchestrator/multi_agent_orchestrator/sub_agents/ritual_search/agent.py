from .tools import search_rituals
from google.adk.agents import LlmAgent
from .prompt import RITUAL_PROMPT

# Only define the agent, do not import or instantiate orchestrator or other sub-agents

ritual_search_agent = LlmAgent(
    name="RitualSearchAgent",
    model="gemini-2.0-flash",
    description="Handles ritual search.",
    instruction=RITUAL_PROMPT,
    tools=[search_rituals],
    output_key="ritual_search_state",
)
