"""
Simple demo of the enhanced easing system.
"""

from manim import *
import numpy as np


# Easing functions from our math3d utilities
def smooth_step(t: float) -> float:
    """Smooth interpolation function (3t² - 2t³)."""
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def smoother_step(t: float) -> float:
    """Even smoother interpolation (6t⁵ - 15t⁴ + 10t³)."""
    t = np.clip(t, 0, 1)
    return t * t * t * (t * (t * 6 - 15) + 10)


def elastic_ease_out(t: float, amplitude: float = 1, period: float = 0.3) -> float:
    """Elastic easing out - overshoots then settles."""
    if t == 0:
        return 0
    if t == 1:
        return 1
    
    s = period / (2 * np.pi) * np.arcsin(1 / amplitude) if amplitude >= 1 else period / 4
    return amplitude * np.power(2, -10 * t) * np.sin((t - s) * 2 * np.pi / period) + 1


def bounce_ease_out(t: float) -> float:
    """Bounce easing out - bounces at the end."""
    if t < 1/2.75:
        return 7.5625 * t * t
    elif t < 2/2.75:
        t -= 1.5/2.75
        return 7.5625 * t * t + 0.75
    elif t < 2.5/2.75:
        t -= 2.25/2.75
        return 7.5625 * t * t + 0.9375
    else:
        t -= 2.625/2.75
        return 7.5625 * t * t + 0.984375


class SimpleEasingDemo(Scene):
    def construct(self):
        # Title
        title = Text("Enhanced Easing Functions", font_size=48)
        subtitle = Text("Integrated Math3D Utilities", font_size=24, color=GRAY)
        subtitle.next_to(title, DOWN)
        
        self.play(Write(title), FadeIn(subtitle))
        self.wait(1)
        self.play(FadeOut(VGroup(title, subtitle)))
        
        # Demo 1: Compare easing functions
        self.demo_easing_comparison()
        
        # Demo 2: Practical animation examples
        self.demo_practical_animations()
    
    def demo_easing_comparison(self):
        """Compare different easing functions visually."""
        title = Text("Easing Function Comparison", font_size=36).to_edge(UP)
        self.play(Write(title))
        
        # Create dots and paths
        easings = [
            ("Linear", lambda t: t, RED),
            ("Smooth Step", smooth_step, BLUE),
            ("Smoother Step", smoother_step, GREEN),
            ("Elastic", lambda t: elastic_ease_out(t), PURPLE),
            ("Bounce", bounce_ease_out, ORANGE)
        ]
        
        dots = VGroup()
        labels = VGroup()
        
        for i, (name, func, color) in enumerate(easings):
            # Create dot
            dot = Dot(radius=0.15, color=color)
            dot.move_to(LEFT * 5 + UP * (2 - i * 0.8))
            dots.add(dot)
            
            # Create label
            label = Text(name, font_size=20, color=color)
            label.move_to(LEFT * 6.5 + UP * (2 - i * 0.8))
            labels.add(label)
            
            # Draw path
            path = self.create_easing_path(
                start=LEFT * 5 + UP * (2 - i * 0.8),
                end=RIGHT * 5 + UP * (2 - i * 0.8),
                easing=func,
                color=color
            )
            self.add(path)
        
        self.play(
            *[FadeIn(label) for label in labels],
            *[FadeIn(dot) for dot in dots]
        )
        
        # Animate dots
        animations = []
        for i, (_, func, _) in enumerate(easings):
            dot = dots[i]
            animations.append(
                dot.animate(rate_func=func, run_time=3).shift(RIGHT * 10)
            )
        
        self.play(*animations)
        self.wait(1)
        
        # Clean up
        self.play(
            FadeOut(dots),
            FadeOut(labels),
            FadeOut(title),
            *[FadeOut(mob) for mob in self.mobjects if isinstance(mob, VMobject)]
        )
    
    def create_easing_path(self, start, end, easing, color):
        """Create a visual representation of an easing function."""
        points = []
        num_samples = 100
        
        for i in range(num_samples):
            t = i / (num_samples - 1)
            eased_t = easing(t)
            
            x = start[0] + (end[0] - start[0]) * t
            y = start[1] + (end[1] - start[1]) * eased_t
            points.append([x, y, 0])
        
        path = VMobject()
        path.set_points_as_corners(points)
        path.set_stroke(color, width=2, opacity=0.5)
        
        return path
    
    def demo_practical_animations(self):
        """Show practical use cases of easing functions."""
        title = Text("Practical Animation Examples", font_size=36).to_edge(UP)
        self.play(Write(title))
        
        # Example 1: UI Card with elastic entrance
        self.demo_ui_card()
        
        # Example 2: Smooth morphing shapes
        self.demo_smooth_morph()
        
        # Example 3: Bouncing elements
        self.demo_bounce_elements()
        
        self.play(FadeOut(title))
    
    def demo_ui_card(self):
        """Demonstrate UI card with elastic entrance."""
        subtitle = Text("Elastic UI Animation", font_size=24, color=GRAY).to_edge(UP).shift(DOWN)
        self.play(Write(subtitle))
        
        # Create cards
        cards = VGroup()
        for i in range(3):
            card = RoundedRectangle(
                width=2.5, height=3.5, corner_radius=0.2,
                fill_color=BLUE_E, fill_opacity=0.8,
                stroke_color=BLUE, stroke_width=2
            )
            card.shift(LEFT * 4 + RIGHT * i * 4)
            
            # Add content
            title = Text(f"Card {i+1}", font_size=20, color=WHITE)
            title.move_to(card.get_center() + UP * 1.2)
            
            lines = VGroup(*[
                Line(LEFT * 0.8, RIGHT * 0.8, stroke_width=2, color=WHITE)
                .move_to(card.get_center() + DOWN * j * 0.4)
                for j in range(3)
            ])
            
            card_group = VGroup(card, title, lines)
            cards.add(card_group)
        
        # Animate with elastic ease
        for card in cards:
            card.scale(0)
        
        self.play(
            LaggedStart(*[
                card.animate(rate_func=elastic_ease_out, run_time=1.5).scale(1)
                for card in cards
            ], lag_ratio=0.2)
        )
        
        self.wait(1)
        self.play(FadeOut(cards), FadeOut(subtitle))
    
    def demo_smooth_morph(self):
        """Demonstrate smooth morphing with smoother step."""
        subtitle = Text("Smooth Morphing", font_size=24, color=GRAY).to_edge(UP).shift(DOWN)
        self.play(Write(subtitle))
        
        # Create shapes
        circle = Circle(radius=1, color=BLUE)
        square = Square(side_length=2, color=BLUE)
        triangle = Triangle(color=BLUE).scale(1.5)
        
        shapes = [circle, square, triangle, circle.copy()]
        
        # Position first shape
        current_shape = shapes[0]
        self.play(FadeIn(current_shape))
        
        # Morph through shapes
        for next_shape in shapes[1:]:
            self.play(
                Transform(current_shape, next_shape, rate_func=smoother_step, run_time=2)
            )
            self.wait(0.5)
        
        self.play(FadeOut(current_shape), FadeOut(subtitle))
    
    def demo_bounce_elements(self):
        """Demonstrate bouncing elements."""
        subtitle = Text("Bounce Effects", font_size=24, color=GRAY).to_edge(UP).shift(DOWN)
        self.play(Write(subtitle))
        
        # Create bouncing dots
        dots = VGroup()
        colors = [RED, GREEN, BLUE, YELLOW, PURPLE]
        
        for i, color in enumerate(colors):
            dot = Dot(radius=0.3, color=color)
            dot.move_to(LEFT * 3 + RIGHT * i * 1.5 + UP * 3)
            dots.add(dot)
        
        self.play(*[FadeIn(dot) for dot in dots])
        
        # Bounce animation
        self.play(
            *[dot.animate(rate_func=bounce_ease_out, run_time=2).shift(DOWN * 5)
              for dot in dots]
        )
        
        # Chain reaction bounce
        self.play(
            LaggedStart(*[
                dot.animate(rate_func=bounce_ease_out, run_time=1).shift(UP * 2)
                for dot in dots
            ], lag_ratio=0.1)
        )
        
        self.play(FadeOut(dots), FadeOut(subtitle))


if __name__ == "__main__":
    # Render the scene
    scene = SimpleEasingDemo()
    scene.render()