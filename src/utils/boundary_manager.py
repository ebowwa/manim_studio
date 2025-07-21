"""
Boundary management utilities for keeping animations within frame.
"""

from typing import Tuple, Optional, Union, List
import numpy as np
from manim import *


class BoundaryManager:
    """Manages boundaries to keep animations within the video frame."""
    
    def __init__(self, scene: Scene, margin: float = 0.5):
        """
        Initialize boundary manager.
        
        Args:
            scene: The Manim scene
            margin: Safety margin from edges in scene units
        """
        self.scene = scene
        self.margin = margin
        
        # Get frame dimensions from config
        self.frame_width = config.frame_width
        self.frame_height = config.frame_height
        
        # Calculate boundaries
        self.x_min = -self.frame_width / 2 + margin
        self.x_max = self.frame_width / 2 - margin
        self.y_min = -self.frame_height / 2 + margin
        self.y_max = self.frame_height / 2 - margin
        
        # Z boundaries (for 3D scenes)
        self.z_min = -2
        self.z_max = 2
    
    def get_safe_area(self) -> Tuple[float, float, float, float]:
        """Get the safe area boundaries."""
        return self.x_min, self.x_max, self.y_min, self.y_max
    
    def is_within_bounds(self, point: np.ndarray) -> bool:
        """Check if a point is within boundaries."""
        x, y = point[0], point[1]
        return (self.x_min <= x <= self.x_max and 
                self.y_min <= y <= self.y_max)
    
    def clamp_position(self, point: np.ndarray) -> np.ndarray:
        """Clamp a position to stay within boundaries."""
        x = np.clip(point[0], self.x_min, self.x_max)
        y = np.clip(point[1], self.y_min, self.y_max)
        z = point[2] if len(point) > 2 else 0
        return np.array([x, y, z])
    
    def clamp_mobject(self, mobject: Mobject) -> np.ndarray:
        """Clamp a mobject's position considering its size."""
        center = mobject.get_center()
        width = mobject.get_width()
        height = mobject.get_height()
        
        # Adjust boundaries for mobject size
        x_min = self.x_min + width / 2
        x_max = self.x_max - width / 2
        y_min = self.y_min + height / 2
        y_max = self.y_max - height / 2
        
        # Clamp position
        x = np.clip(center[0], x_min, x_max)
        y = np.clip(center[1], y_min, y_max)
        z = center[2]
        
        return np.array([x, y, z])
    
    def get_random_position(self, mobject: Optional[Mobject] = None) -> np.ndarray:
        """Get a random position within boundaries."""
        if mobject:
            # Account for mobject size
            width = mobject.get_width()
            height = mobject.get_height()
            x = np.random.uniform(self.x_min + width/2, self.x_max - width/2)
            y = np.random.uniform(self.y_min + height/2, self.y_max - height/2)
        else:
            x = np.random.uniform(self.x_min, self.x_max)
            y = np.random.uniform(self.y_min, self.y_max)
        
        return np.array([x, y, 0])
    
    def create_boundary_box(self, **kwargs) -> Rectangle:
        """Create a visual boundary box."""
        default_style = {
            'stroke_color': GREY,
            'stroke_width': 1,
            'stroke_opacity': 0.3,
            'fill_opacity': 0
        }
        default_style.update(kwargs)
        
        width = self.x_max - self.x_min
        height = self.y_max - self.y_min
        
        box = Rectangle(width=width, height=height, **default_style)
        box.move_to(ORIGIN)
        return box
    
    def create_safe_zone_indicators(self) -> VGroup:
        """Create visual indicators for safe zones."""
        indicators = VGroup()
        
        # Corner markers
        for x, y in [(self.x_min, self.y_min), (self.x_max, self.y_min),
                     (self.x_max, self.y_max), (self.x_min, self.y_max)]:
            corner = VGroup(
                Line(ORIGIN, RIGHT * 0.3, stroke_width=2),
                Line(ORIGIN, UP * 0.3, stroke_width=2)
            )
            corner.set_color(GREY)
            corner.move_to([x, y, 0])
            indicators.add(corner)
        
        # Center crosshair
        crosshair = VGroup(
            Line(LEFT * 0.2, RIGHT * 0.2, stroke_width=1),
            Line(DOWN * 0.2, UP * 0.2, stroke_width=1)
        )
        crosshair.set_color(GREY)
        crosshair.set_opacity(0.5)
        indicators.add(crosshair)
        
        return indicators
    
    def bounce_vector(self, position: np.ndarray, velocity: np.ndarray,
                     mobject: Optional[Mobject] = None) -> np.ndarray:
        """
        Calculate bounced velocity vector when hitting boundaries.
        
        Args:
            position: Current position
            velocity: Current velocity vector
            mobject: Optional mobject to consider its size
            
        Returns:
            New velocity vector after bounce
        """
        new_velocity = velocity.copy()
        
        if mobject:
            width = mobject.get_width()
            height = mobject.get_height()
            x_min = self.x_min + width / 2
            x_max = self.x_max - width / 2
            y_min = self.y_min + height / 2
            y_max = self.y_max - height / 2
        else:
            x_min, x_max = self.x_min, self.x_max
            y_min, y_max = self.y_min, self.y_max
        
        # Check X boundaries
        if position[0] <= x_min or position[0] >= x_max:
            new_velocity[0] = -velocity[0]
        
        # Check Y boundaries
        if position[1] <= y_min or position[1] >= y_max:
            new_velocity[1] = -velocity[1]
        
        return new_velocity
    
    def create_bounded_path(self, start: np.ndarray, end: np.ndarray,
                           mobject: Optional[Mobject] = None) -> List[np.ndarray]:
        """
        Create a path that stays within boundaries.
        
        Args:
            start: Start position
            end: End position
            mobject: Optional mobject to consider its size
            
        Returns:
            List of points forming the bounded path
        """
        # Clamp start and end points
        if mobject:
            start = self.clamp_mobject(mobject)
            mobject_temp = mobject.copy()
            mobject_temp.move_to(end)
            end = self.clamp_mobject(mobject_temp)
        else:
            start = self.clamp_position(start)
            end = self.clamp_position(end)
        
        return [start, end]
    
    def scale_to_fit(self, mobject: Mobject, max_scale: float = 1.0) -> float:
        """
        Calculate maximum scale factor to fit mobject within boundaries.
        
        Args:
            mobject: The mobject to scale
            max_scale: Maximum allowed scale factor
            
        Returns:
            Scale factor that fits within boundaries
        """
        width = mobject.get_width()
        height = mobject.get_height()
        
        # Available space
        available_width = (self.x_max - self.x_min) * 0.9  # 90% of space
        available_height = (self.y_max - self.y_min) * 0.9
        
        # Calculate scale factors
        scale_x = available_width / width if width > 0 else max_scale
        scale_y = available_height / height if height > 0 else max_scale
        
        # Return minimum scale that fits both dimensions
        return min(scale_x, scale_y, max_scale)


class BoundedAnimation:
    """Helper class for creating boundary-aware animations."""
    
    def __init__(self, boundary_manager: BoundaryManager):
        self.boundary = boundary_manager
    
    def bounded_move_to(self, mobject: Mobject, target: np.ndarray, **kwargs):
        """Create animation that moves mobject to target within bounds."""
        clamped_target = self.boundary.clamp_mobject(mobject)
        return mobject.animate(**kwargs).move_to(clamped_target)
    
    def bounded_shift(self, mobject: Mobject, direction: np.ndarray, **kwargs):
        """Create animation that shifts mobject within bounds."""
        current = mobject.get_center()
        target = current + direction
        
        # Temporarily move to check bounds
        mobject_copy = mobject.copy()
        mobject_copy.move_to(target)
        clamped_target = self.boundary.clamp_mobject(mobject_copy)
        
        actual_shift = clamped_target - current
        return mobject.animate(**kwargs).shift(actual_shift)
    
    def bounded_scale(self, mobject: Mobject, scale_factor: float, **kwargs):
        """Create animation that scales mobject within bounds."""
        max_scale = self.boundary.scale_to_fit(mobject, scale_factor)
        return mobject.animate(**kwargs).scale(max_scale)


def create_boundary_aware_updater(mobject: Mobject, velocity: np.ndarray,
                                boundary_manager: BoundaryManager):
    """
    Create an updater that keeps mobject within boundaries.
    
    Args:
        mobject: The mobject to update
        velocity: Initial velocity vector
        boundary_manager: The boundary manager
        
    Returns:
        Updater function
    """
    current_velocity = velocity.copy()
    
    def updater(mob, dt):
        nonlocal current_velocity
        
        # Get current position
        pos = mob.get_center()
        
        # Calculate new position
        new_pos = pos + current_velocity * dt
        
        # Check for boundary collision
        mob.move_to(new_pos)
        clamped_pos = boundary_manager.clamp_mobject(mob)
        
        # If position was clamped, we hit a boundary
        if not np.allclose(new_pos, clamped_pos):
            current_velocity = boundary_manager.bounce_vector(
                clamped_pos, current_velocity, mob
            )
            mob.move_to(clamped_pos)
    
    return updater