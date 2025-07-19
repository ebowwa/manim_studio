"""
Manim Studio - A framework for creating animated videos using Manim
"""

__version__ = "0.2.0"
__author__ = "ebowwa"

from manim_studio.scenes.base_scene import StudioScene
from manim_studio.components.base_components import *
from manim_studio.core import Config, SceneBuilder, Timeline, AssetManager
from manim_studio.components.effects import EffectRegistry, register_effect

__all__ = [
    'StudioScene',
    'Config',
    'SceneBuilder', 
    'Timeline',
    'AssetManager',
    'EffectRegistry',
    'register_effect'
]
