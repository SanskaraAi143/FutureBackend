# Utility for loading environment variables and credentials
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
ASTRA_DB_ID = os.getenv("ASTRA_DB_ID")
ASTRA_DB_REGION = os.getenv("ASTRA_DB_REGION")
ASTRA_DB_APPLICATION_TOKEN = os.getenv("ASTRA_DB_APPLICATION_TOKEN")

# Add more as needed for Google ADK, etc.

# Astra DB and Supabase connection utilities
from astrapy import DataAPIClient
from supabase import create_client, Client

# Astra DB setup
ASTRA_API_TOKEN = os.getenv("ASTRA_API_TOKEN")
ASTRA_API_ENDPOINT = os.getenv("ASTRA_API_ENDPOINT")

astra_client = DataAPIClient(ASTRA_API_TOKEN)
astra_db = astra_client.get_database_by_api_endpoint(ASTRA_API_ENDPOINT)

# Supabase setup (using correct URL and key, no DATABASE_URL needed)
SUPABASE_URL = os.getenv("SUPABASE_URL") 
SUPABASE_KEY = os.getenv("SUPABASE_KEY") 
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ToolContext for ADK tools (if needed)
# tool_context = ToolContext()  # Removed: requires invocation_context, not needed for connection setup

# Add more utility functions as needed for CRUD, search, etc.
# Example: def get_user(user_id): ...
# Example: def search_rituals(query): ...
