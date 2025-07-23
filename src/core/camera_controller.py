"""Advanced camera controller for 3D animations with cinematic movements."""

from typing import List, Tuple, Optional, Dict, Any, Callable
import numpy as np
from manim import *
from src.core.config import Camera3DConfig, Camera2DConfig
from src.utils.math3d import Vector3D, Matrix4x4
from src.core.timeline.easing import EasingLibrary


class CameraMovementPreset:
    """Predefined camera movement patterns for professional cinematography."""
    
    @staticmethod
    def orbit(center: List[float], radius: float, duration: float, 
              revolutions: float = 1.0, axis: str = "z") -> Callable:
        """Create an orbital camera movement around a point."""
        def movement(t: float, camera: Camera3DConfig) -> None:
            angle = 2 * np.pi * revolutions * t
            if axis == "z":
                camera.theta = angle
                camera.phi = np.pi / 3  # 60 degrees from vertical
            elif axis == "y":
                camera.theta = angle
                camera.phi = np.pi / 2  # Horizontal orbit
            elif axis == "x":
                camera.phi = np.pi / 2 + angle * 0.5
                camera.theta = 0
            
            camera.distance = radius
            camera.focal_point = center
            camera.position = camera.spherical_to_cartesian()
        
        return movement
    
    @staticmethod
    def dolly_zoom(start_distance: float, end_distance: float, 
                   start_fov: float, end_fov: float, duration: float) -> Callable:
        """Create a dolly zoom (vertigo) effect."""
        def movement(t: float, camera: Camera3DConfig) -> None:
            # Interpolate distance and FOV inversely
            camera.distance = start_distance + (end_distance - start_distance) * t
            camera.fov = start_fov + (end_fov - start_fov) * t
            camera.position = camera.spherical_to_cartesian()
        
        return movement
    
    @staticmethod
    def fly_through(waypoints: List[List[float]], look_at_points: Optional[List[List[float]]] = None,
                   duration: float = 5.0, easing: str = "ease_in_out") -> Callable:
        """Create a smooth fly-through path through multiple waypoints."""
        easing_func = getattr(EasingLibrary, easing, EasingLibrary.ease_in_out)
        
        def movement(t: float, camera: Camera3DConfig) -> None:
            # Apply easing to time
            eased_t = easing_func(t)
            
            # Find current segment
            num_segments = len(waypoints) - 1
            segment_duration = 1.0 / num_segments
            segment_index = min(int(eased_t / segment_duration), num_segments - 1)
            local_t = (eased_t - segment_index * segment_duration) / segment_duration
            
            # Interpolate position
            p1 = np.array(waypoints[segment_index])
            p2 = np.array(waypoints[segment_index + 1])
            camera.position = (p1 + (p2 - p1) * local_t).tolist()
            
            # Interpolate look-at if provided
            if look_at_points and len(look_at_points) > segment_index + 1:
                l1 = np.array(look_at_points[segment_index])
                l2 = np.array(look_at_points[segment_index + 1])
                camera.focal_point = (l1 + (l2 - l1) * local_t).tolist()
            
            # Update spherical coordinates
            camera.phi, camera.theta, camera.distance = camera.cartesian_to_spherical()
        
        return movement
    
    @staticmethod
    def crane_shot(start_height: float, end_height: float, 
                   start_distance: float, end_distance: float,
                   duration: float = 3.0) -> Callable:
        """Create a crane camera movement (vertical + distance change)."""
        def movement(t: float, camera: Camera3DConfig) -> None:
            # Smooth interpolation using ease_in_out
            eased_t = EasingLibrary.ease_in_out(t)
            
            # Interpolate height and distance
            height = start_height + (end_height - start_height) * eased_t
            distance = start_distance + (end_distance - start_distance) * eased_t
            
            # Update camera position
            camera.position[2] = height
            camera.distance = distance
            camera.position = camera.spherical_to_cartesian()
        
        return movement
    
    @staticmethod
    def handheld_shake(intensity: float = 0.1, frequency: float = 10.0) -> Callable:
        """Add handheld camera shake for documentary feel."""
        def movement(t: float, camera: Camera3DConfig) -> None:
            # Generate smooth noise for shake
            shake_x = intensity * np.sin(frequency * t * 2.1) * 0.3
            shake_y = intensity * np.cos(frequency * t * 1.7) * 0.3
            shake_z = intensity * np.sin(frequency * t * 3.2) * 0.1
            
            # Apply shake as small adjustments
            base_pos = camera.spherical_to_cartesian()
            camera.position = [
                base_pos[0] + shake_x,
                base_pos[1] + shake_y,
                base_pos[2] + shake_z
            ]
        
        return movement
    
    @staticmethod
    def focus_pull(subjects: List[List[float]], duration: float = 2.0) -> Callable:
        """Create a focus pull effect between multiple subjects."""
        def movement(t: float, camera: Camera3DConfig) -> None:
            # Find current subject
            num_subjects = len(subjects)
            subject_duration = 1.0 / (num_subjects - 1)
            subject_index = min(int(t / subject_duration), num_subjects - 2)
            local_t = (t - subject_index * subject_duration) / subject_duration
            
            # Smooth transition using ease_in_out
            eased_t = EasingLibrary.ease_in_out(local_t)
            
            # Interpolate focal point
            s1 = np.array(subjects[subject_index])
            s2 = np.array(subjects[subject_index + 1])
            camera.focal_point = (s1 + (s2 - s1) * eased_t).tolist()
            
            # Update position to maintain distance
            camera.position = camera.spherical_to_cartesian()
        
        return movement


class Camera3DController:
    """Controller for managing 3D camera movements and animations."""
    
    def __init__(self, scene, camera_config: Optional[Camera3DConfig] = None):
        """Initialize camera controller with scene and optional config."""
        self.scene = scene
        self.config = camera_config or Camera3DConfig()
        self.movement_queue = []
        self.current_movement = None
        self.movement_time = 0.0
        
        # Check if scene supports 3D camera
        self.is_3d_scene = hasattr(scene, 'camera') and hasattr(scene.camera, 'set_phi_theta')
        
        if self.is_3d_scene:
            self._apply_config_to_camera()
    
    def _apply_config_to_camera(self):
        """Apply camera configuration to the Manim camera."""
        if not self.is_3d_scene:
            return
        
        # Set camera position using spherical coordinates
        self.scene.camera.set_phi_theta(
            phi=self.config.phi,
            theta=self.config.theta
        )
        
        # Set focal point (if supported)
        if hasattr(self.scene.camera, 'set_focal_point'):
            self.scene.camera.set_focal_point(self.config.focal_point)
        
        # Set field of view
        if hasattr(self.scene.camera, 'set_field_of_view'):
            self.scene.camera.set_field_of_view(self.config.fov)
        
        # Set zoom
        if hasattr(self.scene.camera, 'set_zoom'):
            self.scene.camera.set_zoom(self.config.zoom)
    
    def add_movement(self, movement_func: Callable, duration: float, 
                    name: str = "", delay: float = 0.0):
        """Add a camera movement to the queue."""
        self.movement_queue.append({
            'function': movement_func,
            'duration': duration,
            'name': name,
            'delay': delay,
            'start_time': None
        })
    
    def orbit_around(self, center: List[float], radius: float, 
                    duration: float, **kwargs):
        """Add an orbital movement around a point."""
        movement = CameraMovementPreset.orbit(center, radius, duration, **kwargs)
        self.add_movement(movement, duration, name="Orbit")
    
    def dolly_zoom(self, start_distance: float, end_distance: float,
                  start_fov: float, end_fov: float, duration: float):
        """Add a dolly zoom effect."""
        movement = CameraMovementPreset.dolly_zoom(
            start_distance, end_distance, start_fov, end_fov, duration
        )
        self.add_movement(movement, duration, name="Dolly Zoom")
    
    def fly_through(self, waypoints: List[List[float]], duration: float, **kwargs):
        """Add a fly-through movement."""
        movement = CameraMovementPreset.fly_through(waypoints, duration=duration, **kwargs)
        self.add_movement(movement, duration, name="Fly Through")
    
    def look_at(self, target: List[float], duration: float = 1.0, 
                easing: str = "ease_in_out"):
        """Smoothly transition to look at a target."""
        start_focal = self.config.focal_point.copy()
        easing_func = getattr(EasingLibrary, easing, EasingLibrary.ease_in_out)
        
        def movement(t: float, camera: Camera3DConfig) -> None:
            eased_t = easing_func(t)
            # Interpolate focal point
            camera.focal_point = [
                start_focal[i] + (target[i] - start_focal[i]) * eased_t
                for i in range(3)
            ]
            camera.phi, camera.theta, camera.distance = camera.cartesian_to_spherical()
        
        self.add_movement(movement, duration, name="Look At")
    
    def move_to(self, position: List[float], duration: float = 2.0,
                easing: str = "ease_in_out", maintain_focus: bool = True):
        """Move camera to a specific position."""
        start_pos = self.config.position.copy()
        start_focal = self.config.focal_point.copy()
        easing_func = getattr(EasingLibrary, easing, EasingLibrary.ease_in_out)
        
        def movement(t: float, camera: Camera3DConfig) -> None:
            eased_t = easing_func(t)
            # Interpolate position
            camera.position = [
                start_pos[i] + (position[i] - start_pos[i]) * eased_t
                for i in range(3)
            ]
            
            if not maintain_focus:
                # Also move focal point to maintain relative orientation
                focal_offset = np.array(start_focal) - np.array(start_pos)
                camera.focal_point = (np.array(camera.position) + focal_offset).tolist()
            
            camera.phi, camera.theta, camera.distance = camera.cartesian_to_spherical()
        
        self.add_movement(movement, duration, name="Move To")
    
    def shake(self, intensity: float = 0.1, duration: float = 1.0):
        """Add camera shake effect."""
        movement = CameraMovementPreset.handheld_shake(intensity)
        self.add_movement(movement, duration, name="Shake")
    
    def update(self, dt: float):
        """Update camera movements (call in scene's update loop)."""
        if not self.movement_queue and not self.current_movement:
            return
        
        # Start next movement if none active
        if not self.current_movement and self.movement_queue:
            self.current_movement = self.movement_queue.pop(0)
            self.current_movement['start_time'] = self.scene.renderer.time
            self.movement_time = 0.0
        
        # Update current movement
        if self.current_movement:
            # Handle delay
            if self.movement_time < self.current_movement['delay']:
                self.movement_time += dt
                return
            
            # Calculate normalized time
            effective_time = self.movement_time - self.current_movement['delay']
            t = min(effective_time / self.current_movement['duration'], 1.0)
            
            # Apply movement
            self.current_movement['function'](t, self.config)
            self._apply_config_to_camera()
            
            # Check if movement is complete
            if t >= 1.0:
                self.current_movement = None
                self.movement_time = 0.0
            else:
                self.movement_time += dt
    
    def create_camera_path_visualization(self, num_points: int = 50) -> VGroup:
        """Create a visual representation of the camera path."""
        if not self.movement_queue:
            return VGroup()
        
        path_points = []
        
        # Sample points along the movement path
        for movement in self.movement_queue:
            for i in range(num_points):
                t = i / (num_points - 1)
                temp_camera = self.config.copy()
                movement['function'](t, temp_camera)
                path_points.append(temp_camera.position)
        
        # Create path visualization
        if len(path_points) > 1:
            path = VMobject()
            path.set_points_as_corners([np.array(p) for p in path_points])
            path.set_stroke(YELLOW, width=2, opacity=0.5)
            
            # Add markers at key points
            markers = VGroup()
            for i in range(0, len(path_points), max(1, len(path_points) // 10)):
                marker = Dot(point=path_points[i], radius=0.05, color=YELLOW)
                markers.add(marker)
            
            return VGroup(path, markers)
        
        return VGroup()


class Camera2DController:
    """Simple controller for 2D camera movements (compatibility layer)."""
    
    def __init__(self, scene, camera_config: Optional[Camera2DConfig] = None):
        """Initialize 2D camera controller."""
        self.scene = scene
        self.config = camera_config or Camera2DConfig()
        self.original_zoom = self.config.zoom
        self.original_position = self.config.position.copy()
    
    def zoom_in(self, factor: float = 1.5, duration: float = 1.0):
        """Zoom in by a factor."""
        self.config.zoom *= factor
        # In 2D, we simulate zoom by scaling objects
        return AnimationGroup(
            *[obj.animate.scale(factor) for obj in self.scene.mobjects],
            run_time=duration
        )
    
    def zoom_out(self, factor: float = 1.5, duration: float = 1.0):
        """Zoom out by a factor."""
        self.config.zoom /= factor
        return AnimationGroup(
            *[obj.animate.scale(1/factor) for obj in self.scene.mobjects],
            run_time=duration
        )
    
    def pan(self, dx: float, dy: float, duration: float = 1.0):
        """Pan the camera."""
        self.config.position[0] += dx
        self.config.position[1] += dy
        # In 2D, we simulate pan by shifting objects
        return AnimationGroup(
            *[obj.animate.shift([-dx, -dy, 0]) for obj in self.scene.mobjects],
            run_time=duration
        )
    
    def reset(self, duration: float = 1.0):
        """Reset camera to original position and zoom."""
        zoom_factor = self.original_zoom / self.config.zoom
        dx = self.original_position[0] - self.config.position[0]
        dy = self.original_position[1] - self.config.position[1]
        
        self.config.zoom = self.original_zoom
        self.config.position = self.original_position.copy()
        
        return AnimationGroup(
            *[obj.animate.scale(zoom_factor).shift([dx, dy, 0]) 
              for obj in self.scene.mobjects],
            run_time=duration
        )