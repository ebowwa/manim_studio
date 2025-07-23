"""Rendering pipeline tools for MCP interface."""

from typing import List
import mcp.types as types

def get_render_tools() -> List[types.Tool]:
    """Return rendering pipeline tools."""
    return [
        types.Tool(
            name="batch_render",
            description="Render multiple scenes with different parameters",
            inputSchema={
                "type": "object",
                "properties": {
                    "template": {"type": "string", "description": "Template name"},
                    "variations": {
                        "type": "array",
                        "description": "Parameter variations",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "Variation name"},
                                "params": {"type": "object", "description": "Parameter values"}
                            }
                        }
                    },
                    "output_dir": {"type": "string", "description": "Output directory"},
                    "parallel": {"type": "boolean", "description": "Render in parallel", "default": False}
                },
                "required": ["template", "variations", "output_dir"]
            }
        ),
        types.Tool(
            name="export_frame",
            description="Export a specific frame as an image",
            inputSchema={
                "type": "object",
                "properties": {
                    "time": {"type": "number", "description": "Time in seconds"},
                    "output_path": {"type": "string", "description": "Output image path"},
                    "format": {
                        "type": "string",
                        "enum": ["png", "jpg", "svg"],
                        "description": "Image format",
                        "default": "png"
                    },
                    "resolution": {"type": "array", "description": "Resolution [width, height]"}
                },
                "required": ["time", "output_path"]
            }
        )
    ]