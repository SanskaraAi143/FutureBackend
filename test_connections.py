from config import supabase
from astrapy import DataAPIClient
import os

# Test Supabase connection
try:
    user_response = supabase.table("vendors").select("*").limit(2).execute()
    print("Supabase connection successful. Sample user:", user_response.data)
except Exception as e:
    print("Supabase connection failed:", e)

# Test Astra DB connection using ritual vector search
try:
    # Inline get_rituals_astra logic for test
    ASTRA_API_TOKEN = os.environ.get("ASTRA_API_TOKEN")
    ASTRA_API_ENDPOINT = os.environ.get("ASTRA_API_ENDPOINT")
    client = DataAPIClient(ASTRA_API_TOKEN)
    db = client.get_database_by_api_endpoint(ASTRA_API_ENDPOINT)
    ritual_data = db.get_collection("ritual_data")
    question = "Describe the Haldi ceremony"
    result = ritual_data.find(
        projection={"$vectorize": True},
        sort={"$vectorize": question},
    )
    contexts = []
    docs = 3
    for doc in result:
        if docs == 0:
            break
        contexts.append(doc)
        docs -= 1
    print("Astra DB ritual vector search successful. Sample context:", contexts)
except Exception as e:
    print("Astra DB connection or ritual search failed:", e)
