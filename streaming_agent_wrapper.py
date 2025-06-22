# streaming_agent_wrapper.py
# Async wrapper to call Sanskara AI agent from WebSocket server

import asyncio
from sanskara.agent import root_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# These can be made dynamic per user/session if needed
APP_NAME = "sanskara_ai"
USER_ID = "ws_user"
SESSION_ID = "ws_session"

# Session service and runner are created once per process for demo
session_service = InMemorySessionService()
runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service
)

async def ensure_session():
    # Try to get the session, create if not exists
    try:
        await session_service.get_session(APP_NAME, USER_ID, SESSION_ID)
    except Exception:
        await session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID
        )

async def stream_agent_response(user_text):
    await ensure_session()
    content = types.Content(role='user', parts=[types.Part(text=user_text)])
    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content):
        if event.content and event.content.parts:
            yield event.content.parts[0].text, event.is_final_response()
        elif event.is_final_response():
            yield "", True
