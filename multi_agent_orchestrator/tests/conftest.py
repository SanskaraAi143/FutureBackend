import pytest
from dotenv import load_dotenv
import os

@pytest.fixture(scope="session", autouse=True)
def load_env_vars():
    """Loads environment variables from .env file before any tests run."""
    print("Attempting to load .env file from conftest.py...")
    # .env is in the project root. __file__ is multi_agent_orchestrator/tests/conftest.py
    # Project root is two levels up from this conftest.py
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
    loaded = load_dotenv(dotenv_path)
    if loaded:
        print(f".env file loaded successfully from: {dotenv_path}")
        # Optionally print some of the loaded vars for verification (be careful with sensitive data)
        # print(f"  GOOGLE_API_KEY loaded: {bool(os.getenv('GOOGLE_API_KEY'))}")
        # print(f"  SUPABASE_ACCESS_TOKEN loaded: {bool(os.getenv('SUPABASE_ACCESS_TOKEN'))}")
        # print(f"  ASTRA_API_ENDPOINT loaded: {bool(os.getenv('ASTRA_API_ENDPOINT'))}")
        # print(f"  SUPABASE_URL loaded: {bool(os.getenv('SUPABASE_URL'))}")
    else:
        print(f"Warning: .env file not found at {dotenv_path} or not loaded by conftest.py. Tests might fail if they rely on .env variables.")

# This fixture will run once per session automatically due to autouse=True.
# It ensures that when config.py (or any other module) calls os.getenv(),
# the variables from .env are already loaded into the environment.
