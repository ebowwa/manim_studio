"""
Manim Studio - A framework for creating animated videos using Manim
"""

__version__ = "0.2.0"
__author__ = "ebowwa"

from manim_studio.scenes.base_scene import StudioScene
from manim_studio.components.base_components import *
from manim_studio.core import Config, SceneBuilder, Timeline, AssetManager
from manim_studio.core.timeline_enhanced import (
    EnhancedTimeline, TimelineLayer, TimelineTrack, 
    Keyframe, InterpolationType, TrackType
)
from manim_studio.core.timeline_presets import TimelinePresets, PresetCategory
from manim_studio.components.effects import EffectRegistry, register_effect
from manim_studio.components.timeline_visualizer import TimelineVisualizer
from manim_studio.components.keyframe_editor import KeyframeEditor
from manim_studio.utils.timeline_debugger import TimelineDebugger

__all__ = [
    'StudioScene',
    'Config',
    'SceneBuilder', 
    'Timeline',
    'AssetManager',
    'EffectRegistry',
    'register_effect',
    # Enhanced Timeline
    'EnhancedTimeline',
    'TimelineLayer',
    'TimelineTrack',
    'Keyframe',
    'InterpolationType',
    'TrackType',
    'TimelinePresets',
    'PresetCategory',
    'TimelineVisualizer',
    'KeyframeEditor',
    'TimelineDebugger'
]
