"""Shared functionality for Manim Studio interfaces.

This package contains common features and state management used across
all interfaces (MCP, GUI, API).
"""

from .shared_features import (
    ManimStudioCore,
    SceneManager,
    PresetManager,
    RenderEngine,
    InterfaceResult,
    SceneDefinition,
    TextObject,
    ShapeObject,
    CADDimensionObject,
    AnimationSequence,
    AnimationType,
    ShapeType,
    RenderQuality,
    safe_asdict
)
from .shared_state import shared_core

__all__ = [
    'ManimStudioCore',
    'shared_core',
    'SceneManager',
    'PresetManager',
    'RenderEngine',
    'InterfaceResult',
    'SceneDefinition',
    'TextObject',
    'ShapeObject',
    'CADDimensionObject',
    'AnimationSequence',
    'AnimationType',
    'ShapeType',
    'RenderQuality',
    'safe_asdict'
]