import pytest
import asyncio
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from multi_agent_orchestrator.multi_agent_orchestrator.agent import root_agent
from multi_agent_orchestrator.multi_agent_orchestrator.sub_agents.onboarding.agent import onboarding_agent
from multi_agent_orchestrator.multi_agent_orchestrator.sub_agents.ritual_search.agent import ritual_search_agent
from multi_agent_orchestrator.multi_agent_orchestrator.sub_agents.budget.agent import budget_agent
from multi_agent_orchestrator.multi_agent_orchestrator.sub_agents.vendor_search.agent import vendor_search_agent

# Test cases for orchestrator agent and tools

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
async def test_root_agent():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name="test_app", user_id="test_user", session_id="test_session_root")
    runner = Runner(agent=root_agent, app_name="test_app", session_service=session_service)
    content = types.Content(role='user', parts=[types.Part(text="I want to plan my wedding")])
    responses = []
    async for event in runner.run_async(user_id="test_user", session_id="test_session_root", new_message=content):
        if event.is_final_response():
            responses.append(event.content.parts[0].text)
    assert responses, "Root agent did not respond."
