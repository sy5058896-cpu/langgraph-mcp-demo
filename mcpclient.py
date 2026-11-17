from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio

client = MultiServerMCPClient(
    {"math": {"command": "python", "args": ["mathserver.py"], "transport": "stdio"}}
)


async def get_tools():
    client = MultiServerMCPClient(
        {"math": {"command": "python", "args": ["mathserver.py"], "transport": "stdio"}}
    )
    return await client.get_tools()
