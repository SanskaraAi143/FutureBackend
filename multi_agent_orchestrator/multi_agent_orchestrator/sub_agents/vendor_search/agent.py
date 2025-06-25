from google.adk.agents import LlmAgent
from .prompt import VENDOR_PROMPT

from multi_agent_orchestrator.tools import list_vendors, get_vendor_details
# No longer need placeholders
# def list_vendors(*args, **kwargs): pass # Placeholder
# def get_vendor_details(*args, **kwargs): pass # Placeholder

vendor_search_agent = LlmAgent(
    name="VendorSearchAgent",
    model="gemini-2.0-flash",
    description="Handles vendor search.",
    instruction=VENDOR_PROMPT,
    tools=[
        list_vendors,
        get_vendor_details
    ],
    output_key="vendor_search_state",
)
