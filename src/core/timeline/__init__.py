"""Timeline module for Manim Studio."""

from .timeline import Timeline, TimelineEvent
from .composer_timeline import (
    ComposerTimeline, TimelineLayer, TimelineTrack,
    Keyframe, InterpolationType, TrackType
)
from .timeline_presets import TimelinePresets, PresetCategory, TimelinePreset
from .layer_manager import LayerManager, create_layered_scene

__all__ = [
    'Timeline', 'TimelineEvent',
    'ComposerTimeline', 'TimelineLayer', 'TimelineTrack',
    'Keyframe', 'InterpolationType', 'TrackType',
    'TimelinePresets', 'PresetCategory', 'TimelinePreset',
    'LayerManager', 'create_layered_scene'
]