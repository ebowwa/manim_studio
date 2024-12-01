from manim import *
from manim_studio.components.effects import (
    ParticleSystem,
    MagicalCircle,
    TextEffects,
    EffectTransitions
)

class EffectsShowcase(Scene):
    def construct(self):
        # 1. Opening sequence with particle effects
        title = TextEffects(
            "Manim Studio Effects",
            gradient_colors=(BLUE_A, BLUE_E),
            glow_factor=1.8
        )
        title.create()
        
        particles = ParticleSystem(
            n_emitters=5,
            particles_per_second=30,
            particle_lifetime=2.0,
            velocity_range=(1, 2),
            particle_color=BLUE_A
        )
        
        # Reveal title with particles
        particles.animate(self)
        self.play(FadeIn(title._mobjects, scale=1.2))
        self.wait(1)
        
        # 2. Magical Circle Demonstration
        subtitle = TextEffects(
            "Magical Circle Demo",
            color=BLUE_C,
            glow_factor=1.5
        )
        subtitle.create()
        
        # Transition to subtitle
        transitions = EffectTransitions(duration=1.5)
        transitions.transition_scenes(
            self,
            title._mobjects,
            subtitle._mobjects,
            style="magical"
        )
        self.wait(0.5)
        
        # Create and animate magical circle
        circle = MagicalCircle(
            radius=3,
            n_circles=3,
            n_runes=8,
            rotation_speed=0.5,
            color_scheme={
                'outer': BLUE_A,
                'inner': BLUE_C,
                'runes': BLUE_E,
                'symbols': WHITE,
            }
        )
        
        circle.create()
        circle.animate(self)
        self.wait(2)
        
        # 3. Text Effects Showcase
        text_demos = VGroup()
        
        # Different text animation styles
        styles = ["write", "fade", "typewriter", "sparkle"]
        for i, style in enumerate(styles):
            text = TextEffects(
                f"Text Style: {style}",
                color=BLUE_A,
                glow_factor=1.5
            )
            text.create()
            text._mobjects.shift(UP * (1.5 - i))
            text.animate(self, style=style)
            text_demos.add(text._mobjects)
            self.wait(0.5)
        
        # 4. Particle Effects Showcase
        self.play(FadeOut(text_demos))
        
        particle_title = TextEffects(
            "Particle Systems",
            gradient_colors=(BLUE_A, PURPLE_A),
            glow_factor=1.5
        )
        particle_title.create()
        particle_title.animate(self, style="fade")
        
        # Create multiple particle systems with different behaviors
        particle_systems = [
            ParticleSystem(
                n_emitters=3,
                particles_per_second=20,
                particle_lifetime=1.5,
                velocity_range=(1, 3),
                particle_color=color
            )
            for color in [BLUE_A, PURPLE_A, TEAL_A]
        ]
        
        for system in particle_systems:
            system.animate(self)
        
        self.wait(2)
        
        # 5. Grand Finale
        finale_text = TextEffects(
            "Effects System Complete!",
            gradient_colors=(BLUE_A, PURPLE_A, TEAL_A),
            glow_factor=2.0
        )
        finale_text.create()
        
        # Create a magical circle for the finale
        finale_circle = MagicalCircle(
            radius=4,
            n_circles=4,
            n_runes=12,
            rotation_speed=1.0,
            color_scheme={
                'outer': BLUE_A,
                'inner': PURPLE_A,
                'runes': TEAL_A,
                'symbols': WHITE,
            }
        )
        
        finale_circle.create()
        
        # Transition everything out
        self.play(
            FadeOut(particle_title._mobjects),
            *[system.cleanup() for system in particle_systems]
        )
        
        # Reveal finale
        finale_circle.animate(self)
        finale_text.animate(self, style="sparkle")
        
        self.wait(1)
        
        # Final particle burst
        burst = ParticleSystem(
            n_emitters=8,
            particles_per_second=40,
            particle_lifetime=1.0,
            velocity_range=(2, 4),
            particle_color=WHITE
        )
        burst.animate(self)
        
        self.wait(2)
        
        # Cleanup
        self.play(
            FadeOut(finale_text._mobjects),
            FadeOut(finale_circle.mobjects),
            burst.cleanup(),
            run_time=1.5
        )
