"""Advanced transition effects system."""

from typing import List, Tuple, Optional, Any, Sequence
import numpy as np
from manim import *
from .base_effect import BaseEffect
from .particle_system import ParticleSystem


class EffectTransitions(BaseEffect):
    """Advanced transition effects for scene changes."""
    
    DEFAULT_CONFIG = {
        'duration': 1.0,
        'direction': RIGHT,
        'particles_enabled': True,
        'color_scheme': BLUE,
    }
    
    def __init__(self, **kwargs):
        super().__init__()
        self._config = self.DEFAULT_CONFIG.copy()
        self.update_config(**kwargs)
    
    def create(self) -> VGroup:
        """Create transition elements."""
        return self._mobjects
    
    def animate(self, scene: Scene) -> None:
        """Main animation method (not used directly)."""
        pass
    
    def transition_scenes(
        self,
        scene: Scene,
        old_mobjects: Sequence[Mobject],
        new_mobjects: Sequence[Mobject],
        style: str = "fade"
    ) -> None:
        """Execute a transition between scenes.
        
        Args:
            scene: The scene to animate on
            old_mobjects: Current scene elements to transition out
            new_mobjects: New scene elements to transition in
            style: Transition style ("fade", "slide", "morph", "dissolve", "magical")
        """
        # Ensure mobjects are in lists
        if not isinstance(old_mobjects, (list, tuple)):
            old_mobjects = [old_mobjects]
        if not isinstance(new_mobjects, (list, tuple)):
            new_mobjects = [new_mobjects]
        
        if style == "fade":
            self._fade_transition(scene, old_mobjects, new_mobjects)
        elif style == "slide":
            self._slide_transition(scene, old_mobjects, new_mobjects)
        elif style == "morph":
            self._morph_transition(scene, old_mobjects, new_mobjects)
        elif style == "dissolve":
            self._dissolve_transition(scene, old_mobjects, new_mobjects)
        elif style == "magical":
            self._magical_transition(scene, old_mobjects, new_mobjects)
    
    def _fade_transition(
        self,
        scene: Scene,
        old_mobjects: Sequence[Mobject],
        new_mobjects: Sequence[Mobject]
    ) -> None:
        """Smooth fade transition with optional particles."""
        duration = self.get_config('duration')
        
        if self.get_config('particles_enabled'):
            particles = ParticleSystem(
                n_emitters=5,
                particles_per_second=20,
                particle_lifetime=duration/2,
                particle_color=self.get_config('color_scheme')
            )
            particles.animate(scene)
        
        scene.play(
            *[FadeOut(mob, shift=UP*0.3) for mob in old_mobjects],
            *[FadeIn(mob.set_opacity(0), shift=DOWN*0.3) for mob in new_mobjects],
            rate_func=smooth,
            run_time=duration
        )
        
        if self.get_config('particles_enabled'):
            particles.cleanup()
    
    def _slide_transition(
        self,
        scene: Scene,
        old_mobjects: Sequence[Mobject],
        new_mobjects: Sequence[Mobject]
    ) -> None:
        """Smooth slide transition with direction."""
        direction = self.get_config('direction')
        duration = self.get_config('duration')
        
        # Position new mobjects off-screen
        for mob in new_mobjects:
            mob.shift(-direction * scene.camera.frame_width)
        
        scene.play(
            *[mob.animate.shift(direction * scene.camera.frame_width) 
              for mob in old_mobjects],
            *[mob.animate.shift(direction * scene.camera.frame_width) 
              for mob in new_mobjects],
            rate_func=smooth,
            run_time=duration
        )
    
    def _morph_transition(
        self,
        scene: Scene,
        old_mobjects: Sequence[Mobject],
        new_mobjects: Sequence[Mobject]
    ) -> None:
        """Morphing transition between similar shapes."""
        duration = self.get_config('duration')
        
        if len(old_mobjects) != len(new_mobjects):
            raise ValueError("Morph transition requires equal number of old and new mobjects")
        
        transforms = []
        for old_mob, new_mob in zip(old_mobjects, new_mobjects):
            transforms.append(Transform(old_mob, new_mob))
        
        scene.play(
            *transforms,
            rate_func=smooth,
            run_time=duration
        )
    
    def _dissolve_transition(
        self,
        scene: Scene,
        old_mobjects: Sequence[Mobject],
        new_mobjects: Sequence[Mobject]
    ) -> None:
        """Particle dissolution effect transition."""
        duration = self.get_config('duration')
        
        # Create particle systems for each old mobject
        particle_systems = []
        for mob in old_mobjects:
            particles = ParticleSystem(
                n_emitters=20,
                particles_per_second=30,
                particle_lifetime=duration/2,
                particle_color=mob.color
            )
            
            # Position emitters along the mobject
            for i, emitter in enumerate(particles.emitters):
                point = mob.point_from_proportion(i/len(particles.emitters))
                emitter.position = point
            
            particle_systems.append(particles)
            particles.animate(scene)
        
        scene.play(
            *[FadeOut(mob) for mob in old_mobjects],
            run_time=duration/2
        )
        
        scene.play(
            *[FadeIn(mob) for mob in new_mobjects],
            run_time=duration/2
        )
        
        for particles in particle_systems:
            particles.cleanup()
    
    def _magical_transition(
        self,
        scene: Scene,
        old_mobjects: Sequence[Mobject],
        new_mobjects: Sequence[Mobject]
    ) -> None:
        """Magical effect transition with glows and particles."""
        duration = self.get_config('duration')
        
        # Create magical circle effect
        from .magical_circle import MagicalCircle
        circle = MagicalCircle(
            radius=max(
                max(mob.get_width() for mob in old_mobjects),
                max(mob.get_width() for mob in new_mobjects)
            ) * 0.7
        )
        
        # Create particle effects
        particles = ParticleSystem(
            n_emitters=8,
            particles_per_second=40,
            particle_lifetime=duration/3,
            particle_color=self.get_config('color_scheme')
        )
        
        # Animate transition
        circle.create()
        particles.animate(scene)
        
        scene.play(
            *[FadeOut(mob, scale=1.2) for mob in old_mobjects],
            Create(circle.mobjects),
            run_time=duration/3
        )
        
        scene.play(
            Rotate(circle.mobjects, PI),
            run_time=duration/3
        )
        
        scene.play(
            *[FadeIn(mob, scale=0.8) for mob in new_mobjects],
            Uncreate(circle.mobjects),
            run_time=duration/3
        )
        
        particles.cleanup()
        circle.cleanup()
