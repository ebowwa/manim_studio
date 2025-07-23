"""Scene management tools for MCP interface."""

from typing import List
import mcp.types as types

def get_scene_tools() -> List[types.Tool]:
    """Return scene management tools."""
    return [
        types.Tool(
            name="create_timeline",
            description="Create a timeline with markers and labels",
            inputSchema={
                "type": "object",
                "properties": {
                    "markers": {
                        "type": "array",
                        "description": "Timeline markers",
                        "items": {
                            "type": "object",
                            "properties": {
                                "time": {"type": "number", "description": "Time in seconds"},
                                "label": {"type": "string", "description": "Marker label"},
                                "color": {"type": "string", "description": "Marker color"}
                            }
                        }
                    },
                    "tracks": {
                        "type": "array",
                        "description": "Timeline tracks for organizing animations",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "Track name"},
                                "muted": {"type": "boolean", "description": "Whether track is muted", "default": False}
                            }
                        }
                    }
                }
            }
        ),
        types.Tool(
            name="compose_scenes",
            description="Compose multiple scenes into one",
            inputSchema={
                "type": "object",
                "properties": {
                    "scenes": {
                        "type": "array",
                        "description": "Scenes to compose",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "Scene name"},
                                "start_time": {"type": "number", "description": "Start time"},
                                "duration": {"type": "number", "description": "Duration"},
                                "transition": {
                                    "type": "string",
                                    "enum": ["cut", "fade", "wipe", "slide"],
                                    "description": "Transition type"
                                }
                            }
                        }
                    },
                    "output_name": {"type": "string", "description": "Name for composed scene"}
                },
                "required": ["scenes", "output_name"]
            }
        ),
        types.Tool(
            name="create_template",
            description="Create a reusable scene template",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Template name"},
                    "description": {"type": "string", "description": "Template description"},
                    "parameters": {
                        "type": "array",
                        "description": "Template parameters",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "Parameter name"},
                                "type": {"type": "string", "description": "Parameter type"},
                                "default": {"description": "Default value"},
                                "description": {"type": "string", "description": "Parameter description"}
                            }
                        }
                    },
                    "base_scene": {"type": "string", "description": "Base scene name"}
                },
                "required": ["name", "base_scene"]
            }
        ),
        types.Tool(
            name="analyze_scene",
            description="Analyze scene complexity and provide optimization suggestions",
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_name": {"type": "string", "description": "Scene to analyze"}
                }
            }
        )
    ]