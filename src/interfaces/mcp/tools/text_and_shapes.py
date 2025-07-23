"""Text and shape object tools for MCP interface."""

from typing import List
import mcp.types as types

def get_object_tools() -> List[types.Tool]:
    """Return text and shape object tools."""
    return [
        types.Tool(
            name="add_3d_object",
            description="Add 3D object to the scene",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "Object ID"},
                    "type": {
                        "type": "string",
                        "enum": ["cube", "sphere", "cylinder", "torus", "custom"],
                        "description": "3D object type"
                    },
                    "position": {"type": "array", "description": "3D position [x, y, z]"},
                    "rotation": {"type": "array", "description": "Rotation [x, y, z]"},
                    "scale": {"type": "array", "description": "Scale [x, y, z]"},
                    "color": {"type": "string", "description": "Object color"},
                    "material": {
                        "type": "object",
                        "properties": {
                            "metallic": {"type": "number", "description": "Metallic value 0-1"},
                            "roughness": {"type": "number", "description": "Roughness value 0-1"},
                            "emission": {"type": "string", "description": "Emission color"}
                        }
                    },
                    "model_path": {"type": "string", "description": "Path to 3D model (for custom)"}
                },
                "required": ["id", "type", "position"]
            }
        ),
        types.Tool(
            name="add_lighting",
            description="Add lighting to the scene",
            inputSchema={
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["ambient", "directional", "point", "spot"],
                        "description": "Light type"
                    },
                    "color": {"type": "string", "description": "Light color"},
                    "intensity": {"type": "number", "description": "Light intensity", "default": 1.0},
                    "position": {"type": "array", "description": "Light position (for point/spot)"},
                    "direction": {"type": "array", "description": "Light direction (for directional/spot)"},
                    "angle": {"type": "number", "description": "Spot light angle"}
                },
                "required": ["type", "color"]
            }
        )
    ]