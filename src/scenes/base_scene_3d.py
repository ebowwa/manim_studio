"""Base 3D scene class for Manim Studio with enhanced camera support."""

from manim import *
from typing import Optional, Dict, Any, List
from src.core.camera_controller import Camera3DController
from src.core.config import Camera3DConfig


class StudioScene3D(ThreeDScene):
    """Enhanced 3D scene with camera controller and studio features."""
    
    def __init__(self, camera_config: Optional[Camera3DConfig] = None, **kwargs):
        """Initialize 3D scene with optional camera configuration."""
        super().__init__(**kwargs)
        
        # Initialize camera controller
        self.camera_config = camera_config or Camera3DConfig()
        self.camera_controller = None
        
        # Initialize text manager
        from ..core.text_manager import TextManager
        self.text_manager = TextManager(self)
        
        # Scene metadata
        self.metadata = {
            'scene_type': '3d',
            'camera_enabled': True,
            'effects_enabled': True
        }
    
    def setup(self):
        """Setup the 3D scene with camera configuration."""
        super().setup()
        
        # Initialize camera controller
        self.camera_controller = Camera3DController(self, self.camera_config)
        
        # Apply initial camera configuration
        if self.camera_config:
            self.set_camera_orientation(
                phi=self.camera_config.phi,
                theta=self.camera_config.theta
            )
            
            # Set camera distance (zoom)
            if hasattr(self.camera, 'set_zoom'):
                self.camera.set_zoom(self.camera_config.zoom)
    
    def begin_3d_camera_rotation(self, rate: float = 0.2, about: str = "phi", 
                                begin_time: float = 0, end_time: float = None):
        """Begin automatic camera rotation.
        
        Args:
            rate: Rotation rate in radians per second
            about: Axis to rotate about ('phi', 'theta', or 'both')
            begin_time: Time to begin rotation
            end_time: Time to end rotation (None for continuous)
        """
        if about == "phi":
            self.begin_ambient_camera_rotation(rate=rate, about="phi")
        elif about == "theta":
            self.begin_ambient_camera_rotation(rate=rate, about="theta")
        elif about == "both":
            self.begin_ambient_camera_rotation(rate=rate)
    
    def stop_3d_camera_rotation(self):
        """Stop automatic camera rotation."""
        self.stop_ambient_camera_rotation()
    
    def move_camera_to(self, position: List[float], focal_point: Optional[List[float]] = None,
                      duration: float = 2.0, **kwargs):
        """Move camera to a specific position with animation.
        
        Args:
            position: Target camera position [x, y, z]
            focal_point: Optional focal point to look at
            duration: Duration of the movement
            **kwargs: Additional animation parameters
        """
        if self.camera_controller:
            self.camera_controller.move_to(position, duration, **kwargs)
            if focal_point:
                self.camera_controller.look_at(focal_point, duration)
    
    def orbit_camera(self, center: List[float], radius: float, 
                    duration: float, **kwargs):
        """Orbit camera around a point.
        
        Args:
            center: Center point to orbit around
            radius: Orbital radius
            duration: Duration of one complete orbit
            **kwargs: Additional parameters (revolutions, axis, etc.)
        """
        if self.camera_controller:
            self.camera_controller.orbit_around(center, radius, duration, **kwargs)
    
    def apply_depth_of_field(self, focal_distance: float = None, 
                           aperture: float = None):
        """Apply depth of field effect (if supported).
        
        Args:
            focal_distance: Distance to focal plane
            aperture: Aperture size (smaller = more blur)
        """
        if self.camera_config.dof_enabled:
            # This would require custom shader implementation
            # For now, it's a placeholder for future enhancement
            pass
    
    def create_camera_path_preview(self) -> VGroup:
        """Create a visual preview of the camera path."""
        if self.camera_controller:
            return self.camera_controller.create_camera_path_visualization()
        return VGroup()
    
    def update_camera(self, dt: float):
        """Update camera controller (call in animation loop if needed)."""
        if self.camera_controller:
            self.camera_controller.update(dt)
    
    def set_camera_to_default(self):
        """Reset camera to default position."""
        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES)
        if hasattr(self.camera, 'set_zoom'):
            self.camera.set_zoom(1.0)
    
    def create_axes(self, **kwargs) -> ThreeDAxes:
        """Create 3D axes with default styling."""
        axes = ThreeDAxes(**kwargs)
        axes.set_color(GREY)
        return axes
    
    def create_grid(self, **kwargs) -> VGroup:
        """Create a grid floor for spatial reference."""
        grid = NumberPlane(**kwargs)
        grid.set_color(GREY)
        grid.set_opacity(0.3)
        return grid
    
    def add_ambient_rotation(self, mobject: Mobject, axis: np.ndarray = UP,
                           rate: float = 0.5, **kwargs):
        """Add ambient rotation to a mobject.
        
        Args:
            mobject: The mobject to rotate
            axis: Axis of rotation
            rate: Rotation rate in radians per second
            **kwargs: Additional parameters
        """
        mobject.add_updater(
            lambda m, dt: m.rotate(rate * dt, axis=axis, **kwargs)
        )
    
    def create_3d_text(self, text: str, **kwargs) -> Text:
        """Create text that faces the camera in 3D space.
        
        Note: Returns regular Text that always faces the camera.
        """
        # Import here to avoid circular imports
        from ..core.text_manager import TextManager
        
        text_manager = TextManager(self)
        text_obj = text_manager.create_text(text, **kwargs)
        
        # Make it face camera if in 3D scene
        if hasattr(self.camera, 'get_location'):
            text_obj.add_updater(lambda m: m.look_at(self.camera.get_location()))
        return text_obj