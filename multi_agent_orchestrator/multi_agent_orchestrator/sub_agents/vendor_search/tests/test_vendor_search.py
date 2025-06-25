# Test cases for vendor search sub-agent

import pytest
import asyncio
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from multi_agent_orchestrator.multi_agent_orchestrator.sub_agents.vendor_search.agent import vendor_search_agent

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
