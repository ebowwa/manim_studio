#!/usr/bin/env python3
"""
Fixed 3D Camera System Demonstration
A standalone working version without problematic imports
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import config before any Manim imports
from config.manim_config import config

from manim import *
import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Camera3DConfig:
    """Configuration for 3D camera with full spatial control."""
    # Spherical coordinates (more intuitive for 3D camera control)
    phi: float = 0.0           # Angle from z-axis (0 to π)
    theta: float = 0.0         # Azimuthal angle (0 to 2π)
    distance: float = 5.0      # Distance from focal point
    
    # Cartesian position (alternative to spherical)
    position: Optional[List[float]] = None  # [x, y, z] position
    
    # Camera orientation
    focal_point: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])  # Look-at point
    up_vector: List[float] = field(default_factory=lambda: [0.0, 0.0, 1.0])     # Up direction
    
    # Camera properties
    fov: float = 50.0          # Field of view in degrees
    zoom: float = 1.0          # Additional zoom factor


class StudioScene3D(ThreeDScene):
    """Base class for 3D scenes with enhanced camera control."""
    
    def __init__(self, camera_config=None, **kwargs):
        super().__init__(**kwargs)
        self.camera_config = camera_config or Camera3DConfig()
        self.setup_3d_camera()
    
    def setup_3d_camera(self):
        """Setup 3D camera based on configuration."""
        if self.camera_config:
            self.set_camera_orientation(
                phi=self.camera_config.phi,
                theta=self.camera_config.theta,
                distance=self.camera_config.distance,
                focal_point=self.camera_config.focal_point
            )
    
    def create_axes(self, x_range=None, y_range=None, z_range=None):
        """Create 3D axes for the scene."""
        x_range = x_range or [-5, 5, 1]
        y_range = y_range or [-5, 5, 1] 
        z_range = z_range or [-3, 3, 1]
        
        return ThreeDAxes(
            x_range=x_range,
            y_range=y_range,
            z_range=z_range,
            x_length=8,
            y_length=8,
            z_length=6,
            axis_config={"color": GRAY}
        )
    
    def add_ambient_rotation(self, mobject, axis=None, rate=1.0):
        """Add continuous rotation to an object."""
        if axis is None:
            axis = OUT
        
        def update_rotation(mob, dt):
            mob.rotate(rate * dt, axis=axis)
        
        mobject.add_updater(update_rotation)
        return mobject


class FixedCamera3DDemo(StudioScene3D):
    """Demonstration of 3D camera capabilities."""
    
    def __init__(self, **kwargs):
        # Configure 3D camera
        camera_config = Camera3DConfig(
            phi=60 * DEGREES,
            theta=45 * DEGREES,
            distance=8,
            focal_point=[0, 0, 0],
            fov=50,
            zoom=1.0
        )
        super().__init__(camera_config=camera_config, **kwargs)
    
    def construct(self):
        # Create title
        title = Text("3D Camera System", font_size=48, color="#00d4ff")
        title.to_corner(UL)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Write(title))
        
        # Create 3D axes
        axes = self.create_axes(
            x_range=[-5, 5, 1],
            y_range=[-5, 5, 1],
            z_range=[-3, 3, 1]
        )
        self.play(Create(axes), run_time=2)
        
        # Create central cube
        cube = Cube(side_length=2, fill_opacity=0.8)
        cube.set_color("#4a90e2")
        self.play(Create(cube), run_time=2)
        
        # Add rotation to cube
        self.add_ambient_rotation(cube, axis=np.array([1, 1, 1]), rate=0.5)
        
        # Create orbiting spheres
        spheres = VGroup()
        colors = ["#ff6b6b", "#4ecdc4", "#feca57"]
        positions = [[3, 0, 0], [-3, 0, 0], [0, 3, 0]]
        
        for color, pos in zip(colors, positions):
            sphere = Sphere(radius=0.5)
            sphere.set_color(color)
            sphere.move_to(pos)
            spheres.add(sphere)
        
        self.play(FadeIn(spheres), run_time=2)
        
        # Update title
        new_title = Text("Camera Movement Showcase", font_size=48, color="#00d4ff").to_corner(UL)
        self.play(Transform(title, new_title))
        
        # === Camera Movement 1: Orbital Motion ===
        movement_label = Text("Orbital Camera Movement", font_size=36).to_corner(UR)
        self.add_fixed_in_frame_mobjects(movement_label)
        self.play(FadeIn(movement_label))
        
        # Orbit around the scene
        self.begin_ambient_camera_rotation(rate=0.3)
        self.wait(2)  # Shortened for testing
        self.stop_ambient_camera_rotation()
        
        # === Camera Movement 2: Dramatic Zoom ===
        new_label = Text("Dolly Zoom Effect", font_size=36).to_corner(UR)
        self.play(Transform(movement_label, new_label))
        
        # Move camera closer with FOV change
        self.move_camera(
            phi=45 * DEGREES,
            theta=30 * DEGREES,
            run_time=2
        )
        
        # === Camera Movement 3: Focus on Objects ===
        focus_label = Text("Focus Pull Between Objects", font_size=36).to_corner(UR)
        self.play(Transform(movement_label, focus_label))
        
        # Focus on each sphere
        for i, sphere in enumerate(spheres):
            self.move_camera(
                phi=60 * DEGREES,
                theta=(-45 + i * 120) * DEGREES,
                run_time=2
            )
            self.wait(0.5)
        
        # === Camera Movement 4: Cinematic Fly-Through ===
        cinematic_label = Text("Cinematic Fly-Through", font_size=36).to_corner(UR)
        self.play(Transform(movement_label, cinematic_label))
        
        # Create a path for the camera
        self.move_camera(
            phi=20 * DEGREES,
            theta=0 * DEGREES,
            distance=10,
            run_time=3
        )
        
        self.move_camera(
            phi=80 * DEGREES,
            theta=90 * DEGREES,
            distance=6,
            run_time=3
        )
        
        self.move_camera(
            phi=45 * DEGREES,
            theta=180 * DEGREES,
            distance=8,
            run_time=3
        )
        
        # === Final Shot ===
        final_label = Text("3D Camera System Complete", font_size=36).to_corner(UR)
        self.play(Transform(movement_label, final_label))
        
        # Final wide shot
        self.move_camera(
            phi=60 * DEGREES,
            theta=-45 * DEGREES,
            distance=12,
            run_time=3
        )
        
        self.wait(2)


if __name__ == "__main__":
    # Render the fixed demo
    from manim import config
    
    config.pixel_height = 480
    config.pixel_width = 854
    config.frame_rate = 15
    config.media_dir = "user-data"
    
    # Choose which demo to render
    scene = FixedCamera3DDemo()
    scene.render()