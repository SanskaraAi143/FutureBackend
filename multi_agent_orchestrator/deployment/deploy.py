import os
import logging
import uvicorn
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app
import json
import google.generativeai as genai # Corrected import
from google.genai.types import Content,Part,Blob
from google.adk.runners import Runner, InMemoryRunner
from google.adk.sessions import InMemorySessionService
from google.adk.agents import Agent, LiveRequestQueue
from google.adk.agents.run_config import RunConfig

from fastapi import WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import base64
from multi_agent_orchestrator.agent import root_agent # Import the main orchestrator agent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# AGENT_DIR should point to the main Python package containing the agents.
# deploy.py is in multi_agent_orchestrator/deployment/
# The main agent package is now one level up: multi_agent_orchestrator/
DEPLOY_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
AGENT_DIR = os.path.abspath(os.path.join(DEPLOY_FILE_DIR, '..'))
logging.info(f"Agent directory set for ADK discovery to: {AGENT_DIR}")

# Example session DB URL (e.g., SQLite)
# For SQLite, the path needs to be relative to where the app runs or an absolute path.
# If deploy.py is run from the repo root, './sessions.db' would be in the root.
# If run from multi_agent_orchestrator/, '../sessions.db' would be in the root.
# Using an environment variable is best practice.
SESSION_DB_URL = os.getenv("SESSION_DB_URL", "sqlite:///./sessions.db")
logging.info(f"Session DB URL: {SESSION_DB_URL}")

ALLOWED_ORIGINS_STR = os.getenv("ALLOWED_ORIGINS", "http://localhost:8030,https://sanskaraai.com")
try:
    ALLOWED_ORIGINS = json.loads(ALLOWED_ORIGINS_STR) if ALLOWED_ORIGINS_STR and ALLOWED_ORIGINS_STR.startswith('[') else \
                      [s.strip() for s in ALLOWED_ORIGINS_STR.split(',')] if ALLOWED_ORIGINS_STR else \
                      ["http://localhost:8030", "https://sanskaraai.com"] # Default if empty
except json.JSONDecodeError:
    ALLOWED_ORIGINS = [s.strip() for s in ALLOWED_ORIGINS_STR.split(',')]
logging.info(f"Allowed origins: {ALLOWED_ORIGINS}")

SERVE_WEB_INTERFACE_STR = os.getenv("SERVE_WEB_INTERFACE", "True")
SERVE_WEB_INTERFACE = SERVE_WEB_INTERFACE_STR.lower() == "true"
logging.info(f"Serve web interface: {SERVE_WEB_INTERFACE}")

app: FastAPI

try:
    # Ensure the directory for the SQLite database exists if it's a file path
    if SESSION_DB_URL.startswith("sqlite:///"):
        db_path_full = SESSION_DB_URL.replace("sqlite:///", "")
        # If db_path_full is relative, it's relative to CWD.
        # If absolute, it's used as is.
        # Let's ensure the path is made absolute from the project root (two levels above AGENT_DIR)
        # if it's a relative path starting with './'
        if db_path_full.startswith("./"):
            # AGENT_DIR is multi_agent_orchestrator/ (the container and package root)
            # SESSION_DB_URL = "sqlite:///./sessions.db" should resolve to multi_agent_orchestrator/sessions.db
            db_path_full = os.path.join(AGENT_DIR, db_path_full.lstrip("./"))

        db_dir = os.path.dirname(db_path_full)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            logging.info(f"Created directory for session DB: {db_dir}")
        # Update SESSION_DB_URL if we made it absolute for local file DB
        if db_path_full.startswith("/"): # It's an absolute path
            SESSION_DB_URL = f"sqlite:///{db_path_full}"


    logging.info(f"Attempting to initialize FastAPI app with agents_dir: {AGENT_DIR}")
    # Call the function to get the FastAPI app instance
    # ADK will search for agent definitions (e.g., OrchestratorAgent in agent.py)
    # within the AGENT_DIR.
    app = get_fast_api_app(
        agents_dir=AGENT_DIR, # Points to 'multi_agent_orchestrator'
        session_service_uri=SESSION_DB_URL,
        allow_origins=ALLOWED_ORIGINS,
        web=False, # Disable ADK's default web interface to serve custom client at root
    )
    logging.info("FastAPI app initialized successfully.")

except Exception as e:
    logging.error(f"Failed to initialize FastAPI app: {e}", exc_info=True)
    # Create a dummy app to prevent server from crashing if main module is run
    # Though `raise` is generally better to signal failure.
    app = FastAPI()
    @app.get("/")
    async def failed_app():
        return {"error": "FastAPI app initialization failed", "detail": str(e)}
    # raise # Re-raise the exception to prevent the server from starting in a bad state

# Function to add custom FastAPI configuration (if any)
def configure_custom_routes(current_app: FastAPI):
    @current_app.get("/hello-orchestrator") # Changed path to avoid conflict if web=True
    async def read_root():
        return {"message": "Hello from the Orchestrator's FastAPI app!"}

# Configure the FastAPI app
if app: # Only if app was initialized (or is the dummy error app)
    configure_custom_routes(app)

    # Initialize Gemini Live API clients
    # Assuming API key is available via environment variables or similar
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY")) # Corrected API key setting
    # stt_model = genai.get_default_speech_model() # Not used for text chat
    # tts_model = genai.get_default_text_to_speech_model() # Not used for text chat

    # Configure ADK Runner for the root_agent
    # Using InMemorySessionService for simplicity in this example.
    # For production, consider a persistent session service.
    session_service = InMemorySessionService()
    adk_runner = Runner(
        agent=root_agent,
        app_name="sanskara_ai_orchestrator", # A unique app name for this runner
        session_service=session_service
    )
    logging.info("ADK Runner initialized for orchestration.")

    @app.websocket("/ws/voice_chat/{user_id}")
    async def websocket_endpoint(websocket: WebSocket, user_id: str):
        await websocket.accept()
        logging.info(f"WebSocket accepted for user: {user_id}")

        # Create a Runner for the voice session
        voice_runner = InMemoryRunner(
            app_name="sanskara_ai_voice_orchestrator",
            agent=root_agent,
        )

        # Create a Session
        session = await voice_runner.session_service.create_session(
            app_name="sanskara_ai_voice_orchestrator",
            user_id=user_id,
        )

        # Set response modality to AUDIO
        run_config = RunConfig(response_modalities=["AUDIO"])

        # Create a LiveRequestQueue for this session
        live_request_queue = LiveRequestQueue()

        # Start agent session
        live_events = voice_runner.run_live(
            session=session,
            live_request_queue=live_request_queue,
            run_config=run_config,
        )

        async def agent_to_client_messaging():
            try:
                async for event in live_events:
                    if event.turn_complete or event.interrupted:
                        message = {
                            "turn_complete": event.turn_complete,
                            "interrupted": event.interrupted,
                        }
                        await websocket.send_text(json.dumps(message))
                        logging.info(f"[AGENT TO CLIENT]: {message}")
                        continue

                    part: Part = (
                        event.content and event.content.parts and event.content.parts[0]
                    )
                    if not part:
                        continue

                    is_audio = part.inline_data and part.inline_data.mime_type.startswith("audio/pcm")
                    if is_audio:
                        audio_data = part.inline_data and part.inline_data.data
                        if audio_data:
                            message = {
                                "mime_type": "audio/pcm",
                                "data": base64.b64encode(audio_data).decode("ascii")
                            }
                            await websocket.send_text(json.dumps(message))
                            logging.info(f"[AGENT TO CLIENT]: audio/pcm: {len(audio_data)} bytes.")
                            continue

                    if part.text and event.partial:
                        message = {
                            "mime_type": "text/plain",
                            "data": part.text
                        }
                        await websocket.send_text(json.dumps(message))
                        logging.info(f"[AGENT TO CLIENT]: text/plain: {message}")
            except Exception as e:
                logging.error(f"Error in agent_to_client_messaging: {e}", exc_info=True)

        async def client_to_agent_messaging():
            try:
                while True:
                    message_json = await websocket.receive_text()
                    message = json.loads(message_json)
                    mime_type = message["mime_type"]
                    data = message["data"]

                    if mime_type == "text/plain":
                        content = Content(role="user", parts=[Part.from_text(text=data)])
                        live_request_queue.send_content(content=content)
                        logging.info(f"[CLIENT TO AGENT]: {data}")
                    elif mime_type == "audio/pcm":
                        decoded_data = base64.b64decode(data)
                        live_request_queue.send_realtime(Blob(data=decoded_data, mime_type=mime_type))
                        logging.info(f"[CLIENT TO AGENT]: audio/pcm: {len(decoded_data)} bytes.")
                    else:
                        raise ValueError(f"Mime type not supported: {mime_type}")
            except WebSocketDisconnect:
                logging.info(f"WebSocket disconnected for user: {user_id}")
            except Exception as e:
                logging.error(f"Error receiving from WebSocket for user {user_id}: {e}", exc_info=True)
            finally:
                live_request_queue.close()
                logging.info(f"WebSocket connection closed and tasks cleaned up for user: {user_id}")

        agent_to_client_task = asyncio.create_task(agent_to_client_messaging())
        client_to_agent_task = asyncio.create_task(client_to_agent_messaging())

        await asyncio.gather(agent_to_client_task, client_to_agent_task)

    @app.websocket("/ws/text_chat/{user_id}")
    async def text_websocket_endpoint(websocket: WebSocket, user_id: str):
        await websocket.accept()
        logging.info(f"Text WebSocket accepted for user: {user_id}")

        session_id = f"{user_id}_text_session"  # Unique session ID for text chat
        await session_service.create_session(app_name=adk_runner.app_name, user_id=user_id, session_id=session_id)
        logging.info(f"ADK text session created for user {user_id}: {session_id}")

        try:
            while True:
                message = await websocket.receive_text()
                logging.info(f"Received text message from {user_id}: {message}")
                
                user_message = Content(role='user', parts=[Part(text=message)])
                adk_generator = adk_runner.run_async(user_id=user_id, session_id=session_id, new_message=user_message)
                try:
                    async for event in adk_generator:
                        if event.is_final_response():
                            if event.content and event.content.parts:
                                agent_response = event.content.parts[0].text
                                await websocket.send_text(agent_response)
                                logging.info(f"Sent text response to {user_id}: {agent_response}")
                            break
                        elif event.actions and event.actions.escalate:
                            logging.warning(f"Agent escalated: {getattr(event, 'error_message', 'No specific error message provided.')}")
                            await websocket.send_text("I'm sorry, I encountered an issue and need to escalate.")
                            break
                finally:
                    # Explicitly close the generator if it hasn't been exhausted
                    if hasattr(adk_generator, 'aclose'):
                        await adk_generator.aclose()
                    elif hasattr(adk_generator, 'close'):
                        adk_generator.close()

        except WebSocketDisconnect:
            logging.info(f"Text WebSocket disconnected for user: {user_id}")
        except Exception as e:
            logging.error(f"Error in text WebSocket for user {user_id}: {e}", exc_info=True)
        finally:
            logging.info(f"Text WebSocket connection closed for user: {user_id}")

    # Serve static files for the custom WebSocket client
    app.mount("/client", StaticFiles(directory=os.path.join(AGENT_DIR, "client/custom_ws_client")), name="client")

    @app.get("/")
    async def get_custom_client():
        with open(os.path.join(AGENT_DIR, "client/custom_ws_client/index.html")) as f:
            return HTMLResponse(f.read())

    # This allows running the app directly using: python multi_agent_orchestrator/deploy.py
    # The CWD should ideally be the repository root for consistent relative path handling (e.g. for .env, sessions.db)

    # To ensure .env is loaded from multi_agent_orchestrator/.env if this script is run directly:
    # AGENT_DIR is multi_agent_orchestrator/ (the new project package root)
    dotenv_path = os.path.join(AGENT_DIR, '.env')
    if os.path.exists(dotenv_path):
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=dotenv_path)
        logging.info(f".env loaded from: {dotenv_path}")
    else:
        logging.info(f".env not found at: {dotenv_path}, relying on environment variables.")


    PORT = int(os.environ.get("PORT", 8000)) # Default to 8000 if not set
    HOST = os.environ.get("HOST", "0.0.0.0")

    logging.info(f"Starting Uvicorn server on {HOST}:{PORT}")
    try:
        uvicorn.run(app, host=HOST, port=PORT)
    except Exception as e:
        logging.error(f"Failed to start Uvicorn server: {e}", exc_info=True)
        raise
