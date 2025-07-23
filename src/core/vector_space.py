"""
Centralized Vector Space Management System

This module provides a unified interface for handling coordinate systems,
transformations, and viewport management across Manim Studio.
"""

from typing import Tuple, List, Optional, Union, Dict, Any, Callable
import numpy as np
from dataclasses import dataclass, field
from enum import Enum
from manim import *
from ..utils.math3d import Vector3D, Matrix4x4


class CoordinateSystem(Enum):
    """Available coordinate systems."""
    WORLD = "world"          # 3D world space
    VIEW = "view"            # Camera/eye space
    CLIP = "clip"            # Normalized device coordinates
    SCREEN = "screen"        # Pixel coordinates
    SCENE = "scene"          # Manim scene units
    NORMALIZED = "normalized" # [0,1] range


@dataclass
class ViewportConfig:
    """Viewport configuration for rendering."""
    width: int = 1920
    height: int = 1080
    scene_width: float = 14.222222  # Manim default
    scene_height: float = 8.0
    margin: float = 0.5
    
    @property
    def aspect_ratio(self) -> float:
        return self.width / self.height
    
    @property
    def scene_aspect_ratio(self) -> float:
        return self.scene_width / self.scene_height
    
    @property
    def pixels_per_unit(self) -> float:
        return self.width / self.scene_width


@dataclass
class TransformContext:
    """Context for coordinate transformations."""
    current_system: CoordinateSystem = CoordinateSystem.WORLD
    model_matrix: Matrix4x4 = field(default_factory=Matrix4x4.identity)
    view_matrix: Matrix4x4 = field(default_factory=Matrix4x4.identity)
    projection_matrix: Matrix4x4 = field(default_factory=Matrix4x4.identity)
    viewport_matrix: Matrix4x4 = field(default_factory=Matrix4x4.identity)


class VectorSpace:
    """
    Centralized vector space manager for consistent coordinate handling.
    
    This class provides:
    - Unified coordinate system transformations
    - Viewport and frustum management
    - Scene boundary handling
    - Projection utilities
    """
    
    def __init__(self, viewport_config: Optional[ViewportConfig] = None):
        self.viewport = viewport_config or ViewportConfig()
        self.transform_context = TransformContext()
        self._transformation_cache = {}
        
        # Initialize viewport transformation matrix
        self._update_viewport_matrix()
    
    def _update_viewport_matrix(self):
        """Update the viewport transformation matrix."""
        # Transform from NDC [-1,1] to screen coordinates
        w, h = self.viewport.width, self.viewport.height
        matrix = np.array([
            [w/2, 0, 0, w/2],
            [0, -h/2, 0, h/2],  # Y-flip for screen coordinates
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
        self.transform_context.viewport_matrix = Matrix4x4(matrix)
    
    # Core transformation methods
    
    def transform_point(self, point, 
                       from_system: CoordinateSystem,
                       to_system: CoordinateSystem):
        """
        Transform a point between coordinate systems.
        
        Args:
            point: Point to transform
            from_system: Source coordinate system
            to_system: Target coordinate system
            
        Returns:
            Transformed point as Vector3D
        """
        # Convert to Vector3D if needed
        if not isinstance(point, Vector3D):
            if isinstance(point, (list, tuple)):
                point = Vector3D(*point)
            else:
                point = Vector3D(point[0], point[1], point[2] if len(point) > 2 else 0)
        
        # Short circuit if same system
        if from_system == to_system:
            return point
        
        # Get transformation matrix
        transform = self._get_transformation_matrix(from_system, to_system)
        return transform.transform_point(point)
    
    def transform_vector(self, vector, 
                        from_system: CoordinateSystem,
                        to_system: CoordinateSystem):
        """
        Transform a vector (direction) between coordinate systems.
        Ignores translation components.
        """
        if not isinstance(vector, Vector3D):
            vector = Vector3D(*vector) if isinstance(vector, (list, tuple)) else Vector3D(vector[0], vector[1], vector[2])
        
        if from_system == to_system:
            return vector
        
        transform = self._get_transformation_matrix(from_system, to_system)
        return transform.transform_direction(vector)
    
    def _get_transformation_matrix(self, from_system: CoordinateSystem, 
                                  to_system: CoordinateSystem) -> Matrix4x4:
        """Get or compute transformation matrix between systems."""
        cache_key = (from_system, to_system)
        
        if cache_key in self._transformation_cache:
            return self._transformation_cache[cache_key]
        
        # Build transformation chain
        matrix = Matrix4x4.identity()
        
        # Forward transformations
        if from_system == CoordinateSystem.WORLD and to_system == CoordinateSystem.VIEW:
            matrix = self.transform_context.view_matrix
        elif from_system == CoordinateSystem.VIEW and to_system == CoordinateSystem.CLIP:
            matrix = self.transform_context.projection_matrix
        elif from_system == CoordinateSystem.CLIP and to_system == CoordinateSystem.SCREEN:
            matrix = self.transform_context.viewport_matrix
        elif from_system == CoordinateSystem.SCENE and to_system == CoordinateSystem.SCREEN:
            matrix = self._scene_to_screen_matrix()
        
        # Inverse transformations
        elif from_system == CoordinateSystem.VIEW and to_system == CoordinateSystem.WORLD:
            matrix = self.transform_context.view_matrix.inverse()
        elif from_system == CoordinateSystem.CLIP and to_system == CoordinateSystem.VIEW:
            matrix = self.transform_context.projection_matrix.inverse()
        elif from_system == CoordinateSystem.SCREEN and to_system == CoordinateSystem.CLIP:
            matrix = self.transform_context.viewport_matrix.inverse()
        elif from_system == CoordinateSystem.SCREEN and to_system == CoordinateSystem.SCENE:
            matrix = self._scene_to_screen_matrix().inverse()
        
        # Composite transformations
        elif from_system == CoordinateSystem.WORLD and to_system == CoordinateSystem.SCREEN:
            matrix = (self.transform_context.viewport_matrix * 
                     self.transform_context.projection_matrix * 
                     self.transform_context.view_matrix)
        
        self._transformation_cache[cache_key] = matrix
        return matrix
    
    def _scene_to_screen_matrix(self) -> Matrix4x4:
        """Create transformation from Manim scene units to screen pixels."""
        # Scene coordinates: origin at center, y-up
        # Screen coordinates: origin at top-left, y-down
        sx = self.viewport.pixels_per_unit
        sy = -self.viewport.pixels_per_unit  # Flip Y
        tx = self.viewport.width / 2
        ty = self.viewport.height / 2
        
        matrix = np.array([
            [sx, 0, 0, tx],
            [0, sy, 0, ty],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
        return Matrix4x4(matrix)
    
    # Viewport and boundary methods
    
    def get_scene_bounds(self) -> Tuple[float, float, float, float]:
        """Get scene boundaries in scene units (left, right, bottom, top)."""
        w, h = self.viewport.scene_width / 2, self.viewport.scene_height / 2
        return (-w, w, -h, h)
    
    def get_safe_bounds(self, margin: Optional[float] = None) -> Tuple[float, float, float, float]:
        """Get safe area boundaries with margin."""
        margin = margin or self.viewport.margin
        left, right, bottom, top = self.get_scene_bounds()
        return (left + margin, right - margin, bottom + margin, top - margin)
    
    def is_in_view(self, point: Vector3D, system: CoordinateSystem = CoordinateSystem.SCENE) -> bool:
        """Check if a point is within the viewport."""
        # Transform to screen space if needed
        if system != CoordinateSystem.SCREEN:
            point = self.transform_point(point, system, CoordinateSystem.SCREEN)
        
        return (0 <= point.x <= self.viewport.width and 
                0 <= point.y <= self.viewport.height)
    
    def is_in_frustum(self, point: Vector3D, near: float = 0.1, far: float = 100.0) -> bool:
        """Check if a point is within the view frustum (3D)."""
        # Transform to clip space
        clip_point = self.transform_point(point, CoordinateSystem.WORLD, CoordinateSystem.CLIP)
        
        # Check clip space bounds
        return (-1 <= clip_point.x <= 1 and 
                -1 <= clip_point.y <= 1 and 
                near <= -clip_point.z <= far)
    
    def clamp_to_viewport(self, point: Vector3D, system: CoordinateSystem = CoordinateSystem.SCENE,
                         margin: float = 0) -> Vector3D:
        """Clamp a point to stay within viewport bounds."""
        if system == CoordinateSystem.SCENE:
            left, right, bottom, top = self.get_safe_bounds(margin)
            return Vector3D(
                np.clip(point.x, left, right),
                np.clip(point.y, bottom, top),
                point.z
            )
        elif system == CoordinateSystem.SCREEN:
            return Vector3D(
                np.clip(point.x, margin, self.viewport.width - margin),
                np.clip(point.y, margin, self.viewport.height - margin),
                point.z
            )
        else:
            # Transform to scene, clamp, transform back
            scene_point = self.transform_point(point, system, CoordinateSystem.SCENE)
            clamped = self.clamp_to_viewport(scene_point, CoordinateSystem.SCENE, margin)
            return self.transform_point(clamped, CoordinateSystem.SCENE, system)
    
    # Camera and projection utilities
    
    def set_camera(self, position: Vector3D, target: Vector3D, up: Vector3D = None):
        """Set camera view matrix."""
        up = up or Vector3D(0, 1, 0)
        self.transform_context.view_matrix = Matrix4x4.look_at(position, target, up)
        self._transformation_cache.clear()
    
    def set_perspective_projection(self, fov: float, near: float = 0.1, far: float = 100.0):
        """Set perspective projection matrix."""
        self.transform_context.projection_matrix = Matrix4x4.perspective(
            fov, self.viewport.aspect_ratio, near, far
        )
        self._transformation_cache.clear()
    
    def set_orthographic_projection(self, width: Optional[float] = None, 
                                   height: Optional[float] = None,
                                   near: float = -10.0, far: float = 10.0):
        """Set orthographic projection matrix."""
        width = width or self.viewport.scene_width
        height = height or self.viewport.scene_height
        
        self.transform_context.projection_matrix = Matrix4x4.orthographic_centered(
            width, height, near, far
        )
        self._transformation_cache.clear()
    
    # Utility methods
    
    def scene_to_pixel(self, scene_point):
        """Convert scene coordinates to pixel coordinates."""
        screen_point = self.transform_point(scene_point, CoordinateSystem.SCENE, 
                                          CoordinateSystem.SCREEN)
        return (int(screen_point.x), int(screen_point.y))
    
    def pixel_to_scene(self, x: int, y: int) -> Vector3D:
        """Convert pixel coordinates to scene coordinates."""
        screen_point = Vector3D(x, y, 0)
        return self.transform_point(screen_point, CoordinateSystem.SCREEN, 
                                  CoordinateSystem.SCENE)
    
    def get_visible_region(self, z_depth: float = 0) -> Dict[str, float]:
        """Get visible region bounds at a given depth in world space."""
        # For perspective projection, visible area changes with depth
        if self.transform_context.projection_matrix.matrix[3, 2] != 0:  # Perspective
            # Unproject screen corners at given depth
            corners = [
                self.pixel_to_scene(0, 0),
                self.pixel_to_scene(self.viewport.width, 0),
                self.pixel_to_scene(0, self.viewport.height),
                self.pixel_to_scene(self.viewport.width, self.viewport.height)
            ]
            
            xs = [c.x for c in corners]
            ys = [c.y for c in corners]
            
            return {
                'left': min(xs),
                'right': max(xs),
                'bottom': min(ys),
                'top': max(ys),
                'width': max(xs) - min(xs),
                'height': max(ys) - min(ys)
            }
        else:  # Orthographic
            left, right, bottom, top = self.get_scene_bounds()
            return {
                'left': left,
                'right': right,
                'bottom': bottom,
                'top': top,
                'width': right - left,
                'height': top - bottom
            }
    
    def create_debug_grid(self, spacing: float = 1.0, extent: int = 10) -> VGroup:
        """Create a debug grid for visualizing coordinate space."""
        grid = VGroup()
        
        # Grid lines
        for i in range(-extent, extent + 1):
            # Vertical lines
            grid.add(Line(
                [i * spacing, -extent * spacing, 0],
                [i * spacing, extent * spacing, 0],
                stroke_width=1 if i != 0 else 2,
                stroke_color=GREY if i != 0 else WHITE
            ))
            # Horizontal lines
            grid.add(Line(
                [-extent * spacing, i * spacing, 0],
                [extent * spacing, i * spacing, 0],
                stroke_width=1 if i != 0 else 2,
                stroke_color=GREY if i != 0 else WHITE
            ))
        
        # Origin marker
        origin = Dot(ORIGIN, color=RED, radius=0.1)
        grid.add(origin)
        
        # Axis labels
        x_label = Text("X", font_size=24).next_to([extent * spacing, 0, 0], RIGHT)
        y_label = Text("Y", font_size=24).next_to([0, extent * spacing, 0], UP)
        grid.add(x_label, y_label)
        
        return grid


# Global vector space instance for easy access
_global_vector_space = None

def get_vector_space() -> VectorSpace:
    """Get or create global vector space instance."""
    global _global_vector_space
    if _global_vector_space is None:
        _global_vector_space = VectorSpace()
    return _global_vector_space

def set_vector_space(vector_space: VectorSpace):
    """Set global vector space instance."""
    global _global_vector_space
    _global_vector_space = vector_space