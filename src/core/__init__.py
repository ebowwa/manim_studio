"""Core functionality for Manim Studio."""

from .config import Config, SceneConfig, EffectConfig
from .timeline.timeline import Timeline, TimelineEvent
from .asset_manager import AssetManager
from .scene_builder import SceneBuilder
from .layer_manager import LayerManager
from .cache import CacheManager, SceneCache, get_cache, configure_cache
from .render_hooks import RenderHooks, RenderHookConfig, FrameExtractionMixin, auto_extract_frames

# Vector space and coordinate system management
from .vector_space import (
    VectorSpace, CoordinateSystem, ViewportConfig, TransformContext,
    get_vector_space, set_vector_space
)
from .vector_space_extensions import (
    CoordinateFrame, SphericalCoordinates, CylindricalCoordinates,
    BarycentricCoordinates, PolarCoordinates, VectorFieldSpace,
    CoordinateSystemVisualizer
)
from .viewport_manager import (
    ViewportManager, ViewportMode, Viewport, Frustum
)
from .transform_pipeline import (
    TransformPipeline, TransformStage, TransformNode, TransformController
)

__all__ = [
    'Config', 'SceneConfig', 'EffectConfig',
    'Timeline', 'TimelineEvent',
    'AssetManager', 'SceneBuilder',
    'LayerManager',
    'CacheManager', 'SceneCache', 'get_cache', 'configure_cache',
    'RenderHooks', 'RenderHookConfig', 'FrameExtractionMixin', 'auto_extract_frames',
    # Vector space system
    'VectorSpace', 'CoordinateSystem', 'ViewportConfig', 'TransformContext',
    'get_vector_space', 'set_vector_space',
    'CoordinateFrame', 'SphericalCoordinates', 'CylindricalCoordinates',
    'BarycentricCoordinates', 'PolarCoordinates', 'VectorFieldSpace',
    'CoordinateSystemVisualizer',
    'ViewportManager', 'ViewportMode', 'Viewport', 'Frustum',
    'TransformPipeline', 'TransformStage', 'TransformNode', 'TransformController'
]