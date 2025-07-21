"""Core functionality for Manim Studio."""

from core.config import Config, SceneConfig, EffectConfig
from core.timeline.timeline import Timeline, TimelineEvent
from core.asset_manager import AssetManager
from core.scene_builder import SceneBuilder
from core.layer_manager import LayerManager
from core.cache import CacheManager, SceneCache, get_cache, configure_cache
from core.render_hooks import RenderHooks, RenderHookConfig, FrameExtractionMixin, auto_extract_frames

__all__ = [
    'Config', 'SceneConfig', 'EffectConfig',
    'Timeline', 'TimelineEvent',
    'AssetManager', 'SceneBuilder',
    'LayerManager',
    'CacheManager', 'SceneCache', 'get_cache', 'configure_cache',
    'RenderHooks', 'RenderHookConfig', 'FrameExtractionMixin', 'auto_extract_frames'
]