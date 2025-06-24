import pytest
import asyncio
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

# Adjust import for budget_agent from its new location
from ..agent import budget_agent # Corrected relative import
# Placeholder for now:
# from google.adk.agents import LlmAgent
# BUDGET_PROMPT_PLACEHOLDER = "Test Budget Prompt"
# def add_budget_item_placeholder(*args, **kwargs): return {"status": "success", "data": {"id": "1"}}
# def get_budget_items_placeholder(*args, **kwargs): return [{"id": "1", "item_name": "Venue"}]
# def update_budget_item_placeholder(*args, **kwargs): return {"status": "success"}
# def delete_budget_item_placeholder(*args, **kwargs): return {"status": "success"}
# # Re-using placeholders from onboarding for user data tools for simplicity in this step
# def get_user_data_placeholder_budget(*args, **kwargs): return {"name": "Placeholder User", "preferences": {}}
# def update_user_data_placeholder_budget(*args, **kwargs): return {"status": "success"}


# budget_agent = LlmAgent(
#     name="PlaceholderBudgetAgent",
#     instruction=BUDGET_PROMPT_PLACEHOLDER,
#     tools=[
#         add_budget_item_placeholder,
#         get_budget_items_placeholder,
#         update_budget_item_placeholder,
#         delete_budget_item_placeholder,
#         get_user_data_placeholder_budget,
#         update_user_data_placeholder_budget,
#     ]
# )

@pytest.mark.asyncio
async def test_budget_agent_interaction(): # Renamed
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name="test_app_budget", user_id="test_user_ba", session_id="test_session_budget_interaction")
    runner = Runner(agent=budget_agent, app_name="test_app_budget", session_service=session_service)

    content = types.Content(role='user', parts=[types.Part(text="Set a budget for my wedding.")])
    responses = []
    async for event in runner.run_async(user_id="test_user_ba", session_id="test_session_budget_interaction", new_message=content):
        if event.is_final_response():
            if event.content and event.content.parts:
                responses.append(event.content.parts[0].text)
            elif event.actions and event.actions.escalate:
                responses.append(f"Agent escalated: {getattr(event, 'error_message', 'No message')}")

    assert responses, "Budget agent did not respond."
    # Add more specific assertions based on expected agent behavior

@pytest.mark.asyncio
async def test_budget_agent_invalid_input():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name="test_app_budget", user_id="test_user_ba_err", session_id="test_session_budget_invalid")
    runner = Runner(agent=budget_agent, app_name="test_app_budget", session_service=session_service)

    content = types.Content(role='user', parts=[types.Part(text="Set my budget to 'a lot'")]) # Invalid input
    responses = []
    async for event in runner.run_async(user_id="test_user_ba_err", session_id="test_session_budget_invalid", new_message=content):
        if event.is_final_response():
            if event.content and event.content.parts:
                responses.append(event.content.parts[0].text)
            elif event.actions and event.actions.escalate:
                responses.append(f"Agent escalated: {getattr(event, 'error_message', 'No message')}")

    assert responses, "Budget agent did not respond to invalid input."
    # Example assertion (depends on agent's error handling design)
    # assert any("error" in r.lower() or "invalid" in r.lower() for r in responses), \
    #        f"Expected error/invalid message not found in responses: {responses}"
