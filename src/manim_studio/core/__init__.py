"""Core functionality for Manim Studio."""

from .config import Config, SceneConfig, EffectConfig
from .timeline import Timeline, TimelineEvent
from .asset_manager import AssetManager
from .scene_builder import SceneBuilder

__all__ = [
    'Config', 'SceneConfig', 'EffectConfig',
    'Timeline', 'TimelineEvent',
    'AssetManager', 'SceneBuilder'
]