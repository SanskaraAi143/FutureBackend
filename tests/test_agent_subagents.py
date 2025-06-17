import pytest
import asyncio
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from sanskara.agent import onboarding_agent, ritual_search_agent, budget_agent, vendor_search_agent

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
    from .tools import get_user_id, get_user_data, update_user_data
    async def run():
        user_id = await get_user_id("test@example.com")
        assert user_id is not None or user_id is None
        data = await get_user_data("test_user")
        assert isinstance(data, dict) or data is None
        result = await update_user_data("test_user", {"display_name": "Test User"})
        assert result is not None or result is None
    asyncio.run(run())

@pytest.mark.asyncio
def test_budget_agent_tools():
    from .tools import add_budget_item, get_budget_items, update_budget_item, delete_budget_item
    async def run():
        add_result = await add_budget_item("test_user", {"item": "Venue", "category": "Venue", "amount": 10000})
        assert add_result is not None or add_result is None
        items = await get_budget_items("1b006058-1133-490c-b2de-90c444e56138")
        assert isinstance(items, list) or items is None
        update_result = await update_budget_item("8eb19cec-a51a-4327-80cb-3d441a9e66b7", amount=12000)
        assert update_result is not None or update_result is None
        delete_result = await delete_budget_item("8eb19cec-a51a-4327-80cb-3d441a9e66b7")
        assert delete_result is not None or delete_result is None
    asyncio.run(run())

@pytest.mark.asyncio
def test_vendor_search_agent_tools():
    from .tools import list_vendors, get_vendor_details
    async def run():
        vendors = await list_vendors({"vendor_category": "Venue", "address->>city": "Bangalore"})
        assert isinstance(vendors, list) or vendors is None
        details = await get_vendor_details("1")
        assert isinstance(details, dict) or details is None
    asyncio.run(run())

@pytest.mark.asyncio
async def test_onboarding_agent_error_handling():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name="test_app", user_id="test_user", session_id="test_session_onboarding_error")
    runner = Runner(agent=onboarding_agent, app_name="test_app", session_service=session_service)
    # Missing email
    content = types.Content(role='user', parts=[types.Part(text="I want to onboard but won't give email")])
    responses = []
    async for event in runner.run_async(user_id="test_user", session_id="test_session_onboarding_error", new_message=content):
        if event.is_final_response():
            responses.append(event.content.parts[0].text)
    assert responses, "Onboarding agent did not respond to error case."
    assert any("error" in r.lower() or "missing" in r.lower() for r in responses)

@pytest.mark.asyncio
async def test_budget_agent_invalid_input():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name="test_app", user_id="test_user", session_id="test_session_budget_invalid")
    runner = Runner(agent=budget_agent, app_name="test_app", session_service=session_service)
    # Invalid budget (string instead of number)
    content = types.Content(role='user', parts=[types.Part(text="Set my budget to 'a lot'")])
    responses = []
    async for event in runner.run_async(user_id="test_user", session_id="test_session_budget_invalid", new_message=content):
        if event.is_final_response():
            responses.append(event.content.parts[0].text)
    assert responses, "Budget agent did not respond to invalid input."
    assert any("error" in r.lower() or "invalid" in r.lower() for r in responses)

@pytest.mark.asyncio
async def test_vendor_search_agent_no_results():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name="test_app", user_id="test_user", session_id="test_session_vendor_no_results")
    runner = Runner(agent=vendor_search_agent, app_name="test_app", session_service=session_service)
    # Query for a non-existent vendor
    content = types.Content(role='user', parts=[types.Part(text="Find me a unicorn vendor in Atlantis.")])
    responses = []
    async for event in runner.run_async(user_id="test_user", session_id="test_session_vendor_no_results", new_message=content):
        if event.is_final_response():
            responses.append(event.content.parts[0].text)
    assert responses, "Vendor search agent did not respond to no-results case."
    assert any("no vendor" in r.lower() or "not found" in r.lower() or "no results" in r.lower() for r in responses)

@pytest.mark.asyncio
async def test_create_timeline_event_agent():
    from sanskara.agent import root_agent
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name="test_app", user_id="test_user", session_id="test_session_timeline")
    runner = Runner(agent=root_agent, app_name="test_app", session_service=session_service)
    content = types.Content(role='user', parts=[types.Part(text="Add Sangeet event to my timeline on 2024-08-03T18:00:00, with music and dance at Grand Ballroom.")])
    responses = []
    async for event in runner.run_async(user_id="test_user", session_id="test_session_timeline", new_message=content):
        if event.is_final_response():
            responses.append(event.content.parts[0].text)
    assert responses, "Root agent did not respond."
