# Vendor Search Sub-Agent
# Core logic for vendor search agent

from .tools import list_vendors, get_vendor_details
from google.adk.agents import LlmAgent
from .prompt import VENDOR_PROMPT

# Only define the agent, do not import or instantiate orchestrator or other sub-agents

vendor_search_agent = LlmAgent(
    name="VendorSearchAgent",
    model="gemini-2.0-flash",
    description="Handles vendor search.",
    instruction=VENDOR_PROMPT,
    tools=[list_vendors, get_vendor_details],
    output_key="vendor_search_state",
)
