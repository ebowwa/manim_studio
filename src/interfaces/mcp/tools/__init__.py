"""MCP Tools for Manim Studio - organized by functionality."""

from .scene_management import get_scene_tools
from .text_and_shapes import get_object_tools
from .animation_system import get_animation_tools
from .rendering_pipeline import get_render_tools

def get_all_tools():
    """Get all MCP tools organized by category."""
    tools = []
    tools.extend(get_scene_tools())
    tools.extend(get_object_tools())
    tools.extend(get_animation_tools())
    tools.extend(get_render_tools())
    return tools