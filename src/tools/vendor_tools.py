# src/tools/vendor_tools.py
"""
Tools related to searching, retrieving, and managing vendor information.
These tools will interact with the Supabase service layer.
"""
from typing import Dict, Any, List, Optional
from google.adk.tools import ToolContext
import json # For debug or data manipulation
import uuid # For input validation (e.g. vendor_id)
from datetime import date, datetime # For date operations

# from src.services.supabase_service import execute_sql_query # Will be used after service layer
# Placeholder for the service function, to be replaced by import from supabase_service
async def _execute_supabase_sql_placeholder(sql: str, params: dict = None) -> Dict[str, Any]:
    print(f"[_execute_supabase_sql_placeholder Vendor] SQL: {sql}, Params: {params}")
    # Simulate some common return structures based on query type
    if "SELECT * FROM vendors WHERE vendor_id" in sql: # get_vendor_details
        return {"rows": [{"vendor_id": params.get("vendor_id"), "vendor_name": "Mock Vendor Details"}]}
    if "SELECT * FROM vendors" in sql: # list_vendors
        return {"rows": [{"vendor_id": "mock_vid_1", "vendor_name": "Mock Vendor 1"}, {"vendor_id": "mock_vid_2", "vendor_name": "Mock Vendor 2"}]}
    if "SELECT available_date, status FROM vendor_availability" in sql: # get_vendor_availability
         return {"status": "success", "data": [{"available_date": "2025-01-01", "status": "available"}]} # Note: original returned this structure
    return {"error": "Unknown vendor query type for placeholder"}


async def list_vendors(filters: Optional[Dict[str, Any]] = None, tool_context: Optional[ToolContext] = None) -> List[Dict[str, Any]]:
    """
    List all vendors, optionally filtered by category, city, or other fields.
    Args:
        filters (Optional[dict]): Filter fields (e.g., {"vendor_category": "Venue", "city": "Metropolis"}).
                                 Note: city filter was special cased as "address->>'city'".
        tool_context (ToolContext, optional): ADK Tool context.
    Returns:
        list: List of vendor dicts. Returns empty list on error or if none found.
    """
    # TODO: Refactor to use self.supabase_service.fetch_all("vendors", filters=processed_filters)
    # The service layer should ideally handle the ILIKE and address->>'city' logic if possible,
    # or this tool prepares the specific SQL.

    sql = "SELECT * FROM vendors"
    params = {}
    where_clauses = []

    if filters:
        for key, value in filters.items():
            # Original code used ILIKE for all, and special handling for city.
            # This logic will be part of the service call or SQL construction there.
            # For placeholder, we assume the service will handle it.
            if key == "city": # Assuming 'city' is a top-level filter processed from "address->>'city'"
                where_clauses.append(f"address->>'city' ILIKE :city_filter") # Example of direct SQL part
                params["city_filter"] = f"%{value}%" # Renamed to avoid clash if 'city' is a column
            elif key == "vendor_category":
                 where_clauses.append(f"vendor_category ILIKE :vendor_category_filter")
                 params["vendor_category_filter"] = f"%{value}%"
            # Add other common filterable fields as needed
            # else:
            #     where_clauses.append(f"{key} ILIKE :{key}") # Generic, ensure key is safe
            #     params[key] = f"%{value}%"

        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)

    # result = await execute_sql_query(sql, params) # Target state
    result = await _execute_supabase_sql_placeholder(sql, params) # Placeholder

    print(f"[vendor_tools.list_vendors] SQL: {sql}, Params: {params}, Result: {result}")
    rows = result.get("rows")
    if rows and isinstance(rows, list):
        return rows
    return []


async def get_vendor_details(vendor_id: str, tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    """
    Get all details for a vendor by vendor_id.
    Args:
        vendor_id (str): The vendor's UUID.
        tool_context (ToolContext, optional): ADK Tool context.
    Returns:
        dict: Vendor data or {"error": <str>}
    """
    # TODO: Refactor to use self.supabase_service.fetch_one("vendors", {"vendor_id": vendor_id})
    sql = "SELECT * FROM vendors WHERE vendor_id = :vendor_id LIMIT 1;"
    # result = await execute_sql_query(sql, {"vendor_id": vendor_id}) # Target state
    result = await _execute_supabase_sql_placeholder(sql, {"vendor_id": vendor_id}) # Placeholder

    rows = result.get("rows")
    if rows and isinstance(rows, list) and len(rows) > 0:
        return rows[0]
    return {"error": f"Vendor not found for vendor_id {vendor_id}."}


# --- Functions from old sanskara/tools/vendor_tools.py ---

async def get_vendor_availability(vendor_id: str, tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    """
    Gets all availability data for a vendor after today's date.
    Args:
        vendor_id (str): The UUID of the vendor.
        tool_context (ToolContext, optional): ADK Tool context.
    Returns:
        dict: A dictionary with status ("success" or "error") and data or error message.
              Successful data: {"available_date": "YYYY-MM-DD", "status": "available/booked", ...}
    """
    # TODO: Refactor to use self.supabase_service.fetch_all("vendor_availability", filters, order_by)
    try:
        uuid.UUID(vendor_id)  # Validate input
    except ValueError:
        return {"status": "error", "error": "Invalid vendor_id format."}

    today_iso = date.today().isoformat()
    sql = """
        SELECT available_date, status
        FROM vendor_availability
        WHERE vendor_id = :vendor_id AND available_date >= :today
        ORDER BY available_date;
    """
    params = {"vendor_id": vendor_id, "today": today_iso}

    # result_from_db = await execute_sql_query(sql, params) # Target state
    # This placeholder needs to match the structure the original function expected for its processing logic
    result_from_db_placeholder = await _execute_supabase_sql_placeholder(sql, params)

    # Original code expected `result["status"] == "success"` and `result["data"]` to be a list of items.
    # The placeholder _execute_supabase_sql_placeholder for this query returns this structure directly.
    # So, if the placeholder is adapted correctly, the following logic should work.
    # For now, let's assume the placeholder returns a list of rows under "rows" key for success.

    # Adapting to a more standard service response like {"rows": [...]} or {"error": ...}
    if "error" in result_from_db_placeholder:
        return {"status": "error", "error": result_from_db_placeholder["error"]}

    db_rows = result_from_db_placeholder.get("rows") # Assuming this is what the service layer will give

    # The original code's `execute_supabase_sql` had a complex return that sometimes was a dict with 'status' and 'data'
    # For this specific function in vendor_tools.py, it directly called `execute_supabase_sql` and then
    # checked `result["status"] == "success"` and iterated `result["data"]`.
    # My new `_execute_supabase_sql_placeholder` is simplified to return {"rows": []} or {"error": ""}.
    # I'll adjust the placeholder for this specific call or the processing logic here.
    # Let's assume the placeholder for this specific query was already adapted to return the nested structure.
    if result_from_db_placeholder.get("status") == "success" and isinstance(result_from_db_placeholder.get("data"), list):
        return {"status": "success", "data": result_from_db_placeholder["data"]} # Pass through if already correct
    elif isinstance(db_rows, list): # Adapt if placeholder returned {"rows": [...]}
         return {"status": "success", "data": db_rows}
    else: # Fallback error
        return {"status": "error", "error": "Failed to fetch or process vendor availability."}


async def check_vendor_availability(vendor_id: str, date_to_check_str: str, availability_data: List[Dict[str, Any]], tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    """
    Checks if a vendor is available on a specific date, using pre-fetched availability data.
    Args:
        vendor_id (str): The UUID of the vendor (used for validation).
        date_to_check_str (str): The date to check availability for (YYYY-MM-DD).
        availability_data (list): A list of availability dictionaries (typically from get_vendor_availability).
        tool_context (ToolContext, optional): ADK Tool context.
    Returns:
        dict: {"status": "success", "data": True/False} or {"status": "error", "error": ...}
              (Note: original returned boolean directly under 'data', this wraps it for consistency)
    """
    try:
        uuid.UUID(vendor_id)
    except ValueError:
        return {"status": "error", "error": "Invalid vendor_id format."}
    try:
        datetime.strptime(date_to_check_str, "%Y-%m-%d")
    except ValueError:
        return {"status": "error", "error": "Invalid date format for date_to_check. Use YYYY-MM-DD."}

    if not isinstance(availability_data, list):
        return {"status": "error", "error": "availability_data must be a list."}

    for item in availability_data:
        if item.get("available_date") == date_to_check_str:
            return {"status": "success", "data": {"available": item.get("status") == "available"}}

    # If the date is not found in the provided list, the original code assumed "available: True".
    # This might or might not be the desired business logic.
    # For safety, it might be better to state "not_specified" or require explicit availability.
    # Sticking to original logic for now.
    return {"status": "success", "data": {"available": True}} # Default if not explicitly booked/unavailable in list
