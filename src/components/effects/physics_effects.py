"""Physics-based effects for Manim Studio."""
from manim import *
from typing import Dict, Any, Callable
import numpy as np


class GravityEffect:
    """Apply gravity to objects."""
    
    @staticmethod
    def create(scene: Scene, target: Mobject, properties: Dict[str, Any]) -> Callable:
        """Create a gravity effect updater."""
        gravity = properties.get('gravity', 9.8)
        initial_velocity = np.array(properties.get('initial_velocity', [0, 0, 0]))
        bounce_damping = properties.get('bounce_damping', 0.8)
        ground_level = properties.get('ground_level', -3)
        
        # Initialize velocity
        if not hasattr(target, '_velocity'):
            target._velocity = initial_velocity.copy()
            
        def updater(mob, dt):
            # Update velocity
            mob._velocity[1] -= gravity * dt
            
            # Update position
            new_pos = mob.get_center() + mob._velocity * dt
            
            # Check ground collision
            if new_pos[1] <= ground_level:
                new_pos[1] = ground_level
                mob._velocity[1] = -mob._velocity[1] * bounce_damping
                
            mob.move_to(new_pos)
            
        return updater


class OscillationEffect:
    """Create oscillating motion."""
    
    @staticmethod
    def create(scene: Scene, target: Mobject, properties: Dict[str, Any]) -> Callable:
        """Create an oscillation effect updater."""
        amplitude = properties.get('amplitude', 1.0)
        frequency = properties.get('frequency', 1.0)
        axis = np.array(properties.get('axis', [1, 0, 0]))
        center = target.get_center().copy()
        
        # Track time
        if not hasattr(target, '_oscillation_time'):
            target._oscillation_time = 0
            
        def updater(mob, dt):
            mob._oscillation_time += dt
            offset = amplitude * np.sin(2 * PI * frequency * mob._oscillation_time) * axis
            mob.move_to(center + offset)
            
        return updater


class SpringForceEffect:
    """Apply spring force to objects."""
    
    @staticmethod
    def create(scene: Scene, target: Mobject, properties: Dict[str, Any]) -> Callable:
        """Create a spring force effect."""
        anchor_point = np.array(properties.get('anchor_point', [0, 0, 0]))
        spring_constant = properties.get('spring_constant', 5.0)
        damping = properties.get('damping', 0.1)
        mass = properties.get('mass', 1.0)
        
        # Initialize physics state
        if not hasattr(target, '_velocity'):
            target._velocity = np.array([0., 0., 0.])
            
        def updater(mob, dt):
            # Calculate displacement from anchor
            displacement = mob.get_center() - anchor_point
            
            # Spring force: F = -kx - cv
            force = -spring_constant * displacement - damping * mob._velocity
            
            # Update velocity: a = F/m
            acceleration = force / mass
            mob._velocity += acceleration * dt
            
            # Update position
            new_pos = mob.get_center() + mob._velocity * dt
            mob.move_to(new_pos)
            
        return updater


class CircularOrbitEffect:
    """Create circular orbital motion."""
    
    @staticmethod
    def create(scene: Scene, target: Mobject, properties: Dict[str, Any]) -> Callable:
        """Create a circular orbit effect."""
        center = np.array(properties.get('center', [0, 0, 0]))
        radius = properties.get('radius', 2.0)
        angular_velocity = properties.get('angular_velocity', 1.0)
        plane = properties.get('plane', 'xy')  # 'xy', 'xz', or 'yz'
        
        # Initialize angle
        if not hasattr(target, '_orbit_angle'):
            # Calculate initial angle from current position
            rel_pos = target.get_center() - center
            if plane == 'xy':
                target._orbit_angle = np.arctan2(rel_pos[1], rel_pos[0])
            elif plane == 'xz':
                target._orbit_angle = np.arctan2(rel_pos[2], rel_pos[0])
            else:  # yz
                target._orbit_angle = np.arctan2(rel_pos[2], rel_pos[1])
                
        def updater(mob, dt):
            mob._orbit_angle += angular_velocity * dt
            
            if plane == 'xy':
                offset = radius * np.array([
                    np.cos(mob._orbit_angle),
                    np.sin(mob._orbit_angle),
                    0
                ])
            elif plane == 'xz':
                offset = radius * np.array([
                    np.cos(mob._orbit_angle),
                    0,
                    np.sin(mob._orbit_angle)
                ])
            else:  # yz
                offset = radius * np.array([
                    0,
                    np.cos(mob._orbit_angle),
                    np.sin(mob._orbit_angle)
                ])
                
            mob.move_to(center + offset)
            
        return updater


class WaveMotionEffect:
    """Create wave-like motion."""
    
    @staticmethod
    def create(scene: Scene, target: Mobject, properties: Dict[str, Any]) -> Callable:
        """Create a wave motion effect."""
        wavelength = properties.get('wavelength', 2.0)
        amplitude = properties.get('amplitude', 0.5)
        speed = properties.get('speed', 1.0)
        direction = np.array(properties.get('direction', [1, 0, 0]))
        
        # Normalize direction
        direction = direction / np.linalg.norm(direction)
        
        # Get perpendicular direction for wave oscillation
        if abs(direction[0]) < 0.9:
            perp = np.cross(direction, np.array([1, 0, 0]))
        else:
            perp = np.cross(direction, np.array([0, 1, 0]))
        perp = perp / np.linalg.norm(perp)
        
        # Initialize position
        if not hasattr(target, '_wave_distance'):
            target._wave_distance = 0
            target._wave_center = target.get_center().copy()
            
        def updater(mob, dt):
            mob._wave_distance += speed * dt
            
            # Calculate wave offset
            phase = 2 * PI * mob._wave_distance / wavelength
            offset = amplitude * np.sin(phase) * perp
            
            # Move along direction with wave offset
            new_pos = mob._wave_center + mob._wave_distance * direction + offset
            mob.move_to(new_pos)
            
        return updater


# Registry for physics effects
PHYSICS_EFFECTS = {
    'gravity': GravityEffect,
    'oscillation': OscillationEffect,
    'spring_force': SpringForceEffect,
    'circular_orbit': CircularOrbitEffect,
    'wave_motion': WaveMotionEffect,
}