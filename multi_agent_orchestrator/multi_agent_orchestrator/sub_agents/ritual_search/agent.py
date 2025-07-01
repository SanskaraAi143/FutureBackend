from google.adk.agents import LlmAgent
from .prompt import RITUAL_PROMPT

from ...tools import search_rituals # Relative import for tools
# No longer need placeholder:
# def search_rituals(*args, **kwargs): pass # Placeholder

ritual_search_agent = LlmAgent(
    name="RitualSearchAgent",
    model="gemini-2.0-flash-exp-image-generation",
    description="Handles ritual search.",
    instruction=RITUAL_PROMPT,
    tools=[
        search_rituals
    ],
    output_key="ritual_search_state",
)

