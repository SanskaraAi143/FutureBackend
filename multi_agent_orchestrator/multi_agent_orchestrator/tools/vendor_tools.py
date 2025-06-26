import logging
from typing import List, Dict, Any, Optional
from google.adk.tools import ToolContext # For type hinting context
import json
from ..shared_libraries.helpers import execute_supabase_sql # Relative import

# Configure logging for this module
logger = logging.getLogger(__name__)

# A (non-exhaustive) whitelist of filterable columns for list_vendors and search_vendors to enhance security
# and prevent unintended queries on arbitrary columns.
# This should be adjusted based on the actual 'vendors' table schema and desired filter capabilities.
VALID_VENDOR_FILTER_COLUMNS = {
    "vendor_category",
    "price", # Assuming 'price' is a numeric column for budget range
    "rating", # Assuming 'rating' is a numeric column
    # "address->>'city'", # Handled specially due to JSONB path
    # "fts_data" # Handled specially for full-text search
}


async def list_vendors(filters: Optional[Dict[str, Any]] = None, context: ToolContext = None) -> Dict[str, Any]:
    """
    Lists vendors, optionally filtered by various criteria.

    Args:
        filters (Optional[Dict[str, Any]]): A dictionary of filters.
            Keys should be column names (or special keys like 'city').
            Example: `{"vendor_category": "Venue", "city": "Bangalore"}`
        context (ToolContext): The ADK ToolContext for state management.

    Returns:
        Dict[str, Any]:
            On success: `{"status": "success", "data": [vendor_dict_1, vendor_dict_2, ...]}`
            On failure: `{"status": "error", "error": "Error message"}`
            If no vendors found: `{"status": "success", "data": []}`

    Error Handling:
        - Returns an error dict if database query fails.
        - Logs errors and important actions.
        - Filters keys not in `VALID_VENDOR_FILTER_COLUMNS` (excluding special ones like 'city').

    Dependencies:
        - `execute_supabase_sql` from `shared_libraries.helpers`.

    Example Usage:
        ```python
        response = await list_vendors({"vendor_category": "Photographer", "city": "Goa"}, context)
        if response["status"] == "success":
            for vendor in response["data"]:
                print(vendor["name"])
        else:
            print(f"Error: {response['error']}")
        ```
    """
    if context is None:
        logger.warning("list_vendors: ToolContext not provided. Caching will not be used.")

    cache_key = f"list_vendors_filters:{json.dumps(filters, sort_keys=True) if filters else 'None'}"
    if context and cache_key in context.state:
        logger.info(f"list_vendors: Returning cached data for filters: {filters}")
        return {"status": "success", "data": context.state[cache_key]}

    logger.info(f"list_vendors: Called with filters: {filters}")
    sql = "SELECT * FROM vendors"
    params = {}
    where_clauses = []
    param_idx = 0

    def add_param(value: Any) -> str:
        nonlocal param_idx
        p_name = f"p{param_idx}"
        params[p_name] = value
        param_idx += 1
        return p_name

    if filters:
        for key, value in filters.items():
            if value is None: # Skip None values in filters
                continue

            if key == "city": # Special handling for city (assuming it's in address->>'city')
                where_clauses.append(f"address->>'city' ILIKE :{add_param(f'%{value}%')}")
            elif key in VALID_VENDOR_FILTER_COLUMNS:
                # Basic ILIKE for whitelisted text columns, exact match or range for others could be added
                where_clauses.append(f"{key} ILIKE :{add_param(f'%{value}%')}")
            else:
                logger.warning(f"list_vendors: Ignored filter on unsupported or non-whitelisted key: {key}")

        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)

    logger.debug(f"list_vendors: Executing SQL: {sql} with params: {params}")
    try:
        result = await execute_supabase_sql(sql, params)

        if isinstance(result, dict) and "error" in result:
            logger.error(f"list_vendors: Database error: {result['error']}")
            return {"status": "error", "error": result['error']}

        if isinstance(result, list):
            if context:
                context.state[cache_key] = result # Cache the result
            logger.info(f"list_vendors: Successfully retrieved {len(result)} vendors. Cached: {bool(context)}")
            return {"status": "success", "data": result}
        else:
            logger.error(f"list_vendors: Unexpected result format from database: {result}")
            return {"status": "error", "error": "Unexpected result format from database."}

    except Exception as e:
        logger.exception(f"list_vendors: Unexpected error: {e}")
        return {"status": "error", "error": f"An unexpected error occurred: {str(e)}"}


async def get_vendor_details(vendor_id: str, context: ToolContext = None) -> Dict[str, Any]:
    """
    Retrieves all details for a specific vendor by their vendor_id.

    Args:
        vendor_id (str): The UUID of the vendor. Must be a non-empty string.
        context (ToolContext): The ADK ToolContext for state management.

    Returns:
        Dict[str, Any]:
            On success: `{"status": "success", "data": {vendor_details_dict}}`
            On failure or if not found: `{"status": "error", "error": "Error message"}`

    Error Handling:
        - Returns an error dict if vendor_id is invalid.
        - Returns an error dict if database query fails or vendor is not found.
        - Logs errors.

    Dependencies:
        - `execute_supabase_sql` from `shared_libraries.helpers`.

    Example Usage:
        ```python
        response = await get_vendor_details("some-vendor-uuid", context)
        if response["status"] == "success":
            print(f"Vendor: {response['data']['name']}")
        else:
            print(f"Error: {response['error']}")
        ```
    """
    if not vendor_id or not isinstance(vendor_id, str):
        logger.error("get_vendor_details: Invalid vendor_id provided.")
        return {"status": "error", "error": "Invalid vendor_id. Must be a non-empty string."}

    if context is None:
        logger.warning("get_vendor_details: ToolContext not provided. Caching will not be used.")

    cache_key = f"vendor_details:{vendor_id}"
    if context and cache_key in context.state:
        logger.info(f"get_vendor_details: Returning cached data for vendor_id: {vendor_id}")
        return {"status": "success", "data": context.state[cache_key]}

    logger.info(f"get_vendor_details: Fetching details for vendor_id: {vendor_id}")
    sql = "SELECT * FROM vendors WHERE vendor_id = :vendor_id LIMIT 1;"

    try:
        result = await execute_supabase_sql(sql, {"vendor_id": vendor_id})

        if isinstance(result, dict) and "error" in result:
            logger.error(f"get_vendor_details: Database error for vendor_id {vendor_id}: {result['error']}")
            return {"status": "error", "error": result['error']}

        vendor_data = None
        if isinstance(result, list) and result:
            vendor_data = result[0]
        elif isinstance(result, dict) and "vendor_id" in result and result.get("vendor_id") == vendor_id:
            vendor_data = result

        if vendor_data:
            if context:
                context.state[cache_key] = vendor_data # Cache the result
            logger.info(f"get_vendor_details: Successfully retrieved details for vendor_id {vendor_id}. Cached: {bool(context)}")
            return {"status": "success", "data": vendor_data}
        else:
            logger.warning(f"get_vendor_details: Vendor not found for vendor_id {vendor_id}. Result: {result}")
            return {"status": "error", "error": "Vendor not found."}

    except Exception as e:
        logger.exception(f"get_vendor_details: Unexpected error for vendor_id {vendor_id}: {e}")
        return {"status": "error", "error": f"An unexpected error occurred: {str(e)}"}


async def search_vendors(
    category: Optional[str] = None,
    location: Optional[str] = None, # Corresponds to 'city'
    budget_range: Optional[Dict[str, float]] = None,
    ratings: Optional[float] = None,
    keywords: Optional[List[str]] = None,
    context: ToolContext = None
) -> Dict[str, Any]:
    """
    Searches for vendors based on a combination of criteria, including full-text search.

    Args:
        category (Optional[str]): Vendor category (e.g., "Photographer", "Venue").
        location (Optional[str]): City where the vendor is located.
        budget_range (Optional[Dict[str, float]]): Budget range, e.g., `{"min": 1000.0, "max": 5000.0}`.
                                                  Keys 'min' and 'max' are optional within the dict.
        ratings (Optional[float]): Minimum vendor rating (e.g., 4.0).
        keywords (Optional[List[str]]): List of keywords for full-text search against vendor descriptions/names.
        context (ToolContext): The ADK ToolContext for state management.

    Returns:
        Dict[str, Any]:
            On success: `{"status": "success", "data": [vendor_dict_1, ...]}` (empty list if no matches)
            On failure: `{"status": "error", "error": "Error message"}`

    Error Handling:
        - Validates numeric types for budget and ratings if provided.
        - Returns an error dict for database query failures.
        - Logs errors and search parameters.
        - Uses whitelisted columns for direct filtering and specific handling for keywords and location.

    Dependencies:
        - `execute_supabase_sql` from `shared_libraries.helpers`.

    Example Usage:
        ```python
        search_criteria = {
            "category": "Caterer",
            "location": "Mumbai",
            "ratings": 4.5,
            "keywords": ["indian", "vegetarian"]
        }
        response = await search_vendors(**search_criteria, context=context)
        if response["status"] == "success":
            print(f"Found {len(response['data'])} caterers.")
        else:
            print(f"Search error: {response['error']}")
        ```
    """
    if context is None:
        logger.warning("search_vendors: ToolContext not provided. Caching will not be used.")

    cache_key_parts = [
        f"category:{category}" if category else "",
        f"location:{location}" if location else "",
        f"budget_min:{budget_range.get('min')}" if budget_range and "min" in budget_range else "",
        f"budget_max:{budget_range.get('max')}" if budget_range and "max" in budget_range else "",
        f"ratings:{ratings}" if ratings else "",
        f"keywords:{sorted(keywords)}" if keywords else ""
    ]
    cache_key = "search_vendors:" + ":".join(filter(None, cache_key_parts))

    if context and cache_key in context.state:
        logger.info(f"search_vendors: Returning cached data for search criteria.")
        return {"status": "success", "data": context.state[cache_key]}

    logger.info(f"search_vendors: Called with category='{category}', location='{location}', budget_range='{budget_range}', ratings='{ratings}', keywords='{keywords}'")

    sql = "SELECT * FROM vendors"
    params: Dict[str, Any] = {}
    where_clauses: List[str] = []
    param_idx = 0

    def add_param(value: Any) -> str:
        nonlocal param_idx
        p_name = f"p{param_idx}"
        params[p_name] = value
        param_idx += 1
        return p_name

    try:
        if category and isinstance(category, str):
            if "vendor_category" in VALID_VENDOR_FILTER_COLUMNS:
                where_clauses.append(f"vendor_category ILIKE :{add_param(f'%{category}%')}")
            else: logger.warning("search_vendors: 'vendor_category' not in whitelisted columns for filtering.")

        if location and isinstance(location, str): # 'location' is treated as 'city'
            where_clauses.append(f"address->>'city' ILIKE :{add_param(f'%{location}%')}")

        if budget_range and isinstance(budget_range, dict):
            if "price" in VALID_VENDOR_FILTER_COLUMNS:
                min_budget = budget_range.get("min")
                max_budget = budget_range.get("max")
                if min_budget is not None:
                    try:
                        where_clauses.append(f"price >= :{add_param(float(min_budget))}")
                    except ValueError: logger.warning("search_vendors: Invalid 'min' budget value, not a float.")
                if max_budget is not None:
                    try:
                        where_clauses.append(f"price <= :{add_param(float(max_budget))}")
                    except ValueError: logger.warning("search_vendors: Invalid 'max' budget value, not a float.")
            else: logger.warning("search_vendors: 'price' not in whitelisted columns for budget filtering.")


        if ratings is not None:
            if "rating" in VALID_VENDOR_FILTER_COLUMNS:
                try:
                    where_clauses.append(f"rating >= :{add_param(float(ratings))}")
                except ValueError: logger.warning("search_vendors: Invalid 'ratings' value, not a float.")
            else: logger.warning("search_vendors: 'rating' not in whitelisted columns for filtering.")

        if keywords and isinstance(keywords, list):
            valid_keywords = [str(k).strip() for k in keywords if k and isinstance(k, str) and k.strip()]
            if valid_keywords:
                # For ts_query, keywords are typically joined with '&' or '|'
                # Ensure the fts_data column is indexed with a tsvector.
                # Using plainto_tsquery is generally safer against injection than to_tsquery with user input.
                # However, if specific tsquery operators are needed, ensure sanitization.
                # This example uses to_tsquery as in original, assuming 'english' dictionary.
                # Consider using plainto_tsquery('english', query_string) for more safety with raw user keywords.
                query_string = " & ".join(valid_keywords) # Example: "keyword1 & keyword2"
                where_clauses.append(f"fts_data @@ to_tsquery('english', :{add_param(query_string)})")

        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)

        logger.debug(f"search_vendors: Executing SQL: {sql} with params: {params}")
        result = await execute_supabase_sql(sql, params)

        if isinstance(result, dict) and "error" in result:
            logger.error(f"search_vendors: Database error: {result['error']}")
            return {"status": "error", "error": result['error']}

        if isinstance(result, list):
            if context:
                context.state[cache_key] = result # Cache the result
            logger.info(f"search_vendors: Successfully retrieved {len(result)} vendors matching criteria. Cached: {bool(context)}")
            return {"status": "success", "data": result}
        else:
            logger.error(f"search_vendors: Unexpected result format from database: {result}")
            return {"status": "error", "error": "Unexpected result format from database."}

    except Exception as e:
        logger.exception(f"search_vendors: Unexpected error during search: {e}")
        return {"status": "error", "error": f"An unexpected error occurred during vendor search: {str(e)}"}


async def check_vendor_availability(vendor_id: str, date: str, context: ToolContext = None) -> Dict[str, Any]:
    """
    Checks if a vendor is available on a specific date by looking for bookings.
    Assumes a 'vendor_bookings' table exists with 'vendor_id' and 'booking_date'.
    Args:
        vendor_id (str): The UUID of the vendor.
        date (str): The date to check in 'YYYY-MM-DD' format.
        context (ToolContext): The ADK ToolContext for state management.
    Returns:
        Dict[str, Any]: `{"status": "success", "data": {"available": True/False}}`
    """
    if not all([vendor_id, date]) or not isinstance(vendor_id, str) or not isinstance(date, str):
        return {"status": "error", "error": "Invalid input: vendor_id and date must be non-empty strings."}

    if context is None:
        logger.warning("check_vendor_availability: ToolContext not provided. Caching will not be used.")

    cache_key = f"vendor_availability:{vendor_id}:{date}"
    if context and cache_key in context.state:
        logger.info(f"check_vendor_availability: Returning cached data for vendor availability.")
        return {"status": "success", "data": context.state[cache_key]}

    logger.info(f"Checking availability for vendor {vendor_id} on {date}")
    sql = "SELECT status FROM vendor_availability WHERE vendor_id = :vendor_id AND available_date = :date;"
    params = {"vendor_id": vendor_id, "date": date}

    try:
        result = await execute_supabase_sql(sql, params)
        if isinstance(result, dict) and "error" in result:
            return {"status": "error", "error": result['error']}

        if isinstance(result, list) and result:
            # If an entry exists, check its status
            availability_status = result[0]['status']
            is_available = (availability_status == 'available')
        else:
            # If no entry exists, assume available
            is_available = True
        
        if context:
            context.state[cache_key] = {"available": is_available} # Cache the result
        logger.info(f"Vendor {vendor_id} on {date} is {'available' if is_available else 'not available'}. Cached: {bool(context)}")
        return {"status": "success", "data": {"available": is_available}}
    except Exception as e:
        logger.exception(f"Error checking vendor availability for {vendor_id}: {e}")
        return {"status": "error", "error": f"An unexpected error occurred: {e}"}

async def update_vendor_status(vendor_id: str, status: str, context: ToolContext = None) -> Dict[str, Any]:
    """
    Updates the status of a vendor in the 'vendors' table.
    Args:
        vendor_id (str): The UUID of the vendor to update.
        status (str): The new status to set.
        context (ToolContext): The ADK ToolContext for state management.
    Returns:
        Dict[str, Any]: `{"status": "success", "data": {updated_vendor_data}}` or `{"status": "error", ...}`
    """
    if not all([vendor_id, status]) or not isinstance(vendor_id, str) or not isinstance(status, str):
        return {"status": "error", "error": "Invalid input: vendor_id and status must be non-empty strings."}

    if context is None:
        logger.warning("update_vendor_status: ToolContext not provided. Cache invalidation will not occur.")

    logger.info(f"Updating status for vendor {vendor_id} to '{status}'")
    sql = "UPDATE vendors SET status = :status WHERE vendor_id = :vendor_id RETURNING *;"
    params = {"vendor_id": vendor_id, "status": status}

    try:
        result = await execute_supabase_sql(sql, params)
        if isinstance(result, dict) and "error" in result:
            return {"status": "error", "error": result['error']}
        
        if isinstance(result, list) and result:
            updated_vendor = result[0]
            # Invalidate relevant caches after update
            if context:
                # Invalidate specific vendor details cache
                if f"vendor_details:{vendor_id}" in context.state:
                    del context.state[f"vendor_details:{vendor_id}"]
                # Invalidate general list_vendors and search_vendors caches (more complex, might need to clear all or use more granular keys)
                # For simplicity, we'll just invalidate the specific detail for now.
                # A more robust solution might involve tagging cached items with vendor_id and clearing all tags.
                for key in list(context.state.keys()):
                    if key.startswith("list_vendors_filters:") or key.startswith("search_vendors:"):
                        del context.state[key]

            logger.info(f"Successfully updated status for vendor {vendor_id}. Cache invalidated: {bool(context)}")
            return {"status": "success", "data": updated_vendor}
        else:
            return {"status": "error", "error": "Vendor not found or update failed."}
    except Exception as e:
        logger.exception(f"Error updating vendor status for {vendor_id}: {e}")
        return {"status": "error", "error": f"An unexpected error occurred: {e}"}