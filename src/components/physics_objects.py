"""Minimal physics components for Manim Studio."""
from manim import *
import numpy as np
from typing import Dict, Any, Optional, Callable


class SimplePendulum(VGroup):
    """A simple pendulum with basic physics simulation."""
    
    def __init__(
        self,
        length: float = 2.0,
        angle: float = PI/6,
        gravity: float = 9.8,
        damping: float = 0.99,
        bob_radius: float = 0.1,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        # Physics parameters
        self.length = length
        self.angle = angle
        self.angular_velocity = 0
        self.gravity = gravity
        self.damping = damping
        
        # Visual components
        self.pivot = Dot(ORIGIN, radius=0.05, color=GRAY)
        self.bob = Dot(radius=bob_radius, color=BLUE)
        self.rod = Line(stroke_width=2)
        
        self.add(self.pivot, self.rod, self.bob)
        self.update_position()
        
    def update_position(self):
        """Update visual position based on angle."""
        bob_pos = self.pivot.get_center() + self.length * np.array([
            np.sin(self.angle),
            -np.cos(self.angle),
            0
        ])
        self.bob.move_to(bob_pos)
        self.rod.put_start_and_end_on(
            self.pivot.get_center(),
            self.bob.get_center()
        )
        
    def physics_step(self, dt: float):
        """Simple pendulum physics update."""
        # Angular acceleration = -(g/L) * sin(theta)
        angular_accel = -(self.gravity / self.length) * np.sin(self.angle)
        
        # Update velocity and position
        self.angular_velocity += angular_accel * dt
        self.angular_velocity *= self.damping  # Apply damping
        self.angle += self.angular_velocity * dt
        
        self.update_position()


class Spring(VGroup):
    """A simple spring with Hooke's law physics."""
    
    def __init__(
        self,
        rest_length: float = 2.0,
        spring_constant: float = 5.0,
        mass: float = 1.0,
        damping: float = 0.1,
        coils: int = 10,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        # Physics parameters
        self.rest_length = rest_length
        self.k = spring_constant
        self.mass = mass
        self.damping = damping
        self.velocity = 0
        self.displacement = 0
        
        # Visual components
        self.anchor = Dot(ORIGIN, radius=0.05, color=GRAY)
        self.weight = Square(side_length=0.3, color=BLUE, fill_opacity=1)
        self.spring_visual = self.create_spring_visual(coils)
        
        self.add(self.anchor, self.spring_visual, self.weight)
        self.update_position()
        
    def create_spring_visual(self, coils: int) -> VMobject:
        """Create a visual representation of a spring."""
        points = []
        for i in range(coils * 4):
            t = i / (coils * 4)
            x = 0.1 * np.sin(2 * PI * coils * t)
            y = -t * self.rest_length
            points.append([x, y, 0])
        return VMobject().set_points_smoothly(points)
        
    def update_position(self):
        """Update visual position based on displacement."""
        stretch = self.rest_length + self.displacement
        self.weight.move_to(self.anchor.get_center() + stretch * DOWN)
        
        # Update spring visual
        self.spring_visual.stretch_to_fit_height(stretch)
        self.spring_visual.move_to(
            (self.anchor.get_center() + self.weight.get_center()) / 2
        )
        
    def physics_step(self, dt: float):
        """Spring physics update using Hooke's law."""
        # F = -kx - cv (spring force + damping)
        force = -self.k * self.displacement - self.damping * self.velocity
        
        # a = F/m
        acceleration = force / self.mass
        
        # Update velocity and position
        self.velocity += acceleration * dt
        self.displacement += self.velocity * dt
        
        self.update_position()


class ProjectileMotion(VGroup):
    """Simple projectile motion visualization."""
    
    def __init__(
        self,
        initial_velocity: np.ndarray = np.array([3, 4, 0]),
        gravity: float = 9.8,
        trail_length: int = 20,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        # Physics
        self.velocity = initial_velocity.copy()
        self.position = np.array([0., 0., 0.])
        self.gravity = gravity
        
        # Visual
        self.projectile = Dot(radius=0.1, color=RED)
        self.trail = TracedPath(
            self.projectile.get_center,
            stroke_opacity=[0, 1],
            stroke_width=2
        )
        
        self.add(self.trail, self.projectile)
        
    def physics_step(self, dt: float):
        """Update projectile position."""
        # Update velocity (only y-component affected by gravity)
        self.velocity[1] -= self.gravity * dt
        
        # Update position
        self.position += self.velocity * dt
        
        # Stop at ground level
        if self.position[1] < 0:
            self.position[1] = 0
            self.velocity = np.array([0., 0., 0.])
            
        self.projectile.move_to(self.position)


def create_physics_updater(obj: VGroup, dt: float = 1/60) -> Callable:
    """Create an updater function for physics objects."""
    def updater(mob, delta_time):
        if hasattr(mob, 'physics_step'):
            mob.physics_step(delta_time or dt)
    return updater


# Physics object registry for YAML integration
PHYSICS_OBJECTS = {
    'pendulum': SimplePendulum,
    'spring': Spring,
    'projectile': ProjectileMotion,
}


def create_physics_object(obj_type: str, properties: Dict[str, Any]) -> VGroup:
    """Factory function to create physics objects from config."""
    if obj_type not in PHYSICS_OBJECTS:
        raise ValueError(f"Unknown physics object type: {obj_type}")
    
    obj_class = PHYSICS_OBJECTS[obj_type]
    return obj_class(**properties)