import asyncio
import os
from dotenv import load_dotenv
from google.genai import types # For constructing messages

# Import the main orchestrator agent and session services
from multi_agent_orchestrator.agent import OrchestratorAgent # Corrected path
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
# Sub-agents are now imported by OrchestratorAgent itself.

# --- No longer need Temporary Placeholders for Agents ---
# from google.adk.agents import LlmAgent (OrchestratorAgent is an LlmAgent)

async def run_example():
    load_dotenv() # Load .env from project root

    # --- Session Management ---
    session_service = InMemorySessionService()
    APP_NAME = os.getenv("ADK_APP_NAME", "sanskara_ai_orchestrator") # Example App Name
    USER_ID = "example_user_001"
    SESSION_ID = await session_service.generate_session_id(app_name=APP_NAME, user_id=USER_ID)

    # Create session explicitly if your ADK version requires it or for clarity
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
        initial_state={"example_initial_state_key": "example_value"} # Optional initial state
    )
    print(f"Session created/ensured: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")

    # --- Runner ---
    runner = Runner(
        agent=OrchestratorAgent, # Use the imported actual agent
        app_name=APP_NAME,
        session_service=session_service
    )
    print(f"Runner created for agent '{runner.agent.name}'")

    # Verify API key is loaded (important for LLM agents)
    google_api_key = os.getenv('GOOGLE_API_KEY')
    if not google_api_key:
        print("WARNING: GOOGLE_API_KEY environment variable is not set. LLM calls will likely fail.")
    else:
        print(f"GOOGLE_API_KEY first 5 chars: {google_api_key[:5]}...")


    # Example conversation flow
    messages_to_send = [
        'Hi',
        # 'kpuneeth714@gmail.com', # Example email for onboarding
        # 'confirm',
        # 'what is kanyadhanam ?'
    ]

    for message_text in messages_to_send:
        print(f"\n>>> User Query: {message_text}")
        # Construct the message using google.genai.types.Content
        user_message = types.Content(role='user', parts=[types.Part(text=message_text)])

        final_response_text = "Agent did not produce a final response or stream ended."
        try:
            async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=user_message):
                # print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")
                if event.is_final_response():
                    if event.content and event.content.parts:
                        final_response_text = event.content.parts[0].text
                    elif event.actions and event.actions.escalate: # Check for escalation
                        final_response_text = f"Agent escalated: {getattr(event, 'error_message', 'No specific error message provided.')}"
                    # No break here, allow loop to finish in case of multiple final events (though unusual for simple run_async)

            # After processing all events for this message:
            print(f"<<< Agent Final Response: {final_response_text}")

            # Optionally, retrieve and print session state after each interaction
            # updated_session = await session_service.get_session(APP_NAME, USER_ID, SESSION_ID)
            # print(f"    Session State after response: {updated_session.state}")

        except Exception as e:
            print(f"An error occurred while running the agent: {e}")
            import traceback
            traceback.print_exc()
            break # Stop processing further messages if an error occurs

    print("\nExample agent run completed.")

if __name__ == "__main__":
    # Ensure the event loop is managed correctly for async execution
    # In Python 3.7+ asyncio.run() is preferred
    try:
        asyncio.run(run_example())
    except RuntimeError as e:
        if str(e) == "asyncio.run() cannot be called from a running event loop":
            # This can happen if run in an environment that already has a loop (e.g. Jupyter)
            # Fallback for such cases, though direct script execution should use asyncio.run()
            loop = asyncio.get_event_loop()
            if loop.is_running():
                print("Asyncio loop already running, creating task.")
                task = loop.create_task(run_example())
                # In a script, you might await task here if this __main__ was async itself,
                # but for a synchronous __main__ calling an async function, this is tricky.
                # The initial asyncio.run() is generally the correct pattern for scripts.
            else:
                raise # Re-raise if loop isn't running but run() failed for other reasons
        else:
            raise # Re-raise other RuntimeError
    except KeyboardInterrupt:
        print("\nExample run interrupted by user.")
    finally:
        print("Exiting example script.")
