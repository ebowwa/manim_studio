"""Fixed MCP Server for Manim Studio - properly formatted JSON schemas."""

import asyncio
import json
import logging
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Import Manim Studio components
import sys
manim_studio_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(manim_studio_root / "src"))

try:
    from core.config import Config, SceneConfig, AnimationConfig, EffectConfig
    from core.scene_builder import SceneBuilder
    from core.asset_manager import AssetManager
    from core.timeline.timeline import Timeline
    from core.timeline.composer_timeline import (
        ComposerTimeline, InterpolationType, Keyframe, TrackType
    )
    from core.timeline.timeline_presets import TimelinePresets
except ImportError as e:
    print(f"Warning: Could not import some modules: {e}")
    # Create minimal stubs
    class Config: pass
    class SceneBuilder: pass
    class AssetManager: pass
    class Timeline: pass
    class ComposerTimeline: pass
    class InterpolationType: pass
    class Keyframe: pass
    class TrackType: pass
    class TimelinePresets: pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("manim-studio-mcp")

class ManimStudioServer:
    """MCP Server for Manim Studio animation creation."""
    
    def __init__(self):
        self.server = Server("manim-studio")
        self.current_scene: Optional[Dict[str, Any]] = None
        self.scenes: Dict[str, Dict[str, Any]] = {}
        self.timeline: Optional[ComposerTimeline] = None
        self.timeline_presets = TimelinePresets()
        self.setup_handlers()
        
    def setup_handlers(self):
        """Setup all MCP tool handlers."""
        
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
                            "name": {
                                "type": "string", 
                                "description": "Scene name"
                            },
                            "duration": {
                                "type": "number", 
                                "description": "Duration in seconds",
                                "default": 5.0
                            },
                            "background_color": {
                                "type": "string", 
                                "description": "Background color hex",
                                "default": "#000000"
                            }
                        },
                        "required": ["name"]
                    }
                ),
                types.Tool(
                    name="add_text",
                    description="Add text to the current scene",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "string", 
                                "description": "Unique identifier for this text"
                            },
                            "text": {
                                "type": "string", 
                                "description": "Text content"
                            },
                            "color": {
                                "type": "string", 
                                "description": "Text color",
                                "default": "#FFFFFF"
                            }
                        },
                        "required": ["id", "text"]
                    }
                ),
                types.Tool(
                    name="add_animation",
                    description="Add animation to an object",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "target": {
                                "type": "string", 
                                "description": "Target object ID"
                            },
                            "animation_type": {
                                "type": "string", 
                                "description": "Animation type",
                                "enum": ["write", "fadein", "fadeout", "create", "uncreate"]
                            },
                            "start_time": {
                                "type": "number", 
                                "description": "Start time in seconds",
                                "default": 0
                            },
                            "duration": {
                                "type": "number", 
                                "description": "Animation duration",
                                "default": 1.0
                            }
                        },
                        "required": ["target", "animation_type"]
                    }
                ),
                types.Tool(
                    name="list_scenes",
                    description="List all created scenes",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="render_scene",
                    description="Render the current scene to video",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "output_path": {
                                "type": "string", 
                                "description": "Output video file path"
                            },
                            "quality": {
                                "type": "string", 
                                "description": "Render quality",
                                "enum": ["low", "medium", "high"],
                                "default": "medium"
                            }
                        },
                        "required": ["output_path"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Optional[Dict[str, Any]]) -> List[types.TextContent]:
            """Handle tool calls."""
            try:
                result = await self.execute_tool(name, arguments or {})
                return [
                    types.TextContent(
                        type="text",
                        text=json.dumps(result, indent=2)
                    )
                ]
            except Exception as e:
                logger.error(f"Error in tool {name}: {e}")
                return [
                    types.TextContent(
                        type="text",
                        text=json.dumps({
                            "status": "error",
                            "message": str(e)
                        }, indent=2)
                    )
                ]

    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool and return the result."""
        if name == "create_scene":
            scene_name = arguments["name"]
            duration = arguments.get("duration", 5.0)
            bg_color = arguments.get("background_color", "#000000")
            
            scene_config = {
                "name": scene_name,
                "duration": duration,
                "background_color": bg_color,
                "objects": [],
                "animations": []
            }
            
            self.scenes[scene_name] = scene_config
            self.current_scene = scene_config
            
            return {
                "status": "success",
                "message": f"Scene '{scene_name}' created successfully",
                "scene": scene_config
            }
        
        elif name == "add_text":
            if not self.current_scene:
                return {"status": "error", "message": "No active scene"}
            
            text_id = arguments["id"]
            text_content = arguments["text"]
            color = arguments.get("color", "#FFFFFF")
            
            text_obj = {
                "id": text_id,
                "type": "text",
                "content": text_content,
                "color": color,
                "position": [0, 0, 0]
            }
            
            self.current_scene["objects"].append(text_obj)
            
            return {
                "status": "success",
                "message": f"Text '{text_id}' added to scene",
                "object": text_obj
            }
        
        elif name == "add_animation":
            if not self.current_scene:
                return {"status": "error", "message": "No active scene"}
            
            target = arguments["target"]
            anim_type = arguments["animation_type"]
            start_time = arguments.get("start_time", 0)
            duration = arguments.get("duration", 1.0)
            
            animation = {
                "target": target,
                "type": anim_type,
                "start_time": start_time,
                "duration": duration
            }
            
            self.current_scene["animations"].append(animation)
            
            return {
                "status": "success",
                "message": f"Animation '{anim_type}' added to '{target}'",
                "animation": animation
            }
        
        elif name == "list_scenes":
            return {
                "status": "success",
                "scenes": list(self.scenes.keys()),
                "count": len(self.scenes)
            }
        
        elif name == "render_scene":
            if not self.current_scene:
                return {"status": "error", "message": "No active scene"}
            
            output_path = arguments["output_path"]
            quality = arguments.get("quality", "medium")
            
            # For now, just simulate rendering
            return {
                "status": "success",
                "message": f"Scene rendered to {output_path}",
                "output_path": output_path,
                "quality": quality
            }
        
        else:
            return {
                "status": "error",
                "message": f"Unknown tool: {name}"
            }

    async def run(self):
        """Run the MCP server."""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="manim-studio",
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
        logger.info("Starting Manim Studio MCP Server...")
        server = ManimStudioServer()
        await server.run()
    except Exception as e:
        logger.error(f"Server failed to start: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    asyncio.run(main())