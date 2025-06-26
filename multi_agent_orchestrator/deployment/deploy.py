import os
import logging
import uvicorn
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app
import json

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
        web=SERVE_WEB_INTERFACE,
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

if __name__ == "__main__":
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
