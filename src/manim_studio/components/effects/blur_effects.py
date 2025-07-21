"""Blur and focus effects for Manim Studio."""

from typing import Optional, List, Union, Tuple
import numpy as np
from manim import *
from .base_effect import BaseEffect


class BlurEffect(BaseEffect):
    """Creates blur effects on objects."""
    
    def __init__(self, target: Mobject, **kwargs):
        super().__init__()
        self.target = target
        self.update_config(
            blur_radius=kwargs.get('blur_radius', 0.1),
            blur_samples=kwargs.get('blur_samples', 8),
            blur_opacity=kwargs.get('blur_opacity', 0.3),
            preserve_original=kwargs.get('preserve_original', False),
            blur_type=kwargs.get('blur_type', 'gaussian')  # 'gaussian', 'motion', 'radial'
        )
    
    def create(self) -> VGroup:
        """Create blurred version of the target."""
        blurred = VGroup()
        
        if self.get_config('preserve_original'):
            blurred.add(self.target.copy())
        
        blur_type = self.get_config('blur_type')
        
        if blur_type == 'gaussian':
            blurred.add(*self._create_gaussian_blur())
        elif blur_type == 'motion':
            blurred.add(*self._create_motion_blur())
        elif blur_type == 'radial':
            blurred.add(*self._create_radial_blur())
        
        self.add_mobjects(blurred)
        return self._mobjects
    
    def _create_gaussian_blur(self) -> List[Mobject]:
        """Create Gaussian blur effect."""
        blur_layers = []
        samples = self.get_config('blur_samples')
        radius = self.get_config('blur_radius')
        base_opacity = self.get_config('blur_opacity') / samples
        
        for i in range(samples):
            angle = 2 * PI * i / samples
            offset = radius * np.array([np.cos(angle), np.sin(angle), 0])
            
            layer = self.target.copy()
            layer.shift(offset)
            layer.set_fill(opacity=base_opacity)
            layer.set_stroke(opacity=base_opacity)
            blur_layers.append(layer)
        
        return blur_layers
    
    def _create_motion_blur(self) -> List[Mobject]:
        """Create motion blur effect."""
        blur_layers = []
        samples = self.get_config('blur_samples')
        radius = self.get_config('blur_radius')
        base_opacity = self.get_config('blur_opacity') / samples
        
        # Default motion direction is RIGHT
        direction = self._config.get('motion_direction', RIGHT)
        
        for i in range(samples):
            offset = direction * radius * (i - samples/2) / samples
            
            layer = self.target.copy()
            layer.shift(offset)
            layer.set_fill(opacity=base_opacity * (1 - abs(i - samples/2) / samples))
            layer.set_stroke(opacity=base_opacity * (1 - abs(i - samples/2) / samples))
            blur_layers.append(layer)
        
        return blur_layers
    
    def _create_radial_blur(self) -> List[Mobject]:
        """Create radial blur effect."""
        blur_layers = []
        samples = self.get_config('blur_samples')
        radius = self.get_config('blur_radius')
        base_opacity = self.get_config('blur_opacity') / samples
        
        center = self._config.get('blur_center', self.target.get_center())
        
        for i in range(1, samples + 1):
            scale_factor = 1 + (radius * i / samples)
            
            layer = self.target.copy()
            layer.scale(scale_factor, about_point=center)
            layer.set_fill(opacity=base_opacity * (1 - i / samples))
            layer.set_stroke(opacity=base_opacity * (1 - i / samples))
            blur_layers.append(layer)
        
        return blur_layers
    
    def animate(self, scene: Scene) -> None:
        """Add the blur effect to the scene."""
        scene.add(self._mobjects)


class DepthOfFieldEffect(BaseEffect):
    """Creates depth of field effect with focal planes."""
    
    def __init__(self, objects: List[Mobject], **kwargs):
        super().__init__()
        self.objects = objects
        self.update_config(
            focal_point=kwargs.get('focal_point', ORIGIN),
            focal_depth=kwargs.get('focal_depth', 2.0),
            aperture=kwargs.get('aperture', 0.5),
            max_blur=kwargs.get('max_blur', 0.2),
            blur_samples=kwargs.get('blur_samples', 5)
        )
    
    def create(self) -> VGroup:
        """Create depth of field effect on objects."""
        dof_group = VGroup()
        
        focal_point = self.get_config('focal_point')
        focal_depth = self.get_config('focal_depth')
        aperture = self.get_config('aperture')
        max_blur = self.get_config('max_blur')
        
        for obj in self.objects:
            # Calculate distance from focal plane
            obj_depth = abs(obj.get_center()[2] - focal_point[2])
            
            # Calculate blur amount based on distance
            if obj_depth < focal_depth:
                blur_amount = 0
            else:
                blur_amount = min(max_blur, (obj_depth - focal_depth) * aperture)
            
            if blur_amount > 0.01:
                # Apply blur
                blur_effect = BlurEffect(
                    obj,
                    blur_radius=blur_amount,
                    blur_samples=self.get_config('blur_samples'),
                    blur_opacity=0.8,
                    preserve_original=True
                )
                dof_group.add(blur_effect.create())
            else:
                # In focus
                dof_group.add(obj.copy())
        
        self.add_mobjects(dof_group)
        return self._mobjects
    
    def animate(self, scene: Scene) -> None:
        """Animate depth of field effect."""
        scene.add(self._mobjects)


class FocusPullEffect(BaseEffect):
    """Animates focus transition between objects."""
    
    def __init__(self, objects: List[Mobject], **kwargs):
        super().__init__()
        self.objects = objects
        self.update_config(
            focus_sequence=kwargs.get('focus_sequence', list(range(len(objects)))),
            transition_time=kwargs.get('transition_time', 1.0),
            hold_time=kwargs.get('hold_time', 1.0),
            blur_unfocused=kwargs.get('blur_unfocused', True),
            highlight_focused=kwargs.get('highlight_focused', True)
        )
    
    def create(self) -> VGroup:
        """Create objects with blur states."""
        focus_group = VGroup()
        
        # Create both focused and blurred versions
        self.focused_versions = VGroup()
        self.blurred_versions = VGroup()
        
        for obj in self.objects:
            # Focused version
            focused = obj.copy()
            if self.get_config('highlight_focused'):
                focused.set_color(interpolate_color(obj.get_color(), WHITE, 0.2))
            self.focused_versions.add(focused)
            
            # Blurred version
            if self.get_config('blur_unfocused'):
                blur_effect = BlurEffect(
                    obj,
                    blur_radius=0.15,
                    blur_samples=8,
                    blur_opacity=0.5
                )
                blurred = blur_effect.create()
            else:
                blurred = obj.copy()
                blurred.set_opacity(0.3)
            
            self.blurred_versions.add(blurred)
        
        # Start with all blurred
        focus_group.add(self.blurred_versions)
        
        self.add_mobjects(focus_group)
        return self._mobjects
    
    def animate(self, scene: Scene) -> None:
        """Animate focus pulling sequence."""
        scene.add(self.blurred_versions)
        
        focus_sequence = self.get_config('focus_sequence')
        transition_time = self.get_config('transition_time')
        hold_time = self.get_config('hold_time')
        
        for focus_idx in focus_sequence:
            if 0 <= focus_idx < len(self.objects):
                # Transition animations
                transitions = []
                
                for i in range(len(self.objects)):
                    if i == focus_idx:
                        # Focus this object
                        transitions.append(
                            Transform(
                                self.blurred_versions[i],
                                self.focused_versions[i],
                                run_time=transition_time
                            )
                        )
                    else:
                        # Ensure others are blurred
                        if self.get_config('blur_unfocused'):
                            blur_effect = BlurEffect(
                                self.objects[i],
                                blur_radius=0.15,
                                blur_samples=8,
                                blur_opacity=0.5
                            )
                            target = blur_effect.create()
                        else:
                            target = self.objects[i].copy()
                            target.set_opacity(0.3)
                        
                        transitions.append(
                            Transform(
                                self.blurred_versions[i],
                                target,
                                run_time=transition_time
                            )
                        )
                
                scene.play(*transitions)
                scene.wait(hold_time)


class ChromaticAberrationEffect(BaseEffect):
    """Creates chromatic aberration (color fringing) effect."""
    
    def __init__(self, target: Mobject, **kwargs):
        super().__init__()
        self.target = target
        self.update_config(
            aberration_offset=kwargs.get('aberration_offset', 0.05),
            color_channels=kwargs.get('color_channels', [RED, GREEN, BLUE]),
            blend_mode=kwargs.get('blend_mode', 'additive'),
            offset_direction=kwargs.get('offset_direction', RIGHT)
        )
    
    def create(self) -> VGroup:
        """Create color-separated layers."""
        aberration_group = VGroup()
        
        offset = self.get_config('aberration_offset')
        direction = normalize(self.get_config('offset_direction'))
        channels = self.get_config('color_channels')
        
        for i, color in enumerate(channels):
            channel_offset = (i - len(channels)/2 + 0.5) * offset * direction
            
            channel_layer = self.target.copy()
            channel_layer.shift(channel_offset)
            channel_layer.set_color(color)
            
            if self.get_config('blend_mode') == 'additive':
                channel_layer.set_fill(opacity=0.5)
                channel_layer.set_stroke(opacity=0.5)
            else:
                channel_layer.set_fill(opacity=1.0 / len(channels))
                channel_layer.set_stroke(opacity=1.0 / len(channels))
            
            aberration_group.add(channel_layer)
        
        self.add_mobjects(aberration_group)
        return self._mobjects
    
    def animate(self, scene: Scene) -> None:
        """Add chromatic aberration to scene."""
        scene.add(self._mobjects)


class TiltShiftEffect(BaseEffect):
    """Creates tilt-shift photography effect."""
    
    def __init__(self, scene_objects: List[Mobject], **kwargs):
        super().__init__()
        self.scene_objects = scene_objects
        self.update_config(
            focus_band_center=kwargs.get('focus_band_center', 0),
            focus_band_width=kwargs.get('focus_band_width', 1.0),
            orientation=kwargs.get('orientation', 'horizontal'),  # 'horizontal' or 'vertical'
            max_blur=kwargs.get('max_blur', 0.2),
            blur_falloff=kwargs.get('blur_falloff', 'linear')  # 'linear' or 'gaussian'
        )
    
    def create(self) -> VGroup:
        """Create tilt-shift effect."""
        tilt_shift_group = VGroup()
        
        center = self.get_config('focus_band_center')
        width = self.get_config('focus_band_width')
        orientation = self.get_config('orientation')
        max_blur = self.get_config('max_blur')
        
        for obj in self.scene_objects:
            obj_center = obj.get_center()
            
            # Calculate distance from focus band
            if orientation == 'horizontal':
                distance = abs(obj_center[1] - center)
            else:
                distance = abs(obj_center[0] - center)
            
            # Calculate blur amount
            if distance <= width / 2:
                blur_amount = 0
            else:
                relative_distance = (distance - width / 2) / width
                
                if self.get_config('blur_falloff') == 'gaussian':
                    blur_amount = max_blur * (1 - np.exp(-2 * relative_distance**2))
                else:
                    blur_amount = min(max_blur, max_blur * relative_distance)
            
            if blur_amount > 0.01:
                blur_effect = BlurEffect(
                    obj,
                    blur_radius=blur_amount,
                    blur_samples=6,
                    blur_opacity=0.6,
                    preserve_original=True
                )
                tilt_shift_group.add(blur_effect.create())
            else:
                tilt_shift_group.add(obj.copy())
        
        self.add_mobjects(tilt_shift_group)
        return self._mobjects
    
    def animate(self, scene: Scene) -> None:
        """Apply tilt-shift effect."""
        scene.add(self._mobjects)


class BokehEffect(BaseEffect):
    """Creates bokeh (aesthetic blur) effect for backgrounds."""
    
    def __init__(self, **kwargs):
        super().__init__()
        self.update_config(
            num_bokeh=kwargs.get('num_bokeh', 30),
            bokeh_sizes=kwargs.get('bokeh_sizes', (0.1, 0.5)),
            bokeh_colors=kwargs.get('bokeh_colors', [WHITE, YELLOW, BLUE_E]),
            bokeh_opacity=kwargs.get('bokeh_opacity', (0.2, 0.6)),
            bokeh_shape=kwargs.get('bokeh_shape', 'circle'),  # 'circle', 'hexagon', 'star'
            animation_type=kwargs.get('animation_type', 'drift')  # 'drift', 'pulse', 'static'
        )
    
    def create(self) -> VGroup:
        """Create bokeh elements."""
        bokeh_group = VGroup()
        
        num_bokeh = self.get_config('num_bokeh')
        size_range = self.get_config('bokeh_sizes')
        colors = self.get_config('bokeh_colors')
        opacity_range = self.get_config('bokeh_opacity')
        shape = self.get_config('bokeh_shape')
        
        for i in range(num_bokeh):
            size = np.random.uniform(*size_range)
            color = np.random.choice(colors)
            opacity = np.random.uniform(*opacity_range)
            
            # Random position
            x = np.random.uniform(-7, 7)
            y = np.random.uniform(-4, 4)
            z = np.random.uniform(-2, -0.5)  # Behind main content
            
            if shape == 'circle':
                bokeh = Circle(radius=size)
            elif shape == 'hexagon':
                bokeh = RegularPolygon(n=6, radius=size)
            elif shape == 'star':
                bokeh = Star(n=6, outer_radius=size, inner_radius=size * 0.5)
            
            bokeh.move_to([x, y, z])
            bokeh.set_fill(color, opacity=opacity)
            bokeh.set_stroke(width=0)
            
            # Add glow effect
            glow = bokeh.copy()
            glow.scale(1.5)
            glow.set_fill(opacity=opacity * 0.3)
            
            bokeh_element = VGroup(glow, bokeh)
            bokeh_group.add(bokeh_element)
        
        self.add_mobjects(bokeh_group)
        return self._mobjects
    
    def animate(self, scene: Scene) -> None:
        """Animate bokeh elements."""
        bokeh_elements = self._mobjects
        scene.add(bokeh_elements)
        
        animation_type = self.get_config('animation_type')
        
        if animation_type == 'drift':
            for bokeh in bokeh_elements:
                # Random drift direction and speed
                drift_direction = normalize(np.random.randn(3))
                drift_direction[2] = 0  # Keep in same z-plane
                drift_speed = np.random.uniform(0.1, 0.3)
                
                bokeh.add_updater(
                    lambda m, dt, dir=drift_direction, speed=drift_speed: 
                    m.shift(dir * speed * dt)
                )
        
        elif animation_type == 'pulse':
            for bokeh in bokeh_elements:
                pulse_rate = np.random.uniform(0.5, 2.0)
                base_scale = bokeh.get_height()
                
                def pulse_updater(m, dt, rate=pulse_rate, base=base_scale):
                    time = scene.renderer.time
                    scale_factor = 1 + 0.2 * np.sin(rate * TAU * time)
                    m.set_height(base * scale_factor)
                
                bokeh.add_updater(pulse_updater)