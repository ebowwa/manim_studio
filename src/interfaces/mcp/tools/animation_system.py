"""Animation system tools for MCP interface."""

from typing import List
import mcp.types as types

def get_animation_tools() -> List[types.Tool]:
    """Return animation system tools."""
    return [
        types.Tool(
            name="add_camera_movement",
            description="Add camera movements to the scene",
            inputSchema={
                "type": "object",
                "properties": {
                    "movement_type": {
                        "type": "string",
                        "enum": ["pan", "zoom", "rotate", "follow"],
                        "description": "Camera movement type"
                    },
                    "start_time": {"type": "number", "description": "Start time"},
                    "duration": {"type": "number", "description": "Duration"},
                    "params": {
                        "type": "object",
                        "properties": {
                            "from_position": {"type": "array", "description": "Starting position"},
                            "to_position": {"type": "array", "description": "Ending position"},
                            "zoom_factor": {"type": "number", "description": "Zoom factor"},
                            "target": {"type": "string", "description": "Object to follow"},
                            "smooth": {"type": "boolean", "description": "Smooth movement", "default": True}
                        }
                    }
                },
                "required": ["movement_type", "start_time", "duration"]
            }
        ),
        types.Tool(
            name="add_audio_sync",
            description="Synchronize animations with audio",
            inputSchema={
                "type": "object",
                "properties": {
                    "audio_file": {"type": "string", "description": "Path to audio file"},
                    "sync_points": {
                        "type": "array",
                        "description": "Audio sync points",
                        "items": {
                            "type": "object",
                            "properties": {
                                "time": {"type": "number", "description": "Time in audio"},
                                "action": {"type": "string", "description": "Action to trigger"},
                                "target": {"type": "string", "description": "Target object"}
                            }
                        }
                    },
                    "beat_sync": {
                        "type": "boolean",
                        "description": "Auto-sync to beat",
                        "default": False
                    }
                },
                "required": ["audio_file"]
            }
        )
    ]