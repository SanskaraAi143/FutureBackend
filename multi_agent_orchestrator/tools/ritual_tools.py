from typing import List, Dict, Any, Optional

# Import astra_db from the new config location
from multi_agent_orchestrator.config import astra_db
# We might need to handle the case where astra_db is None if config loading fails,
# or ensure config is loaded before tools are. For now, direct import.

async def search_rituals(question: str) -> Dict[str, Any]:
    """
    Searches for rituals in Astra DB using vector search.
    Returns top 3 most relevant documents. Handles CollectionExceptions.
    Args:
        question (str): The user's query about rituals.
    Returns:
        dict: {"status": "success", "data": contexts} or {"status": "error", "error": <str>}
    """
    try:
        if not question:
            return {"status": "error", "error": "Question is required for ritual search."}

        if astra_db is None:
            # This can happen if ASTRA_API_ENDPOINT or ASTRA_API_TOKEN was missing in .env
            # or if DataAPIClient failed to initialize.
            return {"status": "error", "error": "Astra DB client is not initialized. Check environment variables and config."}

        # Assuming 'ritual_data' is the correct collection name
        ritual_data_collection = astra_db.get_collection("ritual_data")

        # The query structure for DataStax AstraPy
        # projection={"$vectorize": True} might not be valid.
        # Vector search is usually done by providing the query vector directly
        # or by using a $vectorize operator with the query string.
        # The exact syntax depends on the version and specific setup.
        # The original code used:
        # find(projection={"$vectorize": True}, sort={"$vectorize": question}, limit=3)
        # This implies the string 'question' is automatically vectorized by the DB.

        # Let's stick to the original logic assuming it's correct for the environment.
        results = ritual_data_collection.find(
            sort={"$vectorize": question}, # We want to find documents similar to the 'question' string
            limit=3,
            projection={"$vectorize": True} # This seems to ask the DB to also return the vector of the 'question' itself or some related metadata.
                                          # If the goal is to get document text and similarity, projection might be different, e.g. {"text_field": 1, "another_field": 1}
        )

        contexts = [doc for doc in results.get("data", {}).get("documents", [])] if results and results.get("data") else []

        if not contexts and results.get("errors"):
             return {"status": "error", "error": f"Astra DB query failed: {results.get('errors')}"}

        return {"status": "success", "data": contexts}

    except Exception as e:
        # Log the full exception for debugging
        # import traceback
        # print(f"Error in search_rituals: {traceback.format_exc()}")
        return {"status": "error", "error": f"An unexpected error occurred during ritual search: {str(e)}"}

if __name__ == '__main__':
    # Example for testing search_rituals (requires AstraDB setup in .env)
    import asyncio
    async def test_search():
        print("Testing ritual search...")
        # Ensure your .env has ASTRA_API_TOKEN and ASTRA_API_ENDPOINT
        # and the collection 'ritual_data' exists with vectorized data.
        test_question = "What is Kanyadaan?"
        response = await search_rituals(test_question)
        print(f"Search for '{test_question}':")
        if response["status"] == "success":
            for i, doc in enumerate(response["data"]):
                print(f"  Result {i+1}:")
                # Print some fields from the doc, e.g., if it has a 'text' or 'name' field
                # print(f"    ID: {doc.get('_id')}")
                # print(f"    Content: {doc.get('text_content_chunk', 'N/A')}") # Example field
                print(f"    Document: {doc}") # Print whole doc for inspection
        else:
            print(f"  Error: {response['error']}")

    asyncio.run(test_search())
