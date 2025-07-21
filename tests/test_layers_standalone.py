#!/usr/bin/env python
"""Standalone test of the improved timeline layer system."""

from manim import *
import numpy as np
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import only what we need directly
from src.core.timeline.composer_timeline import ComposerTimeline, TimelineLayer
from src.core.timeline.layer_manager import LayerManager, create_layered_scene
from src.components.effects.skull_effects_v2 import ImprovedSkullEffect
from src.components.effects.glow_effects import GlowEffect
from src.components.effects.environment_effects import BokehEffect


class LayerSystemDemo(Scene):
    def construct(self):
        # Create timeline with layer support
        timeline = ComposerTimeline(duration=20.0)
        
        # Create layers with specific z-indices
        timeline.add_layer("Background", ["bg"], z_index=0)
        timeline.add_layer("MidBack", ["particles"], z_index=100)
        timeline.add_layer("Center", ["main"], z_index=200)
        timeline.add_layer("Effects", ["glow"], z_index=300)
        timeline.add_layer("UI", ["text"], z_index=400)
        
        # Create layer manager
        layers = LayerManager(timeline)
        
        # Title
        title = Text("Z-Index Layer System", font_size=48, weight=BOLD)
        title.to_edge(UP)
        self.add(title)
        layers.register_mobject("UI", title)
        
        # Layer 1: Background gradient
        bg = Rectangle(
            width=14, height=8,
            fill_color=[BLUE_E, PURPLE_E],
            fill_opacity=0.3,
            stroke_width=0
        )
        self.add(bg)
        layers.register_mobject("Background", bg)
        
        # Layer 2: Floating particles
        particles = VGroup()
        for _ in range(50):
            particle = Dot(
                radius=np.random.uniform(0.02, 0.05),
                color=random_color(),
                fill_opacity=0.8
            ).move_to(np.random.uniform(-6, 6) * RIGHT + np.random.uniform(-3, 3) * UP)
            particles.add(particle)
        self.add(particles)
        layers.register_mobject("MidBack", particles)
        
        # Layer 3: Main objects - Three colored shapes
        shapes = VGroup(
            Circle(radius=1.5, color=RED, fill_opacity=0.8).shift(LEFT * 3),
            Square(side_length=2.5, color=GREEN, fill_opacity=0.8),
            Triangle(color=BLUE, fill_opacity=0.8).scale(2).shift(RIGHT * 3)
        )
        self.add(shapes)
        for shape in shapes:
            layers.register_mobject("Center", shape)
        
        # Layer 4: Glow effects
        glows = VGroup()
        for shape in shapes:
            glow = Circle(
                radius=2,
                color=shape.get_color(),
                fill_opacity=0.2,
                stroke_width=0
            ).move_to(shape.get_center())
            glows.add(glow)
            self.add(glow)
            layers.register_mobject("Effects", glow)
        
        # Layer 5: UI elements
        layer_info = VGroup()
        layer_names = ["Background (0)", "Particles (100)", "Shapes (200)", "Glows (300)", "UI (400)"]
        for i, name in enumerate(layer_names):
            label = Text(name, font_size=16)
            label.to_edge(LEFT).shift(DOWN * (i * 0.5 + 1))
            layer_info.add(label)
            self.add(label)
            layers.register_mobject("UI", label)
        
        # Apply initial ordering
        layers.apply_layer_ordering(self)
        self.wait(2)
        
        # Demo 1: Move shapes to top
        demo_text = Text("Moving shapes to top...", font_size=24, color=YELLOW)
        demo_text.next_to(title, DOWN)
        self.play(FadeIn(demo_text))
        layers.register_mobject("UI", demo_text)
        
        timeline.move_layer_to_top("Center")
        layers.apply_layer_ordering(self)
        self.wait(2)
        
        # Demo 2: Move glows to bottom
        self.play(demo_text.animate.become(
            Text("Moving glows to bottom...", font_size=24, color=YELLOW).next_to(title, DOWN)
        ))
        
        timeline.move_layer_to_bottom("Effects")
        layers.apply_layer_ordering(self)
        self.wait(2)
        
        # Demo 3: Restore order
        self.play(demo_text.animate.become(
            Text("Restoring original order...", font_size=24, color=YELLOW).next_to(title, DOWN)
        ))
        
        timeline.set_layer_z_index("Effects", 300)
        timeline.set_layer_z_index("Center", 200)
        layers.apply_layer_ordering(self)
        self.wait(2)
        
        # Demo 4: Hide/show layers
        self.play(demo_text.animate.become(
            Text("Hiding particle layer...", font_size=24, color=YELLOW).next_to(title, DOWN)
        ))
        
        layers.hide_layer(self, "MidBack")
        self.wait(2)
        
        self.play(demo_text.animate.become(
            Text("Showing particle layer...", font_size=24, color=YELLOW).next_to(title, DOWN)
        ))
        
        layers.show_layer(self, "MidBack")
        self.wait(2)
        
        # Final animation
        self.play(
            FadeOut(demo_text),
            shapes.animate.scale(0.8).arrange(RIGHT, buff=1).move_to(ORIGIN),
            glows.animate.scale(0.8)
        )
        
        final = Text("Layer System Working!", font_size=36, color=GREEN)
        final.next_to(shapes, DOWN, buff=1)
        self.play(Write(final))
        layers.register_mobject("UI", final)
        layers.apply_layer_ordering(self)
        
        self.wait(3)


if __name__ == "__main__":
    from manim import config
    config.pixel_height = 1080
    config.pixel_width = 1920
    config.frame_rate = 60
    config.quality = "high_quality"
    
    scene = LayerSystemDemo()
    scene.render()