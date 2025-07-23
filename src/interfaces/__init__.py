"""Manim Studio Interfaces Package

This package provides multiple interfaces for interacting with Manim Studio:

1. **Shared Features** (`shared_features.py`):
   - Core functionality shared across all interfaces
   - Standardized data models and business logic
   - Scene management, animation handling, and rendering

2. **MCP Interface** (`mcp_interface.py`):
   - Model Context Protocol integration for AI assistants
   - Tool-based interaction model
   - Supports Claude, ChatGPT, and other AI systems

3. **GUI Interface** (`gui_interface.py`):
   - Web-based visual interface using Gradio
   - User-friendly forms and controls
   - Real-time feedback and JSON output

4. **API Interface** (`api_interface.py`):
   - REST API using FastAPI
   - Programmatic access for developers
   - Batch operations and templates

All interfaces use the same core functionality, ensuring consistency
and reducing code duplication.
"""

from .shared_features import (
    ManimStudioCore,
    SceneManager,
    PresetManager,
    RenderEngine,
    InterfaceResult,
    AnimationType,
    ShapeType,
    RenderQuality,
    TextObject,
    ShapeObject,
    AnimationSequence,
    SceneDefinition
)

__all__ = [
    "ManimStudioCore",
    "SceneManager", 
    "PresetManager",
    "RenderEngine",
    "InterfaceResult",
    "AnimationType",
    "ShapeType", 
    "RenderQuality",
    "TextObject",
    "ShapeObject",
    "AnimationSequence", 
    "SceneDefinition"
]

__version__ = "0.3.0"