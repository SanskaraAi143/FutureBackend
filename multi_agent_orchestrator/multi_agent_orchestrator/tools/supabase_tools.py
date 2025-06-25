"""
supabase_tools.py - Custom tools for ADK agents to interact with Supabase and Astra DB

This module was migrated from sanskara/tools.py as part of the orchestrator refactor.
"""

from typing import List, Dict, Any, Optional
from google.adk.tools import ToolContext, LongRunningFunctionTool
from google.adk.tools.google_search_tool import GoogleSearchTool
from multi_agent_orchestrator.config import astra_db  # Update import path
import json
import os
import asyncio
import dotenv
import ast
import re
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters, StdioConnectionParams
from .extract_untrusted_json import extract_untrusted_json

dotenv.load_dotenv('.env')
SUPABASE_ACCESS_TOKEN = os.getenv("SUPABASE_ACCESS_TOKEN")

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
    """
    mcp, tools = await init_supabase_mcp()
    tool = tools.get("execute_sql")
    if not tool:
        raise RuntimeError("Supabase MCP execute_sql tool not found.")
    try:
        if params:
            for k, v in params.items():
                sql = sql.replace(f":{k}", sql_quote_value(v))
        args = {"query": sql}
        project_id = os.getenv("SUPABASE_PROJECT_ID") or "lylsxoupakajkuisjdfl"
        args["project_id"] = project_id
        result = await tool.run_async(args=args, tool_context=None)
        if hasattr(result, "content") and result.content:
            text = result.content[0].text if hasattr(result.content[0], "text") else str(result.content[0])
            untrusted_json = extract_untrusted_json(text)
            if untrusted_json is not None:
                return untrusted_json
            try:
                parsed = json.loads(text)
                return parsed
            except Exception:
                try:
                    parsed = ast.literal_eval(text)
                    return parsed
                except Exception:
                    return text
        return {"error": "No content returned from tool."}
    except Exception as e:
        return {"error": str(e)}



# --- Supabase Tools (MCP-based, async) ---
async def get_user_id(email: str) -> dict:
    sql = "SELECT user_id FROM users WHERE email = :email LIMIT 1;"
    result = await execute_supabase_sql(sql, {"email": email})
    if isinstance(result, dict) and result.get("rows"):
        return result["rows"][0]
    elif isinstance(result, list) and result:
        return result[0]
    return {"error": f"User not found. {result}"}

async def get_user_data(user_id: str) -> dict:
    sql = "SELECT * FROM users WHERE user_id = :user_id LIMIT 1;"
    result = await execute_supabase_sql(sql, {"user_id": user_id})
    if isinstance(result, dict) and result.get("rows"):
        return result["rows"][0]
    elif isinstance(result, list) and result:
        return result[0]
    return {"error": "User not found."}

async def update_user_data(user_id: str, data: dict) -> dict:
    USERS_TABLE_COLUMNS = {
        "user_id", "supabase_auth_uid", "email", "display_name", "created_at", "updated_at",
        "wedding_date", "wedding_location", "wedding_tradition", "preferences", "user_type"
    }
    preferences_update = data.pop("preferences", None) or {}
    extra_prefs = {k: data.pop(k) for k in list(data.keys()) if k not in USERS_TABLE_COLUMNS}
    if extra_prefs:
        preferences_update.update(extra_prefs)
    if preferences_update:
        user = await get_user_data(user_id)
        current_prefs = user.get("preferences") if user and isinstance(user, dict) else {}
        if not isinstance(current_prefs, dict):
            current_prefs = {}
        current_prefs.update(preferences_update)
        data["preferences"] = current_prefs
    if "preferences" in data:
        data["preferences"] = json.dumps(data["preferences"])
    set_clause = ", ".join([f"{k} = :{k}" for k in data.keys()])
    sql = f"UPDATE users SET {set_clause} WHERE user_id = :user_id RETURNING *;"
    params = {**data, "user_id": user_id}
    result = await execute_supabase_sql(sql, params)
    if result and isinstance(result, dict) and result.get("rows"):
        return result["rows"][0]
    elif isinstance(result, list) and result:
        return result[0]
    return {"error": "Update failed."}

async def list_vendors(filters: Optional[dict] = None) -> list:
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
    sql = "SELECT * FROM vendors WHERE vendor_id = :vendor_id LIMIT 1;"
    result = await execute_supabase_sql(sql, {"vendor_id": vendor_id})
    if isinstance(result, dict) and result.get("rows"):
        return result["rows"][0]
    elif isinstance(result, list) and result:
        return result[0]
    return {"error": "Vendor not found."}

async def add_budget_item(user_id: str, item: dict, vendor_name: Optional[str] = None, status: Optional[str] = "Pending") -> dict:
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
    result = await execute_supabase_sql(sql, params)
    if isinstance(result, dict) and result.get("rows"):
        return result["rows"][0]
    elif isinstance(result, list) and result:
        return result[0]
    return {"error": "Adding budget item failed."}

async def get_budget_items(user_id: str) -> list:
    sql = "SELECT * FROM budget_items WHERE user_id = :user_id;"
    result = await execute_supabase_sql(sql, {"user_id": user_id})
    if isinstance(result, dict) and result.get("rows"):
        return result["rows"]
    elif isinstance(result, list):
        return result
    return []

async def update_budget_item(item_id: str, data: dict) -> dict:
    if not item_id:
        return {"error": "Item ID is required."}
    if not isinstance(data, dict):
        return {"error": "Data must be a dictionary."}
    if not data:
        return {"error": "No fields to update."}
    set_clauses = [f"{k} = :{k}" for k in data]
    set_clause = ", ".join(set_clauses)
    sql = f"UPDATE budget_items SET {set_clause} WHERE item_id = :item_id RETURNING *;"
    params = {**data, "item_id": item_id}
    result = await execute_supabase_sql(sql, params)
    if isinstance(result, dict) and result.get("rows"):
        updated_budget_item = result["rows"][0]
    elif isinstance(result, list) and result:
        updated_budget_item = result[0]
    else:
        return {"error": f"Updating budget item failed: {result}"}
    return {"status": "success", "data": updated_budget_item}

async def delete_budget_item(item_id: str) -> dict:
    if not item_id:
        return {"error": "Item ID is required."}
    sql = "DELETE FROM budget_items WHERE item_id = :item_id RETURNING item_id;"
    params = {"item_id": item_id}
    result = await execute_supabase_sql(sql, params)
    if isinstance(result, dict) and result.get("rows"):
        return {"status": "success"}
    elif isinstance(result, list) and result:
        return {"status": "success"}
    else:
        return {"error": "Deletion failed."}

async def search_rituals(question: str) -> dict:
    try:
        if not question:
            return {"status": "error", "error": "Question is required."}
        from multi_agent_orchestrator.config import astra_db
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

async def get_timeline_events(user_id: str) -> List[dict]:
    """
    Retrieves all timeline events for a given user.
    """
    try:
        if not user_id:
            return {"status": "error", "error": "User ID is required."}
        sql = """
            SELECT *
            FROM timeline_events
            WHERE user_id = :user_id
        """
        params = {"user_id": user_id}
        result = await execute_supabase_sql(sql, params)
        if result and isinstance(result, dict) and result.get("rows"):
            return result["rows"]
        elif isinstance(result, list):
            return result
        else:
            return []
    except Exception as e:
        return {"status": "error", "error": f"An unexpected error occurred: {str(e)}"}

async def create_timeline_event(user_id: str, event: dict) -> dict:
    """
    Create a timeline event for a user.
    """
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
        result = await execute_supabase_sql(sql, params)
        if isinstance(result, dict) and result.get("rows"):
            return {"status": "success", "data": result["rows"][0]}
        elif isinstance(result, list) and result:
            return {"status": "success", "data": result[0]}
        else:
            return {"status": "error", "error": "Creating timeline event failed."}
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def update_timeline_event(event_id: str, updates: Dict[str, Any]) -> dict:
    """
    Updates an existing timeline event.
    """
    try:
        if not event_id:
            raise ValueError("Event ID is required.")
        if not isinstance(updates, dict):
            raise ValueError("Updates must be a dictionary.")
        if not updates:
            raise ValueError("No fields to update provided.")
        set_clauses = [f"{key} = :{key}" for key in updates]
        set_clause = ", ".join(set_clauses)
        sql = f"""
            UPDATE timeline_events
            SET {set_clause}
            WHERE event_id = :event_id
            RETURNING *;
        """
        params = {"event_id": event_id, **updates}
        result = await execute_supabase_sql(sql, params)
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
