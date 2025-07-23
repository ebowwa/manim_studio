#!/usr/bin/env python3
"""Get MCP tutorial to understand correct parameter syntax"""

from src.config.manim_config import config
import asyncio
from src.interfaces.mcp_interface import MCPInterface
import json

async def get_tutorial():
    mcp = MCPInterface()
    
    # Get objects and animations section
    result = await mcp.execute_tool("get_mcp_tutorial", {
        "section": "objects_and_animations"
    })
    
    if result.status == "success":
        print(result.data)
    else:
        print(f"Error: {result.error}")

if __name__ == "__main__":
    asyncio.run(get_tutorial())