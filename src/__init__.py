"""
Manim Studio - A framework for creating animated videos using Manim
"""

__version__ = "0.2.0"
__author__ = "ebowwa"

from .scenes.base_scene import StudioScene
from .components.base_components import *
from .core import Config, SceneBuilder, AssetManager
from .core.timeline import Timeline
from .core.timeline.composer_timeline import (
    ComposerTimeline, TimelineLayer, TimelineTrack, 
    Keyframe, InterpolationType, TrackType
)
from .core.timeline.timeline_presets import TimelinePresets, PresetCategory
from .components.effects import EffectRegistry, register_effect
from .components.timeline_visualizer import TimelineVisualizer
from .components.keyframe_editor import KeyframeEditor
# from .utils.timeline_debugger import TimelineDebugger

__all__ = [
    'StudioScene',
    'Config',
    'SceneBuilder', 
    'Timeline',
    'AssetManager',
    'EffectRegistry',
    'register_effect',
    # Composer Timeline
    'ComposerTimeline',
    'TimelineLayer',
    'TimelineTrack',
    'Keyframe',
    'InterpolationType',
    'TrackType',
    'TimelinePresets',
    'PresetCategory',
    'TimelineVisualizer',
    'KeyframeEditor',
    # 'TimelineDebugger'
]
