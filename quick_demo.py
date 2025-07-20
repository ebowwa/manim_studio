"""Quick demo using standard Manim animations with ComposerTimeline."""

from manim import *

class QuickDemo(Scene):
    def construct(self):
        # Create elements
        title = Text("COMPOSER TIMELINE", font_size=48, weight=BOLD)
        title.set_color_by_gradient(BLUE, PURPLE)
        
        subtitle = Text("Keyframe Animation System", font_size=24)
        subtitle.next_to(title, DOWN)
        
        # Animate using standard Manim
        self.play(Write(title), run_time=2)
        self.play(FadeIn(subtitle, shift=UP), run_time=1)
        
        # Create shapes
        circle = Circle(radius=1, color=BLUE, fill_opacity=0.7)
        square = Square(side_length=1.5, color=RED, fill_opacity=0.7)
        
        circle.shift(LEFT * 3)
        square.shift(RIGHT * 3)
        
        self.play(
            Create(circle),
            Create(square),
            run_time=1
        )
        
        # Animate with timeline-inspired movements
        self.play(
            circle.animate.shift(RIGHT * 6).scale(1.5),
            Rotate(square, angle=TAU),
            run_time=2
        )
        
        self.play(
            circle.animate.shift(LEFT * 6).scale(1/1.5),
            square.animate.scale(1.5),
            run_time=2
        )
        
        # Fade out
        self.play(
            FadeOut(title),
            FadeOut(subtitle),
            FadeOut(circle),
            FadeOut(square),
            run_time=1
        )

if __name__ == "__main__":
    import os
    os.system('manim -pql quick_demo.py QuickDemo')