# src/tools/user_tools.py
"""
Tools related to user management and data retrieval.
These tools will interact with the Supabase service layer.
"""
from typing import Dict, Any, Optional, List
from google.adk.tools import ToolContext
import json # For debug printing if needed, or if passing JSON data

# from src.services.supabase_service import execute_sql_query # Will be used after service layer is implemented
# For now, these functions will temporarily keep their direct call to a placeholder execute_sql_query
# or simulate behavior, to be refactored in Step 4.

# Placeholder for the service function, to be replaced by import from supabase_service
async def _execute_supabase_sql_placeholder(sql: str, params: dict = None) -> Dict[str, Any]:
    print(f"[_execute_supabase_sql_placeholder] SQL: {sql}, Params: {params}")
    # Simulate some common return structures based on query type
    if "SELECT" in sql.upper() and "LIMIT 1" in sql.upper():
        return {"rows": [{"message": "mock single row data"}]} # Simulate single row fetch
    if "SELECT" in sql.upper():
        return {"rows": [{"message": "mock multiple row data"}]} # Simulate multi-row fetch
    if "UPDATE" in sql.upper() or "INSERT" in sql.upper():
        return {"rows": [{"message": "mock mutation success"}]} # Simulate successful mutation
    if "DELETE" in sql.upper():
        return {"rows": []} # Simulate successful delete (often no rows returned, or count)
    return {"error": "Unknown query type for placeholder"}


async def get_user_id(email: str, tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    """
    Get the user_id for a given email from the users table.
    Args:
        email (str): The user's email address.
        tool_context (ToolContext, optional): ADK Tool context.
    Returns:
        dict: {"user_id": <uuid>} or {"error": <str>}
    """
    # TODO: Refactor to use self.supabase_service.fetch_one("users", {"email": email})
    sql = "SELECT user_id FROM users WHERE email = :email LIMIT 1;"
    # result = await execute_sql_query(sql, {"email": email}) # Target state
    result = await _execute_supabase_sql_placeholder(sql, {"email": email}) # Placeholder

    print(f"[user_tools.get_user_id] SQL executed: {sql} with params: {json.dumps({'email': email})} result: {result}")

    rows = result.get("rows")
    if rows and isinstance(rows, list) and len(rows) > 0:
        return rows[0] # Assuming the first row contains the user_id
    return {"error": f"User not found or error fetching user_id for {email}."}


async def get_user_data(user_id: str, tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    """
    Get all user data for a given user_id from the users table.
    Args:
        user_id (str): The user's UUID.
        tool_context (ToolContext, optional): ADK Tool context.
    Returns:
        dict: User data dict or {"error": <str>}
    """
    # TODO: Refactor to use self.supabase_service.fetch_one("users", {"user_id": user_id})
    sql = "SELECT * FROM users WHERE user_id = :user_id LIMIT 1;"
    # result = await execute_sql_query(sql, {"user_id": user_id}) # Target state
    result = await _execute_supabase_sql_placeholder(sql, {"user_id": user_id}) # Placeholder

    rows = result.get("rows")
    if rows and isinstance(rows, list) and len(rows) > 0:
        return rows[0]
    return {"error": f"User data not found for user_id {user_id}."}


async def update_user_data(user_id: str, data: Dict[str, Any], tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    """
    Update user data for a given user_id. Only allowed columns are updated; extra fields go into preferences.
    Args:
        user_id (str): The user's UUID.
        data (dict): Fields to update (top-level or preferences).
        tool_context (ToolContext, optional): ADK Tool context.
    Returns:
        dict: Updated user data or {"error": <str>}
    """
    # TODO: Refactor to use self.supabase_service.update_row("users", {"user_id": user_id}, update_payload)
    # This logic for handling preferences should ideally be in the service or managed carefully.
    USERS_TABLE_COLUMNS = {
        "user_id", "supabase_auth_uid", "email", "display_name", "created_at", "updated_at",
        "wedding_date", "wedding_location", "wedding_tradition", "preferences", "user_type",
    }

    # Deep copy data to avoid modifying the input dict if it's used elsewhere
    data_copy = json.loads(json.dumps(data))

    preferences_update = data_copy.pop("preferences", None) or {}
    extra_prefs = {
        k: data_copy.pop(k) for k in list(data_copy.keys()) if k not in USERS_TABLE_COLUMNS
    }
    if extra_prefs:
        preferences_update.update(extra_prefs)

    # Construct the final data payload for SQL
    update_payload = data_copy # Contains only direct USERS_TABLE_COLUMNS (excluding user_id for SET)

    if preferences_update:
        # Fetch current preferences to merge, or handle this merge at the DB level if possible (e.g. jsonb_set or ||)
        # For now, simulate fetch and merge if service doesn't handle deep preference merge.
        # current_user_data_result = await get_user_data(user_id) # This would be a service call
        # current_prefs = {}
        # if not current_user_data_result.get("error"):
        #    current_prefs = current_user_data_result.get("preferences", {})
        #    if not isinstance(current_prefs, dict): current_prefs = {} # Ensure it's a dict
        # current_prefs.update(preferences_update)
        # update_payload["preferences"] = current_prefs
        # Simpler approach for placeholder: just put the new preferences. DB should ideally merge.
        update_payload["preferences"] = preferences_update

    if "preferences" in update_payload and isinstance(update_payload["preferences"], dict):
        update_payload["preferences"] = json.dumps(update_payload["preferences"]) # Ensure it's a JSON string for DB

    if not update_payload: # Nothing to update if only user_id was passed or all moved to prefs
        if preferences_update: # If only preferences were updated
             update_payload["preferences"] = json.dumps(preferences_update) if isinstance(preferences_update, dict) else preferences_update
        else:
            return {"error": "No valid data provided for update."}


    set_clause_parts = [f"{k} = :{k}" for k in update_payload.keys()]
    if not set_clause_parts:
        return {"error": "No fields to update."}
    set_clause = ", ".join(set_clause_parts)

    sql = f"UPDATE users SET {set_clause} WHERE user_id = :user_id RETURNING *;"

    # Params for SQL: combine update_payload with user_id for the WHERE clause
    sql_params = {**update_payload, "user_id": user_id}

    print(f"[user_tools.update_user_data] Final SQL: {sql} with params: {sql_params}")
    # result = await execute_sql_query(sql, sql_params) # Target state
    result = await _execute_supabase_sql_placeholder(sql, sql_params) # Placeholder

    rows = result.get("rows")
    if rows and isinstance(rows, list) and len(rows) > 0:
        return rows[0]
    return {"error": f"Update failed for user_id {user_id}. Error: {result.get('error', 'Unknown')}"}


async def get_user_activities(user_id: str, tool_context: Optional[ToolContext] = None) -> List[Dict[str, Any]]:
    """
    Get all user activities (chat messages) for a user.
    Args:
        user_id (str): The user's UUID.
        tool_context (ToolContext, optional): ADK Tool context.
    Returns:
        list: List of activity dicts, or an empty list if none/error.
    """
    # TODO: Refactor to use self.supabase_service.fetch_all with appropriate query/view
    sql = """
        SELECT cm.*
        FROM chat_sessions cs
        JOIN chat_messages cm ON cs.session_id = cm.session_id
        WHERE cs.user_id = :user_id
        ORDER BY cm.timestamp DESC;
    """
    # result = await execute_sql_query(sql, {"user_id": user_id}) # Target state
    result = await _execute_supabase_sql_placeholder(sql, {"user_id": user_id}) # Placeholder

    rows = result.get("rows")
    if rows and isinstance(rows, list):
        return rows
    return [] # Return empty list on error or no data, common for list type returns
