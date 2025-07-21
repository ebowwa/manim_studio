"""Glow and lighting effects for Manim Studio."""

from typing import Optional, Union
try:
    from typing import List
except ImportError:
    List = list
from manim import *
from .base_effect import BaseEffect


class GlowEffect(BaseEffect):
    """Creates a glowing effect around objects."""
    
    def __init__(self, target: Mobject, **kwargs):
        super().__init__()
        self.target = target
        self.update_config(
            glow_color=kwargs.get('glow_color', YELLOW),
            glow_radius=kwargs.get('glow_radius', 0.5),
            num_layers=kwargs.get('num_layers', 8),
            opacity_range=kwargs.get('opacity_range', (0.1, 0.6)),
            pulse=kwargs.get('pulse', False),
            pulse_rate=kwargs.get('pulse_rate', 1.0)
        )
    
    def create(self) -> VGroup:
        """Create the glow effect layers."""
        glow_layers = VGroup()
        
        min_opacity, max_opacity = self.get_config('opacity_range')
        num_layers = self.get_config('num_layers')
        glow_radius = self.get_config('glow_radius')
        glow_color = self.get_config('glow_color')
        
        for i in range(num_layers):
            layer_scale = 1 + (i + 1) * glow_radius / num_layers
            layer_opacity = max_opacity - (i * (max_opacity - min_opacity) / num_layers)
            
            glow_layer = self.target.copy()
            glow_layer.set_color(glow_color)
            glow_layer.set_fill(opacity=0)
            glow_layer.set_stroke(color=glow_color, width=8, opacity=layer_opacity)
            glow_layer.scale(layer_scale)
            
            glow_layers.add(glow_layer)
        
        self.add_mobjects(glow_layers)
        return self._mobjects
    
    def animate(self, scene: Scene) -> None:
        """Animate the glow effect."""
        if self.get_config('pulse'):
            pulse_rate = self.get_config('pulse_rate')
            
            def update_glow(mob, dt):
                time = scene.renderer.time
                pulse_factor = 0.8 + 0.2 * np.sin(pulse_rate * TAU * time)
                mob.scale(pulse_factor)
                mob.scale(1 / pulse_factor)
            
            for layer in self._mobjects:
                layer.add_updater(update_glow)
        
        scene.add(self._mobjects)


class NeonEffect(BaseEffect):
    """Creates a neon light effect."""
    
    def __init__(self, target, **kwargs):
        super().__init__()
        self.targets = target if isinstance(target, list) else [target]
        self.update_config(
            neon_color=kwargs.get('neon_color', PINK),
            secondary_color=kwargs.get('secondary_color', WHITE),
            flicker=kwargs.get('flicker', False),
            flicker_probability=kwargs.get('flicker_probability', 0.05),
            brightness=kwargs.get('brightness', 1.0)
        )
    
    def create(self) -> VGroup:
        """Create neon effect elements."""
        neon_group = VGroup()
        
        for target in self.targets:
            # Inner bright core
            core = target.copy()
            core.set_stroke(
                color=self.get_config('secondary_color'),
                width=4,
                opacity=self.get_config('brightness')
            )
            
            # Outer neon glow
            outer_glow = target.copy()
            outer_glow.set_stroke(
                color=self.get_config('neon_color'),
                width=12,
                opacity=0.8 * self.get_config('brightness')
            )
            
            # Ambient glow
            ambient = target.copy()
            ambient.set_stroke(
                color=self.get_config('neon_color'),
                width=20,
                opacity=0.3 * self.get_config('brightness')
            )
            ambient.scale(1.1)
            
            neon_group.add(ambient, outer_glow, core)
        
        self.add_mobjects(neon_group)
        return self._mobjects
    
    def animate(self, scene: Scene) -> None:
        """Animate the neon effect with optional flickering."""
        scene.add(self._mobjects)
        
        if self.get_config('flicker'):
            def flicker_update(mob, dt):
                if np.random.random() < self.get_config('flicker_probability'):
                    mob.set_opacity(0.3)
                else:
                    mob.set_opacity(1.0)
            
            for mob in self._mobjects:
                mob.add_updater(flicker_update)


class SpotlightEffect(BaseEffect):
    """Creates a spotlight or stage light effect."""
    
    def __init__(self, position: np.ndarray = ORIGIN, **kwargs):
        super().__init__()
        self.position = position
        self.update_config(
            radius=kwargs.get('radius', 2.0),
            angle=kwargs.get('angle', 45 * DEGREES),
            direction=kwargs.get('direction', DOWN),
            color=kwargs.get('color', WHITE),
            intensity=kwargs.get('intensity', 0.8),
            soft_edge=kwargs.get('soft_edge', True),
            follow_target=kwargs.get('follow_target', None)
        )
    
    def create(self) -> VGroup:
        """Create the spotlight cone and light effect."""
        spotlight = VGroup()
        
        # Create light cone
        radius = self.get_config('radius')
        angle = self.get_config('angle')
        direction = self.get_config('direction')
        
        # Calculate cone vertices
        height = radius / np.tan(angle / 2)
        cone = Polygon(
            self.position,
            self.position + height * direction + radius * rotate_vector(RIGHT, angle / 2),
            self.position + height * direction,
            self.position + height * direction + radius * rotate_vector(LEFT, angle / 2)
        )
        
        cone.set_fill(
            color=self.get_config('color'),
            opacity=self.get_config('intensity')
        )
        cone.set_stroke(width=0)
        
        if self.get_config('soft_edge'):
            # Add gradient effect for soft edges
            for i in range(5):
                edge = cone.copy()
                edge.scale(1 + 0.1 * i)
                edge.set_fill(opacity=self.get_config('intensity') * (0.5 - 0.1 * i))
                spotlight.add(edge)
        
        spotlight.add(cone)
        self.add_mobjects(spotlight)
        return self._mobjects
    
    def animate(self, scene: Scene) -> None:
        """Animate the spotlight with optional target following."""
        scene.add(self._mobjects)
        
        follow_target = self.get_config('follow_target')
        if follow_target:
            def follow_update(mob, dt):
                target_pos = follow_target.get_center()
                direction = normalize(target_pos - self.position)
                mob.rotate(
                    angle_between_vectors(self.get_config('direction'), direction),
                    about_point=self.position
                )
                self.update_config(direction=direction)
            
            self._mobjects.add_updater(follow_update)


class LensFlareEffect(BaseEffect):
    """Creates a lens flare effect for bright light sources."""
    
    def __init__(self, light_source: np.ndarray = ORIGIN, **kwargs):
        super().__init__()
        self.light_source = light_source
        self.update_config(
            num_flares=kwargs.get('num_flares', 6),
            flare_colors=kwargs.get('flare_colors', [BLUE, GREEN, YELLOW, ORANGE]),
            size_range=kwargs.get('size_range', (0.1, 0.5)),
            opacity_range=kwargs.get('opacity_range', (0.2, 0.6)),
            streak_length=kwargs.get('streak_length', 4.0),
            animate_rotation=kwargs.get('animate_rotation', True)
        )
    
    def create(self) -> VGroup:
        """Create lens flare elements."""
        flares = VGroup()
        
        # Main light source
        main_flare = Circle(radius=0.3)
        main_flare.move_to(self.light_source)
        main_flare.set_fill(WHITE, opacity=1.0)
        main_flare.set_stroke(width=0)
        flares.add(main_flare)
        
        # Secondary flares along axis
        num_flares = self.get_config('num_flares')
        colors = self.get_config('flare_colors')
        size_range = self.get_config('size_range')
        opacity_range = self.get_config('opacity_range')
        
        for i in range(num_flares):
            t = (i + 1) / (num_flares + 1)
            position = self.light_source + t * self.get_config('streak_length') * RIGHT
            
            size = interpolate(size_range[0], size_range[1], np.random.random())
            opacity = interpolate(opacity_range[0], opacity_range[1], 1 - t)
            color = colors[i % len(colors)]
            
            flare = Circle(radius=size)
            flare.move_to(position)
            flare.set_fill(color, opacity=opacity)
            flare.set_stroke(width=0)
            
            # Add hexagonal shape for some flares
            if i % 2 == 0:
                hex_flare = RegularPolygon(n=6, radius=size * 0.8)
                hex_flare.move_to(position)
                hex_flare.set_fill(color, opacity=opacity * 0.5)
                hex_flare.set_stroke(width=0)
                flares.add(hex_flare)
            
            flares.add(flare)
        
        # Add light streaks
        for angle in [0, PI/2, PI, 3*PI/2]:
            streak = Line(
                self.light_source,
                self.light_source + self.get_config('streak_length') * 0.5 * np.array([np.cos(angle), np.sin(angle), 0])
            )
            streak.set_stroke(WHITE, width=2, opacity=0.3)
            flares.add(streak)
        
        self.add_mobjects(flares)
        return self._mobjects
    
    def animate(self, scene: Scene) -> None:
        """Animate the lens flare effect."""
        scene.add(self._mobjects)
        
        if self.get_config('animate_rotation'):
            self._mobjects.add_updater(
                lambda m, dt: m.rotate(0.5 * dt, about_point=self.light_source)
            )