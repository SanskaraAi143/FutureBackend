"""
Using supabase mcp server to get all the available data manipulations for the user to use.
"""
import os
import asyncio
import dotenv
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams, StdioServerParameters

dotenv.load_dotenv('../../.env')
SUPABASE_ACCESS_TOKEN = os.getenv("SUPABASE_ACCESS_TOKEN")
print(f"Supabase access token: {SUPABASE_ACCESS_TOKEN}")
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