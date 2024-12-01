"""Magical circle effect with dynamic runes and symbols."""

from typing import Dict, List, Optional, Union
import numpy as np
from manim import *
from .base_effect import BaseEffect


class MagicalCircle(BaseEffect):
    """Creates a magical circle effect with rotating elements."""
    
    DEFAULT_CONFIG = {
        'radius': 2.0,
        'n_circles': 3,
        'n_runes': 8,
        'rotation_speed': 0.5,
        'color_scheme': {
            'outer': BLUE_A,
            'inner': BLUE_C,
            'runes': BLUE_E,
            'symbols': WHITE,
        }
    }
    
    def __init__(self, **kwargs):
        """Initialize magical circle.
        
        Args:
            **kwargs: Configuration options
        """
        super().__init__()
        self._config = self.DEFAULT_CONFIG.copy()
        self.update_config(**kwargs)
        self._mobjects = None
    
    def create(self) -> VGroup:
        """Create the magical circle elements."""
        radius = self.get_config('radius')
        n_circles = self.get_config('n_circles')
        n_runes = self.get_config('n_runes')
        colors = self.get_config('color_scheme')
        
        # Create concentric circles
        circles = VGroup()
        for i in range(n_circles):
            circle = Circle(
                radius=radius * (1 - i * 0.2),
                stroke_color=colors['outer'],
                stroke_width=2,
            )
            circles.add(circle)
        
        # Create runes
        runes = VGroup()
        for i in range(n_runes):
            angle = i * TAU / n_runes
            rune = self._create_rune()
            rune.rotate(angle)
            rune.shift(radius * RIGHT)
            rune.rotate(angle, about_point=ORIGIN)
            runes.add(rune)
        
        # Create inner symbols
        symbols = self._create_symbols()
        symbols.scale(radius * 0.3)
        
        # Combine all elements
        self._mobjects = VGroup(circles, runes, symbols)
        return self._mobjects
    
    def _create_rune(self) -> VMobject:
        """Create a single rune symbol."""
        colors = self.get_config('color_scheme')
        
        # Create a random rune-like shape
        n_points = np.random.randint(3, 7)
        points = []
        for i in range(n_points):
            angle = i * TAU / n_points + np.random.uniform(-0.2, 0.2)
            radius = np.random.uniform(0.2, 0.4)
            points.append([
                radius * np.cos(angle),
                radius * np.sin(angle),
                0
            ])
        
        rune = VMobject(stroke_color=colors['runes'])
        rune.set_points_smoothly([*points, points[0]])
        return rune
    
    def _create_symbols(self) -> VGroup:
        """Create inner magical symbols."""
        colors = self.get_config('color_scheme')
        
        # Create a pentagram
        pentagram = RegularPolygon(
            n=5,
            stroke_color=colors['symbols'],
            fill_color=colors['symbols'],
            fill_opacity=0.2
        )
        
        # Create a circle around it
        circle = Circle(
            stroke_color=colors['symbols'],
            stroke_width=1
        )
        
        return VGroup(pentagram, circle)
    
    def animate(self, scene: Scene) -> None:
        """Animate the magical circle.
        
        Args:
            scene: The scene to animate on
        """
        if self._mobjects is None:
            self.create()
            
        rotation_speed = self.get_config('rotation_speed')
        
        # Create and add updaters for rotation
        circles, runes, symbols = self._mobjects
        
        # Rotate outer circles one way
        circles.add_updater(
            lambda m, dt: m.rotate(rotation_speed * dt)
        )
        
        # Rotate runes the other way
        runes.add_updater(
            lambda m, dt: m.rotate(-rotation_speed * dt)
        )
        
        # Pulse the symbols
        symbols.add_updater(
            lambda m, dt: m.scale(
                1 + 0.1 * np.sin(2 * TAU * rotation_speed * scene.renderer.time)
            )
        )
        
        # Add everything to scene
        scene.add(self._mobjects)
    
    def cleanup(self, scene: Optional[Scene] = None) -> None:
        """Clean up animations and resources.
        
        Args:
            scene: Optional scene to remove objects from
        """
        if scene and self._mobjects:
            scene.remove(self._mobjects)
        
        # Clear all updaters
        if self._mobjects:
            for mob in self._mobjects:
                mob.clear_updaters()
        
        super().cleanup()
