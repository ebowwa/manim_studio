"""Enhanced MCP Server for Manim Studio with Timeline Presets."""

import asyncio
import json
import logging
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import io
import contextlib

# Redirect all logging to stderr to keep stdout clean for MCP protocol
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger("manim-studio-mcp-enhanced")

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Import Manim Studio components
manim_studio_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(manim_studio_root / "src"))

# Suppress any print statements from imports
with contextlib.redirect_stdout(io.StringIO()):
    try:
        from core.config import Config, SceneConfig, AnimationConfig, EffectConfig
        from core.scene_builder import SceneBuilder
        from core.asset_manager import AssetManager
        from core.timeline.timeline import Timeline
        from core.timeline.composer_timeline import (
            ComposerTimeline, InterpolationType, Keyframe, TrackType
        )
        from core.timeline.timeline_presets import TimelinePresets, PresetCategory
        IMPORTS_SUCCESS = True
    except ImportError as e:
        logger.error(f"Could not import some modules: {e}")
        IMPORTS_SUCCESS = False

class EnhancedManimStudioServer:
    """Enhanced MCP Server for Manim Studio with timeline presets."""
    
    def __init__(self):
        self.server = Server("manim-studio-enhanced")
        self.current_scene: Optional[Dict[str, Any]] = None
        self.scenes: Dict[str, Dict[str, Any]] = {}
        self.timeline: Optional[ComposerTimeline] = None
        
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
                # Basic scene management tools
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
                            },
                            "resolution": {
                                "type": "array",
                                "description": "Resolution [width, height]",
                                "items": {"type": "integer"},
                                "default": [1920, 1080]
                            },
                            "fps": {
                                "type": "integer",
                                "description": "Frames per second",
                                "default": 60
                            }
                        },
                        "required": ["name"]
                    }
                ),
                
                # Timeline preset tools
                types.Tool(
                    name="list_timeline_presets",
                    description="List all available timeline presets",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "category": {
                                "type": "string",
                                "description": "Filter by category (optional)",
                                "enum": ["intro", "outro", "transition", "title", "data_visualization", 
                                         "motion_graphics", "educational", "social_media"]
                            }
                        },
                        "required": []
                    }
                ),
                
                types.Tool(
                    name="get_preset_info",
                    description="Get detailed information about a specific preset",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "preset_name": {
                                "type": "string",
                                "description": "Name of the preset"
                            }
                        },
                        "required": ["preset_name"]
                    }
                ),
                
                types.Tool(
                    name="apply_timeline_preset",
                    description="Apply a timeline preset to the current scene",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "preset_name": {
                                "type": "string",
                                "description": "Name of the preset to apply",
                                "enum": ["fade_in_out", "title_sequence", "data_reveal", 
                                        "kinetic_typography", "educational_diagram", 
                                        "social_media_post", "smooth_transition", 
                                        "logo_animation", "material_design", 
                                        "elastic_pop", "smooth_morph"]
                            },
                            "parameters": {
                                "type": "object",
                                "description": "Custom parameters for the preset (optional)"
                            }
                        },
                        "required": ["preset_name"]
                    }
                ),
                
                # Enhanced animation tools
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
                            },
                            "font_size": {
                                "type": "number",
                                "description": "Font size",
                                "default": 48
                            },
                            "font": {
                                "type": "string",
                                "description": "Font family",
                                "default": "Arial"
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
                                "enum": ["circle", "square", "rectangle", "triangle", 
                                        "polygon", "star", "arrow"]
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
                            },
                            "position": {
                                "type": "array",
                                "description": "Position [x, y, z]",
                                "items": {"type": "number"},
                                "default": [0, 0, 0]
                            }
                        },
                        "required": ["id", "shape_type"]
                    }
                ),
                
                types.Tool(
                    name="add_animation",
                    description="Add animation to an object with easing",
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
                                "enum": ["write", "fadein", "fadeout", "create", "uncreate", 
                                        "move", "scale", "rotate", "morph", "transform"]
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
                            },
                            "easing": {
                                "type": "string",
                                "description": "Easing function",
                                "enum": ["linear", "ease_in", "ease_out", "ease_in_out", 
                                        "bounce", "elastic", "back", "expo"],
                                "default": "ease_in_out"
                            },
                            "properties": {
                                "type": "object",
                                "description": "Animation properties (position, scale, rotation, etc.)"
                            }
                        },
                        "required": ["target", "animation_type"]
                    }
                ),
                
                # Scene management
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
                                "enum": ["low", "medium", "high", "4k"],
                                "default": "high"
                            },
                            "preset": {
                                "type": "string",
                                "description": "Render preset",
                                "enum": ["default", "youtube", "instagram", "tiktok"],
                                "default": "default"
                            }
                        },
                        "required": ["output_path"]
                    }
                ),
                
                types.Tool(
                    name="open_video",
                    description="Open a rendered video file in the default video player",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "video_path": {
                                "type": "string",
                                "description": "Path to the video file to open"
                            }
                        },
                        "required": ["video_path"]
                    }
                ),
                
                types.Tool(
                    name="preview_video",
                    description="Generate a quick preview of the current scene",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "quality": {
                                "type": "string",
                                "description": "Preview quality",
                                "enum": ["low", "medium"],
                                "default": "low"
                            },
                            "auto_open": {
                                "type": "boolean",
                                "description": "Automatically open the preview after rendering",
                                "default": True
                            }
                        },
                        "required": []
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
            resolution = arguments.get("resolution", [1920, 1080])
            fps = arguments.get("fps", 60)
            
            scene_config = {
                "name": scene_name,
                "duration": duration,
                "background_color": bg_color,
                "resolution": resolution,
                "fps": fps,
                "objects": [],
                "animations": [],
                "timeline_preset": None
            }
            
            self.scenes[scene_name] = scene_config
            self.current_scene = scene_config
            
            # Create timeline if available
            if IMPORTS_SUCCESS:
                try:
                    self.timeline = ComposerTimeline(duration=duration, fps=fps)
                except:
                    self.timeline = None
            
            return {
                "status": "success",
                "message": f"Scene '{scene_name}' created",
                "scene": scene_config
            }
        
        elif name == "list_timeline_presets":
            if not self.timeline_presets:
                return {"status": "error", "message": "Timeline presets not available"}
            
            category_filter = arguments.get("category")
            presets_list = []
            
            for preset_name, preset in self.timeline_presets.presets.items():
                if category_filter and preset.category.value != category_filter:
                    continue
                    
                presets_list.append({
                    "name": preset.name,
                    "category": preset.category.value,
                    "description": preset.description,
                    "duration": preset.duration,
                    "tags": preset.tags or []
                })
            
            return {
                "status": "success",
                "presets": presets_list,
                "count": len(presets_list),
                "categories": [cat.value for cat in PresetCategory]
            }
        
        elif name == "get_preset_info":
            if not self.timeline_presets:
                return {"status": "error", "message": "Timeline presets not available"}
            
            preset_name = arguments["preset_name"]
            preset = self.timeline_presets.get_preset(preset_name)
            
            if not preset:
                return {"status": "error", "message": f"Preset '{preset_name}' not found"}
            
            return {
                "status": "success",
                "preset": {
                    "name": preset.name,
                    "category": preset.category.value,
                    "description": preset.description,
                    "duration": preset.duration,
                    "parameters": preset.parameters,
                    "tags": preset.tags or []
                }
            }
        
        elif name == "apply_timeline_preset":
            if not self.current_scene:
                return {"status": "error", "message": "No active scene. Create a scene first."}
            
            if not self.timeline_presets or not self.timeline:
                return {"status": "error", "message": "Timeline system not available"}
            
            preset_name = arguments["preset_name"]
            custom_params = arguments.get("parameters", {})
            
            preset = self.timeline_presets.get_preset(preset_name)
            if not preset:
                return {"status": "error", "message": f"Preset '{preset_name}' not found"}
            
            try:
                # Apply the preset
                preset.apply(self.timeline, custom_params)
                
                # Update scene config
                self.current_scene["timeline_preset"] = {
                    "name": preset_name,
                    "parameters": custom_params
                }
                
                # Update scene duration if needed
                if preset.duration > self.current_scene["duration"]:
                    self.current_scene["duration"] = preset.duration
                    self.timeline.duration = preset.duration
                
                return {
                    "status": "success",
                    "message": f"Applied preset '{preset_name}' to scene",
                    "preset_info": {
                        "name": preset.name,
                        "duration": preset.duration,
                        "description": preset.description
                    }
                }
                
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Failed to apply preset: {str(e)}"
                }
        
        elif name == "add_text":
            if not self.current_scene:
                return {"status": "error", "message": "No active scene. Create a scene first."}
            
            text_id = arguments["id"]
            text_content = arguments["text"]
            color = arguments.get("color", "#FFFFFF")
            position = arguments.get("position", [0, 0, 0])
            font_size = arguments.get("font_size", 48)
            font = arguments.get("font", "Arial")
            
            text_obj = {
                "id": text_id,
                "type": "text",
                "content": text_content,
                "color": color,
                "position": position,
                "font_size": font_size,
                "font": font
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
            position = arguments.get("position", [0, 0, 0])
            
            shape_obj = {
                "id": shape_id,
                "type": "shape",
                "shape_type": shape_type,
                "color": color,
                "size": size,
                "position": position
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
            easing = arguments.get("easing", "ease_in_out")
            properties = arguments.get("properties", {})
            
            # Check if target exists
            target_exists = any(obj["id"] == target for obj in self.current_scene["objects"])
            if not target_exists:
                return {"status": "error", "message": f"Target object '{target}' not found"}
            
            animation = {
                "target": target,
                "type": anim_type,
                "start_time": start_time,
                "duration": duration,
                "easing": easing,
                "properties": properties
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
            quality = arguments.get("quality", "high")
            preset = arguments.get("preset", "default")
            
            # Generate render configuration
            render_config = {
                "scene_name": self.current_scene["name"],
                "output_path": output_path,
                "quality": quality,
                "preset": preset,
                "resolution": self.current_scene["resolution"],
                "fps": self.current_scene["fps"]
            }
            
            # Create a Manim script
            script_content = self._generate_enhanced_manim_script()
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
            temp_file.write(script_content)
            temp_file.close()
            
            # Quality mapping
            quality_map = {
                "low": "l",
                "medium": "m", 
                "high": "h",
                "4k": "k"
            }
            
            return {
                "status": "success",
                "message": "Scene prepared for rendering",
                "script_path": temp_file.name,
                "render_config": render_config,
                "render_command": f"manim {temp_file.name} Scene -{quality_map[quality]} -o {output_path}"
            }
        
        elif name == "open_video":
            video_path = arguments["video_path"]
            
            # Check if file exists
            if not Path(video_path).exists():
                return {"status": "error", "message": f"Video file not found: {video_path}"}
            
            try:
                # Use platform-specific command to open video
                import platform
                import subprocess
                
                if platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", video_path], check=True)
                elif platform.system() == "Windows":
                    subprocess.run(["start", "", video_path], shell=True, check=True)
                else:  # Linux
                    subprocess.run(["xdg-open", video_path], check=True)
                
                return {
                    "status": "success",
                    "message": f"Opened video: {video_path}",
                    "video_path": video_path
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Failed to open video: {str(e)}"
                }
        
        elif name == "preview_video":
            if not self.current_scene:
                return {"status": "error", "message": "No active scene. Create a scene first."}
            
            quality = arguments.get("quality", "low")
            auto_open = arguments.get("auto_open", True)
            
            # Generate temporary output path
            import os
            temp_dir = tempfile.gettempdir()
            scene_name = self.current_scene["name"].replace(" ", "_")
            output_path = os.path.join(temp_dir, f"manim_preview_{scene_name}.mp4")
            
            # Create a Manim script
            script_content = self._generate_enhanced_manim_script()
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
            temp_file.write(script_content)
            temp_file.close()
            
            # Quality mapping
            quality_map = {
                "low": "l",
                "medium": "m"
            }
            
            # Generate render command
            render_command = f"manim {temp_file.name} Scene -{quality_map[quality]} -o {output_path}"
            
            result = {
                "status": "success",
                "message": "Preview prepared",
                "script_path": temp_file.name,
                "output_path": output_path,
                "render_command": render_command,
                "quality": quality,
                "auto_open": auto_open
            }
            
            if auto_open:
                result["note"] = "After rendering, use 'open_video' tool to view the preview"
            
            return result
        
        else:
            return {
                "status": "error",
                "message": f"Unknown tool: {name}"
            }
    
    def _generate_enhanced_manim_script(self) -> str:
        """Generate an enhanced Manim script with timeline presets."""
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
                script += f'''        objects["{obj['id']}"] = Text("{obj['content']}", '''
                script += f'''color="{obj['color']}", font_size={obj.get('font_size', 48)})\n'''
                script += f'''        objects["{obj['id']}"].move_to([{obj['position'][0]}, {obj['position'][1]}, {obj['position'][2]}])\n'''
            elif obj["type"] == "shape":
                if obj["shape_type"] == "circle":
                    script += f'''        objects["{obj['id']}"] = Circle(radius={obj['size']}, color="{obj['color']}")\n'''
                elif obj["shape_type"] == "square":
                    script += f'''        objects["{obj['id']}"] = Square(side_length={obj['size'] * 2}, color="{obj['color']}")\n'''
                elif obj["shape_type"] == "triangle":
                    script += f'''        objects["{obj['id']}"] = Triangle(color="{obj['color']}").scale({obj['size']})\n'''
                elif obj["shape_type"] == "star":
                    script += f'''        objects["{obj['id']}"] = Star(color="{obj['color']}").scale({obj['size']})\n'''
                
                script += f'''        objects["{obj['id']}"].move_to([{obj['position'][0]}, {obj['position'][1]}, {obj['position'][2]}])\n'''
        
        # Handle timeline preset if applied
        if self.current_scene.get("timeline_preset"):
            preset_info = self.current_scene["timeline_preset"]
            script += f'''        
        # Timeline preset: {preset_info['name']}
        # Note: Full preset functionality requires the Manim Studio framework
        '''
        
        script += '''        
        # Execute animations\n'''
        
        # Sort animations by start time
        animations = sorted(self.current_scene.get("animations", []), key=lambda a: a.get("start_time", 0))
        
        current_time = 0
        for anim in animations:
            # Add wait if needed
            if anim["start_time"] > current_time:
                wait_time = anim["start_time"] - current_time
                script += f'''        self.wait({wait_time})\n'''
                current_time = anim["start_time"]
            
            target = anim["target"]
            anim_type = anim["type"]
            duration = anim["duration"]
            easing = anim.get("easing", "linear")
            
            # Map easing to rate_func
            easing_map = {
                "linear": "linear",
                "ease_in": "ease_in_quad",
                "ease_out": "ease_out_quad",
                "ease_in_out": "smooth",
                "bounce": "there_and_back",
                "elastic": "wiggle",
                "back": "ease_out_back",
                "expo": "ease_out_expo"
            }
            rate_func = easing_map.get(easing, "linear")
            
            if anim_type == "create":
                script += f'''        self.play(Create(objects["{target}"], rate_func={rate_func}), run_time={duration})\n'''
            elif anim_type == "write":
                script += f'''        self.play(Write(objects["{target}"], rate_func={rate_func}), run_time={duration})\n'''
            elif anim_type == "fadein":
                script += f'''        self.play(FadeIn(objects["{target}"], rate_func={rate_func}), run_time={duration})\n'''
            elif anim_type == "fadeout":
                script += f'''        self.play(FadeOut(objects["{target}"], rate_func={rate_func}), run_time={duration})\n'''
            elif anim_type == "move" and "properties" in anim and "position" in anim["properties"]:
                pos = anim["properties"]["position"]
                script += f'''        self.play(objects["{target}"].animate.move_to([{pos[0]}, {pos[1]}, {pos[2]}]), '''
                script += f'''rate_func={rate_func}, run_time={duration})\n'''
            elif anim_type == "scale" and "properties" in anim and "scale" in anim["properties"]:
                scale = anim["properties"]["scale"]
                script += f'''        self.play(objects["{target}"].animate.scale({scale}), '''
                script += f'''rate_func={rate_func}, run_time={duration})\n'''
            elif anim_type == "rotate" and "properties" in anim and "angle" in anim["properties"]:
                angle = anim["properties"]["angle"]
                script += f'''        self.play(objects["{target}"].animate.rotate({angle}), '''
                script += f'''rate_func={rate_func}, run_time={duration})\n'''
            
            current_time += duration
        
        # Final wait
        if current_time < self.current_scene["duration"]:
            script += f'''        self.wait({self.current_scene["duration"] - current_time})\n'''
        
        return script

    async def run(self):
        """Run the MCP server."""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="manim-studio-enhanced",
                    server_version="0.2.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )

async def main():
    """Main entry point."""
    logger.info("Starting Enhanced Manim Studio MCP Server...")
    try:
        server = EnhancedManimStudioServer()
        await server.run()
    except Exception as e:
        logger.error(f"Server failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    # Ensure stdout is not buffered
    sys.stdout = sys.stdout.detach()
    sys.stdout = io.TextIOWrapper(sys.stdout, encoding='utf-8', line_buffering=True)
    
    asyncio.run(main())