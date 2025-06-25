import json
import os
import asyncio
import dotenv
import ast
import re
from typing import Optional, Any, List, Dict # Added for type hints used in functions
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters # StdioConnectionParams not used

dotenv.load_dotenv('.env') # Load .env from the project root

SUPABASE_ACCESS_TOKEN = os.getenv("SUPABASE_ACCESS_TOKEN")

# Global MCPToolset instance for Supabase
_supabase_mcp_toolset: Optional[MCPToolset] = None
_supabase_tools: Optional[Dict[str, Any]] = None # Using Any for tool type flexibility

async def init_supabase_mcp():
    """Initializes the Supabase MCP toolset if not already initialized."""
    global _supabase_mcp_toolset, _supabase_tools
    if _supabase_mcp_toolset is None:
        if not SUPABASE_ACCESS_TOKEN:
            raise ValueError("SUPABASE_ACCESS_TOKEN environment variable is not set.")

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

def sql_quote_value(val: Any) -> str:
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
        # Ensure single quotes within JSON are escaped for SQL strings
        val_str = json.dumps(val).replace("'", "''")
        return f"'{val_str}'"
    # Ensure single quotes in general strings are escaped
    val_str = str(val).replace("'", "''")
    return f"'{val_str}'"

async def execute_supabase_sql(sql: str, params: Optional[dict] = None) -> Any:
    """
    Execute a SQL query against Supabase via the MCP server.
    Args:
        sql (str): The SQL query string, with :param placeholders.
        params (dict, optional): Parameters to inline into the SQL string.
    Returns:
        Any: Parsed result (list or dict), or dict with 'error'.
    """
    if _supabase_mcp_toolset is None or _supabase_tools is None:
        # Ensure MCP is initialized if called directly or for the first time
        await init_supabase_mcp()

    # These assertions help mypy and provide runtime checks
    assert _supabase_mcp_toolset is not None, "Supabase MCP toolset not initialized"
    assert _supabase_tools is not None, "Supabase MCP tools not initialized"

    tool = _supabase_tools.get("execute_sql")
    if not tool:
        # This case should ideally be caught by init_supabase_mcp if tool_filter fails
        raise RuntimeError("Supabase MCP execute_sql tool not found after initialization.")

    try:
        # Inline params robustly
        final_sql = sql
        if params:
            # print(f"[MCP SQL DEBUG] SQL before inlining: {final_sql}")
            for k, v in params.items():
                final_sql = final_sql.replace(f":{k}", sql_quote_value(v))

        args = {"query": final_sql}
        project_id = os.getenv("SUPABASE_PROJECT_ID")
        if not project_id:
            # Fallback or error, depending on requirements. For now, using provided default.
            print("[MCP SQL WARNING] SUPABASE_PROJECT_ID not set, using default 'lylsxoupakajkuisjdfl'.")
            project_id = "lylsxoupakajkuisjdfl"
        args["project_id"] = project_id

        # print(f"[MCP SQL DEBUG] Final SQL: {final_sql}")
        # print(f"[MCP SQL DEBUG] Args sent to MCP: {args}")

        # Assuming tool.run_async exists and matches expected signature
        result = await tool.run_async(args=args, tool_context=None)
        # print(f"[MCP SQL DEBUG] Raw result from MCP: {result}")

        if hasattr(result, "content") and result.content and result.content[0]:
            text_content = result.content[0]
            text = text_content.text if hasattr(text_content, "text") else str(text_content)

            untrusted_json = extract_untrusted_json(text)
            # print(f"untrusted_json: {untrusted_json}")
            if untrusted_json is not None:
                # print(f"[MCP SQL DEBUG] Extracted untrusted JSON: {untrusted_json}")
                return untrusted_json
            try:
                # print(f"[MCP SQL DEBUG] Attempting json.loads on: {text}")
                parsed = json.loads(text)
                return parsed
            except json.JSONDecodeError as e1:
                # print(f"[MCP SQL DEBUG] JSON parsing failed: {e1}")
                try:
                    # print(f"[MCP SQL DEBUG] Attempting ast.literal_eval on: {text}")
                    parsed = ast.literal_eval(text) # Be cautious with ast.literal_eval on untrusted input
                    return parsed
                except (ValueError, SyntaxError) as e2:
                    # print(f"[MCP SQL DEBUG] Literal eval failed: {e2}")
                    # If all parsing fails, return the raw text, or an error structure
                    return {"error": "Failed to parse SQL result.", "details": text}
        return {"error": "No content returned from SQL tool or content format unexpected."}
    except Exception as e:
        # print(f"[MCP SQL ERROR] Exception during execute_supabase_sql: {e}")
        return {"error": str(e)}

def extract_untrusted_json(result_text: str) -> Optional[Any]:
    """
    Extract and parse JSON array or object from within the result string using regex.
    Handles escaped double quotes.
    Args:
        result_text (str): The result string potentially containing the JSON.
    Returns:
        Parsed JSON data (list or dict), or None if not found/parsable.
    """
    # Regex to find JSON arrays [...] or JSON objects {...}
    # It's a simplified regex; complex nested structures might need more robust parsing.
    match = re.search(r"(\[.*\]|\{.*\})", result_text, re.DOTALL)
    if match:
        json_str = match.group(0).strip()
        # Unescape double quotes if present (common in some stringified JSON)
        if '\\"' in json_str:
            json_str = json_str.replace('\\"', '"')
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            # print(f"[extract_untrusted_json] JSON parsing failed: {e}\njson_str: {json_str}")
            return None
    return None

if __name__ == "__main__":
    # Example usage for helpers.py (optional, for direct testing)
    async def test_mcp_init():
        print("Attempting to initialize Supabase MCP...")
        try:
            mcp_set, tools_map = await init_supabase_mcp()
            if mcp_set and tools_map:
                print(f"Supabase MCP initialized. Found tools: {list(tools_map.keys())}")
                # Example: Try a simple query if SUPABASE_PROJECT_ID is set
                # project_id_test = os.getenv("SUPABASE_PROJECT_ID")
                # if project_id_test:
                #     print(await execute_supabase_sql("SELECT 1;", {}))
                # else:
                # print("SUPABASE_PROJECT_ID not set, skipping test query.")
            else:
                print("Supabase MCP initialization failed to return expected objects.")
        except Exception as e:
            print(f"Error during MCP initialization test: {e}")

    asyncio.run(test_mcp_init())
