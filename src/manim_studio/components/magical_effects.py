from manim import *
import numpy as np

class MagicalEffects:
    """A collection of magical visual effects for animations"""
    
    @staticmethod
    def create_particles(n_particles=30, radius=0.02, color=BLUE_A, x_range=(-7, 7), y_range=(-4, 4)):
        """Create a group of floating particles
        
        Args:
            n_particles: Number of particles to create
            radius: Size of each particle
            color: Color of particles
            x_range: Range for x coordinates (min, max)
            y_range: Range for y coordinates (min, max)
        """
        particles = VGroup()
        for _ in range(n_particles):
            particle = Dot(radius=radius, color=color)
            particle.move_to(np.array([
                np.random.uniform(*x_range),
                np.random.uniform(*y_range),
                0
            ]))
            particles.add(particle)
        return particles
    
    @staticmethod
    def particle_animation(particles, x_range=(-7, 7), y_range=(-4, 4)):
        """Generate animations for particle movement
        
        Args:
            particles: VGroup of particles to animate
            x_range: Range for x coordinates (min, max)
            y_range: Range for y coordinates (min, max)
        """
        anims = []
        for particle in particles:
            target = np.array([
                np.random.uniform(*x_range),
                np.random.uniform(*y_range),
                0
            ])
            anim = particle.animate.move_to(target)
            anims.append(anim)
        return anims

    @staticmethod
    def create_magic_circle(radius=3, color_scheme=(BLUE_A, BLUE_C, BLUE_E, WHITE)):
        """Create a magical circle with runes and symbols
        
        Args:
            radius: Size of the outer circle
            color_scheme: Tuple of (outer_circle, inner_circle, runes, symbols) colors
        """
        outer_color, inner_color, rune_color, symbol_color = color_scheme
        
        # Create circles
        outer_circle = Circle(radius=radius, color=outer_color)
        inner_circle = Circle(radius=radius*0.8, color=inner_color)
        
        # Create runes
        runes = VGroup()
        for i in range(8):
            rune = Text("*", color=rune_color).scale(0.5)
            rune.move_to(outer_circle.point_from_proportion(i/8))
            runes.add(rune)
        
        # Create alchemical symbols
        symbols = VGroup()
        alchemical = ["⚗", "🜍", "⚖", "🜎"]
        for i, symbol in enumerate(alchemical):
            sym = Text(symbol, color=symbol_color).scale(0.4)
            sym.move_to(inner_circle.point_from_proportion(i/4))
            symbols.add(sym)
        
        return VGroup(outer_circle, inner_circle, runes, symbols)

    @staticmethod
    def gradient_text(text, gradient=(BLUE_A, BLUE_E), weight="BOLD", scale=1.0):
        """Create text with a color gradient
        
        Args:
            text: Text content
            gradient: Tuple of (start_color, end_color)
            weight: Font weight
            scale: Text scale
        """
        return Text(text, gradient=gradient, weight=weight).scale(scale)

    @staticmethod
    def magical_reveal(scene, mobject, style="fade", run_time=1.0):
        """Reveal an object with a magical effect
        
        Args:
            scene: The manim scene
            mobject: Object to reveal
            style: Animation style ("fade", "scale", "sparkle")
            run_time: Duration of animation
        """
        if style == "fade":
            scene.play(FadeIn(mobject, scale=1.2), run_time=run_time)
        elif style == "scale":
            mobject.scale(0)
            scene.play(mobject.animate.scale(1), run_time=run_time)
        elif style == "sparkle":
            particles = MagicalEffects.create_particles(20, color=WHITE)
            scene.play(
                FadeIn(mobject),
                *[FadeIn(p) for p in particles],
                run_time=run_time/2
            )
            scene.play(
                *[FadeOut(p) for p in particles],
                run_time=run_time/2
            )
