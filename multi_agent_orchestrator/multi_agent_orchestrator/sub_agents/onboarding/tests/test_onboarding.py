# Test cases for onboarding sub-agent

import pytest
import asyncio
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from multi_agent_orchestrator.multi_agent_orchestrator.sub_agents.onboarding.agent import onboarding_agent

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
