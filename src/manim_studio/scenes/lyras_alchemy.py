from manim import *
from manim_studio.scenes.base_scene import StudioScene
import os
import numpy as np

class LyrasAlchemy(StudioScene):
    def construct(self):
        # Create a magical atmosphere with particle effects
        def create_particles(n_particles=30):
            particles = VGroup()
            for _ in range(n_particles):
                particle = Dot(radius=0.02, color=BLUE_A)
                particle.move_to(np.array([
                    np.random.uniform(-7, 7),
                    np.random.uniform(-4, 4),
                    0
                ]))
                particles.add(particle)
            return particles
        
        def particle_animation(particles):
            anims = []
            for particle in particles:
                target = np.array([
                    np.random.uniform(-7, 7),
                    np.random.uniform(-4, 4),
                    0
                ])
                anim = particle.animate.move_to(target)
                anims.append(anim)
            return anims

        # Create magical circle
        def create_magic_circle():
            outer_circle = Circle(radius=3, color=BLUE_A)
            inner_circle = Circle(radius=2.5, color=BLUE_C)
            runes = VGroup()
            
            # Add rune symbols around the circle
            for i in range(8):
                angle = i * PI/4
                rune = Text("*", color=BLUE_E).scale(0.5)
                rune.move_to(outer_circle.point_from_proportion(i/8))
                runes.add(rune)
            
            # Add alchemical symbols
            symbols = VGroup()
            alchemical = ["⚗", "🜍", "⚖", "🜎"]  # Basic alchemical symbols
            for i, symbol in enumerate(alchemical):
                pos = i * PI/2
                sym = Text(symbol, color=WHITE).scale(0.4)
                sym.move_to(inner_circle.point_from_proportion(i/4))
                symbols.add(sym)
            
            return VGroup(outer_circle, inner_circle, runes, symbols)

        # Title sequence
        title = Text("Lyra's Alchemy", gradient=(BLUE_A, BLUE_E), weight="BOLD").scale(1.5)
        subtitle = Text("A Tale of Magic and Science", color=BLUE_C).scale(0.8)
        subtitle.next_to(title, DOWN)
        
        # Create initial particles
        particles = create_particles()
        
        # Animate title with particles
        self.play(
            *[FadeIn(p) for p in particles],
            run_time=1
        )
        self.play(
            Write(title),
            *particle_animation(particles),
            run_time=2
        )
        self.play(
            FadeIn(subtitle),
            *particle_animation(particles),
            run_time=1.5
        )
        self.wait(1)
        
        # Transition to magic circle
        magic_circle = create_magic_circle()
        
        self.play(
            FadeOut(title),
            FadeOut(subtitle),
            *[FadeOut(p) for p in particles],
            run_time=1
        )
        
        # Reveal magic circle with glowing effect
        self.play(
            Create(magic_circle[0]),
            Create(magic_circle[1]),
            run_time=1.5
        )
        
        self.play(
            *[FadeIn(rune) for rune in magic_circle[2]],
            run_time=1
        )
        
        # Add symbols with magical effect
        for symbol in magic_circle[3]:
            self.play(
                FadeIn(symbol, scale=1.5),
                run_time=0.3
            )
        
        # Create new particles for final effect
        final_particles = create_particles(50)
        
        # Final magical surge
        self.play(
            *[FadeIn(p) for p in final_particles],
            magic_circle.animate.scale(1.2),
            run_time=1
        )
        
        self.play(
            *particle_animation(final_particles),
            magic_circle.animate.scale(1/1.2),
            run_time=2
        )
        
        # Fade out
        self.play(
            *[FadeOut(mob) for mob in [*final_particles, magic_circle]],
            run_time=1.5
        )
