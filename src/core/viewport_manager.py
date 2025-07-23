"""
Viewport Management System for Manim Studio

This module provides advanced viewport and camera frustum management,
including multi-viewport support and render target management.
"""

from typing import List, Optional, Tuple, Dict, Any, Callable
import numpy as np
from dataclasses import dataclass
from enum import Enum
from manim import *
from .vector_space import VectorSpace, CoordinateSystem, ViewportConfig, Vector3D
from ..utils.math3d import Matrix4x4


class ViewportMode(Enum):
    """Viewport display modes."""
    SINGLE = "single"
    SPLIT_HORIZONTAL = "split_horizontal"
    SPLIT_VERTICAL = "split_vertical"
    QUAD = "quad"
    PICTURE_IN_PICTURE = "pip"


@dataclass
class Viewport:
    """Individual viewport configuration."""
    name: str
    x: int  # Left position in pixels
    y: int  # Top position in pixels
    width: int
    height: int
    camera_position: Optional[Vector3D] = None
    camera_target: Optional[Vector3D] = None
    projection_type: str = "perspective"  # "perspective" or "orthographic"
    fov: float = 60.0  # Field of view in degrees
    active: bool = True
    clear_color: Optional[str] = None
    
    @property
    def aspect_ratio(self) -> float:
        return self.width / self.height
    
    def contains_point(self, x: int, y: int) -> bool:
        """Check if screen point is within this viewport."""
        return (self.x <= x < self.x + self.width and 
                self.y <= y < self.y + self.height)
    
    def to_normalized(self, x: int, y: int) -> Tuple[float, float]:
        """Convert viewport coordinates to normalized [0,1] range."""
        nx = (x - self.x) / self.width
        ny = (y - self.y) / self.height
        return (nx, ny)


class Frustum:
    """View frustum for culling and visibility checks."""
    
    def __init__(self, projection_matrix: Matrix4x4, view_matrix: Matrix4x4):
        self.planes = self._extract_frustum_planes(projection_matrix * view_matrix)
    
    def _extract_frustum_planes(self, mvp: Matrix4x4) -> List[Tuple[Vector3D, float]]:
        """Extract frustum planes from MVP matrix."""
        m = mvp.matrix
        planes = []
        
        # Left plane
        planes.append(self._normalize_plane(
            m[3, 0] + m[0, 0],
            m[3, 1] + m[0, 1],
            m[3, 2] + m[0, 2],
            m[3, 3] + m[0, 3]
        ))
        
        # Right plane
        planes.append(self._normalize_plane(
            m[3, 0] - m[0, 0],
            m[3, 1] - m[0, 1],
            m[3, 2] - m[0, 2],
            m[3, 3] - m[0, 3]
        ))
        
        # Bottom plane
        planes.append(self._normalize_plane(
            m[3, 0] + m[1, 0],
            m[3, 1] + m[1, 1],
            m[3, 2] + m[1, 2],
            m[3, 3] + m[1, 3]
        ))
        
        # Top plane
        planes.append(self._normalize_plane(
            m[3, 0] - m[1, 0],
            m[3, 1] - m[1, 1],
            m[3, 2] - m[1, 2],
            m[3, 3] - m[1, 3]
        ))
        
        # Near plane
        planes.append(self._normalize_plane(
            m[3, 0] + m[2, 0],
            m[3, 1] + m[2, 1],
            m[3, 2] + m[2, 2],
            m[3, 3] + m[2, 3]
        ))
        
        # Far plane
        planes.append(self._normalize_plane(
            m[3, 0] - m[2, 0],
            m[3, 1] - m[2, 1],
            m[3, 2] - m[2, 2],
            m[3, 3] - m[2, 3]
        ))
        
        return planes
    
    def _normalize_plane(self, a: float, b: float, c: float, d: float) -> Tuple[Vector3D, float]:
        """Normalize plane equation ax + by + cz + d = 0."""
        normal = Vector3D(a, b, c)
        length = normal.magnitude()
        if length > 0:
            normal = normal / length
            d = d / length
        return (normal, d)
    
    def contains_point(self, point: Vector3D) -> bool:
        """Check if point is inside frustum."""
        for normal, d in self.planes:
            if normal.dot(point) + d < 0:
                return False
        return True
    
    def contains_sphere(self, center: Vector3D, radius: float) -> bool:
        """Check if sphere intersects frustum."""
        for normal, d in self.planes:
            if normal.dot(center) + d < -radius:
                return False
        return True
    
    def contains_box(self, min_point: Vector3D, max_point: Vector3D) -> bool:
        """Check if axis-aligned box intersects frustum."""
        for normal, d in self.planes:
            # Find the vertex farthest in the direction of the normal
            p = Vector3D(
                max_point.x if normal.x > 0 else min_point.x,
                max_point.y if normal.y > 0 else min_point.y,
                max_point.z if normal.z > 0 else min_point.z
            )
            
            if normal.dot(p) + d < 0:
                return False
        return True


class ViewportManager:
    """
    Manages multiple viewports and their associated cameras.
    Provides split-screen, picture-in-picture, and other multi-view capabilities.
    """
    
    def __init__(self, vector_space: VectorSpace, 
                 screen_width: int = 1920, 
                 screen_height: int = 1080):
        self.vector_space = vector_space
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.viewports: Dict[str, Viewport] = {}
        self.active_viewport: Optional[str] = None
        self.mode = ViewportMode.SINGLE
        
        # Create default viewport
        self.create_viewport("main", 0, 0, screen_width, screen_height)
        self.set_active_viewport("main")
    
    def create_viewport(self, name: str, x: int, y: int, 
                       width: int, height: int, **kwargs) -> Viewport:
        """Create a new viewport."""
        viewport = Viewport(name, x, y, width, height, **kwargs)
        self.viewports[name] = viewport
        return viewport
    
    def set_active_viewport(self, name: str):
        """Set the active viewport for rendering."""
        if name in self.viewports:
            self.active_viewport = name
    
    def get_active_viewport(self) -> Optional[Viewport]:
        """Get the currently active viewport."""
        if self.active_viewport:
            return self.viewports.get(self.active_viewport)
        return None
    
    def set_mode(self, mode: ViewportMode):
        """Set viewport layout mode."""
        self.mode = mode
        self._update_viewport_layout()
    
    def _update_viewport_layout(self):
        """Update viewport positions based on current mode."""
        w, h = self.screen_width, self.screen_height
        
        if self.mode == ViewportMode.SINGLE:
            if "main" in self.viewports:
                self.viewports["main"].x = 0
                self.viewports["main"].y = 0
                self.viewports["main"].width = w
                self.viewports["main"].height = h
        
        elif self.mode == ViewportMode.SPLIT_HORIZONTAL:
            # Two viewports side by side
            half_w = w // 2
            if "left" not in self.viewports:
                self.create_viewport("left", 0, 0, half_w, h)
            else:
                vp = self.viewports["left"]
                vp.x, vp.y, vp.width, vp.height = 0, 0, half_w, h
            
            if "right" not in self.viewports:
                self.create_viewport("right", half_w, 0, half_w, h)
            else:
                vp = self.viewports["right"]
                vp.x, vp.y, vp.width, vp.height = half_w, 0, half_w, h
        
        elif self.mode == ViewportMode.SPLIT_VERTICAL:
            # Two viewports top and bottom
            half_h = h // 2
            if "top" not in self.viewports:
                self.create_viewport("top", 0, 0, w, half_h)
            else:
                vp = self.viewports["top"]
                vp.x, vp.y, vp.width, vp.height = 0, 0, w, half_h
            
            if "bottom" not in self.viewports:
                self.create_viewport("bottom", 0, half_h, w, half_h)
            else:
                vp = self.viewports["bottom"]
                vp.x, vp.y, vp.width, vp.height = 0, half_h, w, half_h
        
        elif self.mode == ViewportMode.QUAD:
            # Four viewports
            half_w, half_h = w // 2, h // 2
            positions = [
                ("top_left", 0, 0),
                ("top_right", half_w, 0),
                ("bottom_left", 0, half_h),
                ("bottom_right", half_w, half_h)
            ]
            
            for name, x, y in positions:
                if name not in self.viewports:
                    self.create_viewport(name, x, y, half_w, half_h)
                else:
                    vp = self.viewports[name]
                    vp.x, vp.y, vp.width, vp.height = x, y, half_w, half_h
        
        elif self.mode == ViewportMode.PICTURE_IN_PICTURE:
            # Main viewport with small PIP
            if "main" in self.viewports:
                self.viewports["main"].x = 0
                self.viewports["main"].y = 0
                self.viewports["main"].width = w
                self.viewports["main"].height = h
            
            # PIP in bottom right corner
            pip_w, pip_h = w // 4, h // 4
            pip_x, pip_y = w - pip_w - 20, h - pip_h - 20
            
            if "pip" not in self.viewports:
                self.create_viewport("pip", pip_x, pip_y, pip_w, pip_h)
            else:
                vp = self.viewports["pip"]
                vp.x, vp.y, vp.width, vp.height = pip_x, pip_y, pip_w, pip_h
    
    def get_viewport_at_position(self, x: int, y: int) -> Optional[Viewport]:
        """Get viewport containing the given screen position."""
        for viewport in self.viewports.values():
            if viewport.active and viewport.contains_point(x, y):
                return viewport
        return None
    
    def setup_viewport_camera(self, viewport_name: str, 
                            position: Vector3D,
                            target: Vector3D,
                            up: Vector3D = None):
        """Setup camera for a specific viewport."""
        if viewport_name not in self.viewports:
            return
        
        viewport = self.viewports[viewport_name]
        viewport.camera_position = position
        viewport.camera_target = target
        
        # Update vector space for this viewport
        self.vector_space.set_camera(position, target, up or Vector3D(0, 1, 0))
        
        # Set appropriate projection
        if viewport.projection_type == "perspective":
            self.vector_space.set_perspective_projection(
                np.radians(viewport.fov),
                0.1, 100.0
            )
        else:
            # Calculate orthographic bounds based on viewport
            height = 10.0  # Default ortho height
            width = height * viewport.aspect_ratio
            self.vector_space.set_orthographic_projection(width, height)
    
    def create_viewport_borders(self) -> VGroup:
        """Create visual borders for viewports."""
        borders = VGroup()
        
        for name, viewport in self.viewports.items():
            if not viewport.active or name == "main":
                continue
            
            # Convert viewport bounds to scene coordinates
            corners = [
                (viewport.x, viewport.y),
                (viewport.x + viewport.width, viewport.y),
                (viewport.x + viewport.width, viewport.y + viewport.height),
                (viewport.x, viewport.y + viewport.height)
            ]
            
            # Convert to scene space
            scene_corners = []
            for x, y in corners:
                scene_point = self.vector_space.pixel_to_scene(x, y)
                scene_corners.append(scene_point.array)
            
            # Create border
            border = Polygon(*scene_corners, 
                           stroke_color=WHITE, 
                           stroke_width=2,
                           fill_opacity=0)
            borders.add(border)
            
            # Add label
            label = Text(name, font_size=16).move_to(scene_corners[0])
            borders.add(label)
        
        return borders
    
    def get_frustum(self, viewport_name: str = None) -> Optional[Frustum]:
        """Get view frustum for a viewport."""
        viewport_name = viewport_name or self.active_viewport
        if not viewport_name or viewport_name not in self.viewports:
            return None
        
        viewport = self.viewports[viewport_name]
        if not viewport.camera_position:
            return None
        
        # Setup camera for viewport
        self.setup_viewport_camera(viewport_name, 
                                 viewport.camera_position,
                                 viewport.camera_target or Vector3D(0, 0, 0))
        
        # Get matrices from vector space
        view_matrix = self.vector_space.transform_context.view_matrix
        proj_matrix = self.vector_space.transform_context.projection_matrix
        
        return Frustum(proj_matrix, view_matrix)
    
    def perform_frustum_culling(self, objects: List[Mobject], 
                              viewport_name: str = None) -> List[Mobject]:
        """Filter objects based on frustum visibility."""
        frustum = self.get_frustum(viewport_name)
        if not frustum:
            return objects
        
        visible_objects = []
        for obj in objects:
            # Get bounding box
            if hasattr(obj, 'get_bounding_box'):
                bbox = obj.get_bounding_box()
                min_point = Vector3D(*bbox[0])
                max_point = Vector3D(*bbox[1])
                
                if frustum.contains_box(min_point, max_point):
                    visible_objects.append(obj)
            else:
                # Simple point check for objects without bounding box
                center = Vector3D(*obj.get_center())
                if frustum.contains_point(center):
                    visible_objects.append(obj)
        
        return visible_objects