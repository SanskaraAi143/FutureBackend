import logging
from typing import List, Dict, Any, Optional
from multi_agent_orchestrator.shared_libraries.helpers import execute_supabase_sql

# Configure logging for this module
logger = logging.getLogger(__name__)

# Whitelist of columns that can be updated by `update_timeline_event`
UPDATABLE_TIMELINE_EVENT_COLUMNS = {"event_name", "event_date_time", "description", "location"}


async def get_timeline_events(user_id: str) -> Dict[str, Any]: # Removed context
    """
    Retrieves all timeline events for a given user, ordered by event_date_time.

    Args:
        user_id (str): The UUID of the user. Must be a non-empty string.
        # context (Optional[ToolContext]): The ADK ToolContext. (Removed for schema compatibility)

    Returns:
        Dict[str, Any]:
            On success: `{"status": "success", "data": [event_dict_1, event_dict_2, ...]}` (empty if none)
            On failure: `{"status": "error", "error": "Error message"}`

    Error Handling:
        - Validates `user_id`.
        - Returns an error dict for database query failures.
        - Logs errors and actions.

    Dependencies:
        - `execute_supabase_sql` from `shared_libraries.helpers`.

    Example Usage:
        ```python
        response = await get_timeline_events("user-uuid-123")
        if response["status"] == "success":
            for event in response["data"]:
                print(f"{event['event_name']} at {event['event_date_time']}")
        else:
            print(f"Error: {response['error']}")
        ```
    """
    if not user_id or not isinstance(user_id, str):
        msg = "Invalid user_id. Must be a non-empty string."
        logger.error(f"get_timeline_events: {msg}")
        return {"status": "error", "error": msg}

    logger.info(f"get_timeline_events: Fetching timeline events for user_id: {user_id}")
    sql = "SELECT * FROM timeline_events WHERE user_id = :user_id ORDER BY event_date_time ASC;" # Added ordering
    params = {"user_id": user_id}

    try:
        result = await execute_supabase_sql(sql, params)

        if isinstance(result, dict) and "error" in result:
            logger.error(f"get_timeline_events: Database error for user {user_id}: {result['error']}")
            return {"status": "error", "error": result['error']}

        if isinstance(result, list):
            logger.info(f"get_timeline_events: Successfully retrieved {len(result)} events for user {user_id}.")
            return {"status": "success", "data": result}
        else:
            logger.warning(f"get_timeline_events: Unexpected result format for user {user_id}. Result: {result}")
            return {"status": "success", "data": []} # Default to empty list for unexpected non-error

    except Exception as e:
        logger.exception(f"get_timeline_events: Unexpected error for user {user_id}: {e}")
        return {"status": "error", "error": f"An unexpected error occurred: {str(e)}"}


async def create_timeline_event(
    user_id: str,
    event_name: str,
    event_date_time: str, # Expecting ISO format string e.g., "YYYY-MM-DDTHH:MM:SS"
    description: Optional[str] = None,
    location: Optional[str] = None
) -> Dict[str, Any]: # Removed context
    """
    Creates a new timeline event for a specified user.

    Args:
        user_id (str): The UUID of the user. Must be non-empty.
        event_name (str): Name of the event (e.g., "Sangeet Ceremony"). Must be non-empty.
        event_date_time (str): ISO formatted date-time string for the event. Must be non-empty.
                               (e.g., "2024-12-20T18:00:00"). Validation for actual datetime format is not done here.
        description (Optional[str]): Optional description for the event.
        location (Optional[str]): Optional location of the event.
        # context (Optional[ToolContext]): The ADK ToolContext. (Removed for schema compatibility)

    Returns:
        Dict[str, Any]:
            On success: `{"status": "success", "data": {created_event_dict}}`
            On failure: `{"status": "error", "error": "Error message"}`

    Error Handling:
        - Validates required parameters (user_id, event_name, event_date_time).
        - Returns an error dict for database insertion failures.
        - Logs errors and actions.

    Dependencies:
        - `execute_supabase_sql` from `shared_libraries.helpers`.

    Example Usage:
        ```python
        event_data = {
            "user_id": "user-uuid-123",
            "event_name": "Haldi Ceremony",
            "event_date_time": "2024-12-19T10:00:00",
            "description": "Turmeric ceremony at home.",
            "location": "Bride's Residence"
        }
        response = await create_timeline_event(**event_data)
        if response["status"] == "success":
            print("Event created:", response["data"])
        else:
            print(f"Error: {response['error']}")
        ```
    """
    if not all([user_id, event_name, event_date_time]) or \
       not isinstance(user_id, str) or not isinstance(event_name, str) or not isinstance(event_date_time, str):
        msg = "Invalid input: user_id, event_name, and event_date_time must be non-empty strings."
        logger.error(f"create_timeline_event: {msg}")
        return {"status": "error", "error": msg}
    # Further validation for event_date_time format could be added here if needed.

    logger.info(f"create_timeline_event: Creating event '{event_name}' for user_id: {user_id}")
    sql = (
        "INSERT INTO timeline_events (user_id, event_name, event_date_time, description, location) "
        "VALUES (:user_id, :event_name, :event_date_time, :description, :location) RETURNING *;"
    )
    params = {
        "user_id": user_id,
        "event_name": event_name,
        "event_date_time": event_date_time,
        "description": description,
        "location": location
    }

    try:
        result = await execute_supabase_sql(sql, params)

        if isinstance(result, dict) and "error" in result:
            logger.error(f"create_timeline_event: Database error for user {user_id}, event '{event_name}': {result['error']}")
            return {"status": "error", "error": result['error']}

        created_data = None
        if isinstance(result, list) and result:
            created_data = result[0]
        elif isinstance(result, dict) and "event_id" in result:
            created_data = result

        if created_data:
            logger.info(f"create_timeline_event: Successfully created event_id {created_data.get('event_id')} for user {user_id}.")
            return {"status": "success", "data": created_data}
        else:
            logger.error(f"create_timeline_event: Create failed or no data returned for user {user_id}, event '{event_name}'. DB Result: {result}")
            return {"status": "error", "error": "Creating timeline event failed or did not return data."}

    except Exception as e:
        logger.exception(f"create_timeline_event: Unexpected error for user {user_id}, event '{event_name}': {e}")
        return {"status": "error", "error": f"An unexpected error occurred: {str(e)}"}


async def update_timeline_event(
    event_id: str,
    updates: Dict[str, Any]
) -> Dict[str, Any]: # Removed context
    """
    Updates an existing timeline event by its event_id.

    Args:
        event_id (str): The UUID of the timeline event to update. Must be non-empty.
        updates (Dict[str, Any]): Dictionary of fields to update. Only keys in
                                  `UPDATABLE_TIMELINE_EVENT_COLUMNS` will be processed.
        # context (Optional[ToolContext]): The ADK ToolContext. (Removed for schema compatibility)

    Returns:
        Dict[str, Any]:
            On success: `{"status": "success", "data": {updated_event_dict}}`
            On failure: `{"status": "error", "error": "Error message"}`

    Error Handling:
        - Validates `event_id` and `updates` payload.
        - Returns error if no valid fields for update after filtering.
        - Returns error for database update failures or if event not found.
        - Logs errors.

    Dependencies:
        - `execute_supabase_sql` from `shared_libraries.helpers`.

    Example Usage:
        ```python
        update_payload = {"description": "Updated Sangeet details", "location": "New Hall"}
        response = await update_timeline_event("event-uuid-456", update_payload)
        if response["status"] == "success":
            print("Event updated:", response["data"])
        else:
            print(f"Update error: {response['error']}")
        ```
    """
    if not event_id or not isinstance(event_id, str):
        logger.error("update_timeline_event: Invalid event_id provided.")
        return {"status": "error", "error": "Invalid event_id. Must be a non-empty string."}
    if not updates or not isinstance(updates, dict):
        logger.error(f"update_timeline_event: Invalid or empty updates payload for event_id {event_id}.")
        return {"status": "error", "error": "Updates payload must be a non-empty dictionary."}

    logger.info(f"update_timeline_event: Attempting to update event_id: {event_id} with updates: {updates}")

    fields_to_set = {}
    for key, value in updates.items():
        if key in UPDATABLE_TIMELINE_EVENT_COLUMNS:
            fields_to_set[key] = value
        else:
            logger.warning(f"update_timeline_event: Ignored invalid or non-updatable field '{key}' for event {event_id}.")

    if not fields_to_set:
        logger.warning(f"update_timeline_event: No valid fields to update for event_id {event_id} from payload {updates}.")
        return {"status": "error", "error": "No valid fields provided for update."}

    set_clause_parts = []
    update_params = {}
    param_idx = 0
    for k, v in fields_to_set.items():
        param_name = f"val{param_idx}"
        set_clause_parts.append(f"{k} = :{param_name}")
        update_params[param_name] = v
        param_idx += 1

    set_clause_str = ", ".join(set_clause_parts)
    sql = f"UPDATE timeline_events SET {set_clause_str} WHERE event_id = :event_id_param RETURNING *;"
    final_params = {**update_params, "event_id_param": event_id}

    try:
        result = await execute_supabase_sql(sql, final_params)

        if isinstance(result, dict) and "error" in result:
            logger.error(f"update_timeline_event: Database error for event_id {event_id}: {result['error']}")
            return {"status": "error", "error": result['error']}

        updated_data = None
        if isinstance(result, list) and result:
            updated_data = result[0]
        elif isinstance(result, dict) and "event_id" in result:
            updated_data = result

        if updated_data:
            logger.info(f"update_timeline_event: Successfully updated event_id {event_id}.")
            return {"status": "success", "data": updated_data}
        else:
            logger.error(f"update_timeline_event: Update failed for event_id {event_id} (event possibly not found or no data returned). DB Result: {result}")
            return {"status": "error", "error": "Update failed, event not found, or no data returned."}

    except Exception as e:
        logger.exception(f"update_timeline_event: Unexpected error for event_id {event_id}: {e}")
        return {"status": "error", "error": f"An unexpected error occurred: {str(e)}"}
