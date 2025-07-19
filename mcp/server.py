"""MCP Server for Manim Studio - enables AI assistants to create animations."""

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
sys.path.append(str(Path(__file__).parent.parent))
from src.manim_studio.core import Config, SceneBuilder, Timeline, AssetManager
from src.manim_studio.core.config import SceneConfig, AnimationConfig, EffectConfig
from src.manim_studio.cli import render_scene

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("manim-studio-mcp")

class ManimStudioServer:
    """MCP Server for Manim Studio animation creation."""
    
    def __init__(self):
        self.server = Server("manim-studio")
        self.current_scene: Optional[Dict[str, Any]] = None
        self.scenes: Dict[str, Dict[str, Any]] = {}
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
                            "name": {"type": "string", "description": "Scene name"},
                            "description": {"type": "string", "description": "Scene description"},
                            "duration": {"type": "number", "description": "Duration in seconds", "default": 5.0},
                            "background_color": {"type": "string", "description": "Background color hex", "default": "#000000"},
                            "resolution": {
                                "type": "array",
                                "items": {"type": "integer"},
                                "description": "Resolution [width, height]",
                                "default": [1920, 1080]
                            },
                            "fps": {"type": "integer", "description": "Frames per second", "default": 60}
                        },
                        "required": ["name"]
                    }
                ),
                types.Tool(
                    name="add_text",
                    description="Add text object to the current scene",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "id": {"type": "string", "description": "Unique identifier for this text"},
                            "text": {"type": "string", "description": "Text content"},
                            "position": {
                                "type": "array",
                                "items": {"type": "number"},
                                "description": "Position [x, y, z]",
                                "default": [0, 0, 0]
                            },
                            "color": {"type": "string", "description": "Text color", "default": "#FFFFFF"},
                            "gradient": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Gradient colors (optional)"
                            },
                            "scale": {"type": "number", "description": "Text scale", "default": 1.0},
                            "font": {"type": "string", "description": "Font name (optional)"},
                            "weight": {"type": "string", "description": "Font weight", "default": "NORMAL"}
                        },
                        "required": ["id", "text"]
                    }
                ),
                types.Tool(
                    name="add_shape",
                    description="Add a shape to the current scene",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "id": {"type": "string", "description": "Unique identifier"},
                            "shape": {
                                "type": "string",
                                "enum": ["circle", "rectangle", "polygon"],
                                "description": "Shape type"
                            },
                            "position": {
                                "type": "array",
                                "items": {"type": "number"},
                                "description": "Position [x, y, z]",
                                "default": [0, 0, 0]
                            },
                            "color": {"type": "string", "description": "Stroke color", "default": "#FFFFFF"},
                            "fill_color": {"type": "string", "description": "Fill color (optional)"},
                            "fill_opacity": {"type": "number", "description": "Fill opacity", "default": 0},
                            "scale": {"type": "number", "description": "Scale factor", "default": 1.0},
                            "radius": {"type": "number", "description": "Circle radius", "default": 1.0},
                            "width": {"type": "number", "description": "Rectangle width", "default": 2.0},
                            "height": {"type": "number", "description": "Rectangle height", "default": 1.0},
                            "vertices": {"type": "integer", "description": "Polygon vertices", "default": 3}
                        },
                        "required": ["id", "shape"]
                    }
                ),
                types.Tool(
                    name="add_animation",
                    description="Add animation to an object",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "target": {"type": "string", "description": "Target object ID"},
                            "animation_type": {
                                "type": "string",
                                "enum": ["fadein", "fadeout", "write", "create", "move", "scale", "rotate"],
                                "description": "Animation type"
                            },
                            "start_time": {"type": "number", "description": "Start time in seconds"},
                            "duration": {"type": "number", "description": "Duration in seconds", "default": 1.0},
                            "params": {
                                "type": "object",
                                "description": "Animation parameters",
                                "properties": {
                                    "to": {"type": "array", "description": "Target position for move"},
                                    "factor": {"type": "number", "description": "Scale factor"},
                                    "angle": {"type": "number", "description": "Rotation angle in radians"},
                                    "shift": {"type": "array", "description": "Shift vector for fadein"}
                                }
                            }
                        },
                        "required": ["target", "animation_type", "start_time"]
                    }
                ),
                types.Tool(
                    name="add_effect",
                    description="Add visual effect to the scene",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": ["particle_system", "magical_circle", "glow_text", "sparkle_text"],
                                "description": "Effect type"
                            },
                            "start_time": {"type": "number", "description": "Start time in seconds"},
                            "duration": {"type": "number", "description": "Duration in seconds"},
                            "params": {
                                "type": "object",
                                "description": "Effect parameters",
                                "properties": {
                                    "position": {"type": "array", "description": "Effect position"},
                                    "particle_count": {"type": "integer", "description": "Number of particles"},
                                    "emit_rate": {"type": "number", "description": "Particles per second"},
                                    "radius": {"type": "number", "description": "Effect radius"},
                                    "rings": {"type": "integer", "description": "Number of rings (magical circle)"},
                                    "target": {"type": "string", "description": "Target object ID (for text effects)"}
                                }
                            }
                        },
                        "required": ["type", "start_time", "duration"]
                    }
                ),
                types.Tool(
                    name="preview_scene",
                    description="Generate a preview of the current scene",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "quality": {
                                "type": "string",
                                "enum": ["low", "medium", "high"],
                                "description": "Preview quality",
                                "default": "low"
                            },
                            "format": {
                                "type": "string",
                                "enum": ["mp4", "gif", "png"],
                                "description": "Output format",
                                "default": "mp4"
                            }
                        }
                    }
                ),
                types.Tool(
                    name="render_scene",
                    description="Render the scene to a video file",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "output_path": {"type": "string", "description": "Output file path"},
                            "quality": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "4k"],
                                "description": "Render quality",
                                "default": "high"
                            }
                        },
                        "required": ["output_path"]
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
                    name="get_scene",
                    description="Get scene configuration",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Scene name"}
                        },
                        "required": ["name"]
                    }
                ),
                types.Tool(
                    name="save_config",
                    description="Save scene configuration to file",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "File path (.json or .yaml)"},
                            "scene_name": {"type": "string", "description": "Scene to save (optional, uses current)"}
                        },
                        "required": ["path"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Optional[Dict[str, Any]]) -> List[types.TextContent]:
            """Handle tool calls."""
            try:
                result = await self.execute_tool(name, arguments or {})
                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                logger.error(f"Tool execution error: {e}")
                return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool and return the result."""
        
        if name == "create_scene":
            scene_config = {
                "name": arguments["name"],
                "description": arguments.get("description", ""),
                "duration": arguments.get("duration", 5.0),
                "background_color": arguments.get("background_color", "#000000"),
                "resolution": arguments.get("resolution", [1920, 1080]),
                "fps": arguments.get("fps", 60),
                "objects": {},
                "animations": [],
                "effects": []
            }
            self.scenes[arguments["name"]] = scene_config
            self.current_scene = scene_config
            return {"status": "success", "scene": scene_config}
        
        elif name == "add_text":
            if not self.current_scene:
                return {"status": "error", "message": "No active scene"}
            
            text_obj = {
                "type": "text",
                "text": arguments["text"],
                "params": {
                    "position": arguments.get("position", [0, 0, 0]),
                    "color": arguments.get("color", "#FFFFFF"),
                    "scale": arguments.get("scale", 1.0),
                    "weight": arguments.get("weight", "NORMAL")
                }
            }
            
            if "gradient" in arguments:
                text_obj["params"]["gradient"] = arguments["gradient"]
            if "font" in arguments:
                text_obj["params"]["font"] = arguments["font"]
            
            self.current_scene["objects"][arguments["id"]] = text_obj
            return {"status": "success", "object": text_obj}
        
        elif name == "add_shape":
            if not self.current_scene:
                return {"status": "error", "message": "No active scene"}
            
            shape_obj = {
                "type": "shape",
                "shape": arguments["shape"],
                "params": {
                    "position": arguments.get("position", [0, 0, 0]),
                    "color": arguments.get("color", "#FFFFFF"),
                    "scale": arguments.get("scale", 1.0)
                }
            }
            
            # Add shape-specific parameters
            if arguments["shape"] == "circle":
                shape_obj["params"]["radius"] = arguments.get("radius", 1.0)
            elif arguments["shape"] == "rectangle":
                shape_obj["params"]["width"] = arguments.get("width", 2.0)
                shape_obj["params"]["height"] = arguments.get("height", 1.0)
            elif arguments["shape"] == "polygon":
                shape_obj["params"]["vertices"] = arguments.get("vertices", 3)
            
            if "fill_color" in arguments:
                shape_obj["params"]["fill_color"] = arguments["fill_color"]
                shape_obj["params"]["fill_opacity"] = arguments.get("fill_opacity", 0.5)
            
            self.current_scene["objects"][arguments["id"]] = shape_obj
            return {"status": "success", "object": shape_obj}
        
        elif name == "add_animation":
            if not self.current_scene:
                return {"status": "error", "message": "No active scene"}
            
            animation = {
                "target": arguments["target"],
                "animation_type": arguments["animation_type"],
                "start_time": arguments["start_time"],
                "duration": arguments.get("duration", 1.0),
                "params": arguments.get("params", {})
            }
            
            self.current_scene["animations"].append(animation)
            return {"status": "success", "animation": animation}
        
        elif name == "add_effect":
            if not self.current_scene:
                return {"status": "error", "message": "No active scene"}
            
            effect = {
                "type": arguments["type"],
                "start_time": arguments["start_time"],
                "duration": arguments["duration"],
                "params": arguments.get("params", {})
            }
            
            self.current_scene["effects"].append(effect)
            return {"status": "success", "effect": effect}
        
        elif name == "preview_scene":
            if not self.current_scene:
                return {"status": "error", "message": "No active scene"}
            
            # Save current scene to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(self.current_scene, f, indent=2)
                temp_path = f.name
            
            # Render preview
            quality = arguments.get("quality", "low")
            output_path = f"/tmp/preview_{self.current_scene['name']}.mp4"
            
            try:
                # Use the CLI render function
                render_scene(temp_path, quality=f"{quality}_quality", preview=True)
                Path(temp_path).unlink()  # Clean up temp file
                return {
                    "status": "success",
                    "preview_path": output_path,
                    "message": f"Preview rendered to {output_path}"
                }
            except Exception as e:
                Path(temp_path).unlink()  # Clean up temp file
                return {"status": "error", "message": str(e)}
        
        elif name == "render_scene":
            if not self.current_scene:
                return {"status": "error", "message": "No active scene"}
            
            # Save current scene to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(self.current_scene, f, indent=2)
                temp_path = f.name
            
            quality = arguments.get("quality", "high")
            output_path = arguments["output_path"]
            
            try:
                # Use the CLI render function
                render_scene(temp_path, quality=f"{quality}_quality", output_file=output_path)
                Path(temp_path).unlink()  # Clean up temp file
                return {
                    "status": "success",
                    "output_path": output_path,
                    "message": f"Scene rendered to {output_path}"
                }
            except Exception as e:
                Path(temp_path).unlink()  # Clean up temp file
                return {"status": "error", "message": str(e)}
        
        elif name == "list_scenes":
            return {
                "status": "success",
                "scenes": list(self.scenes.keys()),
                "current_scene": self.current_scene["name"] if self.current_scene else None
            }
        
        elif name == "get_scene":
            scene_name = arguments["name"]
            if scene_name in self.scenes:
                return {"status": "success", "scene": self.scenes[scene_name]}
            else:
                return {"status": "error", "message": f"Scene '{scene_name}' not found"}
        
        elif name == "save_config":
            scene = self.current_scene
            if "scene_name" in arguments:
                if arguments["scene_name"] in self.scenes:
                    scene = self.scenes[arguments["scene_name"]]
                else:
                    return {"status": "error", "message": f"Scene '{arguments['scene_name']}' not found"}
            
            if not scene:
                return {"status": "error", "message": "No scene to save"}
            
            path = Path(arguments["path"])
            
            try:
                with open(path, 'w') as f:
                    if path.suffix == '.yaml':
                        import yaml
                        yaml.dump(scene, f, default_flow_style=False)
                    else:
                        json.dump(scene, f, indent=2)
                
                return {
                    "status": "success",
                    "path": str(path),
                    "message": f"Scene saved to {path}"
                }
            except Exception as e:
                return {"status": "error", "message": str(e)}
        
        else:
            return {"status": "error", "message": f"Unknown tool: {name}"}
    
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
    server = ManimStudioServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())