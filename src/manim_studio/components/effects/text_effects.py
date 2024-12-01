"""Advanced text effects and animations."""

from typing import List, Tuple, Optional, Union
import numpy as np
from manim import *
from .base_effect import BaseEffect
from .particle_system import ParticleSystem


class GlowingText(Text):
    """Text with dynamic glowing effect."""
    
    def __init__(
        self,
        text: str,
        glow_color: Optional[str] = None,
        glow_factor: float = 1.5,
        **kwargs
    ):
        super().__init__(text, **kwargs)
        self.glow = self._create_glow(glow_color or self.color, glow_factor)
        self.add_to_back(self.glow)
    
    def _create_glow(self, color: str, factor: float) -> VMobject:
        """Create the glowing effect."""
        glow = self.copy()
        glow.set_style(
            fill_color=color,
            fill_opacity=0.3,
            stroke_width=0,
            stroke_opacity=0
        )
        glow.scale(factor)
        return glow
    
    def pulse(self, scene: Scene, duration: float = 1.0):
        """Create a pulsing animation."""
        scene.play(
            self.glow.animate.scale(1.2).set_opacity(0.5),
            rate_func=there_and_back,
            run_time=duration
        )


class TextEffects(BaseEffect):
    """Advanced text effects with multiple animation styles."""
    
    DEFAULT_CONFIG = {
        'font_size': 36,
        'color': WHITE,
        'stroke_width': 0,
        'fill_opacity': 1.0,
        'gradient_colors': None,
        'sparkle_colors': [BLUE_A, BLUE_B, BLUE_C, BLUE_D, BLUE_E],
        'glow_color': BLUE,
        'glow_opacity': 0.8,
    }
    
    def __init__(self, text: str, **kwargs):
        """Initialize text effect.
        
        Args:
            text: The text to display
            **kwargs: Configuration options
        """
        super().__init__()
        self.text = text
        self._config = self.DEFAULT_CONFIG.copy()
        self.update_config(**kwargs)
        self._mobjects = None
        
    def create(self) -> VMobject:
        """Create the text mobject.
        
        Returns:
            The created text mobject
        """
        # Create base text
        text = Text(
            self.text,
            font_size=self.get_config('font_size'),
            color=self.get_config('color'),
            stroke_width=self.get_config('stroke_width'),
            fill_opacity=self.get_config('fill_opacity'),
        )
        
        # Apply gradient if specified
        gradient_colors = self.get_config('gradient_colors')
        if gradient_colors:
            text.set_color_by_gradient(*gradient_colors)
            
        self._mobjects = text
        return text
        
    def animate(self, scene: Scene, style: str = 'write') -> None:
        """Animate the text with the specified style.
        
        Args:
            scene: The scene to animate on
            style: Animation style ('write', 'fade', 'typewriter', 'sparkle')
        """
        if not self._mobjects:
            self.create()
            
        if style == 'write':
            self._write_animation(scene)
        elif style == 'fade':
            self._fade_animation(scene)
        elif style == 'typewriter':
            self._typewriter_animation(scene)
        elif style == 'sparkle':
            self._sparkle_animation(scene)
        else:
            raise ValueError(f"Unknown animation style: {style}")
            
    def _write_animation(self, scene: Scene) -> None:
        """Animate text being written."""
        scene.play(Write(self._mobjects))
        
    def _fade_animation(self, scene: Scene) -> None:
        """Animate text fading in."""
        scene.play(FadeIn(self._mobjects))
        
    def _typewriter_animation(self, scene: Scene) -> None:
        """Animate text appearing like a typewriter."""
        scene.play(AddTextLetterByLetter(self._mobjects))
        
    def _sparkle_animation(self, scene: Scene) -> None:
        """Animate text with sparkle effects."""
        # Create particle system for sparkles
        particles = ParticleSystem(
            n_emitters=len(self.text),
            particles_per_second=20,
            particle_lifetime=0.5,
            velocity_range=(0.5, 1.0),
            particle_color=self.get_config('sparkle_colors'),
            particle_size_range=(0.02, 0.05)
        )
        
        # Position emitters along text
        if isinstance(self._mobjects, VMobject):
            text = self._mobjects
            
            # Get text points at regular intervals
            points = []
            try:
                # Try to get points directly from text
                for i in range(len(self.text)):
                    alpha = i / (len(self.text) - 1) if len(self.text) > 1 else 0.5
                    points.append(text.point_from_proportion(alpha))
            except Exception:
                # Fallback: Use text bounding box
                left = text.get_left()
                right = text.get_right()
                for i in range(len(self.text)):
                    alpha = i / (len(self.text) - 1) if len(self.text) > 1 else 0.5
                    x = left[0] + alpha * (right[0] - left[0])
                    y = (left[1] + right[1]) / 2  # Vertical center
                    points.append(np.array([x, y, 0]))
                
            # Position emitters
            for emitter, point in zip(particles.emitters, points):
                emitter.position = point
                
            # Animate particles and text
            particles.animate(scene)
            scene.play(FadeIn(text), run_time=1.5)
            scene.wait(0.5)
        else:
            # Fallback to simple fade if text is not a VMobject
            self._fade_animation(scene)
            
    def cleanup(self, scene: Optional[Scene] = None) -> None:
        """Clean up animations and resources.
        
        Args:
            scene: Optional scene to remove objects from
        """
        if scene and self._mobjects:
            scene.remove(self._mobjects)
        super().cleanup()


class AddTextLetterByLetter(Animation):
    """Custom animation for typewriter effect."""
    
    def __init__(
        self,
        mobject: VMobject,
        time_per_char: float = 0.1,
        **kwargs
    ):
        """Initialize typewriter animation.
        
        Args:
            mobject: Text mobject to animate
            time_per_char: Time to spend on each character
            **kwargs: Additional animation configuration
        """
        self.time_per_char = time_per_char
        super().__init__(mobject, **kwargs)
    
    def interpolate_mobject(self, alpha: float) -> None:
        """Update animation state.
        
        Args:
            alpha: Animation progress from 0 to 1
        """
        n_letters = len(self.mobject.get_family())
        n_visible = int(alpha * n_letters)
        
        for i, submob in enumerate(self.mobject.get_family()):
            submob.set_fill(opacity=float(i < n_visible))
            submob.set_stroke(opacity=float(i < n_visible))
