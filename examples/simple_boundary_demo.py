"""
Simple boundary-aware animation demo.
"""

from manim import *
import numpy as np


class SimpleBoundaryDemo(Scene):
    def construct(self):
        # Get and display frame dimensions
        fw = config.frame_width
        fh = config.frame_height
        margin = 0.5
        
        # Title
        title = Text(f"Frame: {fw:.1f}x{fh:.1f} units", font_size=36)
        title.to_edge(UP, buff=margin)
        self.play(Write(title))
        
        # Show boundaries
        boundary = Rectangle(
            width=fw - 2*margin,
            height=fh - 2*margin,
            stroke_color=GREY,
            stroke_width=2,
            stroke_opacity=0.5
        )
        
        # Safe area indicators
        safe_text = Text("Safe Area", font_size=20, color=GREY)
        safe_text.next_to(boundary, DOWN, buff=0.1)
        
        self.play(Create(boundary), Write(safe_text))
        
        # Demo 1: Dots bouncing within boundaries
        dots = VGroup()
        for i in range(5):
            dot = Dot(radius=0.2, color=BLUE)
            # Start from left edge
            dot.move_to([-fw/2 + margin + 0.2, (i-2) * 0.8, 0])
            dots.add(dot)
        
        self.play(*[FadeIn(dot) for dot in dots])
        
        # Move dots to right edge
        self.play(
            *[dot.animate(run_time=2).move_to([fw/2 - margin - 0.2, dot.get_y(), 0]) 
              for dot in dots]
        )
        
        # Demo 2: Scaling within bounds
        square = Square(side_length=1, color=RED)
        square.move_to(ORIGIN)
        
        self.play(FadeIn(square))
        
        # Calculate max scale
        max_scale_x = (fw - 2*margin) / square.get_width() * 0.8
        max_scale_y = (fh - 2*margin - 2) / square.get_height() * 0.8  # Leave room for title
        max_scale = min(max_scale_x, max_scale_y)
        
        self.play(square.animate(run_time=1.5).scale(max_scale))
        self.play(square.animate(run_time=1).scale(1/max_scale))
        
        # Demo 3: Text that fits
        long_text = Text(
            "This text automatically fits within boundaries",
            font_size=40
        )
        
        # Scale to fit if needed
        if long_text.get_width() > fw - 2*margin:
            scale_factor = (fw - 2*margin) / long_text.get_width() * 0.9
            long_text.scale(scale_factor)
        
        self.play(Write(long_text))
        self.wait(1)
        
        # Clean up
        self.play(
            FadeOut(dots),
            FadeOut(square),
            FadeOut(long_text),
            FadeOut(boundary),
            FadeOut(safe_text),
            FadeOut(title)
        )


if __name__ == "__main__":
    # Standard HD dimensions
    config.pixel_height = 1080
    config.pixel_width = 1920
    config.frame_rate = 60
    
    print(f"Rendering at {config.pixel_width}x{config.pixel_height}")
    print(f"Frame size: {config.frame_width}x{config.frame_height} Manim units")
    
    scene = SimpleBoundaryDemo()
    scene.render()