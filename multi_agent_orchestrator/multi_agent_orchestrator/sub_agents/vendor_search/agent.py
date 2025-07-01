from google.adk.agents import LlmAgent
from .prompt import VENDOR_PROMPT

from ...tools.vendor_tools import get_vendor_reviews,check_vendor_availability,list_vendors,search_vendors,update_vendor_status # Relative import for tools
# No longer need placeholders
# def list_vendors(*args, **kwargs): pass # Placeholder
# def get_vendor_details(*args, **kwargs): pass # Placeholder

vendor_search_agent = LlmAgent(
    name="VendorSearchAgent",
    model="gemini-2.0-flash-exp-image-generation",
    description="Handles vendor search.",
    instruction=VENDOR_PROMPT,
    tools=[
        list_vendors,
        get_vendor_reviews,
        check_vendor_availability,
        search_vendors,
        update_vendor_status
    ],
    output_key="vendor_search_state",
)

