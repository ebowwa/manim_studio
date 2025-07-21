#!/usr/bin/env python
"""Minimal demo of the layer system with z-indexing."""

from manim import *
import numpy as np
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Direct imports to avoid __init__ issues
import importlib.util

# Load ComposerTimeline directly
spec = importlib.util.spec_from_file_location(
    "composer_timeline", 
    "src/manim_studio/core/timeline/composer_timeline.py"
)
composer_timeline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(composer_timeline)

ComposerTimeline = composer_timeline.ComposerTimeline
TimelineLayer = composer_timeline.TimelineLayer

# Load LayerManager with fixed imports
exec(open("src/manim_studio/core/timeline/layer_manager.py").read().replace(
    "from .composer_timeline import ComposerTimeline, TimelineLayer",
    ""
), globals())


class LayerDemo(Scene):
    def construct(self):
        # Create timeline with layers
        timeline = ComposerTimeline(duration=20.0)
        
        # Add layers with different z-indices
        timeline.add_layer("Background", z_index=0)
        timeline.add_layer("Middle", z_index=100)
        timeline.add_layer("Foreground", z_index=200)
        
        # Create layer manager
        layers = LayerManager(timeline)
        
        # Title
        title = Text("Layer Z-Index Demo", font_size=48, weight=BOLD).to_edge(UP)
        self.add(title)
        layers.register_mobject("Foreground", title)
        
        # Background - large blue rectangle
        bg = Rectangle(width=10, height=6, color=BLUE, fill_opacity=0.3)
        bg.shift(DOWN * 0.5)
        self.add(bg)
        layers.register_mobject("Background", bg)
        
        # Middle layer - red circle
        circle = Circle(radius=2, color=RED, fill_opacity=0.8)
        circle.shift(LEFT * 2)
        self.add(circle)
        layers.register_mobject("Middle", circle)
        
        # Foreground - green square
        square = Square(side_length=3, color=GREEN, fill_opacity=0.8)
        square.shift(RIGHT * 1)
        self.add(square)
        layers.register_mobject("Foreground", square)
        
        # Apply initial ordering
        layers.apply_layer_ordering(self)
        
        # Show layer info
        info = VGroup(
            Text("Background: Blue Rectangle (z=0)", font_size=20, color=BLUE),
            Text("Middle: Red Circle (z=100)", font_size=20, color=RED),
            Text("Foreground: Green Square (z=200)", font_size=20, color=GREEN)
        ).arrange(DOWN, aligned_edge=LEFT).to_corner(DL)
        self.add(info)
        layers.register_mobject("Foreground", info)
        
        self.wait(2)
        
        # Demo: Move middle to top
        demo_text = Text("Moving red circle to top...", font_size=24, color=YELLOW)
        demo_text.next_to(title, DOWN)
        self.play(FadeIn(demo_text))
        layers.register_mobject("Foreground", demo_text)
        
        timeline.move_layer_to_top("Middle")
        layers.apply_layer_ordering(self)
        self.wait(2)
        
        # Demo: Move background to top
        self.play(demo_text.animate.become(
            Text("Moving blue background to top...", font_size=24, color=YELLOW).next_to(title, DOWN)
        ))
        
        timeline.move_layer_to_top("Background")
        layers.apply_layer_ordering(self)
        self.wait(2)
        
        # Restore original order
        self.play(demo_text.animate.become(
            Text("Restoring original order...", font_size=24, color=YELLOW).next_to(title, DOWN)
        ))
        
        timeline.set_layer_z_index("Background", 0)
        timeline.set_layer_z_index("Middle", 100)
        timeline.set_layer_z_index("Foreground", 200)
        layers.apply_layer_ordering(self)
        self.wait(2)
        
        # Final message
        self.play(FadeOut(demo_text))
        final = Text("Layer System Working!", font_size=36, color=GREEN)
        final.shift(DOWN * 2.5)
        self.play(Write(final))
        self.wait(2)


if __name__ == "__main__":
    from manim import config
    config.pixel_height = 1080
    config.pixel_width = 1920
    config.frame_rate = 30
    config.quality = "high_quality"
    
    scene = LayerDemo()
    scene.render()