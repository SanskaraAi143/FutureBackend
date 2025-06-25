# Onboarding Sub-Agent
# Core logic for onboarding agent

from .tools import get_user_id, get_user_data, update_user_data
from google.adk.agents import LlmAgent
from .prompt import ONBOARDING_PROMPT

# Only define the agent, do not import or instantiate orchestrator or other sub-agents

onboarding_agent = LlmAgent(
    name="OnboardingAgent",
    model="gemini-2.0-flash",
    description="Handles user onboarding.",
    instruction=ONBOARDING_PROMPT,
    tools=[get_user_id, get_user_data, update_user_data],
    output_key="onboarding_state",
)
