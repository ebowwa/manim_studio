"""MCP Interface using Shared Features

This module provides MCP-specific functionality while leveraging the shared core features.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
import io
import contextlib

# Redirect all logging to stderr to keep stdout clean for MCP protocol
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr,
    force=True  # Force reconfiguration
)

# Remove any existing handlers that might write to stdout
for handler in logging.root.handlers[:]:
    if hasattr(handler, 'stream') and handler.stream is sys.stdout:
        logging.root.removeHandler(handler)

logger = logging.getLogger("manim-studio-mcp")

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Import shared features
from src.interfaces.shared_features import (
    ManimStudioCore, 
    AnimationType, 
    ShapeType, 
    RenderQuality,
    InterfaceResult
)

# Import organized MCP tools
try:
    from .tools import get_all_tools
except ImportError:
    from tools import get_all_tools

# Clean up logging after all imports to ensure stdout is clean for MCP
for handler in logging.root.handlers[:]:
    if hasattr(handler, 'stream') and handler.stream is sys.stdout:
        logging.root.removeHandler(handler)
        
# Ensure our logger uses stderr
if not logger.handlers:
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(stderr_handler)
    logger.setLevel(logging.INFO)


class MCPInterface:
    """MCP-specific interface implementation using shared features."""
    
    def __init__(self):
        self.server = Server("manim-studio")
        from src.interfaces.shared_state import shared_core
        self.core = shared_core
        self.tools_list = []  # Store tools for index access
        self.setup_handlers()
        
    def setup_handlers(self):
        """Setup all MCP tool handlers."""
        
        # Get all tools from organized modules
        self.tools_list = get_all_tools()
        
        # Add any additional tools specific to MCP
        self.tools_list.extend([
                # Scene Management
                types.Tool(
                    name="create_scene",
                    description="Create a new animation scene",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Scene name"},
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
                
                # Object Creation
                types.Tool(
                    name="add_text",
                    description="Add text object to the current scene",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "id": {"type": "string", "description": "Unique identifier"},
                            "content": {"type": "string", "description": "Text content"},
                            "color": {"type": "string", "description": "Text color", "default": "#FFFFFF"},
                            "position": {
                                "type": "array",
                                "items": {"type": "number"},
                                "description": "Position [x, y, z]",
                                "default": [0, 0, 0]
                            },
                            "font_size": {"type": "integer", "description": "Font size", "default": 48},
                            "font": {"type": "string", "description": "Font family", "default": "Arial"}
                        },
                        "required": ["id", "content"]
                    }
                ),
                
                types.Tool(
                    name="add_shape",
                    description="Add shape object to the current scene",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "id": {"type": "string", "description": "Unique identifier"},
                            "shape_type": {
                                "type": "string",
                                "enum": [shape.value for shape in ShapeType],
                                "description": "Shape type"
                            },
                            "color": {"type": "string", "description": "Shape color", "default": "#FFFFFF"},
                            "size": {"type": "number", "description": "Shape size", "default": 1.0},
                            "position": {
                                "type": "array",
                                "items": {"type": "number"},
                                "description": "Position [x, y, z]",
                                "default": [0, 0, 0]
                            }
                        },
                        "required": ["id", "shape_type"]
                    }
                ),
                
                # Animation
                types.Tool(
                    name="add_animation",
                    description="Add animation to an object",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "target": {"type": "string", "description": "Target object ID"},
                            "animation_type": {
                                "type": "string",
                                "enum": [anim.value for anim in AnimationType],
                                "description": "Animation type"
                            },
                            "start_time": {"type": "number", "description": "Start time in seconds", "default": 0.0},
                            "duration": {"type": "number", "description": "Duration in seconds", "default": 1.0},
                            "easing": {
                                "type": "string",
                                "enum": ["linear", "ease_in", "ease_out", "ease_in_out", "bounce", "elastic", "back", "expo"],
                                "description": "Easing function",
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
                
                # Timeline Presets
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
                            "preset_name": {"type": "string", "description": "Name of the preset"}
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
                            "preset_name": {"type": "string", "description": "Name of the preset to apply"},
                            "parameters": {
                                "type": "object",
                                "description": "Custom parameters for the preset (optional)"
                            }
                        },
                        "required": ["preset_name"]
                    }
                ),
                
                # Scene Management
                types.Tool(
                    name="list_scenes",
                    description="List all created scenes",
                    inputSchema={"type": "object", "properties": {}, "required": []}
                ),
                
                types.Tool(
                    name="get_scene",
                    description="Get scene configuration",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Scene name (optional, defaults to current)"}
                        },
                        "required": []
                    }
                ),
                
                # Rendering
                types.Tool(
                    name="prepare_render",
                    description="Prepare the current scene for rendering (generates script only)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "output_path": {"type": "string", "description": "Output video file path"},
                            "quality": {
                                "type": "string",
                                "enum": [quality.value for quality in RenderQuality],
                                "description": "Render quality",
                                "default": "high"
                            },
                            "save_script": {
                                "type": "boolean",
                                "description": "Save script to permanent location",
                                "default": True
                            }
                        },
                        "required": ["output_path"]
                    }
                ),
                
                types.Tool(
                    name="render_scene",
                    description="Render the current scene to video (prepare and execute)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "output_path": {"type": "string", "description": "Output video file path"},
                            "quality": {
                                "type": "string",
                                "enum": [quality.value for quality in RenderQuality],
                                "description": "Render quality",
                                "default": "high"
                            },
                            "preview": {
                                "type": "boolean",
                                "description": "Open preview after rendering",
                                "default": False
                            },
                            "save_script": {
                                "type": "boolean",
                                "description": "Save script to permanent location",
                                "default": True
                            }
                        },
                        "required": ["output_path"]
                    }
                ),
                
                # Video Management
                types.Tool(
                    name="preview_video",
                    description="Open and preview a generated video file",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "video_path": {"type": "string", "description": "Path to the video file (optional, uses last rendered)"}
                        },
                        "required": []
                    }
                ),
                
                types.Tool(
                    name="list_videos",
                    description="List all generated video files",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "directory": {"type": "string", "description": "Directory to search (optional, searches common locations)"},
                            "limit": {"type": "integer", "description": "Maximum number of videos to return", "default": 10}
                        },
                        "required": []
                    }
                ),
                
                types.Tool(
                    name="get_video_info",
                    description="Get information about a video file",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "video_path": {"type": "string", "description": "Path to the video file"}
                        },
                        "required": ["video_path"]
                    }
                ),
                
                # API Discovery
                types.Tool(
                    name="discover_api_endpoints",
                    description="Discover available API endpoints for external integrations",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "api_base_url": {
                                "type": "string", 
                                "description": "Base URL of the API server",
                                "default": "http://localhost:8000"
                            },
                            "include_schemas": {
                                "type": "boolean",
                                "description": "Include detailed schema information",
                                "default": False
                            }
                        },
                        "required": []
                    }
                ),
                
                types.Tool(
                    name="call_api_endpoint",
                    description="Call a specific API endpoint with data",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "endpoint": {"type": "string", "description": "API endpoint path (e.g., /scenes)"},
                            "method": {
                                "type": "string",
                                "enum": ["GET", "POST", "PUT", "DELETE"],
                                "description": "HTTP method",
                                "default": "GET"
                            },
                            "data": {
                                "type": "object",
                                "description": "Request data for POST/PUT requests"
                            },
                            "api_base_url": {
                                "type": "string",
                                "description": "Base URL of the API server",
                                "default": "http://localhost:8000"
                            }
                        },
                        "required": ["endpoint"]
                    }
                ),
                
                # Utility
                types.Tool(
                    name="save_scene",
                    description="Save scene configuration to file",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "File path (.json or .yaml)"},
                            "scene_name": {"type": "string", "description": "Scene to save (optional, uses current)"}
                        },
                        "required": ["path"]
                    }
                ),
                
                # Documentation & Help
                types.Tool(
                    name="get_mcp_tutorial",
                    description="Get a comprehensive tutorial on using the Manim Studio MCP interface",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "section": {
                                "type": "string",
                                "description": "Specific tutorial section (optional)",
                                "enum": ["getting_started", "scene_creation", "objects_and_animations", "timeline_presets", "rendering", "api_integration", "advanced_features"]
                            }
                        },
                        "required": []
                    }
                ),
                
                types.Tool(
                    name="get_tools_index",
                    description="Get a detailed index of all available MCP tools with their parameters and examples",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "category": {
                                "type": "string",
                                "description": "Filter tools by category (optional)",
                                "enum": ["scene_management", "object_creation", "animation", "timeline_presets", "rendering", "api_discovery", "utility", "documentation"]
                            },
                            "include_examples": {
                                "type": "boolean",
                                "description": "Include usage examples for each tool",
                                "default": True
                            }
                        },
                        "required": []
                    }
                )
            ])
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """Return list of available MCP tools."""
            return self.tools_list

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Optional[Dict[str, Any]]) -> List[types.TextContent]:
            """Handle tool calls using shared features."""
            try:
                result = await self.execute_tool(name, arguments or {})
                return [types.TextContent(type="text", text=result.to_json())]
            except Exception as e:
                logger.error(f"Tool execution error in {name}: {e}")
                error_result = InterfaceResult(
                    status="error",
                    error=str(e),
                    message=f"Failed to execute {name}"
                )
                return [types.TextContent(type="text", text=error_result.to_json())]
    
    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> InterfaceResult:
        """Execute a tool using shared features."""
        
        # Add comprehensive logging for debugging
        logger.info(f"Executing tool: {name}")
        logger.info(f"Raw arguments: {arguments}")
        logger.info(f"Arguments type: {type(arguments)}")
        
        # Ensure arguments is a proper dict
        if arguments is None:
            arguments = {}
        elif not isinstance(arguments, dict):
            logger.error(f"Arguments is not a dict: {type(arguments)}")
            return InterfaceResult(
                status="error",
                error=f"Invalid arguments type: expected dict, got {type(arguments).__name__}"
            )
        
        # Scene Management
        if name == "create_scene":
            # Validate required parameters
            if "name" not in arguments:
                return InterfaceResult(
                    status="error",
                    error="Missing required parameter: name"
                )
            
            try:
                return self.core.create_scene(
                    name=str(arguments["name"]),
                    duration=float(arguments.get("duration", 5.0)),
                    background_color=str(arguments.get("background_color", "#000000")),
                    resolution=list(arguments.get("resolution", [1920, 1080])),
                    fps=int(arguments.get("fps", 60))
                )
            except Exception as e:
                logger.error(f"Error in create_scene: {e}", exc_info=True)
                return InterfaceResult(
                    status="error",
                    error=f"Failed to create scene: {str(e)}"
                )
        
        elif name == "add_text":
            return self.core.add_text(
                text_id=arguments["id"],
                content=arguments["content"],
                color=arguments.get("color", "#FFFFFF"),
                position=arguments.get("position", [0, 0, 0]),
                font_size=arguments.get("font_size", 48),
                font=arguments.get("font", "Arial")
            )
        
        elif name == "add_shape":
            return self.core.add_shape(
                shape_id=arguments["id"],
                shape_type=arguments["shape_type"],
                color=arguments.get("color", "#FFFFFF"),
                size=arguments.get("size", 1.0),
                position=arguments.get("position", [0, 0, 0])
            )
        
        elif name == "add_animation":
            return self.core.add_animation(
                target=arguments["target"],
                animation_type=arguments["animation_type"],
                start_time=arguments.get("start_time", 0.0),
                duration=arguments.get("duration", 1.0),
                easing=arguments.get("easing", "ease_in_out"),
                properties=arguments.get("properties", {})
            )
        
        # Timeline Presets
        elif name == "list_timeline_presets":
            return self.core.list_presets(
                category=arguments.get("category")
            )
        
        elif name == "get_preset_info":
            return self.core.get_preset_info(
                preset_name=arguments["preset_name"]
            )
        
        elif name == "apply_timeline_preset":
            return self.core.apply_preset(
                preset_name=arguments["preset_name"],
                parameters=arguments.get("parameters", {})
            )
        
        # Scene Information
        elif name == "list_scenes":
            return self.core.list_scenes()
        
        elif name == "get_scene":
            return self.core.get_scene(
                scene_name=arguments.get("name")
            )
        
        # Rendering
        elif name == "prepare_render":
            return self.core.prepare_render(
                output_path=arguments["output_path"],
                quality=arguments.get("quality", "high"),
                save_script=arguments.get("save_script", True)  # Default to saving scripts
            )
        
        elif name == "render_scene":
            return self.core.render_scene(
                output_path=arguments["output_path"],
                quality=arguments.get("quality", "high"),
                preview=arguments.get("preview", False),
                save_script=arguments.get("save_script", True)
            )
        
        # API Discovery
        elif name == "discover_api_endpoints":
            return await self._discover_api_endpoints(
                api_base_url=arguments.get("api_base_url", "http://localhost:8000"),
                include_schemas=arguments.get("include_schemas", False)
            )
        
        elif name == "call_api_endpoint":
            return await self._call_api_endpoint(
                endpoint=arguments["endpoint"],
                method=arguments.get("method", "GET"),
                data=arguments.get("data"),
                api_base_url=arguments.get("api_base_url", "http://localhost:8000")
            )
        
        # Utility - MCP specific implementations
        elif name == "save_scene":
            return await self._save_scene(
                path=arguments["path"],
                scene_name=arguments.get("scene_name")
            )
        
        # Video Management
        elif name == "preview_video":
            return await self._preview_video(
                video_path=arguments.get("video_path")
            )
        
        elif name == "list_videos":
            return await self._list_videos(
                directory=arguments.get("directory"),
                limit=arguments.get("limit", 10)
            )
        
        elif name == "get_video_info":
            return await self._get_video_info(
                video_path=arguments["video_path"]
            )
        
        # Documentation & Help
        elif name == "get_mcp_tutorial":
            return await self._get_mcp_tutorial(
                section=arguments.get("section")
            )
        
        elif name == "get_tools_index":
            return await self._get_tools_index(
                category=arguments.get("category"),
                include_examples=arguments.get("include_examples", True)
            )
        
        else:
            return InterfaceResult(
                status="error",
                error=f"Unknown tool: {name}"
            )
    
    async def _save_scene(self, path: str, scene_name: Optional[str] = None) -> InterfaceResult:
        """Save scene configuration to file."""
        try:
            scene_result = self.core.get_scene(scene_name)
            if scene_result.status != "success":
                return scene_result
            
            scene_data = scene_result.data
            file_path = Path(path)
            
            with open(file_path, 'w') as f:
                if file_path.suffix.lower() == '.yaml':
                    import yaml
                    yaml.dump(scene_data, f, default_flow_style=False)
                else:
                    json.dump(scene_data, f, indent=2)
            
            return InterfaceResult(
                status="success",
                data={"path": str(file_path)},
                message=f"Scene saved to {file_path}"
            )
            
        except Exception as e:
            logger.error(f"Failed to save scene: {e}")
            return InterfaceResult(status="error", error=str(e))
    
    async def _discover_api_endpoints(self, api_base_url: str, include_schemas: bool = False) -> InterfaceResult:
        """Discover API endpoints by fetching OpenAPI schema."""
        try:
            import aiohttp
            import asyncio
            
            async with aiohttp.ClientSession() as session:
                # Try to get API info endpoint first (more structured)
                try:
                    async with session.get(f"{api_base_url}/api-info") as response:
                        if response.status == 200:
                            api_info = await response.json()
                            
                            if not include_schemas:
                                # Remove detailed schemas to reduce output size
                                api_info.pop("schemas", None)
                            
                            return InterfaceResult(
                                status="success",
                                data=api_info,
                                message=f"Discovered {api_info.get('total_endpoints', 0)} API endpoints"
                            )
                except Exception:
                    pass
                
                # Fallback to raw OpenAPI schema
                try:
                    async with session.get(f"{api_base_url}/openapi.json") as response:
                        if response.status == 200:
                            openapi_schema = await response.json()
                            
                            # Extract basic endpoint info
                            endpoints = []
                            for path, methods in openapi_schema.get("paths", {}).items():
                                for method, details in methods.items():
                                    if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                                        endpoints.append({
                                            "path": path,
                                            "method": method.upper(),
                                            "summary": details.get("summary", ""),
                                            "description": details.get("description", "")
                                        })
                            
                            result_data = {
                                "api_info": openapi_schema.get("info", {}),
                                "endpoints": endpoints,
                                "base_url": api_base_url,
                                "total_endpoints": len(endpoints)
                            }
                            
                            if include_schemas:
                                result_data["schemas"] = openapi_schema.get("components", {}).get("schemas", {})
                            
                            return InterfaceResult(
                                status="success",
                                data=result_data,
                                message=f"Discovered {len(endpoints)} API endpoints from OpenAPI schema"
                            )
                        else:
                            return InterfaceResult(
                                status="error",
                                error=f"Failed to fetch OpenAPI schema: HTTP {response.status}"
                            )
                except Exception as e:
                    return InterfaceResult(
                        status="error",
                        error=f"Failed to connect to API at {api_base_url}: {str(e)}"
                    )
                    
        except ImportError:
            return InterfaceResult(
                status="error",
                error="aiohttp package required for API discovery. Install with: pip install aiohttp"
            )
        except Exception as e:
            logger.error(f"Failed to discover API endpoints: {e}")
            return InterfaceResult(status="error", error=str(e))
    
    async def _call_api_endpoint(self, endpoint: str, method: str = "GET", 
                                data: Optional[Dict[str, Any]] = None, 
                                api_base_url: str = "http://localhost:8000") -> InterfaceResult:
        """Call a specific API endpoint."""
        try:
            import aiohttp
            import json as json_lib
            
            # Ensure endpoint starts with /
            if not endpoint.startswith("/"):
                endpoint = "/" + endpoint
            
            url = f"{api_base_url}{endpoint}"
            
            async with aiohttp.ClientSession() as session:
                if method.upper() == "GET":
                    async with session.get(url) as response:
                        response_data = await response.json()
                        status_code = response.status
                elif method.upper() == "POST":
                    headers = {"Content-Type": "application/json"}
                    json_data = json_lib.dumps(data) if data else None
                    async with session.post(url, data=json_data, headers=headers) as response:
                        response_data = await response.json()
                        status_code = response.status
                elif method.upper() == "PUT":
                    headers = {"Content-Type": "application/json"}
                    json_data = json_lib.dumps(data) if data else None
                    async with session.put(url, data=json_data, headers=headers) as response:
                        response_data = await response.json()
                        status_code = response.status
                elif method.upper() == "DELETE":
                    async with session.delete(url) as response:
                        response_data = await response.json()
                        status_code = response.status
                else:
                    return InterfaceResult(
                        status="error",
                        error=f"Unsupported HTTP method: {method}"
                    )
                
                if 200 <= status_code < 300:
                    return InterfaceResult(
                        status="success",
                        data={
                            "response": response_data,
                            "status_code": status_code,
                            "endpoint": endpoint,
                            "method": method.upper()
                        },
                        message=f"Successfully called {method.upper()} {endpoint}"
                    )
                else:
                    return InterfaceResult(
                        status="error",
                        error=f"API call failed with status {status_code}: {response_data}",
                        data={
                            "status_code": status_code,
                            "response": response_data,
                            "endpoint": endpoint,
                            "method": method.upper()
                        }
                    )
                    
        except ImportError:
            return InterfaceResult(
                status="error",
                error="aiohttp package required for API calls. Install with: pip install aiohttp"
            )
        except Exception as e:
            logger.error(f"Failed to call API endpoint {endpoint}: {e}")
            return InterfaceResult(status="error", error=str(e))
    
    async def _get_mcp_tutorial(self, section: Optional[str] = None) -> InterfaceResult:
        """Get MCP tutorial content."""
        tutorials = {
            "getting_started": {
                "title": "Getting Started with Manim Studio MCP",
                "content": """Welcome to Manim Studio MCP Interface!

The MCP (Model Context Protocol) interface allows you to create animations programmatically through tool calls.

## Quick Start:
1. Create a scene: Use 'create_scene' with a name and optional parameters
2. Add objects: Use 'add_text' or 'add_shape' to add visual elements
3. Add animations: Use 'add_animation' to animate your objects
4. Render: Use 'render_scene' to create the video

## Example Workflow:
```
1. create_scene(name="my_animation", duration=5)
2. add_text(id="title", content="Hello World", position=[0, 2, 0])
3. add_animation(target="title", animation_type="fade_in", start_time=0, duration=1)
4. render_scene(output_path="my_animation.mp4", quality="high")
```

Use 'get_tools_index' for a complete list of available tools!"""
            },
            "scene_creation": {
                "title": "Scene Creation and Management",
                "content": """## Creating and Managing Scenes

### create_scene
Creates a new animation scene with specified parameters.

Parameters:
- name (required): Unique scene identifier
- duration: Total scene duration in seconds (default: 5.0)
- background_color: Hex color code (default: "#000000")
- resolution: [width, height] array (default: [1920, 1080])
- fps: Frames per second (default: 60)

### list_scenes
Lists all created scenes in the current session.

### get_scene
Retrieves configuration for a specific scene or the current scene.

### save_scene
Saves scene configuration to a JSON or YAML file.

Example:
```
create_scene(name="intro", duration=3, background_color="#1a1a1a")
```"""
            },
            "objects_and_animations": {
                "title": "Objects and Animations",
                "content": """## Adding Objects and Animations

### Objects

**add_text**
- id: Unique identifier for the text object
- content: The text to display
- color: Text color (default: "#FFFFFF")
- position: [x, y, z] coordinates (default: [0, 0, 0])
- font_size: Size in points (default: 48)
- font: Font family (default: "Arial")

**add_shape**
- id: Unique identifier
- shape_type: circle, square, triangle, rectangle, polygon, star, arrow
- color: Shape color (default: "#FFFFFF")
- size: Scale factor (default: 1.0)
- position: [x, y, z] coordinates

### Animations

**add_animation**
- target: ID of object to animate
- animation_type: fade_in, fade_out, move_to, scale, rotate, morph, color_change
- start_time: When to start (seconds)
- duration: Animation duration
- easing: linear, ease_in, ease_out, ease_in_out, bounce, elastic, back, expo
- properties: Type-specific properties (e.g., end_position for move_to)

Example:
```
add_shape(id="circle1", shape_type="circle", color="#FF0000", position=[-3, 0, 0])
add_animation(target="circle1", animation_type="move_to", start_time=1, duration=2, 
              properties={"end_position": [3, 0, 0]}, easing="ease_in_out")
```"""
            },
            "timeline_presets": {
                "title": "Timeline Presets",
                "content": """## Using Timeline Presets

Timeline presets provide pre-built animation sequences that you can apply to your scenes.

### Available Tools:

**list_timeline_presets**
- category (optional): Filter by category
  - intro, outro, transition, title, data_visualization, motion_graphics, educational, social_media

**get_preset_info**
- preset_name: Get detailed information about a specific preset

**apply_timeline_preset**
- preset_name: Name of the preset to apply
- parameters: Custom parameters for the preset

### Common Presets:
- fade_intro: Simple fade-in introduction
- slide_transition: Sliding transition between scenes
- title_reveal: Animated title sequence
- data_chart_build: Animated chart construction
- kinetic_typography: Dynamic text animations

Example:
```
list_timeline_presets(category="intro")
apply_timeline_preset(preset_name="fade_intro", parameters={"duration": 2})
```"""
            },
            "rendering": {
                "title": "Rendering Your Animation",
                "content": """## Rendering Options

### prepare_render
Generates a render script without executing it. Useful for reviewing before rendering.
- output_path: Where to save the video
- quality: low, medium, high, ultra (default: high)
- save_script: Save the script permanently (default: True)

### render_scene
Prepares and executes the full render process.
- output_path: Video file path
- quality: Render quality preset
- preview: Open video after rendering (default: False)
- save_script: Save script to permanent location (default: True)

### Quality Presets:
- low: 480p, 30fps - Fast preview
- medium: 720p, 30fps - Good balance
- high: 1080p, 60fps - Production quality
- ultra: 4K, 60fps - Maximum quality

### Output Formats:
- .mp4: Most compatible format (recommended)
- .mov: High quality, larger files
- .webm: Web-optimized format

Example:
```
render_scene(output_path="final_animation.mp4", quality="high", preview=True)
```"""
            },
            "api_integration": {
                "title": "API Integration",
                "content": """## External API Integration

The MCP interface can discover and interact with external APIs.

### discover_api_endpoints
Discovers available endpoints from an API server.
- api_base_url: Base URL of the API (default: http://localhost:8000)
- include_schemas: Include detailed schema information

### call_api_endpoint
Calls a specific API endpoint.
- endpoint: API path (e.g., "/scenes")
- method: GET, POST, PUT, DELETE
- data: Request payload for POST/PUT
- api_base_url: Base URL of the API

### Use Cases:
1. Import scenes from external sources
2. Export rendered videos to cloud storage
3. Integrate with asset management systems
4. Synchronize with collaborative platforms

Example:
```
discover_api_endpoints(api_base_url="http://api.example.com")
call_api_endpoint(endpoint="/scenes", method="POST", 
                  data={"name": "new_scene", "config": {...}})
```"""
            },
            "advanced_features": {
                "title": "Advanced Features",
                "content": """## Advanced MCP Features

### Script Preservation
All MCP-generated scripts are automatically saved to prevent losing work:
- Location: user-data/mcp-scripts/
- Includes metadata with scene configuration
- Recovery tool available at src/interfaces/mcp/recover_scripts.py

### Batch Operations
Create complex animations by chaining multiple tool calls:
```
# Create multiple objects in a loop
for i in range(5):
    add_shape(id=f"shape_{i}", shape_type="circle", 
              position=[i-2, 0, 0], color=f"#{i}0{i}0FF")
    add_animation(target=f"shape_{i}", animation_type="fade_in",
                  start_time=i*0.2, duration=0.5)
```

### Custom Easing Functions
Available easing types for smooth animations:
- linear: Constant speed
- ease_in/out: Acceleration/deceleration
- bounce: Bouncing effect
- elastic: Spring-like motion
- back: Overshoot and return
- expo: Exponential acceleration

### Performance Tips:
1. Use lower quality for previews
2. Batch similar operations together
3. Reuse scenes when possible
4. Optimize asset sizes before importing"""
            }
        }
        
        if section and section in tutorials:
            tutorial = tutorials[section]
            return InterfaceResult(
                status="success",
                data={
                    "section": section,
                    "title": tutorial["title"],
                    "content": tutorial["content"]
                },
                message=f"Tutorial section: {tutorial['title']}"
            )
        elif section:
            return InterfaceResult(
                status="error",
                error=f"Unknown tutorial section: {section}",
                data={"available_sections": list(tutorials.keys())}
            )
        else:
            # Return overview with all sections
            overview = """# Manim Studio MCP Tutorial

Welcome to the comprehensive Manim Studio MCP interface tutorial!

## Available Tutorial Sections:

1. **getting_started** - Quick introduction and basic workflow
2. **scene_creation** - Creating and managing animation scenes
3. **objects_and_animations** - Adding visual elements and animations
4. **timeline_presets** - Using pre-built animation sequences
5. **rendering** - Rendering options and output formats
6. **api_integration** - Connecting to external APIs
7. **advanced_features** - Script preservation, batch operations, and tips

To view a specific section, use:
`get_mcp_tutorial(section="section_name")`

For a complete tool reference, use:
`get_tools_index()`
"""
            return InterfaceResult(
                status="success",
                data={
                    "overview": overview,
                    "sections": {k: v["title"] for k, v in tutorials.items()}
                },
                message="MCP Tutorial Overview"
            )
    
    async def _get_tools_index(self, category: Optional[str] = None, 
                              include_examples: bool = True) -> InterfaceResult:
        """Get an index of all available tools."""
        
        # Use the stored tools list
        tools = self.tools_list
        
        # Categorize tools
        categorized_tools = {
            "scene_management": [],
            "object_creation": [],
            "animation": [],
            "timeline_presets": [],
            "rendering": [],
            "api_discovery": [],
            "utility": [],
            "documentation": []
        }
        
        # Tool examples
        examples = {
            "create_scene": 'create_scene(name="my_animation", duration=5, background_color="#1a1a1a")',
            "add_text": 'add_text(id="title", content="Hello World", position=[0, 2, 0], color="#FFD700")',
            "add_shape": 'add_shape(id="circle1", shape_type="circle", size=1.5, color="#FF0000")',
            "add_animation": 'add_animation(target="circle1", animation_type="rotate", duration=2, properties={"angle": 360})',
            "list_timeline_presets": 'list_timeline_presets(category="intro")',
            "apply_timeline_preset": 'apply_timeline_preset(preset_name="fade_intro")',
            "render_scene": 'render_scene(output_path="output.mp4", quality="high", preview=True)',
            "save_scene": 'save_scene(path="my_scene.yaml")',
            "get_mcp_tutorial": 'get_mcp_tutorial(section="getting_started")',
            "get_tools_index": 'get_tools_index(category="animation", include_examples=True)'
        }
        
        # Categorize each tool
        for tool in tools:
            tool_data = {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema.get("properties", {}),
                "required": tool.inputSchema.get("required", [])
            }
            
            if include_examples and tool.name in examples:
                tool_data["example"] = examples[tool.name]
            
            # Determine category
            if tool.name in ["create_scene", "list_scenes", "get_scene"]:
                categorized_tools["scene_management"].append(tool_data)
            elif tool.name in ["add_text", "add_shape"]:
                categorized_tools["object_creation"].append(tool_data)
            elif tool.name in ["add_animation"]:
                categorized_tools["animation"].append(tool_data)
            elif tool.name in ["list_timeline_presets", "get_preset_info", "apply_timeline_preset"]:
                categorized_tools["timeline_presets"].append(tool_data)
            elif tool.name in ["prepare_render", "render_scene"]:
                categorized_tools["rendering"].append(tool_data)
            elif tool.name in ["discover_api_endpoints", "call_api_endpoint"]:
                categorized_tools["api_discovery"].append(tool_data)
            elif tool.name in ["get_mcp_tutorial", "get_tools_index"]:
                categorized_tools["documentation"].append(tool_data)
            else:
                categorized_tools["utility"].append(tool_data)
        
        # Filter by category if specified
        if category:
            if category in categorized_tools:
                result_data = {
                    "category": category,
                    "tools": categorized_tools[category],
                    "total_tools": len(categorized_tools[category])
                }
            else:
                return InterfaceResult(
                    status="error",
                    error=f"Unknown category: {category}",
                    data={"available_categories": list(categorized_tools.keys())}
                )
        else:
            # Return all categories
            result_data = {
                "categories": categorized_tools,
                "total_tools": sum(len(tools) for tools in categorized_tools.values()),
                "summary": {cat: len(tools) for cat, tools in categorized_tools.items()}
            }
        
        return InterfaceResult(
            status="success",
            data=result_data,
            message=f"Found {result_data.get('total_tools', 0)} tools"
        )
    
    async def _preview_video(self, video_path: Optional[str] = None) -> InterfaceResult:
        """Open and preview a video file."""
        try:
            import subprocess
            import platform
            import glob
            
            # If no path provided, try to find the most recent video
            if not video_path:
                search_paths = [
                    "user-data/videos/**/*.mp4",
                    "user-data/**/*.mp4",
                    "/tmp/**/*.mp4",
                    "./**/*.mp4"
                ]
                
                all_videos = []
                for pattern in search_paths:
                    try:
                        videos = glob.glob(pattern, recursive=True)
                        all_videos.extend(videos)
                    except:
                        pass
                
                if not all_videos:
                    return InterfaceResult(
                        status="error",
                        error="No video files found. Please render a scene first."
                    )
                
                # Get the most recent video
                all_videos.sort(key=lambda x: os.path.getmtime(x), reverse=True)
                video_path = all_videos[0]
            
            # Check if file exists
            if not os.path.exists(video_path):
                return InterfaceResult(
                    status="error",
                    error=f"Video file not found: {video_path}"
                )
            
            # Open the video with the default system player
            system = platform.system()
            if system == "Darwin":  # macOS
                subprocess.run(["open", video_path])
            elif system == "Linux":
                subprocess.run(["xdg-open", video_path])
            elif system == "Windows":
                subprocess.run(["start", video_path], shell=True)
            else:
                return InterfaceResult(
                    status="error",
                    error=f"Unsupported platform: {system}"
                )
            
            return InterfaceResult(
                status="success",
                data={
                    "video_path": video_path,
                    "file_size": os.path.getsize(video_path),
                    "opened": True
                },
                message=f"Opened video: {video_path}"
            )
            
        except Exception as e:
            logger.error(f"Failed to preview video: {e}")
            return InterfaceResult(status="error", error=str(e))
    
    async def _list_videos(self, directory: Optional[str] = None, limit: int = 10) -> InterfaceResult:
        """List available video files."""
        try:
            import glob
            from datetime import datetime
            
            if directory:
                search_patterns = [f"{directory}/**/*.mp4", f"{directory}/**/*.mov"]
            else:
                search_patterns = [
                    "user-data/videos/**/*.mp4",
                    "user-data/**/*.mp4",
                    "/tmp/**/*.mp4",
                    "./**/*.mp4",
                    "user-data/videos/**/*.mov",
                    "/tmp/**/*.mov"
                ]
            
            all_videos = []
            for pattern in search_patterns:
                try:
                    videos = glob.glob(pattern, recursive=True)
                    all_videos.extend(videos)
                except:
                    pass
            
            # Remove duplicates
            all_videos = list(set(all_videos))
            
            # Get file info and sort by modification time
            video_info = []
            for video in all_videos:
                try:
                    stat = os.stat(video)
                    video_info.append({
                        "path": video,
                        "filename": os.path.basename(video),
                        "size": stat.st_size,
                        "size_mb": round(stat.st_size / (1024 * 1024), 2),
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "modified_timestamp": stat.st_mtime
                    })
                except:
                    pass
            
            # Sort by modification time (newest first)
            video_info.sort(key=lambda x: x["modified_timestamp"], reverse=True)
            
            # Limit results
            video_info = video_info[:limit]
            
            # Remove timestamp from final output
            for info in video_info:
                info.pop("modified_timestamp", None)
            
            return InterfaceResult(
                status="success",
                data={
                    "videos": video_info,
                    "total_found": len(video_info),
                    "search_patterns": search_patterns if directory else ["various locations"]
                },
                message=f"Found {len(video_info)} video files"
            )
            
        except Exception as e:
            logger.error(f"Failed to list videos: {e}")
            return InterfaceResult(status="error", error=str(e))
    
    async def _get_video_info(self, video_path: str) -> InterfaceResult:
        """Get detailed information about a video file."""
        try:
            if not os.path.exists(video_path):
                return InterfaceResult(
                    status="error",
                    error=f"Video file not found: {video_path}"
                )
            
            stat = os.stat(video_path)
            from datetime import datetime
            
            # Try to get video metadata using ffprobe if available
            metadata = {}
            try:
                import subprocess
                result = subprocess.run(
                    ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", video_path],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    import json as json_lib
                    probe_data = json_lib.loads(result.stdout)
                    if "streams" in probe_data and probe_data["streams"]:
                        stream = probe_data["streams"][0]
                        metadata = {
                            "width": stream.get("width"),
                            "height": stream.get("height"),
                            "duration": stream.get("duration"),
                            "fps": stream.get("r_frame_rate"),
                            "codec": stream.get("codec_name")
                        }
            except:
                # ffprobe not available
                pass
            
            return InterfaceResult(
                status="success",
                data={
                    "path": video_path,
                    "filename": os.path.basename(video_path),
                    "size": stat.st_size,
                    "size_mb": round(stat.st_size / (1024 * 1024), 2),
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "metadata": metadata
                },
                message=f"Video info for {os.path.basename(video_path)}"
            )
            
        except Exception as e:
            logger.error(f"Failed to get video info: {e}")
            return InterfaceResult(status="error", error=str(e))
    
    async def run(self):
        """Run the MCP server."""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="manim-studio",
                    server_version="0.3.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )


async def main():
    """Main entry point."""
    # Log to stderr only, not stdout
    print("Starting Manim Studio MCP Interface...", file=sys.stderr)
    try:
        interface = MCPInterface()
        await interface.run()
    except Exception as e:
        print(f"MCP Interface failed to start: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    # Ensure stdout is not buffered for MCP protocol
    sys.stdout = sys.stdout.detach()
    sys.stdout = io.TextIOWrapper(sys.stdout, encoding='utf-8', line_buffering=True)
    
    asyncio.run(main())