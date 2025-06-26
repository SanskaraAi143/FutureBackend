from multi_agent_orchestrator.config import supabase, astra_db # Corrected for flattened structure
from astrapy import DataAPIClient # Keep for direct client use if needed, or remove if astra_db from config is sufficient
import os
from dotenv import load_dotenv

# Load .env from the root directory, especially if running this script directly
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)


# Test Supabase connection
try:
    if supabase:
        user_response = supabase.table("vendors").select("*").limit(2).execute()
        print("Supabase connection successful. Sample vendor data:", user_response.data)
    else:
        print("Supabase client not initialized in config.")
except Exception as e:
    print("Supabase connection failed:", e)

# Test Astra DB connection using ritual vector search
try:
    if astra_db:
        ritual_data_collection = astra_db.get_collection("ritual_data")
        question = "Describe the Haldi ceremony"

        # Simplified find, actual query might depend on AstraPy version and setup
        # The original query used projection={"$vectorize": True}, sort={"$vectorize": question}
        # This implies the DB handles vectorization of the 'question' string.
        results_cursor = ritual_data_collection.find(
            sort={"$vectorize": question},
            limit=3
            # projection might not be needed if default includes text fields
            # projection={"$vectorize": True} # This was in original, purpose might be specific
        )

        contexts = [doc for doc in results_cursor.get("data", {}).get("documents", [])] if results_cursor and results_cursor.get("data") else []

        if not contexts and results_cursor.get("errors"):
            print(f"Astra DB query failed: {results_cursor.get('errors')}")
        elif contexts:
            print("Astra DB ritual vector search successful. Sample context:", contexts)
        else:
            print("Astra DB query successful but no documents found for the test query.")

    else:
        print("Astra DB client not initialized in config. Skipping Astra DB test.")
except Exception as e:
    print(f"Astra DB connection or ritual search failed: {e}")
    import traceback
    traceback.print_exc()
