from google.adk.agents import LlmAgent

from multi_agent_orchestrator.multi_agent_orchestrator.tools import get_user_id, get_user_data, update_user_data
# No longer need placeholders:
# def get_user_id(*args, **kwargs): pass
# def get_user_data(*args, **kwargs): pass
# def update_user_data(*args, **kwargs): pass

from .prompt import ONBOARDING_PROMPT

onboarding_agent = LlmAgent(
    name="OnboardingAgent",
    model="gemini-2.0-flash",
    description="Handles user onboarding.",
    instruction=ONBOARDING_PROMPT,
    tools=[
        get_user_id,
        get_user_data,
        update_user_data
    ],
    output_key="onboarding_state",
)
