# src/services/astradb_service.py
"""
Service layer for interacting with Astra DB.
This module abstracts the direct database interactions, especially for vector search.
"""
from typing import Any, Dict, List, Optional
from astrapy import DataAPIClient
from astrapy.exceptions import CollectionNotFoundException # Example exception

# Assuming settings are centralized and imported
from config.settings import ASTRA_API_TOKEN, ASTRA_API_ENDPOINT

# Astra DB client instance, managed within this service
_astradb_client_instance: Optional[DataAPIClient] = None
_astradb_database_instance: Optional[Any] = None # Adjust type hint as per DataAPIClient.get_database_by_api_endpoint return

def _get_astradb_database():
    """
    Initializes and/or returns the Astra DB database instance.
    Raises ValueError if configuration is missing.
    """
    global _astradb_client_instance, _astradb_database_instance
    if _astradb_database_instance is None:
        if not ASTRA_API_TOKEN:
            raise ValueError("Astra API Token (ASTRA_API_TOKEN) is not configured.")
        if not ASTRA_API_ENDPOINT:
            raise ValueError("Astra API Endpoint (ASTRA_API_ENDPOINT) is not configured.")

        print(f"[AstraDBService] Initializing AstraDB client for endpoint: {ASTRA_API_ENDPOINT}")
        _astradb_client_instance = DataAPIClient(ASTRA_API_TOKEN)
        try:
            _astradb_database_instance = _astradb_client_instance.get_database_by_api_endpoint(ASTRA_API_ENDPOINT)
            print("[AstraDBService] AstraDB database instance initialized successfully.")
        except Exception as e: # Catch specific exceptions if known, e.g., connection errors
            _astradb_database_instance = None # Ensure it's reset on failure
            raise RuntimeError(f"Failed to connect to AstraDB at {ASTRA_API_ENDPOINT}: {e}")

    return _astradb_database_instance

async def vector_search_documents(
    collection_name: str,
    query_vector: Optional[List[float]] = None, # If providing pre-computed vector
    query_text: Optional[str] = None, # If relying on Astra's $vectorize
    limit: int = 3,
    projection: Optional[Dict[str, Any]] = None,
    filter_criteria: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Performs a vector search on a specified Astra DB collection.

    Args:
        collection_name (str): The name of the collection to search.
        query_vector (Optional[List[float]]): The vector to search with.
        query_text (Optional[str]): Text to be vectorized by Astra DB for the search.
                                     Either query_vector or query_text must be provided.
        limit (int): The maximum number of documents to return.
        projection (Optional[Dict[str, Any]]): Specifies which fields to include or exclude.
                                              Example: {"$vectorize": True} or {"field1": 1, "field2": 0}
        filter_criteria (Optional[Dict[str, Any]]): Additional filters for the query.

    Returns:
        Dict[str, Any]: A dictionary containing "status": "success" and "data": [documents]
                        or "status": "error" and "error": <description>.
    """
    if not query_vector and not query_text:
        return {"status": "error", "error": "Either query_vector or query_text must be provided for vector search."}

    try:
        db = _get_astradb_database()
        collection = db.get_collection(collection_name)

        find_options: Dict[str, Any] = {"limit": limit}
        if projection:
            find_options["projection"] = projection

        sort_clause: Dict[str, Any]
        if query_text:
            # Using $vectorize assumes the collection/Astra setup supports it for the given text.
            sort_clause = {"$vectorize": query_text}
        elif query_vector: # This assumes query_vector is the pre-computed embedding
            sort_clause = {"$vector": query_vector} # Or however astrapy expects pre-computed vectors
        else: # Should be caught by the initial check, but as a safeguard
             return {"status": "error", "error": "No valid query vector or text for sorting."}

        print(f"[AstraDBService.vector_search] Searching collection '{collection_name}' with text: '{query_text[:50]}...' (limit: {limit})")

        # The find method in astrapy might not directly support async/await in its typical usage.
        # If astrapy's find is blocking, this service method cannot be truly async without
        # running it in a thread pool executor. For now, assuming it's okay or will be handled.
        # For a truly async library, you'd await collection.find(...)

        # Construct the find query
        query_filter = filter_criteria if filter_criteria else {}

        # The `find` method in `astrapy.collection.Collection` takes `filter`, `sort`, `projection`, `options`.
        # Let's map our parameters to these.
        # `sort` is used for vector similarity search.
        # `projection` is passed directly.
        # `options` can include `limit`.

        results = collection.find(
            filter=query_filter,
            sort=sort_clause,
            projection=projection, # This might be redundant if also in options, check astrapy docs
            options={"limit": limit}
        )

        documents = [doc for doc in results.get("data", {}).get("documents", [])]
        return {"status": "success", "data": documents}

    except CollectionNotFoundException:
        return {"status": "error", "error": f"Astra DB Collection '{collection_name}' not found."}
    except Exception as e:
        print(f"[AstraDBService.vector_search] Exception: {e}")
        return {"status": "error", "error": f"An unexpected error occurred during Astra DB vector search: {str(e)}"}

# You can add other AstraDB related service methods here, e.g.,
# - get_document_by_id
# - insert_document
# - update_document

if __name__ == "__main__":
    # Example usage (for testing this module directly)
    async def _test_service():
        print("Testing AstraDB Service...")
        # Ensure your .env file is correctly set up at the project root for this to work.

        # Example: Search rituals (assuming 'ritual_data' collection exists and is set up for vector search)
        # search_result = await vector_search_documents(
        #     collection_name="ritual_data", # Make sure this collection exists in your Astra DB
        #     query_text="What is Kanyadana?",
        #     limit=2,
        #     projection={"$vectorize": True} # Or specific fields like {"ritual_name": 1, "description": 1}
        # )
        # print(f"Ritual search result: {search_result}")

        # Test with a non-existent collection
        # error_result = await vector_search_documents(collection_name="non_existent_collection", query_text="test")
        # print(f"Error search result: {error_result}")
        print("To run tests, uncomment calls in _test_service() and ensure .env is configured for AstraDB.")
        print("And that the specified collection (e.g., 'ritual_data') exists and is ready for vector search.")

    import asyncio
    # asyncio.run(_test_service()) # Commented out for automated runs.
