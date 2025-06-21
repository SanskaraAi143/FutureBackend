# src/services/supabase_service.py
"""
Service layer for interacting with Supabase.
This module abstracts the direct database interactions, including MCP calls.
"""
import json
import os
from typing import Any, Dict, List, Optional, Tuple

from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

# Assuming settings are centralized and imported
from config.settings import SUPABASE_ACCESS_TOKEN, SUPABASE_PROJECT_ID
from src.tools.common_utils import sql_quote_value # Re-using the quoting utility

# Global MCPToolset instance for Supabase, managed within this service
_mcp_toolset_instance: Optional[MCPToolset] = None
_mcp_tools: Optional[Dict[str, Any]] = None

async def _get_mcp_toolset() -> Tuple[MCPToolset, Dict[str, Any]]:
    """
    Initializes and/or returns the Supabase MCP toolset.
    Raises ValueError if configuration is missing.
    """
    global _mcp_toolset_instance, _mcp_tools
    if _mcp_toolset_instance is None or _mcp_tools is None:
        if not SUPABASE_ACCESS_TOKEN:
            raise ValueError("Supabase access token (SUPABASE_ACCESS_TOKEN) is not configured.")
        if not SUPABASE_PROJECT_ID:
            # While the original code had a default, it's better to require it if MCP needs it.
            # Or, make it truly optional if the MCP server doesn't always need it.
            raise ValueError("Supabase project ID (SUPABASE_PROJECT_ID) is not configured.")

        print(f"[SupabaseService] Initializing MCP Toolset for project: {SUPABASE_PROJECT_ID}")
        mcp = MCPToolset(
            connection_params=StdioServerParameters(
                command='npx',
                args=["-y", "@supabase/mcp-server-supabase@latest", "--access-token", SUPABASE_ACCESS_TOKEN],
            ),
            tool_filter=["execute_sql"] # We are primarily interested in the SQL execution tool
        )
        tools = await mcp.get_tools()
        if "execute_sql" not in tools:
            raise RuntimeError("The 'execute_sql' tool is not available from the Supabase MCP server.")

        _mcp_toolset_instance = mcp
        _mcp_tools = {tool.name: tool for tool in tools} # Store all available tools, though we expect one
        print("[SupabaseService] MCP Toolset initialized successfully.")

    return _mcp_toolset_instance, _mcp_tools

async def execute_sql_query(sql_query: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Executes a given SQL query against Supabase via the MCP server.

    Args:
        sql_query (str): The SQL query string. Can use :param placeholders for params.
        params (Optional[Dict[str, Any]]): Parameters to be inlined into the SQL query.

    Returns:
        Dict[str, Any]: A dictionary containing either "rows" with the query result (typically a list of dicts)
                        or "error" with an error message.
    """
    _, tools = await _get_mcp_toolset()
    sql_tool = tools.get("execute_sql")
    if not sql_tool: # Should not happen if _get_mcp_toolset worked
        return {"error": "Supabase MCP execute_sql tool not found after initialization."}

    final_sql = sql_query
    if params:
        for key, value in params.items():
            final_sql = final_sql.replace(f":{key}", sql_quote_value(value))

    # The MCP tool expects 'project_id' in its arguments.
    tool_args = {"query": final_sql, "project_id": SUPABASE_PROJECT_ID}

    print(f"[SupabaseService.execute_sql_query] Executing SQL: {final_sql[:200]}...") # Log snippet
    try:
        result = await sql_tool.run_async(args=tool_args, tool_context=None) # ToolContext not strictly needed here

        # Process the result (this part might need adjustment based on actual MCP server output structure)
        if hasattr(result, "content") and result.content:
            # Assuming content is a list and the first part has text
            raw_text_output = result.content[0].text if hasattr(result.content[0], "text") else str(result.content[0])
            try:
                # Supabase MCP often returns a JSON string that itself contains a list of records or an object.
                parsed_output = json.loads(raw_text_output)
                # The original code checked for a "rows" key or returned the list directly.
                # Let's standardize to always return a dict with a "rows" key for success.
                if isinstance(parsed_output, list):
                    return {"rows": parsed_output}
                elif isinstance(parsed_output, dict) and "rows" in parsed_output: # If it already has "rows"
                    return parsed_output
                elif isinstance(parsed_output, dict) and not parsed_output.get("error"): # If it's a single object result
                    return {"rows": [parsed_output]} # Wrap single dict in a list
                else: # If it's a dict but has an error or unexpected structure
                    return {"error": f"Parsed output is not a list of rows: {parsed_output}"}

            except json.JSONDecodeError:
                # If JSON parsing fails, it might be a plain string message (e.g., an error message not in JSON)
                return {"error": f"Failed to parse MCP output as JSON: {raw_text_output}"}
            except Exception as e: # Catch other parsing/processing errors
                return {"error": f"Error processing MCP result: {str(e)}"}
        elif hasattr(result, "error_message"): # If the result object itself has an error message
             return {"error": result.error_message}
        else:
            return {"error": "No content or error message returned from MCP tool."}

    except Exception as e:
        print(f"[SupabaseService.execute_sql_query] Exception during MCP call: {e}")
        return {"error": f"An exception occurred while executing SQL via MCP: {str(e)}"}

# --- Higher-level CRUD-like methods ---

async def fetch_one(table_name: str, criteria: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Fetches a single record from a table based on criteria."""
    # Example: criteria = {"user_id": "some-uuid"}
    # TODO: Implement using execute_sql_query
    # Needs to construct SQL: SELECT * FROM {table_name} WHERE key1 = :value1 AND key2 = :value2 LIMIT 1;
    if not table_name or not criteria:
        return {"error": "Table name and criteria are required for fetch_one."}

    where_clauses = [f"{key} = :{key}" for key in criteria.keys()]
    sql = f"SELECT * FROM {table_name} WHERE {' AND '.join(where_clauses)} LIMIT 1;"

    result = await execute_sql_query(sql, params=criteria)
    if "error" in result:
        return result # Propagate error

    rows = result.get("rows")
    if rows and isinstance(rows, list) and len(rows) > 0:
        return rows[0]
    return None # Return None if no record found, or an error dict if execute_sql_query failed


async def fetch_all(
    table_name: str,
    criteria: Optional[Dict[str, Any]] = None,
    order_by: Optional[str] = None,
    select_columns: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Fetches multiple records from a table, optionally filtered, ordered, and with specific columns.
    Returns a list of dictionaries, or an empty list if no records found or an error occurs.
    """
    if not table_name:
        # Or raise ValueError, but for tools, returning empty list with logged error might be preferred.
        print("[SupabaseService.fetch_all] Error: Table name is required.")
        return []

    column_selection = ", ".join(select_columns) if select_columns else "*"
    sql = f"SELECT {column_selection} FROM {table_name}"
    params = {}

    if criteria:
        where_clauses = []
        # Need to handle different types of criteria, e.g., ILIKE for text search, exact match, etc.
        # For simplicity, this example uses exact match. Tools might need to specify operator.
        for idx, (key, value) in enumerate(criteria.items()):
            param_key = f"crit{idx}_{key}" # Create unique param key
            where_clauses.append(f"{key} = :{param_key}") # Example: exact match
            params[param_key] = value
        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)

    if order_by:
        # Basic safety: ensure order_by doesn't contain injection.
        # A more robust solution would be to validate column names against a schema.
        if not all(c.isalnum() or c in ['_', ' ', ','] for c in order_by):
            print(f"[SupabaseService.fetch_all] Warning: Invalid characters in order_by clause: {order_by}. Ignoring.")
        else:
            sql += f" ORDER BY {order_by}"

    result = await execute_sql_query(sql, params=params)

    if "error" in result:
        print(f"[SupabaseService.fetch_all] Error executing query: {result['error']}")
        return [] # Return empty list on error as per function's docstring promise

    return result.get("rows", [])


async def insert_row(table_name: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Inserts a new row into the table and returns the inserted row (if RETURNING * is used).
    """
    if not table_name or not data:
        return {"error": "Table name and data are required for insert_row."}

    columns = ", ".join(data.keys())
    placeholders = ", ".join([f":{key}" for key in data.keys()])
    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders}) RETURNING *;"

    result = await execute_sql_query(sql, params=data)
    if "error" in result:
        return result

    rows = result.get("rows")
    if rows and isinstance(rows, list) and len(rows) > 0:
        return rows[0]
    return None # Or an error if RETURNING * failed to bring back the row


async def update_row(table_name: str, criteria: Dict[str, Any], data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Updates rows matching criteria and returns the updated row (if single and RETURNING *).
    If multiple rows could be updated, the return might be the first updated one or a list.
    For simplicity, this assumes RETURNING * on a single row update or first of many.
    """
    if not table_name or not criteria or not data:
        return {"error": "Table name, criteria, and data are required for update_row."}

    set_clauses = [f"{key} = :data_{key}" for key in data.keys()] # Prefix data keys to avoid clash with criteria
    update_params = {f"data_{key}": value for key, value in data.items()}

    where_clauses = [f"{key} = :crit_{key}" for key in criteria.keys()]
    criteria_params = {f"crit_{key}": value for key, value in criteria.items()}

    sql = f"UPDATE {table_name} SET {', '.join(set_clauses)} WHERE {' AND '.join(where_clauses)} RETURNING *;"

    combined_params = {**update_params, **criteria_params}
    result = await execute_sql_query(sql, params=combined_params)

    if "error" in result:
        return result

    rows = result.get("rows")
    if rows and isinstance(rows, list) and len(rows) > 0:
        return rows[0] # Return the first updated row
    return None # No rows updated or RETURNING * didn't yield data


async def delete_row(table_name: str, criteria: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deletes rows matching criteria.
    Returns a dict like {"status": "success", "deleted_count": N} or {"status": "error", "error": ...}.
    Note: Standard SQL DELETE doesn't typically return count unless using specific DB features or CTEs.
          RETURNING * can show what was deleted. For count, a separate SELECT COUNT(*) might be needed.
          This implementation will return success if no error, and the (potentially empty) list of deleted rows.
    """
    if not table_name or not criteria:
        return {"status": "error", "error": "Table name and criteria are required for delete_row."}

    where_clauses = [f"{key} = :{key}" for key in criteria.keys()]
    sql = f"DELETE FROM {table_name} WHERE {' AND '.join(where_clauses)} RETURNING *;" # RETURNING * to see what was deleted

    result = await execute_sql_query(sql, params=criteria)

    if "error" in result:
        return {"status": "error", "error": result["error"]}

    # If no error, deletion is considered successful.
    # The number of deleted rows can be inferred from len(result.get("rows", []))
    deleted_rows = result.get("rows", [])
    return {"status": "success", "deleted_count": len(deleted_rows), "deleted_rows": deleted_rows}


if __name__ == "__main__":
    async def _test_crud_operations():
        print("\n--- Testing CRUD Operations ---")
        # Note: These tests require a Supabase instance with a 'test_items' table:
        # CREATE TABLE test_items (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), name TEXT, value INT);

        test_table = "test_items" # Make sure this table exists in your Supabase
        test_item_name = "TestItemCRUD"
        test_item_value = 123
        test_item_id = None

        # 1. Insert Row
        print(f"\n1. Testing insert_row into {test_table}...")
        inserted = await insert_row(test_table, {"name": test_item_name, "value": test_item_value})
        if inserted and "error" not in inserted:
            test_item_id = inserted.get("id")
            print(f"   Inserted: {inserted}")
            assert test_item_id is not None
            assert inserted.get("name") == test_item_name
        else:
            print(f"   Insert failed: {inserted}")
            return # Stop if insert fails

        # 2. Fetch One
        print(f"\n2. Testing fetch_one from {test_table} with id: {test_item_id}...")
        fetched_one = await fetch_one(test_table, {"id": test_item_id})
        if fetched_one and "error" not in fetched_one:
            print(f"   Fetched (one): {fetched_one}")
            assert fetched_one.get("name") == test_item_name
        else:
            print(f"   Fetch_one failed: {fetched_one}")

        # 3. Update Row
        print(f"\n3. Testing update_row in {test_table} for id: {test_item_id}...")
        updated_value = 456
        updated_row = await update_row(test_table, {"id": test_item_id}, {"value": updated_value, "name": "Updated TestItem"})
        if updated_row and "error" not in updated_row:
            print(f"   Updated: {updated_row}")
            assert updated_row.get("value") == updated_value
            assert updated_row.get("name") == "Updated TestItem"
        else:
            print(f"   Update failed: {updated_row}")

        # 4. Fetch All (with filter)
        print(f"\n4. Testing fetch_all from {test_table} with name: Updated TestItem...")
        all_updated = await fetch_all(test_table, criteria={"name": "Updated TestItem"})
        print(f"   Fetched (all with filter): {all_updated}")
        assert len(all_updated) >= 1
        if all_updated:
             assert all_updated[0].get("id") == test_item_id

        # 5. Delete Row
        print(f"\n5. Testing delete_row from {test_table} for id: {test_item_id}...")
        delete_result = await delete_row(test_table, {"id": test_item_id})
        print(f"   Delete result: {delete_result}")
        assert delete_result.get("status") == "success"
        assert delete_result.get("deleted_count", 0) == 1

        # Verify deletion
        deleted_item_check = await fetch_one(test_table, {"id": test_item_id})
        print(f"   Post-delete fetch_one check: {deleted_item_check}")
        assert deleted_item_check is None or "error" in deleted_item_check # Should be None or error if not found

        print("\n--- CRUD Operation Tests Completed ---")
    # Example usage (for testing this module directly)
    async def _test_service():
        print("Testing Supabase Service...")
        # Ensure your .env file is correctly set up at the project root for this to work.
        # Test 1: Simple query
        # result = await execute_sql_query("SELECT email FROM users WHERE user_id = :user_id;", {"user_id": "1b006058-1133-490c-b2de-90c444e56138"})
        # print(f"Test query result: {result}")

        # Test 2: A query that might return an error (e.g., syntax error or non-existent table)
        # error_result = await execute_sql_query("SELECT * FROM non_existent_table;")
        # print(f"Test error query result: {error_result}")
        print("To run tests, uncomment calls in _test_service() and ensure .env is configured.")
        print("Make sure the MCP server can be started (npx @supabase/mcp-server-supabase).")

    import asyncio
    # asyncio.run(_test_service()) # Commented out to prevent execution during automated runs unless intended.
