from typing import List, Dict, Any, Optional
from multi_agent_orchestrator.multi_agent_orchestrator.shared_libraries.helpers import execute_supabase_sql

async def add_budget_item(user_id: str, item: dict, vendor_name: Optional[str] = None, status: Optional[str] = "Pending") -> Dict[str, Any]:
    """
    Add a budget item for a user.
    Args:
        user_id (str): The user's UUID.
        item (dict): {"item_name": str, "category": str, "amount": number} - note: changed "item" to "item_name" to match DB
        vendor_name (Optional[str]): Vendor name.
        status (Optional[str]): Status string.
    Returns:
        dict: Inserted budget item or {"error": <str>}
    """
    if not (user_id and item.get("item_name") and item.get("category") and item.get("amount") is not None):
        return {"error": "Missing required fields for budget item (user_id, item_name, category, amount)."}

    sql = (
        "INSERT INTO budget_items (user_id, item_name, category, amount, vendor_name, status) "
        "VALUES (:user_id, :item_name, :category, :amount, :vendor_name, :status) RETURNING *;"
    )
    params = {
        "user_id": user_id,
        "item_name": item.get("item_name"), # Changed from item.get("item")
        "category": item.get("category"),
        "amount": item.get("amount"),
        "vendor_name": vendor_name,
        "status": status
    }
    # print(f"Final SQL for add_budget_item: {sql} with params: {params}")
    result = await execute_supabase_sql(sql, params)
    if isinstance(result, list) and result:
        return result[0]
    elif isinstance(result, dict) and "item_id" in result: # If it's already the flat dict
        return result
    return {"error": f"Adding budget item failed or unexpected result. Result: {result}"}

async def get_budget_items(user_id: str) -> List[Dict[str, Any]]:
    """
    Get all budget items for a user.
    Args:
        user_id (str): The user's UUID.
    Returns:
        list: List of budget item dicts, or an error dict if issues.
    """
    sql = "SELECT * FROM budget_items WHERE user_id = :user_id;"
    result = await execute_supabase_sql(sql, {"user_id": user_id})
    # print(f"result of get_budget_items: {result}")
    if isinstance(result, list):
        return result
    elif isinstance(result, dict) and "error" in result:
        return result # Propagate error
    # print(f"Unexpected result from get_budget_items: {result}")
    return [] # Default to empty list

async def update_budget_item(item_id: str, data: dict) -> Dict[str, Any]:
    """
    Update a budget item by item_id.
    Args:
        item_id (str): The budget item's UUID.
        data (dict): Fields to update (e.g., amount, status, item_name, category).
    Returns:
        dict: {"status": "success", "data": updated_item} or {"status": "error", "error": <str>}
    """
    try:
        if not item_id:
            return {"status": "error", "error": "Item ID is required."}
        if not isinstance(data, dict):
            return {"status": "error", "error": "Data must be a dictionary."}
        if not data:
            return {"status": "error", "error": "No fields to update provided."}

        # Whitelist valid columns for budget_items table to prevent injection with keys
        valid_columns = {"item_name", "category", "amount", "vendor_name", "status"}

        set_clauses = []
        update_params = {}
        param_idx = 0

        for k, v in data.items():
            if k in valid_columns:
                param_name = f"param_{param_idx}"
                set_clauses.append(f"{k} = :{param_name}")
                update_params[param_name] = v
                param_idx +=1
            # Silently ignore invalid keys, or raise error:
            # else:
            #     return {"status": "error", "error": f"Invalid field '{k}' for budget item."}


        if not set_clauses:
            return {"status": "error", "error": "No valid fields to update."}

        set_clause_str = ", ".join(set_clauses)
        sql = f"UPDATE budget_items SET {set_clause_str} WHERE item_id = :item_id RETURNING *;"

        final_params = {**update_params, "item_id": item_id}
        # print(f"Executing SQL for update_budget_item: {sql} with params: {final_params}")

        result = await execute_supabase_sql(sql, final_params)

        if isinstance(result, list) and result:
            return {"status": "success", "data": result[0]}
        elif isinstance(result, dict) and "item_id" in result: # If it's already the flat dict
             return {"status": "success", "data": result}
        else: # Error from execute_supabase_sql or unexpected format
            error_detail = result.get("error") if isinstance(result, dict) else str(result)
            return {"status": "error", "error": f"Updating budget item failed: {error_detail}"}

    except Exception as e:
        return {"status": "error", "error": str(e)}

async def delete_budget_item(item_id: str) -> Dict[str, str]:
    """
    Delete a budget item by item_id.
    Args:
        item_id (str): The budget item's UUID.
    Returns:
        dict: {"status": "success"} or {"status": "error", "error": <str>}
    """
    try:
        if not item_id:
            return {"status": "error", "error": "Item ID is required."}

        sql = "DELETE FROM budget_items WHERE item_id = :item_id RETURNING item_id;"
        params = {"item_id": item_id}
        # print(f"Final SQL for delete_budget_item: {sql} with params: {params}")
        result = await execute_supabase_sql(sql, params)

        # Successful deletion might return the deleted item_id or an empty list if RETURNING is not fully processed by MCP layer as expected
        if (isinstance(result, list) and result and result[0].get("item_id") == item_id) or \
           (isinstance(result, dict) and result.get("item_id") == item_id) or \
           (isinstance(result, list) and not result): # Some DBs return empty list on successful delete with RETURNING if no rows matched (though item_id implies one should)
            return {"status": "success", "message": f"Budget item {item_id} deleted."}
        else:
            error_detail = result.get("error") if isinstance(result, dict) else str(result)
            return {"status": "error", "error": f"Deletion failed or item not found. Detail: {error_detail}"}

    except Exception as e:
        return {"status": "error", "error": str(e)}
