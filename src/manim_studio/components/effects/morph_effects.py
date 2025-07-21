"""Morphing and shape transformation effects for Manim Studio."""

from typing import Union, List, Callable, Optional
from manim import *
from .base_effect import BaseEffect


class MorphEffect(BaseEffect):
    """Morphs between different shapes with customizable interpolation."""
    
    def __init__(self, start_shape: Mobject, end_shape: Mobject, **kwargs):
        super().__init__()
        self.start_shape = start_shape
        self.end_shape = end_shape
        self.update_config(
            morph_time=kwargs.get('morph_time', 2.0),
            path_func=kwargs.get('path_func', straight_path),
            rate_func=kwargs.get('rate_func', smooth),
            color_interpolation=kwargs.get('color_interpolation', True),
            maintain_center=kwargs.get('maintain_center', False)
        )
    
    def create(self) -> VGroup:
        """Create the morphing shape."""
        morph_shape = self.start_shape.copy()
        self.add_mobjects(morph_shape)
        return self._mobjects
    
    def animate(self, scene: Scene) -> None:
        """Animate the morphing effect."""
        morph_shape = self._mobjects[0]
        scene.add(morph_shape)
        
        if self.get_config('maintain_center'):
            center = morph_shape.get_center()
            target = self.end_shape.copy().move_to(center)
        else:
            target = self.end_shape
        
        scene.play(
            Transform(
                morph_shape, 
                target,
                path_func=self.get_config('path_func'),
                rate_func=self.get_config('rate_func'),
                run_time=self.get_config('morph_time')
            )
        )


class ShapeShifterEffect(BaseEffect):
    """Continuously morphs through a sequence of shapes."""
    
    def __init__(self, shapes: List[Mobject], **kwargs):
        super().__init__()
        self.shapes = shapes
        self.update_config(
            cycle=kwargs.get('cycle', True),
            transition_time=kwargs.get('transition_time', 1.5),
            pause_time=kwargs.get('pause_time', 0.5),
            smooth_transitions=kwargs.get('smooth_transitions', True),
            color_flow=kwargs.get('color_flow', True)
        )
    
    def create(self) -> VGroup:
        """Create the initial shape."""
        if not self.shapes:
            raise ValueError("ShapeShifterEffect requires at least one shape")
        
        current_shape = self.shapes[0].copy()
        self.add_mobjects(current_shape)
        return self._mobjects
    
    def animate(self, scene: Scene) -> None:
        """Animate the shape shifting sequence."""
        current_shape = self._mobjects[0]
        scene.add(current_shape)
        
        shapes_to_morph = self.shapes[1:] if len(self.shapes) > 1 else []
        if self.get_config('cycle') and len(shapes_to_morph) > 0:
            shapes_to_morph.append(self.shapes[0])
        
        for next_shape in shapes_to_morph:
            if self.get_config('smooth_transitions'):
                scene.play(
                    Transform(
                        current_shape,
                        next_shape,
                        rate_func=smooth,
                        run_time=self.get_config('transition_time')
                    )
                )
            else:
                scene.play(
                    ReplacementTransform(
                        current_shape,
                        next_shape,
                        run_time=self.get_config('transition_time')
                    )
                )
                current_shape = next_shape
            
            if self.get_config('pause_time') > 0:
                scene.wait(self.get_config('pause_time'))


class LiquidMorphEffect(BaseEffect):
    """Creates a liquid-like morphing effect between shapes."""
    
    def __init__(self, start_shape: Mobject, end_shape: Mobject, **kwargs):
        super().__init__()
        self.start_shape = start_shape
        self.end_shape = end_shape
        self.update_config(
            num_droplets=kwargs.get('num_droplets', 20),
            droplet_size=kwargs.get('droplet_size', 0.1),
            flow_time=kwargs.get('flow_time', 3.0),
            viscosity=kwargs.get('viscosity', 0.5),
            color=kwargs.get('color', BLUE),
            gravity=kwargs.get('gravity', True)
        )
    
    def create(self) -> VGroup:
        """Create liquid droplets for morphing."""
        droplets = VGroup()
        
        # Sample points from start shape
        num_droplets = self.get_config('num_droplets')
        start_points = [
            self.start_shape.point_from_proportion(i / num_droplets)
            for i in range(num_droplets)
        ]
        
        # Create droplets
        for point in start_points:
            droplet = Circle(
                radius=self.get_config('droplet_size'),
                color=self.get_config('color')
            )
            droplet.move_to(point)
            droplet.set_fill(opacity=0.8)
            droplet.set_stroke(width=0)
            droplets.add(droplet)
        
        self.add_mobjects(droplets)
        return self._mobjects
    
    def animate(self, scene: Scene) -> None:
        """Animate liquid morphing."""
        droplets = self._mobjects
        scene.add(droplets)
        
        # Calculate target positions
        num_droplets = len(droplets)
        end_points = [
            self.end_shape.point_from_proportion(i / num_droplets)
            for i in range(num_droplets)
        ]
        
        # Create flowing animations
        animations = []
        viscosity = self.get_config('viscosity')
        
        for i, (droplet, end_point) in enumerate(zip(droplets, end_points)):
            # Add some randomness to make it look more liquid-like
            path = self._create_liquid_path(droplet.get_center(), end_point, i)
            
            animations.append(
                MoveAlongPath(
                    droplet,
                    path,
                    rate_func=lambda t: smooth(t) * (1 - viscosity) + viscosity * t,
                    run_time=self.get_config('flow_time')
                )
            )
        
        scene.play(*animations)
        
        # Merge droplets into final shape
        scene.play(
            Transform(droplets, self.end_shape),
            run_time=1
        )
    
    def _create_liquid_path(self, start: np.ndarray, end: np.ndarray, seed: int) -> VMobject:
        """Create a curved path for liquid-like motion."""
        np.random.seed(seed)
        
        # Add control points for bezier curve
        mid_point = (start + end) / 2
        
        if self.get_config('gravity'):
            # Add downward bias
            mid_point += DOWN * np.random.uniform(0.5, 1.5)
        
        # Add some horizontal randomness
        mid_point += (RIGHT * np.random.uniform(-0.5, 0.5) + 
                      UP * np.random.uniform(-0.3, 0.3))
        
        path = CubicBezier(start, mid_point - 0.5, mid_point + 0.5, end)
        return path


class GeometricMorphEffect(BaseEffect):
    """Morphs shapes through geometric transformations."""
    
    def __init__(self, shape: Mobject, **kwargs):
        super().__init__()
        self.original_shape = shape
        self.update_config(
            transformations=kwargs.get('transformations', ['rotate', 'scale', 'shear']),
            num_steps=kwargs.get('num_steps', 5),
            step_time=kwargs.get('step_time', 0.5),
            return_to_original=kwargs.get('return_to_original', True),
            randomize=kwargs.get('randomize', False)
        )
    
    def create(self) -> VGroup:
        """Create the shape for transformation."""
        shape = self.original_shape.copy()
        self.add_mobjects(shape)
        return self._mobjects
    
    def animate(self, scene: Scene) -> None:
        """Animate geometric transformations."""
        shape = self._mobjects[0]
        scene.add(shape)
        
        transformations = self.get_config('transformations')
        num_steps = self.get_config('num_steps')
        step_time = self.get_config('step_time')
        
        for _ in range(num_steps):
            if self.get_config('randomize'):
                transform = np.random.choice(transformations)
            else:
                transform = transformations[_ % len(transformations)]
            
            animation = self._get_transformation_animation(shape, transform)
            scene.play(animation, run_time=step_time)
        
        if self.get_config('return_to_original'):
            scene.play(
                Transform(shape, self.original_shape),
                run_time=step_time * 2
            )
    
    def _get_transformation_animation(self, shape: Mobject, transform_type: str) -> Animation:
        """Get animation for specific transformation type."""
        if transform_type == 'rotate':
            return Rotate(shape, angle=PI/4, rate_func=there_and_back)
        elif transform_type == 'scale':
            return shape.animate.scale(1.5).scale(1/1.5)
        elif transform_type == 'shear':
            return ApplyMatrix(
                [[1, 0.5, 0], [0, 1, 0], [0, 0, 1]],
                shape,
                rate_func=there_and_back
            )
        elif transform_type == 'stretch':
            return shape.animate.stretch(2, 0).stretch(0.5, 0)
        else:
            return Wait(0.1)


class ParticleMorphEffect(BaseEffect):
    """Morphs shapes by breaking them into particles and reassembling."""
    
    def __init__(self, start_shape: Mobject, end_shape: Mobject, **kwargs):
        super().__init__()
        self.start_shape = start_shape
        self.end_shape = end_shape
        self.update_config(
            num_particles=kwargs.get('num_particles', 100),
            particle_size=kwargs.get('particle_size', 0.05),
            explosion_radius=kwargs.get('explosion_radius', 2.0),
            assembly_time=kwargs.get('assembly_time', 2.0),
            particle_color=kwargs.get('particle_color', None),
            glow=kwargs.get('glow', True)
        )
    
    def create(self) -> VGroup:
        """Create particles from the start shape."""
        particles = VGroup()
        num_particles = self.get_config('num_particles')
        
        # Sample points from start shape
        for i in range(num_particles):
            t = i / num_particles
            point = self.start_shape.point_from_proportion(t)
            
            particle = Dot(
                point=point,
                radius=self.get_config('particle_size'),
                color=self.get_config('particle_color') or self.start_shape.get_color()
            )
            
            if self.get_config('glow'):
                particle.set_glow_factor(0.8)
            
            particles.add(particle)
        
        self.add_mobjects(particles)
        return self._mobjects
    
    def animate(self, scene: Scene) -> None:
        """Animate particle explosion and reassembly."""
        particles = self._mobjects
        scene.add(self.start_shape)
        scene.wait(0.5)
        
        # Replace shape with particles
        scene.play(
            FadeOut(self.start_shape, scale=0.5),
            FadeIn(particles, scale=2),
            run_time=0.5
        )
        
        # Explode particles
        explosion_radius = self.get_config('explosion_radius')
        explosion_anims = []
        
        for particle in particles:
            direction = normalize(particle.get_center() - self.start_shape.get_center())
            if np.linalg.norm(direction) < 0.01:
                direction = normalize(np.random.randn(3))
            
            target_pos = particle.get_center() + direction * explosion_radius * np.random.uniform(0.5, 1.5)
            explosion_anims.append(
                particle.animate.move_to(target_pos)
            )
        
        scene.play(*explosion_anims, run_time=1)
        
        # Reassemble into end shape
        num_particles = len(particles)
        assembly_anims = []
        
        for i, particle in enumerate(particles):
            t = i / num_particles
            target_point = self.end_shape.point_from_proportion(t)
            assembly_anims.append(
                particle.animate.move_to(target_point)
            )
        
        scene.play(
            *assembly_anims,
            run_time=self.get_config('assembly_time')
        )
        
        # Replace particles with final shape
        scene.play(
            FadeOut(particles),
            FadeIn(self.end_shape),
            run_time=0.5
        )