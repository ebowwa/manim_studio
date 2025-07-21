"""Skull-themed effects and components for Manim Studio."""

from typing import Optional, List, Tuple
import numpy as np
from manim import *
from .base_effect import BaseEffect


class SkullEffect(BaseEffect):
    """Creates an animated skull with various styles."""
    
    def __init__(self, position: np.ndarray = ORIGIN, **kwargs):
        super().__init__()
        self.position = position
        self.update_config(
            size=kwargs.get('size', 1.0),
            style=kwargs.get('style', 'normal'),  # 'normal', 'cute', 'scary', 'pixelated'
            color=kwargs.get('color', WHITE),
            eye_glow=kwargs.get('eye_glow', False),
            eye_color=kwargs.get('eye_color', RED),
            animate_jaw=kwargs.get('animate_jaw', False),
            floating=kwargs.get('floating', False)
        )
    
    def create(self) -> VGroup:
        """Create the skull shape."""
        skull = VGroup()
        size = self.get_config('size')
        style = self.get_config('style')
        
        if style == 'normal':
            skull = self._create_normal_skull(size)
        elif style == 'cute':
            skull = self._create_cute_skull(size)
        elif style == 'scary':
            skull = self._create_scary_skull(size)
        elif style == 'pixelated':
            skull = self._create_pixelated_skull(size)
        
        skull.move_to(self.position)
        skull.set_color(self.get_config('color'))
        
        if self.get_config('eye_glow'):
            self._add_eye_glow(skull)
        
        self.add_mobjects(skull)
        return self._mobjects
    
    def _create_normal_skull(self, size: float) -> VGroup:
        """Create a normal skull shape."""
        skull = VGroup()
        
        # Main skull shape
        cranium = Circle(radius=size)
        cranium.stretch(1.2, 1)  # Make it slightly taller
        
        # Eye sockets
        left_eye = Circle(radius=size * 0.25)
        left_eye.move_to(LEFT * size * 0.3 + UP * size * 0.2)
        left_eye.set_fill(BLACK, opacity=1)
        
        right_eye = Circle(radius=size * 0.25)
        right_eye.move_to(RIGHT * size * 0.3 + UP * size * 0.2)
        right_eye.set_fill(BLACK, opacity=1)
        
        # Nasal cavity
        nose = Triangle()
        nose.scale(size * 0.2)
        nose.move_to(DOWN * size * 0.1)
        nose.set_fill(BLACK, opacity=1)
        
        # Jaw
        jaw = Rectangle(width=size * 1.5, height=size * 0.6)
        jaw.move_to(DOWN * size * 0.8)
        
        # Teeth
        teeth = VGroup()
        for i in range(6):
            tooth = Rectangle(width=size * 0.15, height=size * 0.25)
            tooth.move_to(
                LEFT * size * 0.6 + RIGHT * i * size * 0.25 + 
                DOWN * size * 0.8
            )
            teeth.add(tooth)
        
        skull.add(cranium, left_eye, right_eye, nose, jaw, teeth)
        return skull
    
    def _create_cute_skull(self, size: float) -> VGroup:
        """Create a cute/kawaii style skull."""
        skull = VGroup()
        
        # Round head
        head = Circle(radius=size)
        
        # Large cute eyes
        left_eye = Circle(radius=size * 0.3)
        left_eye.move_to(LEFT * size * 0.35 + UP * size * 0.1)
        left_eye.set_fill(BLACK, opacity=1)
        
        right_eye = Circle(radius=size * 0.3)
        right_eye.move_to(RIGHT * size * 0.35 + UP * size * 0.1)
        right_eye.set_fill(BLACK, opacity=1)
        
        # Small dot nose (cute style)
        nose = Dot(radius=size * 0.05)
        nose.move_to(DOWN * size * 0.2)
        nose.set_fill(BLACK, opacity=1)
        
        # Cute smile
        smile = Arc(
            start_angle=PI + PI/6,
            angle=-PI/3,
            radius=size * 0.4
        )
        smile.move_to(DOWN * size * 0.5)
        
        skull.add(head, left_eye, right_eye, nose, smile)
        return skull
    
    def _create_scary_skull(self, size: float) -> VGroup:
        """Create a scary/horror style skull."""
        skull = VGroup()
        
        # Distorted cranium
        cranium = Circle(radius=size)
        cranium.apply_function(
            lambda p: p + 0.1 * size * np.array([
                np.sin(5 * np.arctan2(p[1], p[0])),
                np.cos(5 * np.arctan2(p[1], p[0])),
                0
            ])
        )
        
        # Hollow eyes with cracks
        left_eye = Circle(radius=size * 0.3)
        left_eye.move_to(LEFT * size * 0.3 + UP * size * 0.15)
        left_eye.set_fill(BLACK, opacity=1)
        
        left_crack = Line(
            left_eye.get_center() + UP * size * 0.3,
            left_eye.get_center() + UP * size * 0.6
        )
        left_crack.set_stroke(width=2)
        
        right_eye = Circle(radius=size * 0.3)
        right_eye.move_to(RIGHT * size * 0.3 + UP * size * 0.15)
        right_eye.set_fill(BLACK, opacity=1)
        
        # Jagged nose hole
        nose = Polygon(
            ORIGIN,
            LEFT * size * 0.1 + UP * size * 0.1,
            UP * size * 0.2,
            RIGHT * size * 0.1 + UP * size * 0.1
        )
        nose.move_to(DOWN * size * 0.15)
        nose.set_fill(BLACK, opacity=1)
        
        # Menacing jaw with sharp teeth
        jaw = VGroup()
        for i in range(8):
            tooth = Triangle()
            tooth.scale(size * 0.15)
            tooth.move_to(
                LEFT * size * 0.7 + RIGHT * i * size * 0.2 + 
                DOWN * size * 0.7
            )
            if i % 2 == 0:
                tooth.rotate(PI)
            jaw.add(tooth)
        
        skull.add(cranium, left_eye, left_crack, right_eye, nose, jaw)
        return skull
    
    def _create_pixelated_skull(self, size: float) -> VGroup:
        """Create a pixelated/8-bit style skull."""
        skull = VGroup()
        pixel_size = size * 0.1
        
        # Define skull pattern (1 = filled, 0 = empty)
        pattern = [
            [0,0,1,1,1,1,0,0],
            [0,1,1,1,1,1,1,0],
            [1,1,0,1,1,0,1,1],
            [1,1,0,1,1,0,1,1],
            [1,1,1,0,0,1,1,1],
            [0,1,1,1,1,1,1,0],
            [0,1,0,1,0,1,0,0],
            [0,1,1,1,1,1,0,0]
        ]
        
        for i, row in enumerate(pattern):
            for j, pixel in enumerate(row):
                if pixel == 1:
                    square = Square(side_length=pixel_size)
                    square.move_to(
                        LEFT * size + RIGHT * j * pixel_size + 
                        UP * size - DOWN * i * pixel_size
                    )
                    square.set_fill(self.get_config('color'), opacity=1)
                    square.set_stroke(width=0)
                    skull.add(square)
        
        skull.move_to(ORIGIN)  # Re-center
        return skull
    
    def _add_eye_glow(self, skull: VGroup) -> None:
        """Add glowing effect to eye sockets."""
        eye_color = self.get_config('eye_color')
        
        # Find eye shapes (assumes they're circles filled with black)
        for mob in skull:
            if isinstance(mob, Circle) and mob.get_fill_color() == BLACK:
                # Add glow
                glow = Circle(radius=mob.get_radius() * 0.3)
                glow.move_to(mob.get_center())
                glow.set_fill(eye_color, opacity=0.8)
                glow.set_stroke(eye_color, width=2, opacity=0.6)
                skull.add(glow)
    
    def animate(self, scene: Scene) -> None:
        """Animate the skull."""
        skull = self._mobjects[0]
        scene.add(skull)
        
        if self.get_config('animate_jaw'):
            # Animate jaw movement
            jaw_parts = [mob for mob in skull if isinstance(mob, (Rectangle, Triangle))]
            if jaw_parts:
                def jaw_updater(mob, dt):
                    time = scene.renderer.time
                    offset = 0.1 * self.get_config('size') * np.sin(2 * time)
                    for part in jaw_parts:
                        if part.get_center()[1] < self.position[1]:  # Lower parts
                            part.shift(DOWN * offset * dt)
                
                skull.add_updater(jaw_updater)
        
        if self.get_config('floating'):
            # Add floating animation
            def float_updater(mob, dt):
                time = scene.renderer.time
                mob.shift(UP * 0.02 * np.sin(time) * dt)
            
            skull.add_updater(float_updater)


class SkullParticleEffect(BaseEffect):
    """Creates particle effects that form into a skull shape."""
    
    def __init__(self, position: np.ndarray = ORIGIN, **kwargs):
        super().__init__()
        self.position = position
        self.update_config(
            num_particles=kwargs.get('num_particles', 500),
            particle_size=kwargs.get('particle_size', 0.02),
            formation_time=kwargs.get('formation_time', 3.0),
            particle_color=kwargs.get('particle_color', WHITE),
            glow=kwargs.get('glow', True),
            disperse_after=kwargs.get('disperse_after', False)
        )
    
    def create(self) -> VGroup:
        """Create particles that will form a skull."""
        particles = VGroup()
        num_particles = self.get_config('num_particles')
        
        # Create skull outline points
        skull_points = self._generate_skull_points(num_particles)
        
        # Create particles at random starting positions
        for i, target_point in enumerate(skull_points):
            # Random starting position
            start_angle = np.random.uniform(0, 2 * PI)
            start_radius = np.random.uniform(3, 5)
            start_pos = self.position + start_radius * np.array([
                np.cos(start_angle),
                np.sin(start_angle),
                0
            ])
            
            particle = Dot(
                point=start_pos,
                radius=self.get_config('particle_size'),
                color=self.get_config('particle_color')
            )
            
            if self.get_config('glow'):
                particle.set_glow_factor(0.5)
            
            # Store target position
            particle.target_position = target_point + self.position
            particles.add(particle)
        
        self.add_mobjects(particles)
        return self._mobjects
    
    def _generate_skull_points(self, num_points: int) -> List[np.ndarray]:
        """Generate points that outline a skull shape."""
        points = []
        
        # Cranium (circle)
        cranium_points = int(num_points * 0.4)
        for i in range(cranium_points):
            angle = 2 * PI * i / cranium_points
            if angle < PI:  # Upper half
                radius = 1.0
            else:  # Lower half slightly narrower
                radius = 0.9
            point = radius * np.array([np.cos(angle), np.sin(angle), 0])
            points.append(point)
        
        # Eye sockets
        eye_points = int(num_points * 0.2)
        for i in range(eye_points // 2):
            # Left eye
            angle = 2 * PI * i / (eye_points // 2)
            left_eye = 0.25 * np.array([np.cos(angle), np.sin(angle), 0])
            left_eye += np.array([-0.3, 0.2, 0])
            points.append(left_eye)
            
            # Right eye
            right_eye = 0.25 * np.array([np.cos(angle), np.sin(angle), 0])
            right_eye += np.array([0.3, 0.2, 0])
            points.append(right_eye)
        
        # Nose
        nose_points = int(num_points * 0.1)
        for i in range(nose_points):
            t = i / nose_points
            # Triangle shape
            if t < 0.5:
                point = np.array([-0.1 + 0.2 * t, -0.1 - 0.1 * t, 0])
            else:
                point = np.array([0.1 * (t - 0.5) * 2, -0.2 + 0.1 * (t - 0.5) * 2, 0])
            points.append(point)
        
        # Jaw and teeth
        jaw_points = int(num_points * 0.3)
        for i in range(jaw_points):
            x = -0.7 + 1.4 * i / jaw_points
            if i % 4 < 2:  # Create teeth pattern
                y = -0.8
            else:
                y = -0.6
            points.append(np.array([x, y, 0]))
        
        return points
    
    def animate(self, scene: Scene) -> None:
        """Animate particles forming into skull shape."""
        particles = self._mobjects[0]
        scene.add(particles)
        
        # Animate formation
        formation_anims = []
        for particle in particles:
            formation_anims.append(
                particle.animate.move_to(particle.target_position)
            )
        
        scene.play(
            *formation_anims,
            run_time=self.get_config('formation_time'),
            rate_func=smooth
        )
        
        if self.get_config('disperse_after'):
            scene.wait(2)
            
            # Disperse particles
            disperse_anims = []
            for particle in particles:
                direction = normalize(particle.get_center() - self.position)
                if np.linalg.norm(direction) < 0.01:
                    direction = normalize(np.random.randn(3))
                
                target = particle.get_center() + direction * 5 * np.random.uniform(0.5, 1.5)
                disperse_anims.append(
                    particle.animate.move_to(target).set_opacity(0)
                )
            
            scene.play(
                *disperse_anims,
                run_time=2,
                rate_func=rush_into
            )


class GhostlySkullEffect(BaseEffect):
    """Creates a ghostly, semi-transparent skull that fades in and out."""
    
    def __init__(self, position: np.ndarray = ORIGIN, **kwargs):
        super().__init__()
        self.position = position
        self.update_config(
            size=kwargs.get('size', 1.5),
            base_opacity=kwargs.get('base_opacity', 0.3),
            fade_cycle_time=kwargs.get('fade_cycle_time', 4.0),
            distortion=kwargs.get('distortion', True),
            color=kwargs.get('color', BLUE_E),
            num_layers=kwargs.get('num_layers', 3)
        )
    
    def create(self) -> VGroup:
        """Create ghostly skull layers."""
        ghost_skull = VGroup()
        
        base_skull = SkullEffect(
            position=self.position,
            size=self.get_config('size'),
            style='scary',
            color=self.get_config('color')
        ).create()
        
        # Create multiple semi-transparent layers
        for i in range(self.get_config('num_layers')):
            layer = base_skull.copy()
            layer.set_fill(opacity=self.get_config('base_opacity') / (i + 1))
            layer.set_stroke(opacity=self.get_config('base_opacity') / (i + 1))
            layer.scale(1 + i * 0.1)
            
            if self.get_config('distortion'):
                # Apply wave distortion
                layer.apply_function(
                    lambda p: p + 0.05 * np.array([
                        np.sin(3 * p[1]),
                        np.cos(3 * p[0]),
                        0
                    ])
                )
            
            ghost_skull.add(layer)
        
        self.add_mobjects(ghost_skull)
        return self._mobjects
    
    def animate(self, scene: Scene) -> None:
        """Animate ghostly appearance."""
        ghost_skull = self._mobjects[0]
        scene.add(ghost_skull)
        
        cycle_time = self.get_config('fade_cycle_time')
        base_opacity = self.get_config('base_opacity')
        
        def ghost_updater(mob, dt):
            time = scene.renderer.time
            
            # Fade in and out
            opacity_factor = (np.sin(2 * PI * time / cycle_time) + 1) / 2
            
            for i, layer in enumerate(mob):
                layer.set_fill(opacity=base_opacity * opacity_factor / (i + 1))
                layer.set_stroke(opacity=base_opacity * opacity_factor / (i + 1))
                
                # Slight rotation for ethereal effect
                layer.rotate(0.1 * dt * (i + 1), about_point=self.position)
                
                # Vertical drift
                layer.shift(UP * 0.01 * np.sin(time + i) * dt)
        
        ghost_skull.add_updater(ghost_updater)


class SkullTransformEffect(BaseEffect):
    """Transforms objects into skull shapes."""
    
    def __init__(self, source_object: Mobject, **kwargs):
        super().__init__()
        self.source_object = source_object
        self.update_config(
            skull_size=kwargs.get('skull_size', 1.0),
            skull_style=kwargs.get('skull_style', 'normal'),
            transform_time=kwargs.get('transform_time', 2.0),
            intermediate_shapes=kwargs.get('intermediate_shapes', True),
            final_color=kwargs.get('final_color', WHITE)
        )
    
    def create(self) -> VGroup:
        """Create the transformation elements."""
        transform_group = VGroup()
        
        # Start with source object
        start_obj = self.source_object.copy()
        transform_group.add(start_obj)
        
        # Create target skull
        self.target_skull = SkullEffect(
            position=self.source_object.get_center(),
            size=self.get_config('skull_size'),
            style=self.get_config('skull_style'),
            color=self.get_config('final_color')
        ).create()
        
        self.add_mobjects(transform_group)
        return self._mobjects
    
    def animate(self, scene: Scene) -> None:
        """Animate transformation to skull."""
        transform_obj = self._mobjects[0][0]
        scene.add(transform_obj)
        
        if self.get_config('intermediate_shapes'):
            # Create intermediate morph stages
            intermediate = self._create_intermediate_shape()
            
            scene.play(
                Transform(transform_obj, intermediate),
                run_time=self.get_config('transform_time') / 2
            )
            scene.play(
                Transform(transform_obj, self.target_skull),
                run_time=self.get_config('transform_time') / 2
            )
        else:
            scene.play(
                Transform(transform_obj, self.target_skull),
                run_time=self.get_config('transform_time')
            )
    
    def _create_intermediate_shape(self) -> VGroup:
        """Create an intermediate shape between source and skull."""
        intermediate = VGroup()
        
        # Blend between source and skull shapes
        source_center = self.source_object.get_center()
        
        # Create a distorted circular shape
        circle = Circle(radius=self.get_config('skull_size'))
        circle.move_to(source_center)
        circle.apply_function(
            lambda p: p + 0.2 * np.array([
                np.sin(4 * np.arctan2(p[1] - source_center[1], p[0] - source_center[0])),
                np.cos(4 * np.arctan2(p[1] - source_center[1], p[0] - source_center[0])),
                0
            ])
        )
        
        # Add some hole-like features
        holes = VGroup()
        for offset in [LEFT * 0.3 + UP * 0.2, RIGHT * 0.3 + UP * 0.2, DOWN * 0.1]:
            hole = Circle(radius=0.2)
            hole.move_to(source_center + offset * self.get_config('skull_size'))
            hole.set_fill(BLACK, opacity=1)
            holes.add(hole)
        
        intermediate.add(circle, holes)
        intermediate.set_color(
            interpolate_color(
                self.source_object.get_color(),
                self.get_config('final_color'),
                0.5
            )
        )
        
        return intermediate