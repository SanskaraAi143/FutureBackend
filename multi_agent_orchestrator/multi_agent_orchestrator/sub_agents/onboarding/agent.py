from google.adk.agents import LlmAgent

from ...tools import get_user_id, get_user_data, update_user_data # Relative import for tools
# No longer need placeholders:
# def get_user_id(*args, **kwargs): pass
# def get_user_data(*args, **kwargs): pass
# def update_user_data(*args, **kwargs): pass

from .prompt import ONBOARDING_PROMPT

onboarding_agent = LlmAgent(
    name="OnboardingAgent",
    model="gemini-2.0-flash-exp-image-generation",
    description="Handles user onboarding.",
    instruction=ONBOARDING_PROMPT,
    tools=[
        get_user_id,
        get_user_data,
        update_user_data
    ],
    output_key="onboarding_state",
)
