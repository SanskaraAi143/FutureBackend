"""
Using supabase mcp server to get all the available data manipulations for the user to use.
"""
import os
import asyncio
import dotenv
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters # SseServerParams not used

# Load .env from the project root directory (one level up from 'scripts/')
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if dotenv.load_dotenv(dotenv_path=dotenv_path):
    print(f"Loaded .env from: {dotenv_path}")
else:
    # Fallback if .env is in current dir (e.g. if script run from root and .env is there)
    if dotenv.load_dotenv(): # Checks .env in CWD or parent dirs based on dotenv logic
        print("Loaded .env from current directory or parent.")
    else:
        print("Warning: .env file not found or not loaded. SUPABASE_ACCESS_TOKEN must be set in environment.")


SUPABASE_ACCESS_TOKEN = os.getenv("SUPABASE_ACCESS_TOKEN")
# print(f"Supabase access token: {SUPABASE_ACCESS_TOKEN}") # Print only if needed for debug
if not SUPABASE_ACCESS_TOKEN:
    print("Error: SUPABASE_ACCESS_TOKEN is not set. Please ensure it's in your .env file or environment.")
    # exit(1) # Optional: exit if token is crucial

async def get_tools():
    tools,exit_stack = await MCPToolset.from_server(
        connection_params=StdioServerParameters(
            command='npx',
            args=["-y", "@supabase/mcp-server-supabase@latest","--access-token", SUPABASE_ACCESS_TOKEN],
        )
    )
    print("MCP tools loaded successfully.")
    print("Available tools:")
    for tool in tools:

        print(f"- {tool.name}: {tool.description}")
    return tools, exit_stack

async def use_tools():
    pass
async def main():
    global tools
    tools,exit_stack = await get_tools()
    await exit_stack.aclose()

if __name__ == "__main__":
    asyncio.run(main())