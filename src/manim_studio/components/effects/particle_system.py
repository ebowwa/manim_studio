"""Advanced particle system for creating dynamic particle effects."""

from typing import List, Tuple, Optional
import numpy as np
from manim import *
from .base_effect import BaseEffect


class Particle(Dot):
    """Individual particle with physics properties."""
    
    def __init__(
        self,
        position: np.ndarray,
        velocity: np.ndarray,
        acceleration: np.ndarray,
        lifetime: float,
        color: str = WHITE,
        radius: float = 0.05
    ):
        """Initialize particle.
        
        Args:
            position: Starting position
            velocity: Initial velocity
            acceleration: Constant acceleration
            lifetime: Time before particle dies
            color: Particle color
            radius: Particle size
        """
        super().__init__(point=position, color=color, radius=radius)
        self.velocity = velocity
        self.acceleration = acceleration
        self.lifetime = lifetime
        self.age = 0.0
    
    def update_physics(self, dt: float) -> bool:
        """Update particle state.
        
        Args:
            dt: Time step
            
        Returns:
            bool: True if particle is still alive
        """
        self.age += dt
        if self.age >= self.lifetime:
            return False
        
        # Update physics
        self.velocity += self.acceleration * dt
        self.shift(self.velocity * dt)
        
        # Fade out near end of life
        remaining_life = 1 - (self.age / self.lifetime)
        self.set_opacity(remaining_life)
        
        return True


class ParticleEmitter:
    """Controls particle emission and behavior."""
    
    def __init__(
        self,
        position: np.ndarray,
        emission_rate: float,
        particle_lifetime: float,
        velocity_range: Tuple[float, float],
        particle_color: str = WHITE,
        particle_radius: float = 0.05
    ):
        """Initialize emitter.
        
        Args:
            position: Emitter position
            emission_rate: Particles per second
            particle_lifetime: How long particles live
            velocity_range: Min/max initial velocity
            particle_color: Color of emitted particles
            particle_radius: Size of particles
        """
        self.position = position
        self.emission_rate = emission_rate
        self.particle_lifetime = particle_lifetime
        self.velocity_range = velocity_range
        self.particle_color = particle_color
        self.particle_radius = particle_radius
        self.time_since_last_emission = 0.0
    
    def emit_particle(self) -> Optional[Particle]:
        """Create a new particle.
        
        Returns:
            Optional[Particle]: New particle or None
        """
        # Random direction
        angle = np.random.uniform(0, TAU)
        speed = np.random.uniform(*self.velocity_range)
        velocity = speed * np.array([
            np.cos(angle),
            np.sin(angle),
            0
        ])
        
        return Particle(
            position=self.position.copy(),
            velocity=velocity,
            acceleration=np.array([0, -1, 0]),  # Basic gravity
            lifetime=self.particle_lifetime,
            color=self.particle_color,
            radius=self.particle_radius
        )
    
    def update(self, dt: float) -> List[Particle]:
        """Update emitter and create new particles.
        
        Args:
            dt: Time step
            
        Returns:
            List[Particle]: Newly created particles
        """
        self.time_since_last_emission += dt
        
        new_particles = []
        
        while self.time_since_last_emission >= 1/self.emission_rate:
            new_particle = self.emit_particle()
            if new_particle:
                new_particles.append(new_particle)
            self.time_since_last_emission -= 1/self.emission_rate
        
        return new_particles


class ParticleSystem(BaseEffect):
    """Advanced particle system with physics and emission control."""
    
    def __init__(
        self,
        n_emitters: int = 1,
        particles_per_second: float = 10,
        particle_lifetime: float = 2.0,
        velocity_range: Tuple[float, float] = (1, 3),
        particle_color: str = BLUE_A,
        particle_radius: float = 0.02,
        **kwargs
    ):
        super().__init__()
        self.update_config(
            n_emitters=n_emitters,
            particles_per_second=particles_per_second,
            particle_lifetime=particle_lifetime,
            velocity_range=velocity_range,
            particle_color=particle_color,
            particle_radius=particle_radius,
            **kwargs
        )
        
        self.emitters: List[ParticleEmitter] = []
        self.particles: List[Particle] = []
        self._setup_emitters()
    
    def _setup_emitters(self) -> None:
        """Initialize particle emitters."""
        n_emitters = self.get_config('n_emitters')
        
        for i in range(n_emitters):
            angle = i * 2 * PI / n_emitters
            position = np.array([np.cos(angle), np.sin(angle), 0])
            
            emitter = ParticleEmitter(
                position=position,
                emission_rate=self.get_config('particles_per_second'),
                particle_lifetime=self.get_config('particle_lifetime'),
                velocity_range=self.get_config('velocity_range'),
                particle_color=self.get_config('particle_color'),
                particle_radius=self.get_config('particle_radius')
            )
            self.emitters.append(emitter)
    
    def create(self) -> VGroup:
        """Create initial particle system state."""
        return self.mobjects
    
    def update_particles(self, dt: float) -> None:
        """Update all particles and emitters."""
        # Update existing particles
        alive_particles = []
        dead_particles = []
        
        for particle in self.particles:
            if particle.update_physics(dt):
                alive_particles.append(particle)
            else:
                dead_particles.append(particle)
        
        # Remove dead particles
        for particle in dead_particles:
            self.remove_mobjects(particle)
        
        self.particles = alive_particles
        
        # Emit new particles
        for emitter in self.emitters:
            new_particles = emitter.update(dt)
            for particle in new_particles:
                self.particles.append(particle)
                self.add_mobjects(particle)
    
    def animate(self, scene: Scene) -> None:
        """Animate the particle system."""
        def updater(mob: VGroup, dt: float):
            self.update_particles(dt)
        
        self.mobjects.add_updater(updater)
        scene.add(self.mobjects)
    
    def cleanup(self) -> None:
        """Clean up particle system resources."""
        self.mobjects.clear_updaters()
        super().cleanup()
