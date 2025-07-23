"""
Manim Studio Components

This package contains all the visual components and objects available
for creating animations in Manim Studio.
"""

from .scene_composition import AdvancedScene, LayeredScene, SceneTemplate
from .timeline_visualizer import TimelineVisualizer
from .mathematical_objects import (
    Inequality,
    FeasibleArea,
    get_infinite_square,
    crop_line_to_screen
)

# Import effects system
from .effects import *

# Import visual array components
from .visual_array import (
    VisualArray,
    VisualArrayElement,
    ArrayPointer,
    ArraySlidingWindow,
    ArrayBuilder,
    ComponentPropertyMixin,
    DisplayFormatter,
    DecimalFormatter,
    HexFormatter,
    BinaryFormatter
)

# Import CAD objects if available
try:
    from .cad_objects import (
        RoundCorners,
        ChamferCorners,
        LinearDimension,
        AngularDimension,
        PointerLabel,
        HatchPattern,
        DashedLine,
        PathMapper,
        CADArrowHead,
        create_cad_object,
        angle_between_vectors_signed
    )
    CAD_AVAILABLE = True
except ImportError:
    CAD_AVAILABLE = False

# Import physics objects if available
try:
    from .physics_objects import (
        SimplePendulum,
        Spring,
        ProjectileMotion,
        create_physics_updater,
        PHYSICS_OBJECTS
    )
    PHYSICS_AVAILABLE = True
except ImportError:
    PHYSICS_AVAILABLE = False

# Import hyperplane objects if available
try:
    from .hyperplane_objects import (
        HyperplaneVisualization2D,
        HyperplaneRegionVisualization,
        HyperplaneIntersectionVisualization,
        create_hyperplane_object
    )
    HYPERPLANE_AVAILABLE = True
except ImportError:
    HYPERPLANE_AVAILABLE = False

__all__ = [
    'AdvancedScene',
    'LayeredScene', 
    'SceneTemplate',
    'TimelineVisualizer',
    'Inequality',
    'FeasibleArea',
    'get_infinite_square',
    'crop_line_to_screen',
    'VisualArray',
    'VisualArrayElement',
    'ArrayPointer',
    'ArraySlidingWindow',
    'ArrayBuilder',
    'ComponentPropertyMixin',
    'DisplayFormatter',
    'DecimalFormatter',
    'HexFormatter',
    'BinaryFormatter'
]

# Add CAD objects to exports if available
if CAD_AVAILABLE:
    __all__.extend([
        'RoundCorners',
        'ChamferCorners',
        'LinearDimension',
        'AngularDimension',
        'PointerLabel',
        'HatchPattern',
        'DashedLine',
        'PathMapper',
        'CADArrowHead',
        'create_cad_object',
        'angle_between_vectors_signed'
    ])

# Add physics objects to exports if available
if PHYSICS_AVAILABLE:
    __all__.extend([
        'SimplePendulum',
        'Spring',
        'ProjectileMotion',
        'create_physics_updater',
        'PHYSICS_OBJECTS'
    ])

# Add hyperplane objects to exports if available
if HYPERPLANE_AVAILABLE:
    __all__.extend([
        'HyperplaneVisualization2D',
        'HyperplaneRegionVisualization',
        'HyperplaneIntersectionVisualization',
        'create_hyperplane_object'
    ])