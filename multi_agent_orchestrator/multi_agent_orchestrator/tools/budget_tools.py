import logging
from typing import List, Dict, Any, Optional
from google.adk.tools import ToolContext # For type hinting context

from ..shared_libraries.helpers import execute_supabase_sql # Relative import

# Configure logging for this module
logger = logging.getLogger(__name__)

# Whitelist of columns that can be updated by `update_budget_item`
# This helps prevent unintended updates to columns like 'user_id' or 'item_id' via the data payload.
UPDATABLE_BUDGET_ITEM_COLUMNS = {"item_name", "category", "amount", "vendor_name", "status"}


async def add_budget_item(
    user_id: str,
    item_name: str,
    category: str,
    amount: float, # Enforce float for amount
    vendor_name: Optional[str] = None,
    status: Optional[str] = "Pending"
) -> Dict[str, Any]: # Removed context
    """
    Adds a new budget item for a specified user.

    Args:
        user_id (str): The UUID of the user. Must be a non-empty string.
        item_name (str): Name of the budget item (e.g., "Venue Rental"). Must be non-empty.
        category (str): Category of the budget item (e.g., "Venue", "Catering"). Must be non-empty.
        amount (float): Cost of the budget item. Must be a non-negative number.
        vendor_name (Optional[str]): Name of the associated vendor. Defaults to None.
        status (Optional[str]): Status of the budget item (e.g., "Pending", "Paid"). Defaults to "Pending".
        # context (Optional[ToolContext]): The ADK ToolContext. (Removed for schema compatibility)

    Returns:
        Dict[str, Any]:
            On success: `{"status": "success", "data": {inserted_budget_item_dict}}`
            On failure: `{"status": "error", "error": "Error message"}`

    Error Handling:
        - Validates required parameters (user_id, item_name, category, amount).
        - Ensures amount is a non-negative float.
        - Returns an error dict for database insertion failures.
        - Logs errors and important actions.

    Dependencies:
        - `execute_supabase_sql` from `shared_libraries.helpers`.

    Example Usage:
        ```python
        item_details = {
            "user_id": "user-uuid-123",
            "item_name": "DJ Services",
            "category": "Entertainment",
            "amount": 500.00,
            "status": "Confirmed"
        }
        response = await add_budget_item(**item_details)
        if response["status"] == "success":
            print("Budget item added:", response["data"])
        else:
            print(f"Error: {response['error']}")
        ```
    """
    if not all([user_id, item_name, category]) or not isinstance(user_id, str) \
            or not isinstance(item_name, str) or not isinstance(category, str):
        msg = "Invalid input: user_id, item_name, and category must be non-empty strings."
        logger.error(f"add_budget_item: {msg}")
        return {"status": "error", "error": msg}

    try:
        amount = float(amount) # Ensure amount is float
        if amount < 0:
            msg = "Invalid amount: Budget item amount cannot be negative."
            logger.error(f"add_budget_item: {msg} (user: {user_id}, item: {item_name})")
            return {"status": "error", "error": msg}
    except ValueError:
        msg = "Invalid amount: Budget item amount must be a valid number."
        logger.error(f"add_budget_item: {msg} (user: {user_id}, item: {item_name})")
        return {"status": "error", "error": msg}

    logger.info(f"add_budget_item: Adding item '{item_name}' for user_id: {user_id}")

    sql = (
        "INSERT INTO budget_items (user_id, item_name, category, amount, vendor_name, status) "
        "VALUES (:user_id, :item_name, :category, :amount, :vendor_name, :status) RETURNING *;"
    )
    params = {
        "user_id": user_id,
        "item_name": item_name,
        "category": category,
        "amount": amount,
        "vendor_name": vendor_name,
        "status": status
    }

    try:
        result = await execute_supabase_sql(sql, params)

        if isinstance(result, dict) and "error" in result:
            logger.error(f"add_budget_item: Database error for user {user_id}, item '{item_name}': {result['error']}")
            return {"status": "error", "error": result['error']}

        item_data = None
        if isinstance(result, list) and result:
            item_data = result[0]
        elif isinstance(result, dict) and "item_id" in result: # Direct dict if MCP returns single object
            item_data = result

        if item_data:
            logger.info(f"add_budget_item: Successfully added item_id {item_data.get('item_id')} for user {user_id}.")
            return {"status": "success", "data": item_data}
        else:
            logger.error(f"add_budget_item: Add failed or no data returned for user {user_id}, item '{item_name}'. DB Result: {result}")
            return {"status": "error", "error": "Adding budget item failed or did not return data."}

    except Exception as e:
        logger.exception(f"add_budget_item: Unexpected error for user {user_id}, item '{item_name}': {e}")
        return {"status": "error", "error": f"An unexpected error occurred: {str(e)}"}


async def get_budget_items(user_id: str) -> Dict[str, Any]: # Removed context
    """
    Retrieves all budget items for a specified user.

    Args:
        user_id (str): The UUID of the user. Must be a non-empty string.
        # context (Optional[ToolContext]): The ADK ToolContext. (Removed for schema compatibility)

    Returns:
        Dict[str, Any]:
            On success: `{"status": "success", "data": [budget_item_1, budget_item_2, ...]}` (empty list if none)
            On failure: `{"status": "error", "error": "Error message"}`

    Error Handling:
        - Returns an error dict if user_id is invalid.
        - Returns an error dict for database query failures.
        - Logs errors.

    Dependencies:
        - `execute_supabase_sql` from `shared_libraries.helpers`.

    Example Usage:
        ```python
        response = await get_budget_items("user-uuid-123")
        if response["status"] == "success":
            for item in response["data"]:
                print(item["item_name"])
        else:
            print(f"Error: {response['error']}")
        ```
    """
    if not user_id or not isinstance(user_id, str):
        logger.error("get_budget_items: Invalid user_id provided.")
        return {"status": "error", "error": "Invalid user_id. Must be a non-empty string."}

    logger.info(f"get_budget_items: Fetching budget items for user_id: {user_id}")
    sql = "SELECT * FROM budget_items WHERE user_id = :user_id;"

    try:
        result = await execute_supabase_sql(sql, {"user_id": user_id})

        if isinstance(result, dict) and "error" in result:
            logger.error(f"get_budget_items: Database error for user {user_id}: {result['error']}")
            return {"status": "error", "error": result['error']}

        if isinstance(result, list):
            logger.info(f"get_budget_items: Successfully retrieved {len(result)} items for user {user_id}.")
            return {"status": "success", "data": result}
        else:
            logger.warning(f"get_budget_items: Unexpected result format for user {user_id}. Result: {result}")
            # Assuming empty list is valid if DB returns non-list, non-error (though helpers should ensure dict or list)
            return {"status": "success", "data": []}

    except Exception as e:
        logger.exception(f"get_budget_items: Unexpected error for user {user_id}: {e}")
        return {"status": "error", "error": f"An unexpected error occurred: {str(e)}"}


async def update_budget_item(item_id: str, data: Dict[str, Any]) -> Dict[str, Any]: # Removed context
    """
    Updates an existing budget item by its item_id.

    Args:
        item_id (str): The UUID of the budget item to update. Must be a non-empty string.
        data (Dict[str, Any]): Dictionary of fields to update. Only keys in
                               `UPDATABLE_BUDGET_ITEM_COLUMNS` will be processed.
                               Amount will be converted to float; other values used as is.
        # context (Optional[ToolContext]): The ADK ToolContext. (Removed for schema compatibility)

    Returns:
        Dict[str, Any]:
            On success: `{"status": "success", "data": {updated_budget_item_dict}}`
            On failure: `{"status": "error", "error": "Error message"}`

    Error Handling:
        - Validates item_id and data payload.
        - Returns an error if no valid fields for update are provided after filtering.
        - Returns an error for database update failures or if item not found.
        - Logs errors.

    Dependencies:
        - `execute_supabase_sql` from `shared_libraries.helpers`.

    Example Usage:
        ```python
        update_payload = {"amount": 1200.50, "status": "Paid"}
        response = await update_budget_item("item-uuid-456", update_payload)
        if response["status"] == "success":
            print("Item updated:", response["data"])
        else:
            print(f"Update error: {response['error']}")
        ```
    """
    if not item_id or not isinstance(item_id, str):
        logger.error("update_budget_item: Invalid item_id provided.")
        return {"status": "error", "error": "Invalid item_id. Must be a non-empty string."}
    if not data or not isinstance(data, dict):
        logger.error(f"update_budget_item: Invalid or empty data payload for item_id {item_id}.")
        return {"status": "error", "error": "Data payload must be a non-empty dictionary."}

    logger.info(f"update_budget_item: Attempting to update item_id: {item_id} with data: {data}")

    fields_to_set = {}
    for key, value in data.items():
        if key in UPDATABLE_BUDGET_ITEM_COLUMNS:
            if key == "amount":
                try:
                    fields_to_set[key] = float(value)
                    if fields_to_set[key] < 0:
                         logger.warning(f"update_budget_item: Negative amount {value} provided for item {item_id}. Clamping to 0 or erroring based on policy (here, allowing).")
                         # Or: return {"status": "error", "error": "Amount cannot be negative."}
                except (ValueError, TypeError):
                    logger.error(f"update_budget_item: Invalid amount '{value}' for item {item_id}. Must be a number.")
                    return {"status": "error", "error": f"Invalid amount '{value}'. Must be a number."}
            else:
                fields_to_set[key] = value
        else:
            logger.warning(f"update_budget_item: Ignored invalid or non-updatable field '{key}' for item {item_id}.")

    if not fields_to_set:
        logger.warning(f"update_budget_item: No valid fields to update for item_id {item_id} from payload {data}.")
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
    sql = f"UPDATE budget_items SET {set_clause_str} WHERE item_id = :item_id_param RETURNING *;"
    final_params = {**update_params, "item_id_param": item_id}

    try:
        result = await execute_supabase_sql(sql, final_params)

        if isinstance(result, dict) and "error" in result:
            logger.error(f"update_budget_item: Database error for item_id {item_id}: {result['error']}")
            return {"status": "error", "error": result['error']}

        updated_data = None
        if isinstance(result, list) and result:
            updated_data = result[0]
        elif isinstance(result, dict) and "item_id" in result:
            updated_data = result

        if updated_data:
            logger.info(f"update_budget_item: Successfully updated item_id {item_id}.")
            return {"status": "success", "data": updated_data}
        else:
            logger.error(f"update_budget_item: Update failed for item_id {item_id} (item possibly not found or no data returned). DB Result: {result}")
            return {"status": "error", "error": "Update failed, item not found, or no data returned."}

    except Exception as e:
        logger.exception(f"update_budget_item: Unexpected error for item_id {item_id}: {e}")
        return {"status": "error", "error": f"An unexpected error occurred: {str(e)}"}


async def delete_budget_item(item_id: str) -> Dict[str, Any]: # Removed context
    """
    Deletes a budget item by its item_id.

    Args:
        item_id (str): The UUID of the budget item to delete. Must be a non-empty string.
        # context (Optional[ToolContext]): The ADK ToolContext. (Removed for schema compatibility)

    Returns:
        Dict[str, Any]:
            On success: `{"status": "success", "message": "Budget item deleted successfully."}`
            On failure: `{"status": "error", "error": "Error message"}` (e.g., if item not found or DB error)

    Error Handling:
        - Validates item_id.
        - Returns an error dict for database deletion failures or if item not found.
        - Logs errors.

    Dependencies:
        - `execute_supabase_sql` from `shared_libraries.helpers`.

    Example Usage:
        ```python
        response = await delete_budget_item("item-uuid-789")
        if response["status"] == "success":
            print(response["message"])
        else:
            print(f"Delete error: {response['error']}")
        ```
    """
    if not item_id or not isinstance(item_id, str):
        logger.error("delete_budget_item: Invalid item_id provided.")
        return {"status": "error", "error": "Invalid item_id. Must be a non-empty string."}

    logger.info(f"delete_budget_item: Attempting to delete item_id: {item_id}")
    # RETURNING * to check if a row was actually deleted.
    # Some DBs/clients might return an empty list if no row matched,
    # or the affected row count. execute_supabase_sql behavior might vary.
    sql = "DELETE FROM budget_items WHERE item_id = :item_id RETURNING *;"
    params = {"item_id": item_id}

    try:
        result = await execute_supabase_sql(sql, params)

        if isinstance(result, dict) and "error" in result:
            logger.error(f"delete_budget_item: Database error for item_id {item_id}: {result['error']}")
            return {"status": "error", "error": result['error']}

        # Check if RETURNING * actually gave back the deleted row
        deleted_item = None
        if isinstance(result, list) and result:
            deleted_item = result[0]
        elif isinstance(result, dict) and result.get("item_id") == item_id : # If it returns the single deleted object
            deleted_item = result

        if deleted_item:
            logger.info(f"delete_budget_item: Successfully deleted item_id {item_id}.")
            return {"status": "success", "message": f"Budget item {item_id} deleted successfully.", "data": deleted_item}
        else:
            # This case means the DELETE statement ran but no rows were affected (item_id not found)
            # or the result format was unexpected and didn't indicate a deletion.
            logger.warning(f"delete_budget_item: Item_id {item_id} not found for deletion, or no data returned. DB Result: {result}")
            return {"status": "error", "error": f"Item with ID '{item_id}' not found or deletion failed to confirm."}

    except Exception as e:
        logger.exception(f"delete_budget_item: Unexpected error for item_id {item_id}: {e}")
        return {"status": "error", "error": f"An unexpected error occurred: {str(e)}"}
