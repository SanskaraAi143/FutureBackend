import os
import asyncio
import dotenv
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams, StdioServerParameters

dotenv.load_dotenv('.env')
SUPABASE_ACCESS_TOKEN = os.getenv("SUPABASE_ACCESS_TOKEN")
print(f"Supabase access token: {SUPABASE_ACCESS_TOKEN}")
async def get_tools():
    tools =  MCPToolset(
        connection_params=StdioServerParameters(
            command='npx',
            args=["-y", "@supabase/mcp-server-supabase@latest","--access-token", SUPABASE_ACCESS_TOKEN],
        ),
        tool_filter=["execute_sql"]
    )
    tool= await tools.get_tools()
    print("MCP tools loaded successfully.")
    for tool1 in tool:
        print(f"- {tool1.name}: {tool1.description}")
    # all = await tool[1].run_async(args=None, tool_context=None)
    # print(f"All tools: {all}")
asyncio.run(get_tools())