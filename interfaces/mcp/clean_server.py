"""Clean MCP Server for Manim Studio - no stdout pollution."""

import asyncio
import json
import logging
import sys
import tempfile
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Redirect all logging to stderr to keep stdout clean for MCP protocol
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr  # Important: log to stderr, not stdout
)
logger = logging.getLogger("manim-studio-mcp")

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Import Manim Studio components
manim_studio_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(manim_studio_root / "src"))

# Suppress any print statements from imports
import contextlib
import io

with contextlib.redirect_stdout(io.StringIO()):
    try:
        from core.config import Config, SceneConfig, AnimationConfig, EffectConfig
        from core.scene_builder import SceneBuilder
        from core.asset_manager import AssetManager
        from core.timeline.timeline import Timeline
        from core.timeline.composer_timeline import (
            ComposerTimeline, InterpolationType, Keyframe, TrackType
        )
        from core.timeline.timeline_presets import TimelinePresets
        IMPORTS_SUCCESS = True
    except ImportError as e:
        logger.error(f"Could not import some modules: {e}")
        IMPORTS_SUCCESS = False

class ManimStudioServer:
    """MCP Server for Manim Studio animation creation."""
    
    def __init__(self):
        self.server = Server("manim-studio")
        self.current_scene: Optional[Dict[str, Any]] = None
        self.scenes: Dict[str, Dict[str, Any]] = {}
        # Configure script storage directory
        self.script_storage_dir = Path("/Users/ebowwa/apps/manim_studio/user-data/mcp-scripts")
        self.script_storage_dir.mkdir(parents=True, exist_ok=True)
        self.timeline = None
        if IMPORTS_SUCCESS:
            self.timeline_presets = TimelinePresets()
        else:
            self.timeline_presets = None
        self.setup_handlers()
        
    def setup_handlers(self):
        """Setup all MCP tool handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """Return list of available tools."""
            tools = [
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
                            },
                            "position": {
                                "type": "array",
                                "description": "Position [x, y, z]",
                                "items": {"type": "number"},
                                "default": [0, 0, 0]
                            }
                        },
                        "required": ["id", "text"]
                    }
                ),
                types.Tool(
                    name="add_shape",
                    description="Add shape to the current scene",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "string", 
                                "description": "Unique identifier"
                            },
                            "shape_type": {
                                "type": "string", 
                                "description": "Shape type",
                                "enum": ["circle", "square", "rectangle", "triangle"]
                            },
                            "color": {
                                "type": "string", 
                                "description": "Shape color",
                                "default": "#FFFFFF"
                            },
                            "size": {
                                "type": "number", 
                                "description": "Shape size",
                                "default": 1.0
                            }
                        },
                        "required": ["id", "shape_type"]
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
                                "enum": ["write", "fadein", "fadeout", "create", "uncreate", "move", "scale", "rotate"]
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
                        "properties": {},
                        "required": []
                    }
                ),
                types.Tool(
                    name="get_scene",
                    description="Get current scene configuration",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Scene name (optional, defaults to current)"
                            }
                        },
                        "required": []
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
            
            return tools

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Optional[Dict[str, Any]]) -> List[types.TextContent]:
            """Handle tool calls."""
            if arguments is None:
                arguments = {}
                
            try:
                result = await self.execute_tool(name, arguments)
                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                logger.error(f"Error in tool {name}: {e}", exc_info=True)
                error_result = {
                    "status": "error",
                    "message": str(e),
                    "tool": name
                }
                return [types.TextContent(type="text", text=json.dumps(error_result, indent=2))]

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
            
            # Create timeline if available
            if IMPORTS_SUCCESS:
                try:
                    self.timeline = ComposerTimeline(duration=duration)
                except:
                    self.timeline = None
            
            return {
                "status": "success",
                "message": f"Scene '{scene_name}' created",
                "scene": scene_config
            }
        
        elif name == "add_text":
            if not self.current_scene:
                return {"status": "error", "message": "No active scene. Create a scene first."}
            
            text_id = arguments["id"]
            text_content = arguments["text"]
            color = arguments.get("color", "#FFFFFF")
            position = arguments.get("position", [0, 0, 0])
            
            text_obj = {
                "id": text_id,
                "type": "text",
                "content": text_content,
                "color": color,
                "position": position
            }
            
            self.current_scene["objects"].append(text_obj)
            
            return {
                "status": "success",
                "message": f"Text '{text_id}' added",
                "object": text_obj
            }
        
        elif name == "add_shape":
            if not self.current_scene:
                return {"status": "error", "message": "No active scene. Create a scene first."}
            
            shape_id = arguments["id"]
            shape_type = arguments["shape_type"]
            color = arguments.get("color", "#FFFFFF")
            size = arguments.get("size", 1.0)
            
            shape_obj = {
                "id": shape_id,
                "type": "shape",
                "shape_type": shape_type,
                "color": color,
                "size": size,
                "position": [0, 0, 0]
            }
            
            self.current_scene["objects"].append(shape_obj)
            
            return {
                "status": "success",
                "message": f"Shape '{shape_id}' added",
                "object": shape_obj
            }
        
        elif name == "add_animation":
            if not self.current_scene:
                return {"status": "error", "message": "No active scene. Create a scene first."}
            
            target = arguments["target"]
            anim_type = arguments["animation_type"]
            start_time = arguments.get("start_time", 0)
            duration = arguments.get("duration", 1.0)
            
            # Check if target exists
            target_exists = any(obj["id"] == target for obj in self.current_scene["objects"])
            if not target_exists:
                return {"status": "error", "message": f"Target object '{target}' not found"}
            
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
                "count": len(self.scenes),
                "current_scene": self.current_scene["name"] if self.current_scene else None
            }
        
        elif name == "get_scene":
            scene_name = arguments.get("name")
            if scene_name:
                if scene_name not in self.scenes:
                    return {"status": "error", "message": f"Scene '{scene_name}' not found"}
                scene = self.scenes[scene_name]
            else:
                if not self.current_scene:
                    return {"status": "error", "message": "No active scene"}
                scene = self.current_scene
                
            return {
                "status": "success",
                "scene": scene
            }
        
        elif name == "render_scene":
            if not self.current_scene:
                return {"status": "error", "message": "No active scene. Create a scene first."}
            
            output_path = arguments["output_path"]
            quality = arguments.get("quality", "medium")
            
            # Create a simple Python script that can be run with manim
            script_content = self._generate_manim_script()
            
            # Save to permanent location with timestamp and scene name
            script_hash = hashlib.md5(script_content.encode()).hexdigest()[:8]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            scene_name = self.current_scene.get("name", "Scene")
            permanent_filename = f"{timestamp}_{scene_name}_{script_hash}.py"
            permanent_path = self.script_storage_dir / permanent_filename
            
            # Check if identical script already exists
            existing_scripts = list(self.script_storage_dir.glob(f"*_{scene_name}_*.py"))
            script_already_saved = False
            
            for existing_script in existing_scripts:
                try:
                    existing_content = existing_script.read_text()
                    if existing_content == script_content:
                        script_already_saved = True
                        permanent_path = existing_script
                        break
                except Exception:
                    continue
            
            # Save script if not already saved
            if not script_already_saved:
                permanent_path.write_text(script_content)
            
            # Also create temporary file for immediate rendering
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
            temp_file.write(script_content)
            temp_file.close()
            
            # Create metadata file
            metadata = {
                "scene_name": scene_name,
                "timestamp": timestamp,
                "quality": quality,
                "output_path": output_path,
                "scene_config": self.current_scene,
                "script_hash": script_hash,
                "permanent_script": str(permanent_path),
                "temp_script": temp_file.name
            }
            
            metadata_path = permanent_path.with_suffix('.json')
            metadata_path.write_text(json.dumps(metadata, indent=2))
            
            return {
                "status": "success",
                "message": f"Scene prepared for rendering. Script saved to {permanent_path.name}",
                "script_path": temp_file.name,
                "permanent_script_path": str(permanent_path),
                "output_path": output_path,
                "quality": quality,
                "render_command": f"manim {temp_file.name} Scene -o {output_path}",
                "saved_as": permanent_filename
            }
        
        else:
            return {
                "status": "error",
                "message": f"Unknown tool: {name}"
            }
    
    def _generate_manim_script(self) -> str:
        """Generate a Manim script from the current scene configuration."""
        if not self.current_scene:
            return ""
            
        script = f'''from manim import *

class Scene(Scene):
    def construct(self):
        # Set background
        self.camera.background_color = "{self.current_scene.get('background_color', '#000000')}"
        
        # Create objects
        objects = {{}}
'''
        
        # Add objects
        for obj in self.current_scene.get("objects", []):
            if obj["type"] == "text":
                script += f'''        objects["{obj['id']}"] = Text("{obj['content']}", color="{obj['color']}")\n'''
                script += f'''        objects["{obj['id']}"].move_to([{obj['position'][0]}, {obj['position'][1]}, {obj['position'][2]}])\n'''
            elif obj["type"] == "shape":
                if obj["shape_type"] == "circle":
                    script += f'''        objects["{obj['id']}"] = Circle(radius={obj['size']}, color="{obj['color']}")\n'''
                elif obj["shape_type"] == "square":
                    script += f'''        objects["{obj['id']}"] = Square(side_length={obj['size'] * 2}, color="{obj['color']}")\n'''
                # Add more shapes as needed
        
        script += '''        
        # Execute animations\n'''
        
        # Add animations
        for anim in self.current_scene.get("animations", []):
            target = anim["target"]
            anim_type = anim["type"]
            
            if anim_type == "create":
                script += f'''        self.play(Create(objects["{target}"]), run_time={anim['duration']})\n'''
            elif anim_type == "write":
                script += f'''        self.play(Write(objects["{target}"]), run_time={anim['duration']})\n'''
            elif anim_type == "fadein":
                script += f'''        self.play(FadeIn(objects["{target}"]), run_time={anim['duration']})\n'''
            elif anim_type == "fadeout":
                script += f'''        self.play(FadeOut(objects["{target}"]), run_time={anim['duration']})\n'''
            # Add more animation types as needed
            
            if anim["start_time"] > 0:
                script += f'''        self.wait({anim['start_time']})\n'''
        
        return script

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
    logger.info("Starting Manim Studio MCP Server...")
    try:
        server = ManimStudioServer()
        await server.run()
    except Exception as e:
        logger.error(f"Server failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    # Ensure stdout is not buffered
    sys.stdout = sys.stdout.detach()
    sys.stdout = io.TextIOWrapper(sys.stdout, encoding='utf-8', line_buffering=True)
    
    asyncio.run(main())