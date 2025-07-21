"""Core functionality for Manim Studio."""

from .config import Config, SceneConfig, EffectConfig
from .timeline.timeline import Timeline, TimelineEvent
from .asset_manager import AssetManager
from .scene_builder import SceneBuilder
from .layer_manager import LayerManager
from .cache import CacheManager, SceneCache, get_cache, configure_cache
from .render_hooks import RenderHooks, RenderHookConfig, FrameExtractionMixin, auto_extract_frames

__all__ = [
    'Config', 'SceneConfig', 'EffectConfig',
    'Timeline', 'TimelineEvent',
    'AssetManager', 'SceneBuilder',
    'LayerManager',
    'CacheManager', 'SceneCache', 'get_cache', 'configure_cache',
    'RenderHooks', 'RenderHookConfig', 'FrameExtractionMixin', 'auto_extract_frames'
]