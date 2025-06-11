import os
import logging
import uvicorn
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Get the directory where main.py is located
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
logging.info(f"Agent directory: {AGENT_DIR}")
# Example session DB URL (e.g., SQLite)
SESSION_DB_URL = os.getenv("SESSION_DB_URL", "sqlite:///./sessions.db")
# Allow CORS for localhost:8030
ALLOWED_ORIGINS_STR = os.getenv("ALLOWED_ORIGINS", "http://localhost:8030,https://sanskaraai.com")
# Set web=True if you intend to serve a web interface, False otherwise
SERVE_WEB_INTERFACE_STR = os.getenv("SERVE_WEB_INTERFACE", "True")

# Call the function to get the FastAPI app instance
app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    session_db_url=SESSION_DB_URL,
    allow_origins=ALLOWED_ORIGINS,
    web=SERVE_WEB_INTERFACE,
)
except Exception as e:
    logging.error(f"Failed to initialize FastAPI app: {e}", exc_info=True)
    raise  # Re-raise the exception to prevent the server from starting

# Function to add custom FastAPI configuration
def configure_fastapi(app: FastAPI):
    @app.get("/hello")
    async def read_root():
        return {"Hello": "World"}

# Configure the FastAPI app
configure_fastapi(app)

if __name__ == "__main__":
    # Use the PORT environment variable provided by Cloud Run, defaulting to 8080
    PORT = int(os.environ.get("PORT", 8000))
    try:
        uvicorn.run(app, host="0.0.0.0", port=PORT)
    except Exception as e:
        logging.error(f"Failed to start Uvicorn server: {e}", exc_info=True)
        # Optionally, you might want to exit the program if the server fails to start
        # sys.exit(1)
        raise
