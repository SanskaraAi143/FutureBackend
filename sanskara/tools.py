# tools.py - Custom tools for ADK agents to interact with Supabase and Astra DB

from typing import List, Dict, Any, Optional
from google.adk.tools import  ToolContext, LongRunningFunctionTool
from google.adk.tools.google_search_tool import GoogleSearchTool
from sanskara.config import astra_db # Import configured clients
from typing import Optional
import json
import os
import asyncio
import dotenv
import ast
import re
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters,StdioConnectionParams

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
                command='/usr/bin/npx',
                args=["-y", "@supabase/mcp-server-supabase@latest", "--access-token", SUPABASE_ACCESS_TOKEN],
            ),
            tool_filter=["execute_sql"]
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
        val = json.dumps(val).replace("'", "''")
        return f"'{val}'"
    val = str(val).replace("'", "''")
    return f"'{val}'"

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
            print(f"[MCP SQL DEBUG] SQL before inlining: {sql}")  # Log before inlining
            for k, v in params.items():
                sql = sql.replace(f":{k}", sql_quote_value(v))
        args = {"query": sql}
        project_id = os.getenv("SUPABASE_PROJECT_ID") or "lylsxoupakajkuisjdfl"
        args["project_id"] = project_id
        print(f"[MCP SQL DEBUG] Final SQL: {sql}")
        print(f"[MCP SQL DEBUG] Args sent to MCP: {args}")
        result = await tool.run_async(args=args, tool_context=None)
        print(f"[MCP SQL DEBUG] Raw result from MCP: {result}") # Added logging
        if hasattr(result, "content") and result.content:
            text = result.content[0].text if hasattr(result.content[0], "text") else str(result.content[0])
            # Try to extract untrusted JSON if present
            untrusted_json = extract_untrusted_json(text)
            print(f"untrusted_json: {untrusted_json}")  # Debug log for untrusted JSON
            if untrusted_json is not None:
                print(f"[MCP SQL DEBUG] Extracted untrusted JSON: {untrusted_json}")
                return untrusted_json
            try:
                parsed = json.loads(text)
                return parsed
            except Exception as e1:
                print(f"[MCP SQL DEBUG] JSON parsing failed: {e1}")
                try:
                    parsed = ast.literal_eval(text)
                    return parsed
                except Exception as e2:
                    print(f"[MCP SQL DEBUG] Literal eval failed: {e2}")
                    # If parsing fails, return the raw text
                    return text
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
    return {"error": f"User not found. {result}"}

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
        user_data = result[0]
    else:
        user_data = {"error": "User not found."}

    return user_data

async def update_user_data(user_id: str, data: dict) -> dict:
    """
    Update user data for a given user_id. Only allowed columns are updated; extra fields go into preferences, user_type is cannot be updated.
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
        updated_user_data = result[0]
    else:
        updated_user_data = {"error": "Update failed."}

    return updated_user_data

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
    print(f"result of get_budget_items: {result}")
    if isinstance(result, dict) and result.get("rows"):
        return result["rows"]
    elif isinstance(result, list):
        return result
    return []

async def update_budget_item(item_id: str, data: dict) -> dict:
    """
    Update a budget item by item_id.
    Args:
        item_id (str): The budget item's UUID.
        data (dict): Fields to update (e.g., amount, status).
    Returns:
        dict:  with updated budget item or error.
    """
    try:
        if not item_id:
            raise ("Item ID is required.")
        if not isinstance(data, dict):
            raise ("Data must be a dictionary.")
        if not data:
            raise ("No fields to update.")
        set_clauses = [f"{k} = :{k}" for k in data]
        set_clause = ", ".join(set_clauses)

        sql = f"UPDATE budget_items SET {set_clause} WHERE item_id = :item_id RETURNING *;"
        params = {**data, "item_id": item_id}

        print(f"Executing SQL: {sql} with params: {params}")

        result = await execute_supabase_sql(sql, params) # type: ignore

        if isinstance(result, dict) and result.get("rows"):
            updated_budget_item = result["rows"][0]
        elif isinstance(result, list) and result:
            updated_budget_item = result[0]
        else:
            raise (f"Updating budget item failed: {result}")

        return {"status": "success", "data": updated_budget_item}
    except Exception as e:
        return {"status": "error", "error": str(e)}


async def delete_budget_item(item_id: str) -> dict:
    """
    Delete a budget item by item_id.
    Args:
        item_id (str): The budget item's UUID.
    Returns:
        dict:  with success status or error.
    """
    try:
        if not item_id:
            raise ("Item ID is required.")

        sql = "DELETE FROM budget_items WHERE item_id = :item_id RETURNING item_id;"
        params = {"item_id": item_id}
        print(f"Final SQL for delete_budget_item: {sql} with params: {params}")
        result = await execute_supabase_sql(sql, params)
        if isinstance(result, dict) and result.get("rows"):
            return {"status": "success"}
        elif isinstance(result, list) and result:
            return {"status": "success"}
        else:
            raise ("Deletion failed.")
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def search_rituals(question: str) -> dict:
    """
    Searches for rituals in Astra DB using vector search.  Returns top 3 most relevant documents.  Handles CollectionExceptions.
    """
    """ input: question - a string containing the user's query about rituals"""
    try:
        if not question:
            return {"status": "error", "error": "Question is required."}

        ritual_data = astra_db.get_collection("ritual_data")
        result = ritual_data.find(
            projection={"$vectorize": True},
            sort={"$vectorize": question},
            limit=3
            
        )
        contexts = [doc for doc in result]
        return {"status": "success", "data": contexts}
    except Exception as e:
        return {"status": "error", "error": f"An unexpected error occurred during ritual search: {e}"}

async def get_timeline_events(
    user_id: str,
    
) -> List[dict]:
    """
    Retrieves all timeline events for a given user.

    Args:
        user_id: The UUID of the user.
        context: Tool execution context.

    Returns:
        A list of dictionaries, where each dictionary represents a timeline event.
        If no events are found, returns an empty list [].
        If an error occurs, returns a dictionary with "status": "error" and "error": <description>.
    """
    try:
        # Input validation
        if not user_id:
            return {"status": "error", "error": "User ID is required."}

        # Construct the SQL query
        sql = """
            SELECT *
            FROM timeline_events
            WHERE user_id = :user_id
        """

        # Prepare the parameters for the SQL query
        params = {
            "user_id": user_id,
        }

        # Execute the SQL query
        result = await execute_supabase_sql(sql, params)

        # Check if the query was successful
        if result and isinstance(result, dict) and result.get("rows"):
            timeline_events = result["rows"]
            return timeline_events
        elif isinstance(result, list):
            return result
        else:
            return []  # Return an empty list if no events are found

    except Exception as e:
        return {"status": "error", "error": f"An unexpected error occurred: {str(e)}"}

async def create_timeline_event(user_id: str, event: dict) -> dict:
    """
    Create a timeline event for a user.
    Args:
        user_id (str): The user's UUID.
        event (dict): {"event_name": str, "event_date_time": str, "description": str, "location": str}
    Returns:
        dict: Inserted timeline event or {"error": <str>}
    """
    # Ensure all required fields
    if not user_id:
        return {"status": "error", "error": "User ID is required."}
    if not isinstance(event, dict):
        return {"status": "error", "error": "Event data must be a dictionary."}
    if not (event.get("event_name") and event.get("event_date_time")):
        return {"status": "error", "error": "Missing required fields for timeline event."}

    sql = (
        "INSERT INTO timeline_events (user_id, event_name, event_date_time, description, location) "
        "VALUES (:user_id, :event_name, :event_date_time, :description, :location) RETURNING *;"
    )
    try:
        params = {
            "user_id": user_id,
            "event_name": event.get("event_name"),
            "event_date_time": event.get("event_date_time"),
            "description": event.get("description"),
            "location": event.get("location")
        }
        print(f"Final SQL for create_timeline_event: {sql} with params: {params}")
        result = await execute_supabase_sql(sql, params)
        if isinstance(result, dict) and result.get("rows"):
            return {"status": "success", "data": result["rows"][0]}
        elif isinstance(result, list) and result:
            return {"status": "success", "data": result[0]}
        else:
            return {"status": "error", "error": "Creating timeline event failed."}
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def update_timeline_event(
    event_id: str,
    updates: Dict[str, Any]
) -> dict:
    """
    Updates an existing timeline event.

    Args:
        event_id: The UUID of the timeline event to update.
        updates: A dictionary containing the fields to update (e.g., event_name, start_time, description) and their new values.

    Returns:
        A dictionary with the following structure:
          - "status": "success" or "error"
          - If "status" is "success":
            - "data": A dictionary containing the updated event data.
          - If "status" is "error":
            - "error": A description of the error.

    Raises:
        ValueError: If input validation fails.
        Exception: For database errors.
    """
    try:
        # Input validation
        if not event_id:
            raise ValueError("Event ID is required.")
        if not isinstance(updates, dict):
            raise ValueError("Updates must be a dictionary.")
        if not updates:
            raise ValueError("No fields to update provided.")

        # Construct the SET clause for the SQL query
        set_clauses = [f"{key} = :{key}" for key in updates]
        set_clause = ", ".join(set_clauses)

        # Construct the SQL query
        sql = f"""
            UPDATE timeline_events
            SET {set_clause}
            WHERE event_id = :event_id
            RETURNING *;
        """

        # Prepare the parameters for the SQL query
        params = {
            "event_id": event_id,
            **updates,
        }

        # Execute the SQL query
        result = await execute_supabase_sql(sql, params)

        # Check if the update was successful
        if result and isinstance(result, dict) and result.get("rows"):
            updated_event = result["rows"][0]
            return {"status": "success", "data": updated_event}
        elif isinstance(result, list) and result:
            updated_event = result[0]
            return {"status": "success", "data": updated_event}
        else:
            return {"status": "error", "error": "Event not found or update failed."}

    except ValueError as ve:
        return {"status": "error", "error": str(ve)}
    except Exception as e:
        return {"status": "error", "error": f"An unexpected error occurred: {str(e)}"}

def extract_untrusted_json(result_text: str) -> Optional[Any]:
    """
    Extract and parse JSON array from within the result string using regex \[.*\].
    Handles escaped double quotes.
    Args:
        result_text (str): The result string containing the JSON array.
    Returns:
        Parsed JSON data (list or dict), or None if not found/parsable.
    """
    match = re.search(r"\[.*\]", result_text, re.DOTALL)
    if match:
        json_str = match.group(0).strip()
        # Unescape double quotes if present
        if '\\"' in json_str:
            json_str = json_str.replace('\\"', '"')
        try:
            return json.loads(json_str)
        except Exception as e:
            print(f"[extract_untrusted_json] JSON parsing failed: {e}\njson_str: {json_str}")
            return None
    return None

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

# get_user_activities
# Input: {"user_id": <uuid>}
# Output: [activity_dict, ...] or {"error": <str>}

# get_budget_items
# Input: {"user_id": <uuid>}
# Output: [budget_item_dict, ...] or {"error": <str>}

# update_budget_item
# Input: {"item_id": <uuid>, "fields": {fields to update}}
# Output: {updated_budget_item_dict} or {"error": <str>}

# delete_budget_item
# Input: {"item_id": <uuid>}
# Output: {"status": "success"} or {"error": <str>}

async def get_user_activities(user_id: str) -> list:
    """
    Get all user activities for a user.
    Args:
        user_id (str): The user's UUID.
    Returns:
        list: List of activity dicts.
    """
    sql = """
        SELECT cm.*
        FROM chat_sessions cs
        JOIN chat_messages cm ON cs.session_id = cm.session_id
        WHERE cs.user_id = :user_id
        ORDER BY cm.timestamp DESC;
    """
    result = await execute_supabase_sql(sql, {"user_id": user_id})
    if isinstance(result, dict) and result.get("rows"):
        return result["rows"]
    elif isinstance(result, list):
        return result
    return []

async def search_vendors(
    category: str = None,
    location: str = None,
    budget_range: dict = None,
    ratings: float = None,
    keywords: list = None,
    
) -> list:
    """
    Search vendors based on various criteria, including full-text search.
    Args:
        category (str, optional): Vendor category.
        location (str, optional): Vendor location.
        budget_range (dict, optional): Budget range ({"min": float, "max": float}).
        ratings (float, optional): Minimum vendor rating.
        keywords (list, optional): List of keywords for full-text search.
    Returns:
        list: List of vendor dicts matching the criteria.
    """
    sql = "SELECT * FROM vendors WHERE TRUE"  # Start with a base query
    params = {}
    where_clauses = []

    if category:
        where_clauses.append("vendor_category ILIKE :category")
        params["category"] = f"%{category}%"
    if location:
        where_clauses.append("address->>'city' ILIKE :location")
        params["location"] = f"%{location}%"
    if budget_range:
        if "min" in budget_range:
            where_clauses.append("price >= :min_price")
            params["min_price"] = budget_range["min"]
        if "max" in budget_range:
            where_clauses.append("price <= :max_price")
            params["max_price"] = budget_range["max"]
    if ratings:
        where_clauses.append("rating >= :min_rating")
        params["min_rating"] = ratings
    # Full-text search using keywords
    if keywords:
        keywords_str = " & ".join(keywords)  # Combine keywords for tsquery
        where_clauses.append("fts_data @@ to_tsquery('english', :keywords)")
        params["keywords"] = keywords_str

    if where_clauses:
        sql += " AND " + " AND ".join(where_clauses)

    result = await execute_supabase_sql(sql, params)
    if isinstance(result, dict) and result.get("rows"):
        return result["rows"]
    elif isinstance(result, list):
        return result
    return []

if __name__ == "__main__":
    # Example usage
    async def main():
        await init_supabase_mcp()
        # Removed call to list_tables (no longer exists)
        print("Supabase MCP initialized.")
    asyncio.run(main())
