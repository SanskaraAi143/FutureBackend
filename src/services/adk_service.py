# src/services/adk_service.py
"""
Service layer for common Google ADK (Agent Development Kit) patterns and utilities.
This can include abstractions for session management, event handling,
or wrappers around ADK functionalities to simplify agent code.
"""
from typing import Any, Dict, Optional, AsyncGenerator
from google.adk.runners import Runner
from google.adk.sessions import Session, BaseSessionService, InMemorySessionService
from google.adk.agents import Agent
from google.adk.events import Event
from google.genai import types as GoogleGenAITypes # For message content types

from config.settings import APP_NAME, DEFAULT_USER_ID, DEFAULT_SESSION_ID

# This service might not have a persistent client like DB services,
# but rather utility functions or classes that operate on ADK objects.

class ADKService:
    """
    Provides helper methods and common patterns for working with the Google ADK.
    """
    def __init__(self, session_service: Optional[BaseSessionService] = None, app_name: str = APP_NAME):
        self.session_service = session_service if session_service else InMemorySessionService()
        self.app_name = app_name
        print(f"[ADKService] Initialized with app_name: {self.app_name}")

    async def get_or_create_session(self, user_id: str = DEFAULT_USER_ID, session_id: Optional[str] = None) -> Session:
        """
        Retrieves an existing session or creates a new one for the given user and session ID.
        If session_id is None, a new unique session might be created by the session_service.
        """
        # Some session services might require session_id to be provided for creation.
        # InMemorySessionService can create one if session_id is None or use the provided one.
        # This logic might need adjustment based on the specific session_service behavior.

        _session_id = session_id or DEFAULT_SESSION_ID # Fallback, though typically ADK might generate one

        try:
            # Try to get existing session - behavior depends on BaseSessionService implementation
            # For InMemorySessionService, get_session usually expects an exact match.
            session = await self.session_service.get_session(
                app_name=self.app_name, user_id=user_id, session_id=_session_id
            )
            if session:
                print(f"[ADKService] Retrieved existing session: User='{user_id}', Session='{session.session_id}'")
                return session
        except Exception as e: # Catch specific "not found" errors if possible
            print(f"[ADKService] Could not retrieve session (User='{user_id}', Session='{_session_id}'): {e}. Attempting to create.")

        # If get_session fails or returns None, create a new one
        session = await self.session_service.create_session(
            app_name=self.app_name,
            user_id=user_id,
            session_id=_session_id # Pass it along; InMemorySessionService will use it or create if it was None initially
        )
        print(f"[ADKService] Created new session: User='{user_id}', Session='{session.session_id}'")
        return session

    async def run_agent_interaction(
        self,
        agent: Agent,
        user_id: str,
        session_id: str,
        query: str,
        runner_app_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Runs a single interaction with an agent and streams events, returning the final response.

        Args:
            agent (Agent): The ADK agent to interact with.
            user_id (str): The ID of the user.
            session_id (str): The ID of the session.
            query (str): The user's input/query to the agent.
            runner_app_name (Optional[str]): App name for the runner, defaults to ADKService's app_name.

        Returns:
            Dict[str, Any]: A dictionary containing the final response text and potentially other details.
                            Example: {"final_response_text": "...", "error": None} or {"error": "..."}
        """
        runner = Runner(
            agent=agent,
            app_name=runner_app_name or self.app_name,
            session_service=self.session_service
        )
        print(f"[ADKService] Running agent '{agent.name}' for query: '{query[:50]}...'")

        message_content = GoogleGenAITypes.Content(role='user', parts=[GoogleGenAITypes.Part(text=query)])

        final_response_text = "Agent did not produce a final response."
        error_message = None

        try:
            async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=message_content):
                # Basic event logging (can be expanded)
                # print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}")
                if event.is_final_response():
                    if event.content and event.content.parts:
                        final_response_text = event.content.parts[0].text
                    elif event.actions and event.actions.escalate and hasattr(event.actions.escalate, "error_message"):
                        # This path for escalation might need refinement based on actual escalate event structure
                        final_response_text = f"Agent escalated: {getattr(event.actions.escalate, 'error_message', 'No specific message.')}"
                        error_message = final_response_text # Treat escalation as an error for this simplified return
                    break # Found final response

            updated_session = await self.session_service.get_session(runner_app_name or self.app_name, user_id, session_id)
            print(f"[ADKService] Agent run completed. Session state example: {str(updated_session.state)[:100]}...")

            return {"final_response_text": final_response_text, "error": error_message, "session_state": updated_session.state}

        except Exception as e:
            print(f"[ADKService] Exception during agent run: {e}")
            return {"final_response_text": None, "error": str(e)}

    # Potentially add methods for:
    # - Handling common ADK errors or error patterns.
    # - Managing ADK-specific session state transformations if needed.
    # - Abstracting pagination if tools interact with paginated Google services via ADK.

if __name__ == "__main__":
    # Example usage (for testing this module directly)
    async def _test_service():
        print("Testing ADK Service...")
        # This test requires a mock or simple agent to be defined.
        from google.adk.agents import LlmAgent

        # Define a very simple mock agent for testing
        mock_llm_agent = LlmAgent(
            name="MockEchoAgent",
            model="gemini-1.5-flash", # Actual model won't be hit if prompt is simple enough or mocked
            instruction="You are an echo agent. Repeat the user's message.",
            # No tools needed for this simple echo
        )

        adk_service_instance = ADKService()

        user_id = "test_user_adk_service"
        session_id_val = "test_session_adk_service" # Provide a session_id

        # Test session creation/retrieval
        session = await adk_service_instance.get_or_create_session(user_id, session_id_val)
        assert session is not None
        assert session.user_id == user_id
        assert session.session_id == session_id_val # For InMemorySessionService, it should use the provided one
        print(f"Session test passed: {session.session_id}")

        # Test agent interaction
        # interaction_result = await adk_service_instance.run_agent_interaction(
        #     agent=mock_llm_agent,
        #     user_id=user_id,
        #     session_id=session.session_id,
        #     query="Hello, Echo!"
        # )
        # print(f"Agent interaction result: {interaction_result}")
        # if interaction_result and not interaction_result.get("error"):
        #     assert "Hello, Echo!" in interaction_result.get("final_response_text", "") # LLM might add fluff
        #     print("Agent interaction test seemed okay (check LLM output).")
        # else:
        #     print(f"Agent interaction test failed or had an error: {interaction_result.get('error')}")
        print("To run full agent interaction tests, uncomment and ensure GOOGLE_API_KEY is set for the LLM.")

    import asyncio
    # asyncio.run(_test_service()) # Commented out for automated runs.
