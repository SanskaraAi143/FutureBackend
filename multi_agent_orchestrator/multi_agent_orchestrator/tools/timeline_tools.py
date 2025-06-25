from typing import List, Dict, Any, Optional
from multi_agent_orchestrator.multi_agent_orchestrator.shared_libraries.helpers import execute_supabase_sql

async def get_timeline_events(user_id: str) -> List[Dict[str, Any]]:
    """
    Retrieves all timeline events for a given user.
    Args:
        user_id: The UUID of the user.
    Returns:
        A list of dictionaries, where each dictionary represents a timeline event.
        If no events are found, returns an empty list [].
        If an error occurs, returns a list containing a dict with "status": "error" and "error": <description>.
    """
    try:
        if not user_id:
            # Returning a list with an error dict to maintain type hint consistency
            return [{"status": "error", "error": "User ID is required."}]

        sql = "SELECT * FROM timeline_events WHERE user_id = :user_id"
        params = {"user_id": user_id}
        result = await execute_supabase_sql(sql, params)

        if isinstance(result, list):
            return result
        elif isinstance(result, dict) and "error" in result:
             # Propagate error from execute_supabase_sql, wrapped in a list
            return [{"status": "error", "error": result["error"]}]
        # print(f"Unexpected result from get_timeline_events: {result}")
        return [] # Default to empty list for unexpected non-error results

    except Exception as e:
        # print(f"Exception in get_timeline_events: {str(e)}")
        return [{"status": "error", "error": f"An unexpected error occurred: {str(e)}"}]

async def create_timeline_event(user_id: str, event: dict) -> Dict[str, Any]:
    """
    Create a timeline event for a user.
    Args:
        user_id (str): The user's UUID.
        event (dict): {"event_name": str, "event_date_time": str, "description": Optional[str], "location": Optional[str]}
    Returns:
        dict: {"status": "success", "data": inserted_event} or {"status": "error", "error": <str>}
    """
    if not user_id:
        return {"status": "error", "error": "User ID is required."}
    if not isinstance(event, dict):
        return {"status": "error", "error": "Event data must be a dictionary."}
    if not (event.get("event_name") and event.get("event_date_time")): # Core fields
        return {"status": "error", "error": "Missing required fields for timeline event (event_name, event_date_time)."}

    sql = (
        "INSERT INTO timeline_events (user_id, event_name, event_date_time, description, location) "
        "VALUES (:user_id, :event_name, :event_date_time, :description, :location) RETURNING *;"
    )
    try:
        params = {
            "user_id": user_id,
            "event_name": event.get("event_name"),
            "event_date_time": event.get("event_date_time"),
            "description": event.get("description"), # Will be NULL if not provided
            "location": event.get("location")      # Will be NULL if not provided
        }
        # print(f"Final SQL for create_timeline_event: {sql} with params: {params}")
        result = await execute_supabase_sql(sql, params)

        if isinstance(result, list) and result:
            return {"status": "success", "data": result[0]}
        elif isinstance(result, dict) and "event_id" in result: # If it's already the flat dict
             return {"status": "success", "data": result}
        else:
            error_detail = result.get("error") if isinstance(result, dict) else str(result)
            return {"status": "error", "error": f"Creating timeline event failed. Detail: {error_detail}"}
    except Exception as e:
        # print(f"Exception in create_timeline_event: {str(e)}")
        return {"status": "error", "error": str(e)}

async def update_timeline_event(event_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Updates an existing timeline event.
    Args:
        event_id: The UUID of the timeline event to update.
        updates: A dictionary containing the fields to update and their new values.
                 Valid keys: "event_name", "event_date_time", "description", "location".
    Returns:
        dict: {"status": "success", "data": updated_event} or {"status": "error", "error": <str>}
    """
    try:
        if not event_id:
            return {"status": "error", "error": "Event ID is required."}
        if not isinstance(updates, dict):
            return {"status": "error", "error": "Updates must be a dictionary."}
        if not updates:
            return {"status": "error", "error": "No fields to update provided."}

        valid_columns = {"event_name", "event_date_time", "description", "location"}

        set_clauses = []
        update_params = {}
        param_idx = 0

        for key, value in updates.items():
            if key in valid_columns:
                param_name = f"param_{param_idx}"
                set_clauses.append(f"{key} = :{param_name}")
                update_params[param_name] = value
                param_idx += 1
            # else:
                # Optionally, return an error for invalid keys
                # return {"status": "error", "error": f"Invalid field '{key}' for timeline event update."}

        if not set_clauses:
            return {"status": "error", "error": "No valid fields to update provided."}

        set_clause_str = ", ".join(set_clauses)
        sql = f"UPDATE timeline_events SET {set_clause_str} WHERE event_id = :event_id RETURNING *;"

        final_params = {**update_params, "event_id": event_id}
        # print(f"Executing SQL for update_timeline_event: {sql} with params: {final_params}")
        result = await execute_supabase_sql(sql, final_params)

        if isinstance(result, list) and result:
            return {"status": "success", "data": result[0]}
        elif isinstance(result, dict) and "event_id" in result: # If it's already the flat dict
             return {"status": "success", "data": result}
        else:
            error_detail = result.get("error") if isinstance(result, dict) else str(result)
            return {"status": "error", "error": f"Updating timeline event failed. Detail: {error_detail}"}

    except Exception as e:
        # print(f"Exception in update_timeline_event: {str(e)}")
        return {"status": "error", "error": f"An unexpected error occurred: {str(e)}"}
