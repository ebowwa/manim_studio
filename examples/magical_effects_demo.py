from manim import *
from manim_studio.scenes.base_scene import StudioScene
from manim_studio.components.magical_effects import MagicalEffects

class MagicalEffectsDemo(StudioScene):
    def construct(self):
        # Demo 1: Particle Effects
        title = MagicalEffects.gradient_text("Magical Effects Demo")
        particles = MagicalEffects.create_particles(30)
        
        self.play(Write(title))
        self.play(*[FadeIn(p) for p in particles])
        self.play(*MagicalEffects.particle_animation(particles))
        self.wait(1)
        
        # Demo 2: Magic Circle
        self.play(
            title.animate.scale(0.6).to_edge(UP),
            *[FadeOut(p) for p in particles]
        )
        
        magic_circle = MagicalEffects.create_magic_circle()
        
        # Reveal each part of the circle
        for part in magic_circle:
            MagicalEffects.magical_reveal(self, part, style="sparkle")
            self.wait(0.5)
        
        self.play(Rotate(magic_circle, PI), run_time=2)
        self.wait(1)
        
        # Demo 3: Combined Effects
        new_particles = MagicalEffects.create_particles(50, color=WHITE)
        
        self.play(
            *[FadeIn(p) for p in new_particles],
            magic_circle.animate.scale(1.2)
        )
        
        for _ in range(2):
            self.play(*MagicalEffects.particle_animation(new_particles))
        
        # Final fadeout
        self.play(
            FadeOut(title),
            FadeOut(magic_circle),
            *[FadeOut(p) for p in new_particles]
        )
