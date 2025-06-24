import json # For logging params if needed
from typing import List, Dict, Any, Optional
from multi_agent_orchestrator.shared_libraries.helpers import execute_supabase_sql, sql_quote_value # Adjusted import

async def get_user_id(email: str) -> dict:
    """
    Get the user_id for a given email from the users table.
    Args:
        email (str): The user's email address.
    Returns:
        dict: {"user_id": <uuid>} or {"error": <str>}
    """
    sql = "SELECT user_id FROM users WHERE email = :email LIMIT 1;"
    # print(f"Executing SQL: {sql} with params: {json.dumps({'email': email})}")
    result = await execute_supabase_sql(sql, {"email": email})
    # print(f"Result from get_user_id: {result}")
    if isinstance(result, list) and result: # MCP often returns a list of rows
        return result[0]
    elif isinstance(result, dict) and result.get("rows"): # Older direct Supabase client style
         return result["rows"][0]
    elif isinstance(result, dict) and "user_id" in result: # If it's already the flat dict
        return result
    return {"error": f"User not found or unexpected result format. Result: {result}"}

async def get_user_data(user_id: str) -> dict:
    """
    Get all user data for a given user_id from the users table.
    Args:
        user_id (str): The user's UUID.
    Returns:
        dict: User data dict or {"error": <str>}
    """
    sql = "SELECT * FROM users WHERE user_id = :user_id LIMIT 1;"
    result = await execute_supabase_sql(sql, {"user_id": user_id})
    if isinstance(result, list) and result:
        return result[0]
    elif isinstance(result, dict) and result.get("rows"):
         return result["rows"][0]
    elif isinstance(result, dict) and "user_id" in result and result.get("user_id") == user_id : # Check if it's the data
        return result
    return {"error": f"User data not found or unexpected result format for user_id: {user_id}. Result: {result}"}

async def update_user_data(user_id: str, data: dict) -> dict:
    """
    Update user data for a given user_id. Only allowed columns are updated;
    extra fields go into preferences. user_type cannot be updated by this function directly.
    Args:
        user_id (str): The user's UUID.
        data (dict): Fields to update (top-level or preferences).
    Returns:
        dict: Updated user data or {"error": <str>}
    """
    USERS_TABLE_COLUMNS = {
        "user_id", "supabase_auth_uid", "email", "display_name", "created_at", "updated_at",
        "wedding_date", "wedding_location", "wedding_tradition", "preferences"
        # "user_type" is intentionally excluded as per prompt instructions for onboarding agent
    }

    fields_to_update = {}
    preferences_to_update = data.get("preferences", {}) # Start with existing preferences if provided
    if not isinstance(preferences_to_update, dict): # Ensure preferences is a dict
        preferences_to_update = {}

    for key, value in data.items():
        if key == "preferences": # Already handled
            continue
        if key in USERS_TABLE_COLUMNS:
            fields_to_update[key] = value
        else: # Extra fields go into preferences
            preferences_to_update[key] = value

    # Fetch current preferences if we are adding new ones, to merge correctly
    if preferences_to_update:
        current_user_data = await get_user_data(user_id)
        if not current_user_data or "error" in current_user_data:
            # Decide handling: error out, or proceed with empty current_prefs?
            # For now, let's assume if user_id is valid, we can update.
            # This part might need refinement based on how strictly we want to enforce prior existence.
            current_prefs = {}
        else:
            current_prefs = current_user_data.get("preferences", {})
            if not isinstance(current_prefs, dict): # Ensure current_prefs is a dict
                current_prefs = {}

        current_prefs.update(preferences_to_update)
        fields_to_update["preferences"] = current_prefs # Add potentially merged preferences to update set

    if not fields_to_update:
        return {"error": "No valid fields provided for update."}

    # Always JSON-serialize preferences if it's in the update list
    if "preferences" in fields_to_update and isinstance(fields_to_update["preferences"], dict):
        fields_to_update["preferences"] = json.dumps(fields_to_update["preferences"])

    set_clause_parts = []
    update_params = {}
    for i, (k, v) in enumerate(fields_to_update.items()):
        param_name = f"param_{i}"
        set_clause_parts.append(f"{k} = :{param_name}")
        update_params[param_name] = v

    set_clause = ", ".join(set_clause_parts)

    sql = f"UPDATE users SET {set_clause} WHERE user_id = :user_id RETURNING *;"
    final_params = {**update_params, "user_id": user_id}

    # print(f"Final SQL for update_user_data: {sql} with params: {final_params}")
    result = await execute_supabase_sql(sql, final_params)

    if isinstance(result, list) and result:
        return result[0]
    elif isinstance(result, dict) and result.get("rows"):
        return result["rows"][0]
    elif isinstance(result, dict) and "user_id" in result: # If it's already the flat dict
        return result
    return {"error": f"Update failed or unexpected result format. Result: {result}"}


async def get_user_activities(user_id: str) -> list:
    """
    Get all user activities (chat messages) for a user.
    Args:
        user_id (str): The user's UUID.
    Returns:
        list: List of activity dicts or an error dict.
    """
    sql = """
        SELECT cm.*
        FROM chat_sessions cs
        JOIN chat_messages cm ON cs.session_id = cm.session_id
        WHERE cs.user_id = :user_id
        ORDER BY cm.timestamp DESC;
    """
    result = await execute_supabase_sql(sql, {"user_id": user_id})
    if isinstance(result, list): # Assumes execute_supabase_sql returns list for SELECT
        return result
    elif isinstance(result, dict) and "error" in result:
        return result # Propagate error
    return {"error": f"Could not fetch user activities or unexpected format. Result: {result}"}
