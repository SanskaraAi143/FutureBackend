# src/tools/common_utils.py
"""
Common utility functions shared across different tool modules or services.
Also includes placeholder for timeline tools until they warrant a separate file.
"""
import json
from typing import Any, Dict, List, Optional # Added List
from google.adk.tools import ToolContext # Added ToolContext

# from src.services.supabase_service import execute_sql_query # Will be used after service layer

# Placeholder for the service function, to be replaced by import from supabase_service
async def _execute_supabase_sql_placeholder(sql: str, params: dict = None) -> Dict[str, Any]:
    print(f"[_execute_supabase_sql_placeholder CommonUtils/Timeline] SQL: {sql}, Params: {params}")
    if "SELECT * FROM timeline_events" in sql:
        return {"rows": [{"event_id": "mock_event_1", "description": "Mock timeline event"}]}
    if "INSERT INTO timeline_events" in sql or "UPDATE timeline_events" in sql:
        return {"rows": [{"event_id": "mock_event_1", "status": "success"}]}
    return {"error": "Unknown query type for common_utils placeholder"}


def sql_quote_value(val: Any) -> str:
    """
    Safely quote and format a value for SQL inlining.
    This is a direct carry-over. Consider if this is the best long-term approach
    versus parameterized queries handled by a DB driver if possible,
    though with MCP, this might be the way it expects queries.

    Args:
        val: The value to quote (str, int, float, dict, list, or None).

    Returns:
        str: The SQL-safe string representation of the value.
    """
    if val is None:
        return 'NULL'
    if isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, (dict, list)):
        # Ensure inner quotes are also escaped if the JSON string itself contains single quotes
        return f"'{json.dumps(val).replace("'", "''")}'"
    return f"'{str(val).replace("'", "''")}'"


# --- Timeline Tools (Consider moving to src/tools/timeline_tools.py if they grow) ---

async def get_timeline_events(user_id: str, tool_context: Optional[ToolContext] = None) -> List[Dict[str, Any]]:
    """
    Retrieves all timeline events for a given user.
    (Placeholder - to be refactored to use SupabaseService)
    Args:
        user_id (str): The UUID of the user.
        tool_context (ToolContext, optional): ADK Tool context.
    Returns:
        List[Dict[str, Any]]: List of timeline event dicts. Empty list if none or error.
    """
    # TODO: Refactor to use self.supabase_service.fetch_all("timeline_events", {"user_id": user_id})
    if not user_id: # Basic validation
        # Consider returning {"status": "error", "error": "User ID is required."} if tools should have this richer error structure
        # For now, matching original which implies empty list for errors too.
        return []

    sql = "SELECT * FROM timeline_events WHERE user_id = :user_id ORDER BY event_date_time;" # Added ORDER BY
    # result = await execute_sql_query(sql, {"user_id": user_id}) # Target state
    result = await _execute_supabase_sql_placeholder(sql, {"user_id": user_id}) # Placeholder

    rows = result.get("rows")
    if rows and isinstance(rows, list):
        return rows
    # Original code returned [] for errors in one path, and specific error dict in another.
    # Standardizing to return empty list for "not found" or "error" for list-returning functions.
    # If richer error reporting is needed, the return type should be Union[List[Dict], Dict[str,str]]
    return []


async def create_timeline_event(user_id: str, event: Dict[str, Any], tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    """
    Create a timeline event for a user.
    (Placeholder - to be refactored to use SupabaseService)
    Args:
        user_id (str): The user's UUID.
        event (dict): {"event_name": str, "event_date_time": str (ISO format),
                       "description": Optional[str], "location": Optional[str]}
        tool_context (ToolContext, optional): ADK Tool context.
    Returns:
        dict: {"status": "success", "data": inserted_event} or {"status": "error", "error": <desc>}
    """
    # TODO: Refactor to use self.supabase_service.insert_row("timeline_events", data_to_insert)
    if not user_id:
        return {"status": "error", "error": "User ID is required."}
    if not isinstance(event, dict) or not event.get("event_name") or not event.get("event_date_time"):
        return {"status": "error", "error": "Missing required fields for timeline event (event_name, event_date_time)."}

    sql = (
        "INSERT INTO timeline_events (user_id, event_name, event_date_time, description, location) "
        "VALUES (:user_id, :event_name, :event_date_time, :description, :location) RETURNING *;"
    )
    params = {
        "user_id": user_id,
        "event_name": event.get("event_name"),
        "event_date_time": event.get("event_date_time"),
        "description": event.get("description"), # Will be NULL if not provided
        "location": event.get("location")      # Will be NULL if not provided
    }
    print(f"[common_utils.create_timeline_event] SQL: {sql} with params: {params}")
    # result = await execute_sql_query(sql, params) # Target state
    result = await _execute_supabase_sql_placeholder(sql, params) # Placeholder

    rows = result.get("rows")
    if rows and isinstance(rows, list) and len(rows) > 0:
        return {"status": "success", "data": rows[0]}

    error_msg = result.get('error', 'Creating timeline event failed.')
    return {"status": "error", "error": error_msg}


async def update_timeline_event(event_id: str, updates: Dict[str, Any], tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    """
    Updates an existing timeline event.
    (Placeholder - to be refactored to use SupabaseService)
    Args:
        event_id (str): The UUID of the timeline event to update.
        updates (Dict[str, Any]): Fields to update.
        tool_context (ToolContext, optional): ADK Tool context.
    Returns:
        dict: {"status": "success", "data": updated_event} or {"status": "error", "error": <desc>}
    """
    # TODO: Refactor to use self.supabase_service.update_row("timeline_events", {"event_id": event_id}, updates)
    if not event_id:
        return {"status": "error", "error": "Event ID is required."}
    if not isinstance(updates, dict) or not updates:
        return {"status": "error", "error": "Updates must be a non-empty dictionary."}

    set_clauses = [f"{key} = :{key}" for key in updates.keys()]
    set_clause = ", ".join(set_clauses)
    sql = f"UPDATE timeline_events SET {set_clause} WHERE event_id = :event_id RETURNING *;"
    params = {**updates, "event_id": event_id}

    print(f"[common_utils.update_timeline_event] SQL: {sql} with params: {params}")
    # result = await execute_sql_query(sql, params) # Target state
    result = await _execute_supabase_sql_placeholder(sql, params) # Placeholder

    rows = result.get("rows")
    if rows and isinstance(rows, list) and len(rows) > 0:
        return {"status": "success", "data": rows[0]}

    error_msg = result.get('error', f"Event {event_id} not found or update failed.")
    return {"status": "error", "error": error_msg}
