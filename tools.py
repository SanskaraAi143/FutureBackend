# tools.py - Custom tools for ADK agents to interact with Supabase and Astra DB

from typing import List, Dict, Any, Optional
from .config import astra_db # Import configured clients
import json
import os
import asyncio
import dotenv
import ast
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

dotenv.load_dotenv('.env')
SUPABASE_ACCESS_TOKEN = os.getenv("SUPABASE_ACCESS_TOKEN")

# Global MCPToolset instance for Supabase
_supabase_mcp_toolset = None
_supabase_tools = None

async def init_supabase_mcp():
    global _supabase_mcp_toolset, _supabase_tools
    if _supabase_mcp_toolset is None:
        mcp = MCPToolset(
            connection_params=StdioServerParameters(
                command='npx',
                args=["-y", "@supabase/mcp-server-supabase@latest", "--access-token", SUPABASE_ACCESS_TOKEN],
            ),
            tool_filter=["execute_sql","list_tables"]
        )
        tools = await mcp.get_tools()
        _supabase_mcp_toolset = mcp
        _supabase_tools = {tool.name: tool for tool in tools}
    return _supabase_mcp_toolset, _supabase_tools

def sql_quote_value(val):
    """
    Safely quote and format a value for SQL inlining.
    Args:
        val: The value to quote (str, int, float, dict, list, or None).
    Returns:
        str: The SQL-safe string representation of the value.
    """
    if val is None:
        return 'NULL'
    if isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, dict) or isinstance(val, list):
        return f"'{json.dumps(val).replace("'", "''")}'"
    return f"'{str(val).replace("'", "''")}'"

async def execute_supabase_sql(sql: str, params: dict = None):
    """
    Execute a SQL query against Supabase via the MCP server.
    Args:
        sql (str): The SQL query string, with :param placeholders.
        params (dict, optional): Parameters to inline into the SQL string.
    Returns:
        Any: Parsed result (list or dict), or dict with 'error'.
    """
    mcp, tools = await init_supabase_mcp()
    tool = tools.get("execute_sql")
    if not tool:
        raise RuntimeError("Supabase MCP execute_sql tool not found.")
    try:
        # Inline params robustly
        if params:
            for k, v in params.items():
                sql = sql.replace(f":{k}", sql_quote_value(v))
        args = {"query": sql}
        project_id = os.getenv("SUPABASE_PROJECT_ID") or "lylsxoupakajkuisjdfl"
        args["project_id"] = project_id
        print(f"[MCP SQL DEBUG] Final SQL: {sql}")
        print(f"[MCP SQL DEBUG] Args sent to MCP: {args}")
        result = await tool.run_async(args=args, tool_context=None)
        if hasattr(result, "content") and result.content:
            text = result.content[0].text if hasattr(result.content[0], "text") else str(result.content[0])
            try:
                parsed = json.loads(text)
                return parsed
            except Exception:
                try:
                    parsed = ast.literal_eval(text)
                    return parsed
                except Exception:
                    return {"error": f"Unparsable tool result: {text}"}
        return {"error": "No content returned from tool."}
    except Exception as e:
        return {"error": str(e)}

# --- Supabase Tools (MCP-based, async) ---

async def get_user_id(email: str) -> dict:
    """
    Get the user_id for a given email from the users table.
    Args:
        email (str): The user's email address.
    Returns:
        dict: {"user_id": <uuid>} or {"error": <str>}
    """
    sql = "SELECT user_id FROM users WHERE email = :email LIMIT 1;"
    result = await execute_supabase_sql(sql, {"email": email})
    print(f"SQL executed: {sql} with params: {json.dumps({'email': email})} result: {result}")
    # Handle both dict-with-rows and list result
    if isinstance(result, dict) and result.get("rows"):
        return result["rows"][0]
    elif isinstance(result, list) and result:
        return result[0]
    return {"error": "User not found."}

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
    if isinstance(result, dict) and result.get("rows"):
        return result["rows"][0]
    elif isinstance(result, list) and result:
        return result[0]
    return {"error": "User not found."}

async def update_user_data(user_id: str, data: dict) -> dict:
    """
    Update user data for a given user_id. Only allowed columns are updated; extra fields go into preferences.
    Args:
        user_id (str): The user's UUID.
        data (dict): Fields to update (top-level or preferences).
    Returns:
        dict: Updated user data or {"error": <str>}
    """
    USERS_TABLE_COLUMNS = {
        "user_id", "supabase_auth_uid", "email", "display_name", "created_at", "updated_at",
        "wedding_date", "wedding_location", "wedding_tradition", "preferences", "user_type"
    }
    preferences_update = data.pop("preferences", None) or {}
    extra_prefs = {k: data.pop(k) for k in list(data.keys()) if k not in USERS_TABLE_COLUMNS}
    if extra_prefs:
        preferences_update.update(extra_prefs)
    if preferences_update:
        # Fetch current preferences
        user = await get_user_data(user_id)
        current_prefs = user.get("preferences") if user and isinstance(user, dict) else {}
        if not isinstance(current_prefs, dict):
            current_prefs = {}
        current_prefs.update(preferences_update)
        data["preferences"] = current_prefs
    # Always JSON-serialize preferences if present
    if "preferences" in data:
        data["preferences"] = json.dumps(data["preferences"])
    # Build SET clause
    set_clause = ", ".join([f"{k} = :{k}" for k in data.keys()])
    sql = f"UPDATE users SET {set_clause} WHERE user_id = :user_id RETURNING *;"
    params = {**data, "user_id": user_id}
    print(f"Final SQL for update_user_data: {sql} with params: {params}")
    result = await execute_supabase_sql(sql, params)
    if result and isinstance(result, dict) and result.get("rows"):
        return result["rows"][0]
    elif isinstance(result, list) and result:
        return result[0]
    return {"error": "Update failed."}

async def list_vendors(filters: Optional[dict] = None) -> list:
    """
    List all vendors, optionally filtered by category, city, or other fields.
    Args:
        filters (Optional[dict]): Filter fields (e.g., {"vendor_category": "Venue"}).
    Returns:
        list: List of vendor dicts.
    """
    sql = "SELECT * FROM vendors"
    params = {}
    if filters:
        where_clauses = []
        for key, value in filters.items():
            if key == "address->>'city'":
                where_clauses.append("address->>'city' ILIKE :city")
                params["city"] = f"%{value}%"
            else:
                where_clauses.append(f"{key} ILIKE :{key}")
                params[key] = f"%{value}%"
        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)
    result = await execute_supabase_sql(sql, params)
    if isinstance(result, dict) and result.get("rows"):
        return result["rows"]
    elif isinstance(result, list):
        return result
    return []

async def get_vendor_details(vendor_id: str) -> dict:
    """
    Get all details for a vendor by vendor_id.
    Args:
        vendor_id (str): The vendor's UUID.
    Returns:
        dict: Vendor data or {"error": <str>}
    """
    sql = "SELECT * FROM vendors WHERE vendor_id = :vendor_id LIMIT 1;"
    result = await execute_supabase_sql(sql, {"vendor_id": vendor_id})
    if isinstance(result, dict) and result.get("rows"):
        return result["rows"][0]
    elif isinstance(result, list) and result:
        return result[0]
    return {"error": "Vendor not found."}

async def add_budget_item(user_id: str, item: dict, vendor_name: Optional[str] = None, status: Optional[str] = "Pending") -> dict:
    """
    Add a budget item for a user.
    Args:
        user_id (str): The user's UUID.
        item (dict): {"item": str, "category": str, "amount": number}
        vendor_name (Optional[str]): Vendor name.
        status (Optional[str]): Status string.
    Returns:
        dict: Inserted budget item or {"error": <str>}
    """
    # Ensure all required fields
    if not (user_id and item.get("item") and item.get("category") and item.get("amount")):
        return {"error": "Missing required fields for budget item."}
    sql = (
        "INSERT INTO budget_items (user_id, item_name, category, amount, vendor_name, status) "
        "VALUES (:user_id, :item_name, :category, :amount, :vendor_name, :status) RETURNING *;"
    )
    params = {
        "user_id": user_id,
        "item_name": item.get("item"),
        "category": item.get("category"),
        "amount": item.get("amount"),
        "vendor_name": vendor_name,
        "status": status
    }
    print(f"Final SQL for add_budget_item: {sql} with params: {params}")
    result = await execute_supabase_sql(sql, params)
    if isinstance(result, dict) and result.get("rows"):
        return result["rows"][0]
    elif isinstance(result, list) and result:
        return result[0]
    return {"error": "Adding budget item failed."}

async def get_budget_items(user_id: str) -> list:
    """
    Get all budget items for a user.
    Args:
        user_id (str): The user's UUID.
    Returns:
        list: List of budget item dicts.
    """
    sql = "SELECT * FROM budget_items WHERE user_id = :user_id;"
    result = await execute_supabase_sql(sql, {"user_id": user_id})
    if isinstance(result, dict) and result.get("rows"):
        return result["rows"]
    elif isinstance(result, list):
        return result
    return []

async def update_budget_item(item_id: str, **kwargs) -> dict:
    """
    Update a budget item by item_id.
    Args:
        item_id (str): The budget item's UUID.
        kwargs: Fields to update (e.g., amount, status).
    Returns:
        dict: Updated budget item or {"error": <str>}
    """
    if not kwargs:
        return {"error": "No fields to update."}
    set_clause = ", ".join([f"{k} = :{k}" for k in kwargs.keys()])
    sql = f"UPDATE budget_items SET {set_clause} WHERE item_id = :item_id RETURNING *;"
    params = {**kwargs, "item_id": item_id}
    print(f"Final SQL for update_budget_item: {sql} with params: {params}")
    result = await execute_supabase_sql(sql, params)
    if isinstance(result, dict) and result.get("rows"):
        return result["rows"][0]
    elif isinstance(result, list) and result:
        return result[0]
    return {"error": "Updating budget item failed."}

async def delete_budget_item(item_id: str) -> dict:
    """
    Delete a budget item by item_id.
    Args:
        item_id (str): The budget item's UUID.
    Returns:
        dict: {"status": "success"} or {"error": <str>}
    """
    sql = "DELETE FROM budget_items WHERE item_id = :item_id RETURNING item_id;"
    params = {"item_id": item_id}
    print(f"Final SQL for delete_budget_item: {sql} with params: {params}")
    result = await execute_supabase_sql(sql, params)
    if isinstance(result, dict) and result.get("rows"):
        return {"status": "success"}
    elif isinstance(result, list) and result:
        return {"status": "success"}
    return {"error": "Deletion failed."}

# --- Astra DB Tools ---

def search_rituals(question: str) -> List[Dict[str, Any]]:
    """
    Searches for rituals in Astra DB using vector search.  Returns top 3 most relevant documents.  Handles CollectionExceptions.
    """
    """ input: question - a string containing the user's query about rituals"""
    try:
        ritual_data = astra_db.get_collection("ritual_data")
        result = ritual_data.find(
            projection={"$vectorize": True},
            sort={"$vectorize": question},
            limit=3
            
        )
        contexts = [doc for doc in result]
        return contexts
    except Exception as e:
        return {"error": f"An unexpected error occurred during ritual search: {e}"}



# --- AGENT/TOOL PROMPT INPUT/OUTPUT RECOMMENDATIONS (ENHANCED) ---
# For each tool, specify clear, robust input and output formats for agent use.
# For agents/sub-agents, specify orchestration and error handling best practices.

# get_user_id
# Input: {"email": <user_email:str>}
# Output: {"user_id": <uuid>} or {"error": <str>}

# get_user_data
# Input: {"user_id": <uuid>}
# Output: {user_data_dict} or {"error": <str>}

# update_user_data
# Input: {"user_id": <uuid>, "data": {fields to update}}
# Output: {updated_user_data_dict} or {"error": <str>}

# list_vendors
# Input: {"filters": {optional filter dict}}
# Output: [vendor_dict, ...]

# get_vendor_details
# Input: {"vendor_id": <uuid>}
# Output: {vendor_dict} or {"error": <str>}

# add_budget_item
# Input: {"user_id": <uuid>, "item": {"item": str, "category": str, "amount": number}}
# Output: {inserted_budget_item_dict} or {"error": <str>}

# get_budget_items
# Input: {"user_id": <uuid>}
# Output: [budget_item_dict, ...] or {"error": <str>}

# update_budget_item
# Input: {"item_id": <uuid>, "fields": {fields to update}}
# Output: {updated_budget_item_dict} or {"error": <str>}

# delete_budget_item
# Input: {"item_id": <uuid>}
# Output: {"status": "success"} or {"error": <str>}

if __name__ == "__main__":
    # Example usage
    async def main():
        await init_supabase_mcp()
        # Removed call to list_tables (no longer exists)
        print("Supabase MCP initialized.")
    asyncio.run(main())