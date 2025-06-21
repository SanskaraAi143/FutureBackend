# src/tools/budget_tools.py
"""
Tools related to budget management for users.
These tools will interact with the Supabase service layer.
"""
from typing import Dict, Any, List, Optional
from google.adk.tools import ToolContext
import json # For debug printing or data manipulation

# from src.services.supabase_service import execute_sql_query # Will be used after service layer
# Placeholder for the service function, to be replaced by import from supabase_service
async def _execute_supabase_sql_placeholder(sql: str, params: dict = None) -> Dict[str, Any]:
    print(f"[_execute_supabase_sql_placeholder Budget] SQL: {sql}, Params: {params}")
    if "SELECT" in sql.upper():
        return {"rows": [{"item_id": "mock_id", "message": "mock budget data"}]}
    if "INSERT" in sql.upper() or "UPDATE" in sql.upper() or "DELETE" in sql.upper():
        return {"rows": [{"item_id": "mock_id", "status": "success"}]}
    return {"error": "Unknown query type for budget placeholder"}


async def add_budget_item(user_id: str, item: Dict[str, Any], vendor_name: Optional[str] = None, status: Optional[str] = "Pending", tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    """
    Add a budget item for a user.
    Args:
        user_id (str): The user's UUID.
        item (dict): {"item_name": str, "category": str, "amount": number} (Note: original code used item.get('item') for item_name)
        vendor_name (Optional[str]): Vendor name.
        status (Optional[str]): Status string.
        tool_context (ToolContext, optional): ADK Tool context.
    Returns:
        dict: Inserted budget item or {"error": <str>}
    """
    # TODO: Refactor to use self.supabase_service.insert_row("budget_items", data_to_insert)
    # Validate with BudgetItemCreate schema

    item_name = item.get("item_name", item.get("item")) # Handle old 'item' key for item_name
    category = item.get("category")
    amount = item.get("amount")

    if not (user_id and item_name and category and amount is not None): # amount can be 0
        return {"error": "Missing required fields for budget item (user_id, item_name, category, amount)."}

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
    print(f"[budget_tools.add_budget_item] SQL: {sql} with params: {params}")
    # result = await execute_sql_query(sql, params) # Target state
    result = await _execute_supabase_sql_placeholder(sql, params) # Placeholder

    rows = result.get("rows")
    if rows and isinstance(rows, list) and len(rows) > 0:
        return rows[0]
    return {"error": f"Adding budget item failed. Error: {result.get('error', 'Unknown')}"}


async def get_budget_items(user_id: str, tool_context: Optional[ToolContext] = None) -> List[Dict[str, Any]]:
    """
    Get all budget items for a user.
    Args:
        user_id (str): The user's UUID.
        tool_context (ToolContext, optional): ADK Tool context.
    Returns:
        list: List of budget item dicts. Returns empty list on error or if none found.
    """
    # TODO: Refactor to use self.supabase_service.fetch_all("budget_items", {"user_id": user_id})
    sql = "SELECT * FROM budget_items WHERE user_id = :user_id;"
    # result = await execute_sql_query(sql, {"user_id": user_id}) # Target state
    result = await _execute_supabase_sql_placeholder(sql, {"user_id": user_id}) # Placeholder

    print(f"[budget_tools.get_budget_items] Result for user_id {user_id}: {result}")
    rows = result.get("rows")
    if rows and isinstance(rows, list):
        return rows
    return [] # Consistent return type for lists


async def update_budget_item(item_id: str, data: Dict[str, Any], tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    """
    Update a budget item by item_id.
    Args:
        item_id (str): The budget item's UUID.
        data (dict): Fields to update (e.g., amount, status).
        tool_context (ToolContext, optional): ADK Tool context.
    Returns:
        dict: Updated budget item with "status":"success" or an error dict {"status":"error", "error":...}
    """
    # TODO: Refactor to use self.supabase_service.update_row("budget_items", {"item_id": item_id}, data)
    # Validate with BudgetItemUpdate schema
    if not item_id:
        return {"status": "error", "error": "Item ID is required."}
    if not isinstance(data, dict) or not data:
        return {"status": "error", "error": "Data must be a non-empty dictionary."}

    set_clauses = [f"{k} = :{k}" for k in data.keys()]
    set_clause = ", ".join(set_clauses)
    sql = f"UPDATE budget_items SET {set_clause} WHERE item_id = :item_id RETURNING *;"
    params = {**data, "item_id": item_id}

    print(f"[budget_tools.update_budget_item] Executing SQL: {sql} with params: {params}")
    # result = await execute_sql_query(sql, params) # Target state
    result = await _execute_supabase_sql_placeholder(sql, params) # Placeholder

    rows = result.get("rows")
    if rows and isinstance(rows, list) and len(rows) > 0:
        return {"status": "success", "data": rows[0]}

    # Original code had a complex return, this simplifies to always include 'status'
    # If result itself contains an error from the DB call, propagate it
    db_error = result.get("error")
    if db_error:
         return {"status": "error", "error": f"Updating budget item failed: {db_error}"}
    return {"status": "error", "error": f"Updating budget item failed or item_id {item_id} not found."}


async def delete_budget_item(item_id: str, tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    """
    Delete a budget item by item_id.
    Args:
        item_id (str): The budget item's UUID.
        tool_context (ToolContext, optional): ADK Tool context.
    Returns:
        dict: {"status": "success"} or {"status": "error", "error": <str>}
    """
    # TODO: Refactor to use self.supabase_service.delete_row("budget_items", {"item_id": item_id})
    if not item_id:
        return {"status": "error", "error": "Item ID is required."}

    sql = "DELETE FROM budget_items WHERE item_id = :item_id RETURNING item_id;" # RETURNING helps confirm deletion
    params = {"item_id": item_id}
    print(f"[budget_tools.delete_budget_item] SQL: {sql} with params: {params}")
    # result = await execute_sql_query(sql, params) # Target state
    result = await _execute_supabase_sql_placeholder(sql, params) # Placeholder

    rows = result.get("rows")
    # If RETURNING item_id was successful and we got rows back, it means deletion happened.
    if rows and isinstance(rows, list) and len(rows) > 0 and rows[0].get("item_id") == item_id:
        return {"status": "success", "deleted_item_id": item_id}
    elif not result.get("error"): # No rows returned, but no DB error, means item might not have existed
        return {"status": "success", "message": f"Item with id {item_id} not found or already deleted."}

    return {"status": "error", "error": f"Deletion failed for item_id {item_id}. Error: {result.get('error', 'Unknown')}"}


# This is a utility/business logic function, not directly a DB interaction tool, so it stays.
async def suggest_budget_allocations(total_budget: float, preferences: Optional[Dict[str, Any]] = None, tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    """
    Suggests budget allocations based on total budget and optional user preferences.
    This is a business logic function that might not directly call a DB service for this step,
    but could use data fetched by other tools/services.

    Args:
        total_budget (float): The total available budget.
        preferences (Optional[Dict[str, Any]]): User preferences that might influence allocations.
        tool_context (ToolContext, optional): ADK Tool context.

    Returns:
        Dict[str, Any]: A dictionary with suggested allocations per category or an error message.
    """
    if total_budget <= 0:
        return {"error": "Total budget must be positive."}

    # Example allocation logic (can be made more sophisticated)
    # These categories and splits should ideally come from a configuration or a more dynamic source
    base_categories_split = {
        "Venue": 0.30,
        "Catering": 0.20,
        "Photography": 0.10,
        "Decorations": 0.10,
        "Attire": 0.10,
        "Entertainment": 0.05,
        "Miscellaneous": 0.15 # Ensure splits sum to 1.0
    }

    # Adjust based on preferences if provided (simplified example)
    # This logic can be expanded significantly.
    # For instance, preferences could specify "high-priority" categories.
    # if preferences:
    #     if preferences.get("focus_on") == "venue_and_catering":
    #         # Example: Increase venue/catering, decrease misc. Needs to re-normalize.
    #         pass # More complex logic needed here for re-normalization

    allocations = {
        category: round(total_budget * percentage, 2)
        for category, percentage in base_categories_split.items()
    }

    # Ensure the sum of allocations matches total_budget due to rounding
    current_sum = sum(allocations.values())
    difference = round(total_budget - current_sum, 2)
    if difference != 0 and allocations: # Add difference to the largest item to minimize percentage change
        largest_category = max(allocations, key=allocations.get)
        allocations[largest_category] = round(allocations[largest_category] + difference, 2)

    return {"allocations": allocations, "total_suggested": sum(allocations.values())}
