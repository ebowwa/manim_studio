"""Wave and ripple effects for Manim Studio."""

from typing import Optional, Callable, List, Tuple
import numpy as np
from manim import *
from .base_effect import BaseEffect


class WaveEffect(BaseEffect):
    """Creates wave animations on objects."""
    
    def __init__(self, target: Mobject, **kwargs):
        super().__init__()
        self.target = target
        self.update_config(
            wave_direction=kwargs.get('wave_direction', RIGHT),
            wavelength=kwargs.get('wavelength', 1.0),
            amplitude=kwargs.get('amplitude', 0.3),
            frequency=kwargs.get('frequency', 1.0),
            wave_speed=kwargs.get('wave_speed', 1.0),
            damping=kwargs.get('damping', 0.0),
            wave_color=kwargs.get('wave_color', None)
        )
        self.time_elapsed = 0
    
    def create(self) -> VGroup:
        """Create the wave-affected object."""
        wave_obj = self.target.copy()
        if self.get_config('wave_color'):
            wave_obj.set_color(self.get_config('wave_color'))
        
        self.add_mobjects(wave_obj)
        return self._mobjects
    
    def animate(self, scene: Scene) -> None:
        """Animate the wave effect."""
        wave_obj = self._mobjects[0]
        scene.add(wave_obj)
        
        def wave_updater(mob, dt):
            self.time_elapsed += dt
            points = mob.get_points()
            original_points = self.target.get_points()
            
            wave_dir = normalize(self.get_config('wave_direction'))
            wavelength = self.get_config('wavelength')
            amplitude = self.get_config('amplitude')
            frequency = self.get_config('frequency')
            speed = self.get_config('wave_speed')
            damping = self.get_config('damping')
            
            for i, (point, orig_point) in enumerate(zip(points, original_points)):
                distance_along_wave = np.dot(orig_point, wave_dir)
                phase = 2 * PI * (distance_along_wave / wavelength - frequency * speed * self.time_elapsed)
                
                displacement = amplitude * np.sin(phase)
                if damping > 0:
                    displacement *= np.exp(-damping * distance_along_wave)
                
                perpendicular = rotate_vector(wave_dir, PI/2)
                points[i] = orig_point + displacement * perpendicular
            
            mob.set_points(points)
        
        wave_obj.add_updater(wave_updater)


class RippleEffect(BaseEffect):
    """Creates ripple effects emanating from a point."""
    
    def __init__(self, center: np.ndarray = ORIGIN, **kwargs):
        super().__init__()
        self.center = center
        self.update_config(
            num_ripples=kwargs.get('num_ripples', 5),
            max_radius=kwargs.get('max_radius', 3.0),
            ripple_color=kwargs.get('ripple_color', BLUE),
            fade_out=kwargs.get('fade_out', True),
            ripple_width=kwargs.get('ripple_width', 3),
            speed=kwargs.get('speed', 1.0),
            lifetime=kwargs.get('lifetime', 3.0)
        )
    
    def create(self) -> VGroup:
        """Create ripple circles."""
        ripples = VGroup()
        
        for i in range(self.get_config('num_ripples')):
            ripple = Circle(
                radius=0.01,
                color=self.get_config('ripple_color'),
                stroke_width=self.get_config('ripple_width')
            )
            ripple.move_to(self.center)
            ripples.add(ripple)
        
        self.add_mobjects(ripples)
        return self._mobjects
    
    def animate(self, scene: Scene) -> None:
        """Animate expanding ripples."""
        ripples = self._mobjects
        scene.add(ripples)
        
        max_radius = self.get_config('max_radius')
        speed = self.get_config('speed')
        lifetime = self.get_config('lifetime')
        num_ripples = self.get_config('num_ripples')
        
        animations = []
        for i, ripple in enumerate(ripples):
            delay = i * lifetime / num_ripples
            
            expand_anim = ripple.animate(
                run_time=lifetime,
                rate_func=linear
            ).scale(max_radius / 0.01)
            
            if self.get_config('fade_out'):
                fade_anim = ripple.animate(
                    run_time=lifetime,
                    rate_func=lambda t: 1 - t
                ).set_stroke(opacity=0)
                
                animations.append(
                    AnimationGroup(
                        expand_anim,
                        fade_anim,
                        lag_ratio=0
                    )
                )
            else:
                animations.append(expand_anim)
        
        scene.play(
            LaggedStart(*animations, lag_ratio=1/num_ripples),
            run_time=lifetime + lifetime/num_ripples
        )


class OceanWaveEffect(BaseEffect):
    """Creates realistic ocean wave animations."""
    
    def __init__(self, width: float = 8, height: float = 2, **kwargs):
        super().__init__()
        self.width = width
        self.height = height
        self.update_config(
            num_waves=kwargs.get('num_waves', 3),
            wave_height=kwargs.get('wave_height', 0.5),
            wave_speed=kwargs.get('wave_speed', 0.5),
            wave_color=kwargs.get('wave_color', BLUE),
            foam_color=kwargs.get('foam_color', WHITE),
            show_foam=kwargs.get('show_foam', True),
            turbulence=kwargs.get('turbulence', 0.1)
        )
        self.time = 0
    
    def create(self) -> VGroup:
        """Create ocean wave layers."""
        waves = VGroup()
        
        num_waves = self.get_config('num_waves')
        for i in range(num_waves):
            z_offset = -i * 0.2
            opacity = 1 - (i * 0.2)
            
            wave = self._create_wave_shape(z_offset)
            wave.set_fill(
                self.get_config('wave_color'),
                opacity=opacity
            )
            wave.set_stroke(width=0)
            
            waves.add(wave)
        
        if self.get_config('show_foam'):
            foam = self._create_foam()
            waves.add(foam)
        
        self.add_mobjects(waves)
        return self._mobjects
    
    def _create_wave_shape(self, z_offset: float = 0) -> VMobject:
        """Create a single wave shape."""
        wave_func = lambda x: self.get_config('wave_height') * np.sin(2 * PI * x / 2)
        
        wave = ParametricFunction(
            lambda t: np.array([t, wave_func(t), z_offset]),
            t_range=[-self.width/2, self.width/2],
            fill_opacity=1
        )
        
        # Close the shape to make it fillable
        bottom_left = np.array([-self.width/2, -self.height/2, z_offset])
        bottom_right = np.array([self.width/2, -self.height/2, z_offset])
        
        wave.add_points_as_corners([bottom_right, bottom_left])
        wave.close_path()
        
        return wave
    
    def _create_foam(self) -> VGroup:
        """Create foam on wave crests."""
        foam = VGroup()
        
        for x in np.linspace(-self.width/2, self.width/2, 20):
            if np.random.random() < 0.3:
                bubble = Circle(
                    radius=np.random.uniform(0.02, 0.05),
                    color=self.get_config('foam_color')
                )
                bubble.set_fill(opacity=0.8)
                bubble.set_stroke(width=0)
                foam.add(bubble)
        
        return foam
    
    def animate(self, scene: Scene) -> None:
        """Animate ocean waves."""
        waves = self._mobjects
        scene.add(waves)
        
        def wave_updater(mob, dt):
            self.time += dt
            speed = self.get_config('wave_speed')
            turbulence = self.get_config('turbulence')
            
            for i, wave in enumerate(mob[:-1] if self.get_config('show_foam') else mob):
                phase = i * PI / 3
                
                def wave_func(x):
                    base_wave = self.get_config('wave_height') * np.sin(
                        2 * PI * (x / 2 - speed * self.time) + phase
                    )
                    if turbulence > 0:
                        noise = turbulence * np.sin(5 * x + 10 * self.time)
                        base_wave += noise
                    return base_wave
                
                new_wave = ParametricFunction(
                    lambda t: np.array([t, wave_func(t), -i * 0.2]),
                    t_range=[-self.width/2, self.width/2]
                )
                
                bottom_left = np.array([-self.width/2, -self.height/2, -i * 0.2])
                bottom_right = np.array([self.width/2, -self.height/2, -i * 0.2])
                new_wave.add_points_as_corners([bottom_right, bottom_left])
                new_wave.close_path()
                
                wave.set_points(new_wave.get_points())
        
        waves.add_updater(wave_updater)


class ShockwaveEffect(BaseEffect):
    """Creates a shockwave effect from an impact point."""
    
    def __init__(self, impact_point: np.ndarray = ORIGIN, **kwargs):
        super().__init__()
        self.impact_point = impact_point
        self.update_config(
            shockwave_radius=kwargs.get('shockwave_radius', 4.0),
            shockwave_color=kwargs.get('shockwave_color', WHITE),
            distortion_strength=kwargs.get('distortion_strength', 0.5),
            propagation_time=kwargs.get('propagation_time', 1.5),
            num_rings=kwargs.get('num_rings', 3),
            affect_objects=kwargs.get('affect_objects', [])
        )
    
    def create(self) -> VGroup:
        """Create shockwave rings."""
        shockwave = VGroup()
        
        for i in range(self.get_config('num_rings')):
            ring = Circle(
                radius=0.01,
                color=self.get_config('shockwave_color'),
                stroke_width=8 - i * 2
            )
            ring.move_to(self.impact_point)
            shockwave.add(ring)
        
        self.add_mobjects(shockwave)
        return self._mobjects
    
    def animate(self, scene: Scene) -> None:
        """Animate the shockwave propagation."""
        shockwave_rings = self._mobjects
        scene.add(shockwave_rings)
        
        max_radius = self.get_config('shockwave_radius')
        propagation_time = self.get_config('propagation_time')
        affect_objects = self.get_config('affect_objects')
        
        # Animate rings
        ring_animations = []
        for i, ring in enumerate(shockwave_rings):
            delay = i * 0.1
            
            ring_animations.append(
                AnimationGroup(
                    ring.animate(
                        run_time=propagation_time - delay,
                        rate_func=rush_from
                    ).scale(max_radius / 0.01),
                    ring.animate(
                        run_time=propagation_time - delay,
                        rate_func=lambda t: 1 - smooth(t)
                    ).set_stroke(opacity=0),
                    lag_ratio=0
                )
            )
        
        # Apply distortion to affected objects
        if affect_objects:
            distortion_anims = []
            for obj in affect_objects:
                distance = np.linalg.norm(obj.get_center() - self.impact_point)
                if distance < max_radius:
                    delay = distance / max_radius * propagation_time * 0.8
                    strength = self.get_config('distortion_strength') * (1 - distance / max_radius)
                    
                    distortion_anims.append(
                        Succession(
                            Wait(delay),
                            obj.animate(
                                run_time=0.3,
                                rate_func=there_and_back
                            ).scale(1 + strength)
                        )
                    )
            
            scene.play(
                LaggedStart(*ring_animations, lag_ratio=0.3),
                *distortion_anims
            )
        else:
            scene.play(
                LaggedStart(*ring_animations, lag_ratio=0.3)
            )


class SoundWaveEffect(BaseEffect):
    """Creates visual representation of sound waves."""
    
    def __init__(self, source: np.ndarray = ORIGIN, **kwargs):
        super().__init__()
        self.source = source
        self.update_config(
            wave_pattern=kwargs.get('wave_pattern', 'circular'),  # 'circular' or 'directional'
            frequency_bands=kwargs.get('frequency_bands', [0.5, 1.0, 2.0]),
            max_amplitude=kwargs.get('max_amplitude', 1.0),
            wave_color=kwargs.get('wave_color', GREEN),
            direction=kwargs.get('direction', RIGHT),
            visualization_style=kwargs.get('visualization_style', 'lines')  # 'lines' or 'bars'
        )
    
    def create(self) -> VGroup:
        """Create sound wave visualization."""
        sound_waves = VGroup()
        
        if self.get_config('wave_pattern') == 'circular':
            for freq in self.get_config('frequency_bands'):
                wave_circle = self._create_circular_wave(freq)
                sound_waves.add(wave_circle)
        else:
            sound_waves = self._create_directional_waves()
        
        self.add_mobjects(sound_waves)
        return self._mobjects
    
    def _create_circular_wave(self, frequency: float) -> VGroup:
        """Create circular sound wave pattern."""
        wave_group = VGroup()
        num_points = 100
        
        for r in np.linspace(0.5, 2.0, 5):
            points = []
            for i in range(num_points):
                theta = 2 * PI * i / num_points
                amplitude = self.get_config('max_amplitude') * 0.1 * np.sin(frequency * 8 * theta)
                radius = r + amplitude
                
                point = self.source + radius * np.array([np.cos(theta), np.sin(theta), 0])
                points.append(point)
            
            wave = VMobject()
            wave.set_points_as_corners(points + [points[0]])
            wave.set_stroke(
                self.get_config('wave_color'),
                width=2,
                opacity=0.8 - 0.15 * r
            )
            wave_group.add(wave)
        
        return wave_group
    
    def _create_directional_waves(self) -> VGroup:
        """Create directional sound wave pattern."""
        waves = VGroup()
        direction = normalize(self.get_config('direction'))
        perpendicular = rotate_vector(direction, PI/2)
        
        if self.get_config('visualization_style') == 'lines':
            for i in range(10):
                x = i * 0.3
                wave_line = ParametricFunction(
                    lambda t: self.source + x * direction + 
                             self.get_config('max_amplitude') * np.sin(2 * PI * t) * perpendicular,
                    t_range=[-1, 1]
                )
                wave_line.set_stroke(
                    self.get_config('wave_color'),
                    width=3,
                    opacity=1 - i * 0.08
                )
                waves.add(wave_line)
        else:  # bars
            for i, freq in enumerate(self.get_config('frequency_bands')):
                for j in range(20):
                    height = self.get_config('max_amplitude') * np.random.uniform(0.2, 1.0)
                    bar = Rectangle(
                        width=0.1,
                        height=height,
                        color=self.get_config('wave_color')
                    )
                    bar.move_to(self.source + (j - 10) * 0.15 * perpendicular + i * 0.5 * direction)
                    bar.set_fill(opacity=0.8)
                    waves.add(bar)
        
        return waves
    
    def animate(self, scene: Scene) -> None:
        """Animate sound waves."""
        waves = self._mobjects
        scene.add(waves)
        
        def sound_updater(mob, dt):
            time = scene.renderer.time
            
            if self.get_config('wave_pattern') == 'circular':
                for wave_group in mob:
                    wave_group.rotate(0.5 * dt, about_point=self.source)
            else:
                if self.get_config('visualization_style') == 'bars':
                    for bar in mob:
                        new_height = self.get_config('max_amplitude') * (
                            0.5 + 0.5 * np.sin(5 * time + bar.get_center()[0])
                        )
                        bar.stretch_to_fit_height(new_height)
        
        waves.add_updater(sound_updater)