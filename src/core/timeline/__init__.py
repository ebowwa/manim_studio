"""Timeline module for Manim Studio."""

from core.timeline.timeline import Timeline, TimelineEvent
from core.timeline.composer_timeline import (
    ComposerTimeline, TimelineLayer, TimelineTrack,
    Keyframe, InterpolationType, TrackType
)
from core.timeline.timeline_presets import TimelinePresets, PresetCategory, TimelinePreset
from core.timeline.layer_manager import LayerManager, create_layered_scene

__all__ = [
    'Timeline', 'TimelineEvent',
    'ComposerTimeline', 'TimelineLayer', 'TimelineTrack',
    'Keyframe', 'InterpolationType', 'TrackType',
    'TimelinePresets', 'PresetCategory', 'TimelinePreset',
    'LayerManager', 'create_layered_scene'
]