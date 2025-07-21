"""Simple MCP Server for Manim Studio - minimal version for testing."""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("manim-studio-mcp-simple")

class SimpleManimStudioServer:
    """Simplified MCP Server for Manim Studio."""
    
    def __init__(self):
        self.server = Server("manim-studio-simple")
        self.scenes: Dict[str, Dict[str, Any]] = {}
        self.setup_handlers()
        
    def setup_handlers(self):
        """Setup basic MCP tool handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """Return list of available tools."""
            return [
                types.Tool(
                    name="create_scene",
                    description="Create a new animation scene",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Scene name"},
                            "duration": {"type": "number", "description": "Duration in seconds", "default": 5.0},
                            "background_color": {"type": "string", "description": "Background color", "default": "#000000"},
                            "resolution": {"type": "array", "items": {"type": "integer"}, "description": "Resolution [width, height]", "default": [1920, 1080]}
                        },
                        "required": ["name"]
                    }
                ),
                types.Tool(
                    name="list_scenes",
                    description="List all created scenes",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                types.Tool(
                    name="get_scene",
                    description="Get scene configuration",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Scene name"}
                        },
                        "required": ["name"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> List[types.TextContent]:
            """Handle tool calls."""
            try:
                if name == "create_scene":
                    scene_name = arguments["name"]
                    duration = arguments.get("duration", 5.0)
                    bg_color = arguments.get("background_color", "#000000")
                    resolution = arguments.get("resolution", [1920, 1080])
                    
                    scene_config = {
                        "name": scene_name,
                        "duration": duration,
                        "background_color": bg_color,
                        "resolution": resolution,
                        "objects": [],
                        "animations": []
                    }
                    
                    self.scenes[scene_name] = scene_config
                    
                    return [
                        types.TextContent(
                            type="text",
                            text=json.dumps({
                                "status": "success",
                                "message": f"Scene '{scene_name}' created successfully",
                                "scene": scene_config
                            }, indent=2)
                        )
                    ]
                
                elif name == "list_scenes":
                    scene_list = list(self.scenes.keys())
                    return [
                        types.TextContent(
                            type="text",
                            text=json.dumps({
                                "status": "success",
                                "scenes": scene_list,
                                "count": len(scene_list)
                            }, indent=2)
                        )
                    ]
                
                elif name == "get_scene":
                    scene_name = arguments["name"]
                    if scene_name not in self.scenes:
                        return [
                            types.TextContent(
                                type="text",
                                text=json.dumps({
                                    "status": "error",
                                    "message": f"Scene '{scene_name}' not found"
                                }, indent=2)
                            )
                        ]
                    
                    return [
                        types.TextContent(
                            type="text",
                            text=json.dumps({
                                "status": "success",
                                "scene": self.scenes[scene_name]
                            }, indent=2)
                        )
                    ]
                
                else:
                    return [
                        types.TextContent(
                            type="text",
                            text=json.dumps({
                                "status": "error",
                                "message": f"Unknown tool: {name}"
                            }, indent=2)
                        )
                    ]
                    
            except Exception as e:
                logger.error(f"Error handling tool {name}: {e}")
                return [
                    types.TextContent(
                        type="text",
                        text=json.dumps({
                            "status": "error",
                            "message": str(e)
                        }, indent=2)
                    )
                ]

    async def run(self):
        """Run the MCP server."""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream, 
                write_stream, 
                InitializationOptions(
                    server_name="manim-studio-simple",
                    server_version="0.1.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )

async def main():
    """Main entry point."""
    try:
        logger.info("Starting Simple Manim Studio MCP Server...")
        server = SimpleManimStudioServer()
        await server.run()
    except Exception as e:
        logger.error(f"Server failed to start: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    asyncio.run(main())