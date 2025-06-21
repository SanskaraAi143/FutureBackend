# config/settings.py
"""
Centralized configuration loading from environment variables.
This module loads environment variables from a .env file (if present)
and makes them available as Python constants.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file located at the project root
# Adjust the path if your .env file is located elsewhere.
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
load_dotenv(dotenv_path=dotenv_path)

# --- Core API Keys ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY") # If used

# --- Supabase Configuration ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_ACCESS_TOKEN = os.getenv("SUPABASE_ACCESS_TOKEN") # For MCP server
SUPABASE_PROJECT_ID = os.getenv("SUPABASE_PROJECT_ID") # Often needed for MCP tools

# --- Astra DB Configuration ---
ASTRA_API_TOKEN = os.getenv("ASTRA_API_TOKEN")
ASTRA_API_ENDPOINT = os.getenv("ASTRA_API_ENDPOINT")
ASTRA_DB_ID = os.getenv("ASTRA_DB_ID")
ASTRA_DB_REGION = os.getenv("ASTRA_DB_REGION")
# ASTRA_DB_APPLICATION_TOKEN = os.getenv("ASTRA_DB_APPLICATION_TOKEN") # Believed to be same as ASTRA_API_TOKEN

# --- Application Specific Settings ---
APP_NAME = os.getenv("APP_NAME", "FutureBackendApp")
DEFAULT_USER_ID = os.getenv("DEFAULT_USER_ID", "default_user")
DEFAULT_SESSION_ID = os.getenv("DEFAULT_SESSION_ID", "default_session")

# --- ADK / LLM Model Configuration ---
DEFAULT_LLM_MODEL = os.getenv("DEFAULT_LLM_MODEL", "gemini-1.5-flash")


# --- Validation (Optional but Recommended) ---
# You can add checks here to ensure critical variables are set
# For example:
# if not GOOGLE_API_KEY:
#     raise ValueError("Missing required environment variable: GOOGLE_API_KEY")
# if not SUPABASE_URL or not SUPABASE_KEY:
#     raise ValueError("Missing Supabase URL or Key.")
# if not ASTRA_API_TOKEN or not ASTRA_API_ENDPOINT:
#     raise ValueError("Missing Astra API Token or Endpoint.")

def print_loaded_config():
    """Prints a summary of the loaded configuration for debugging."""
    print("--- Configuration Summary ---")
    print(f"GOOGLE_API_KEY: {'Set' if GOOGLE_API_KEY else 'Not Set'}")
    print(f"SUPABASE_URL: {SUPABASE_URL}")
    print(f"ASTRA_API_ENDPOINT: {ASTRA_API_ENDPOINT}")
    print(f"DEFAULT_LLM_MODEL: {DEFAULT_LLM_MODEL}")
    print("---------------------------")

if __name__ == "__main__":
    # This allows you to run `python config/settings.py` to check your config
    print_loaded_config()
