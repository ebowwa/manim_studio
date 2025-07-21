#!/usr/bin/env python
"""Test the auto-layered scene with automatic registration."""

from manim import *
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.timeline import ComposerTimeline
from src.core.timeline.auto_layered_scene import AutoLayeredScene


class AutoLayerDemo(AutoLayeredScene):
    """Demo showing the simplicity of auto-layered scenes."""
    
    def construct(self):
        # Title - automatically goes to default "Main" layer
        title = Text("Auto-Layered Scene", font_size=48, weight=BOLD).to_edge(UP)
        self.add(title)  # No manual registration needed!
        
        # Add background elements using context manager
        with self.use_layer("Background"):
            # These all go to Background layer automatically
            bg = Rectangle(width=14, height=8, color=BLUE_E, fill_opacity=0.2)
            self.add(bg)
            
            # Add stars
            for _ in range(50):
                star = Dot(
                    radius=np.random.uniform(0.01, 0.03),
                    color=WHITE,
                    fill_opacity=np.random.uniform(0.3, 0.7)
                ).move_to(np.random.uniform(-7, 7) * RIGHT + np.random.uniform(-4, 4) * UP)
                self.add(star)
        
        # Add main content - explicit layer specification
        circle = Circle(radius=2, color=RED, fill_opacity=0.8).shift(LEFT * 3)
        self.add(circle, layer="Main")
        
        square = Square(side_length=3, color=GREEN, fill_opacity=0.8)
        self.add(square, layer="Main")
        
        triangle = Triangle(color=YELLOW, fill_opacity=0.8).scale(2).shift(RIGHT * 3)
        self.add(triangle, layer="Main")
        
        # Add foreground elements
        info = Text("Objects automatically registered to layers!", font_size=20)
        info.to_edge(DOWN)
        self.add(info, layer="Foreground")
        
        self.wait(2)
        
        # Demo: Move objects between layers
        demo_text = Text("Moving circle to foreground...", font_size=24, color=YELLOW)
        demo_text.next_to(title, DOWN)
        self.play(FadeIn(demo_text))
        
        # Simply move to new layer - no manual deregistration needed
        self.move_to_layer(circle, "Foreground")
        self.wait(2)
        
        # Demo: Batch operations
        self.play(demo_text.animate.become(
            Text("Adding particles efficiently...", font_size=24, color=YELLOW).next_to(title, DOWN)
        ))
        
        # Use auto_ordering context to prevent reordering during batch add
        with self.auto_ordering(False):
            particles = VGroup()
            for i in range(100):
                particle = Dot(
                    radius=0.03,
                    color=ORANGE,
                    fill_opacity=0.6
                ).move_to(square.get_center() + np.random.uniform(-1, 1) * RIGHT + np.random.uniform(-1, 1) * UP)
                particles.add(particle)
            
            # Add all particles at once
            self.add(particles, layer="Main")
        # Reordering happens once here
        
        self.play(
            particles.animate.scale(3).set_opacity(0.2),
            run_time=2
        )
        
        # Demo: Layer visibility
        self.play(demo_text.animate.become(
            Text("Hiding background layer...", font_size=24, color=YELLOW).next_to(title, DOWN)
        ))
        
        self.hide_layer("Background")
        self.wait(2)
        
        self.show_layer("Background")
        
        # Demo: Bring layer to front
        self.play(demo_text.animate.become(
            Text("Background to front...", font_size=24, color=YELLOW).next_to(title, DOWN)
        ))
        
        self.bring_to_layer_front("Background")
        self.wait(2)
        
        # Clean finish
        self.play(FadeOut(demo_text))
        
        final = VGroup(
            Text("Auto-Registration Complete!", font_size=36, weight=BOLD),
            Text("No manual layer management needed", font_size=24, slant=ITALIC)
        ).arrange(DOWN).set_color_by_gradient(GREEN, BLUE)
        
        self.play(
            Transform(title, final),
            run_time=2
        )
        self.wait(2)


class BatchOperationDemo(AutoLayeredScene):
    """Demo showing efficient batch operations."""
    
    def __init__(self):
        # Create scene with custom default layer
        super().__init__(default_layer="Particles")
    
    def construct(self):
        title = Text("Batch Layer Operations", font_size=36).to_edge(UP)
        self.add(title, layer="UI")
        
        # Prepare objects for different layers
        backgrounds = [
            Rectangle(width=15, height=8.5, color=color, fill_opacity=0.1)
            for color in [BLUE_E, PURPLE_E, TEAL_E]
        ]
        
        shapes = [
            Circle(radius=1, color=RED).shift(LEFT * 3),
            Square(side_length=2, color=GREEN),
            Triangle(color=BLUE).scale(1.5).shift(RIGHT * 3)
        ]
        
        effects = [
            Circle(radius=1.5, color=YELLOW, fill_opacity=0.2).shift(LEFT * 3),
            Circle(radius=2.5, color=ORANGE, fill_opacity=0.2),
            Circle(radius=1.8, color=PINK, fill_opacity=0.2).shift(RIGHT * 3)
        ]
        
        # Add everything in one batch operation
        self.add_batch({
            "Background": backgrounds,
            "Main": shapes,
            "Foreground": effects
        })
        
        self.wait(2)
        
        # Demo clearing a layer
        info = Text("Clearing effects layer...", font_size=24).to_edge(DOWN)
        self.play(Write(info))
        
        self.clear_layer("Foreground")
        self.wait(2)
        
        # Add new effects
        self.play(info.animate.become(
            Text("Adding new effects...", font_size=24).to_edge(DOWN)
        ))
        
        new_effects = VGroup()
        for shape in shapes:
            for i in range(5):
                ring = Circle(
                    radius=0.5 + i * 0.3,
                    color=shape.get_color(),
                    stroke_width=2,
                    fill_opacity=0
                ).move_to(shape.get_center())
                new_effects.add(ring)
        
        self.add(new_effects, layer="Foreground")
        
        self.play(
            new_effects.animate.scale(1.5).set_stroke(width=1),
            run_time=2
        )
        
        self.wait(2)


if __name__ == "__main__":
    from manim import config
    config.pixel_height = 1080
    config.pixel_width = 1920
    config.frame_rate = 60
    config.quality = "high_quality"
    
    # Run auto layer demo
    scene1 = AutoLayerDemo()
    scene1.render()
    
    # Run batch operations demo
    scene2 = BatchOperationDemo()
    scene2.render()