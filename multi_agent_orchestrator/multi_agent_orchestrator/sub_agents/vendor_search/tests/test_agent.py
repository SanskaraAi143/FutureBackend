import pytest
import asyncio
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

# Adjust import for vendor_search_agent from its new location
from ..agent import vendor_search_agent # Reverted to .. for correct relative path
from ..prompt import VENDOR_PROMPT # Reverted to .. for correct relative path
# Placeholder for now:
# from google.adk.agents import LlmAgent
# VENDOR_PROMPT_PLACEHOLDER = "Test Vendor Prompt"
# def list_vendors_placeholder(*args, **kwargs): return [{"name": "Placeholder Vendor"}]
# def get_vendor_details_placeholder(*args, **kwargs): return {"id": "1", "name": "Placeholder Vendor"}

# vendor_search_agent = LlmAgent(
#     name="PlaceholderVendorSearchAgent",
#     instruction=VENDOR_PROMPT_PLACEHOLDER,
#     tools=[list_vendors_placeholder, get_vendor_details_placeholder]
# )

@pytest.mark.asyncio
async def test_vendor_search_agent_interaction(): # Renamed
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name="test_app_vendor", user_id="test_user_vs", session_id="test_session_vendor_interaction")
    runner = Runner(agent=vendor_search_agent, app_name="test_app_vendor", session_service=session_service)

    content = types.Content(role='user', parts=[types.Part(text="Find me a wedding photographer in Bangalore.")])
    responses = []
    async for event in runner.run_async(user_id="test_user_vs", session_id="test_session_vendor_interaction", new_message=content):
        if event.is_final_response():
            if event.content and event.content.parts:
                responses.append(event.content.parts[0].text)
            elif event.actions and event.actions.escalate:
                responses.append(f"Agent escalated: {getattr(event, 'error_message', 'No message')}")

    assert responses, "Vendor search agent did not respond."
    # Add more specific assertions based on expected agent behavior

@pytest.mark.asyncio
async def test_vendor_search_agent_no_results():
    from google.adk.agents import LlmAgent # Import LlmAgent
    from ..prompt import VENDOR_PROMPT # Corrected indentation and path

    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name="test_app_vendor", user_id="test_user_vs_err", session_id="test_session_vendor_no_results")

    # Simulate a tool that returns no results for the "no results" agent behavior test
    def list_vendors_no_results_placeholder_local(*args, **kwargs): return []
    # Define a local placeholder for the other tool used by this test agent
    def get_vendor_details_placeholder_local(*args, **kwargs): return {"id": "any", "name": "Any Vendor Details"}

    no_results_vendor_agent = LlmAgent(
        name="NoResultsVendorSearchAgent", # More specific name
        model="gemini-1.0-pro", # Add a dummy/placeholder model
        instruction=VENDOR_PROMPT, # Use actual prompt
        tools=[list_vendors_no_results_placeholder_local, get_vendor_details_placeholder_local]
    )
    runner = Runner(agent=no_results_vendor_agent, app_name="test_app_vendor", session_service=session_service)

    content = types.Content(role='user', parts=[types.Part(text="Find me a unicorn vendor in Atlantis.")])
    responses = []
    async for event in runner.run_async(user_id="test_user_vs_err", session_id="test_session_vendor_no_results", new_message=content):
        if event.is_final_response():
            if event.content and event.content.parts:
                responses.append(event.content.parts[0].text)
            elif event.actions and event.actions.escalate:
                responses.append(f"Agent escalated: {getattr(event, 'error_message', 'No message')}")

    assert responses, "Vendor search agent did not respond to no-results case."
    # Example assertion (depends on agent's error handling design)
    # assert any("no vendor" in r.lower() or "not found" in r.lower() or "no results" in r.lower() for r in responses), \
    #        f"Expected 'no results' message not found in responses: {responses}"
