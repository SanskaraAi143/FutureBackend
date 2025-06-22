# Add this to requirements.txt if not present:
# google-generativeai>=0.5.0

import os
import google.generativeai as genai
import asyncio
from sanskara.agent import root_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import base64
import logging

logging.basicConfig(level=logging.INFO)

# Set up Gemini API key from environment
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Session and runner setup (reuse for all requests)
APP_NAME = "sanskara_ai"
USER_ID = "ws_user"
SESSION_ID = "ws_session"
session_service = InMemorySessionService()
runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service
)

async def adk_streaming_response(user_text, user_audio=None):
    logging.info(f"[ADK Streaming] Received user_text: {user_text}")
    if user_audio:
        logging.info(f"[ADK Streaming] Received user_audio: {len(user_audio)} bytes")
        logging.warning("[ADK Streaming] Audio input received, but audio is not supported by the current ADK version. Only text will be processed.")
    # Ensure session exists
    try:
        await session_service.get_session(APP_NAME, USER_ID, SESSION_ID)
        logging.info("[ADK Streaming] Session found.")
    except Exception:
        await session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID
        )
        logging.info("[ADK Streaming] Session created.")
    # Build ADK Content
    parts = []
    if user_text:
        parts.append(types.Part(text=user_text))
    logging.info(f"[ADK Streaming] Parts for Content: {parts}")
    content = types.Content(role='user', parts=parts)
    # Stream events from ADK agent
    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content):
        logging.info(f"[ADK Streaming] Event: is_final={event.is_final_response()}, content={getattr(event.content, 'parts', None)}")
        if event.content and event.content.parts:
            yield event.content.parts[0].text, event.is_final_response()
        elif event.is_final_response():
            yield "", True

async def gemini_multimodal_streaming(user_text=None, user_audio=None):
    import google.generativeai as genai
    import base64
    # Set up Gemini API key from environment
    GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    parts = []
    if user_text:
        parts.append({"text": user_text})
    if user_audio:
        # Gemini expects audio as bytes, not base64 string
        parts.append({"audio": user_audio})
    # Streaming Gemini response
    response = model.generate_content(parts, stream=True)
    async for chunk in response:
        if hasattr(chunk, 'text') and chunk.text:
            yield chunk.text, False
    yield "", True
