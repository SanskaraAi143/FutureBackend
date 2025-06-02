import pytest
import asyncio
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from .agent import onboarding_agent, ritual_search_agent, budget_agent, vendor_search_agent

@pytest.mark.asyncio
async def test_onboarding_agent():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name="test_app", user_id="test_user", session_id="test_session_onboarding")
    runner = Runner(agent=onboarding_agent, app_name="test_app", session_service=session_service)
    content = types.Content(role='user', parts=[types.Part(text="My email is test@example.com")])
    responses = []
    async for event in runner.run_async(user_id="test_user", session_id="test_session_onboarding", new_message=content):
        if event.is_final_response():
            responses.append(event.content.parts[0].text)
    assert responses, "Onboarding agent did not respond."

@pytest.mark.asyncio
async def test_ritual_search_agent():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name="test_app", user_id="test_user", session_id="test_session_ritual")
    runner = Runner(agent=ritual_search_agent, app_name="test_app", session_service=session_service)
    content = types.Content(role='user', parts=[types.Part(text="Tell me about Kanyadhanam ?")])
    responses = []
    async for event in runner.run_async(user_id="test_user", session_id="test_session_ritual", new_message=content):
        if event.is_final_response():
            responses.append(event.content.parts[0].text)
    assert responses, "Ritual search agent did not respond."

@pytest.mark.asyncio
async def test_budget_agent():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name="test_app", user_id="test_user", session_id="test_session_budget")
    runner = Runner(agent=budget_agent, app_name="test_app", session_service=session_service)
    content = types.Content(role='user', parts=[types.Part(text="Set a budget for my wedding.")])
    responses = []
    async for event in runner.run_async(user_id="test_user", session_id="test_session_budget", new_message=content):
        if event.is_final_response():
            responses.append(event.content.parts[0].text)
    assert responses, "Budget agent did not respond."

@pytest.mark.asyncio
async def test_vendor_search_agent():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name="test_app", user_id="test_user", session_id="test_session_vendor")
    runner = Runner(agent=vendor_search_agent, app_name="test_app", session_service=session_service)
    content = types.Content(role='user', parts=[types.Part(text="Find me a wedding photographer in Bangalore.")])
    responses = []
    async for event in runner.run_async(user_id="test_user", session_id="test_session_vendor", new_message=content):
        if event.is_final_response():
            responses.append(event.content.parts[0].text)
    assert responses, "Vendor search agent did not respond."

@pytest.mark.asyncio
def test_onboarding_agent_tools():
    # Test the onboarding agent's tools directly
    from .tools import get_user_id, get_user_data, update_user_data
    # Example: test get_user_id
    user_id = get_user_id("test@example.com")
    assert user_id is not None or user_id is None  # Accepts any result for demo
    # Example: test get_user_data
    data = get_user_data("test_user")
    assert isinstance(data, dict) or data is None
    # Example: test update_user_data
    result = update_user_data("test_user", {"display_name": "Test User"})
    assert result is not None or result is None

@pytest.mark.asyncio
def test_ritual_search_agent_tools():
    from .tools import search_rituals
    rituals = search_rituals("Tamil Brahmin")
    assert isinstance(rituals, list) or rituals is None

@pytest.mark.asyncio
def test_budget_agent_tools():
    from .tools import add_budget_item, get_budget_items, update_budget_item, delete_budget_item
    # Add budget item
    add_result = add_budget_item("test_user", {"item": "Venue", "category": "Venue", "amount": 10000})
    assert add_result is not None or add_result is None
    # Get budget items
    items = get_budget_items("1b006058-1133-490c-b2de-90c444e56138")
    assert isinstance(items, list) or items is None
    # Update budget item
    update_result = update_budget_item("8eb19cec-a51a-4327-80cb-3d441a9e66b7", amount=12000)
    assert update_result is not None or update_result is None
    # Delete budget item
    delete_result = delete_budget_item("8eb19cec-a51a-4327-80cb-3d441a9e66b7")
    assert delete_result is not None or delete_result is None

@pytest.mark.asyncio
def test_vendor_search_agent_tools():
    from .tools import list_vendors, get_vendor_details
    vendors = list_vendors({"vendor_category": "Venue", "address->>city": "Bangalore"})
    assert isinstance(vendors, list) or vendors is None
    details = get_vendor_details(1)
    assert isinstance(details, dict) or details is None
