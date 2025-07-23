#!/usr/bin/env python3
"""
Direct Manim animation script that bypasses MCP client issues.
This creates a simple animation with text and shapes.
"""

from manim import *

class ExampleWorkflow(Scene):
    def construct(self):
        # Create title text
        title = Text("Hello World", font_size=72, color="#FFD700")
        title.shift(UP * 2)
        
        # Create subtitle
        subtitle = Text("Tutorial section: Getting Started", font_size=36, color="#FFFFFF")
        subtitle.next_to(title, DOWN, buff=0.5)
        
        # Create a circle
        circle = Circle(radius=1.5, color="#FF0000", fill_opacity=0.7)
        circle.shift(DOWN * 1)
        
        # Animate everything
        self.play(FadeIn(title))
        self.wait(0.5)
        self.play(FadeIn(subtitle))
        self.wait(0.5)
        self.play(Create(circle))
        self.wait(1)
        
        # Move the circle
        self.play(circle.animate.shift(RIGHT * 3))
        self.wait(0.5)
        self.play(circle.animate.shift(LEFT * 6))
        self.wait(0.5)
        self.play(circle.animate.shift(RIGHT * 3))
        
        # Fade out
        self.play(FadeOut(title), FadeOut(subtitle), FadeOut(circle))


if __name__ == "__main__":
    # Run with: python render_scene.py
    # Or: manim render_scene.py ExampleWorkflow -q m -p
    pass