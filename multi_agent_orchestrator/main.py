import os
import logging
import uvicorn
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Get the directory where main.py is located
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
logging.info(f"Agent directory: {AGENT_DIR}")
# Example session DB URL (e.g., SQLite)
SESSION_DB_URL = os.getenv("SESSION_DB_URL", "sqlite:///./sessions.db")

# Allow CORS for localhost:8030
ALLOWED_ORIGINS_STR = os.getenv("ALLOWED_ORIGINS", "http://localhost:8030,https://sanskaraai.com")
try:
    ALLOWED_ORIGINS = json.loads(ALLOWED_ORIGINS_STR) if ALLOWED_ORIGINS_STR else ["http://localhost:8030","https://sanskaraai.com"]
except json.JSONDecodeError:
    ALLOWED_ORIGINS = [s.strip() for s in ALLOWED_ORIGINS_STR.split(',')]
# Set web=True if you intend to serve a web interface, False otherwise
SERVE_WEB_INTERFACE_STR = os.getenv("SERVE_WEB_INTERFACE", "True")
SERVE_WEB_INTERFACE = SERVE_WEB_INTERFACE_STR.lower() == "true"

try:
    # Ensure the directory for the database exists
    db_path = SESSION_DB_URL.replace("sqlite:///", "")
    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    # Call the function to get the FastAPI app instance, without root_agent (ADK will auto-discover agents)
    app: FastAPI = get_fast_api_app(
        agents_dir=AGENT_DIR,  # This is required by ADK
        session_service_uri=SESSION_DB_URL,
        allow_origins=ALLOWED_ORIGINS,
        web=SERVE_WEB_INTERFACE
    )
except Exception as e:
    logging.error(f"Failed to initialize FastAPI app: {e}", exc_info=True)
    raise  # Re-raise the exception to prevent the server from starting

def configure_fastapi(app: FastAPI):
    @app.get("/hello")
    async def read_root():
        return {"Hello": "World"}

configure_fastapi(app)

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 8000))
    try:
        uvicorn.run(app, host="0.0.0.0", port=PORT)
    except Exception as e:
        logging.error(f"Failed to start Uvicorn server: {e}", exc_info=True)
        raise
