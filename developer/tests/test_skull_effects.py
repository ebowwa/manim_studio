#!/usr/bin/env python
"""Test script for skull effects - run from project root."""

# Configure Manim to use user-data directory
from src.config.manim_config import config

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from manim import *
from src.components.effects import (
    SkullEffect,
    SkullParticleEffect,
    GhostlySkullEffect,
    SkullTransformEffect,
    GlowEffect,
    NeonEffect,
    RippleEffect
)


class SkullEffectsDemo(Scene):
    def construct(self):
        # Title
        title = Text("SKULL EFFECTS DEMO", font_size=48, color=RED)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait()
        
        # Demo 1: Basic Skull Styles
        self.play(FadeOut(title))
        style_text = Text("Skull Styles", font_size=36).to_edge(UP)
        self.play(Write(style_text))
        
        # Create different skull styles
        styles = [
            ("Normal", "normal", WHITE, LEFT * 3),
            ("Cute", "cute", PINK, LEFT),
            ("Scary", "scary", RED, RIGHT),
            ("Pixel", "pixelated", GREEN, RIGHT * 3)
        ]
        
        skull_groups = VGroup()
        for name, style, color, pos in styles:
            skull = SkullEffect(
                position=pos,
                size=0.8,
                style=style,
                color=color,
                eye_glow=(style == "scary"),
                eye_color=YELLOW if style == "scary" else RED
            )
            skull_mob = skull.create()
            label = Text(name, font_size=20).next_to(pos + DOWN * 1.5, DOWN)
            
            self.play(
                FadeIn(skull_mob, scale=0.5),
                Write(label),
                run_time=0.5
            )
            skull_groups.add(skull_mob, label)
        
        self.wait(2)
        
        # Demo 2: Particle Formation
        self.play(FadeOut(skull_groups), FadeOut(style_text))
        particle_text = Text("Particle Formation", font_size=36).to_edge(UP)
        self.play(Write(particle_text))
        
        particle_skull = SkullParticleEffect(
            position=ORIGIN,
            num_particles=500,
            particle_size=0.03,
            particle_color=BLUE,
            glow=True,
            formation_time=2.5
        )
        
        particle_skull.create()
        particle_skull.animate(self)
        
        self.wait(2)
        
        # Demo 3: Ghostly Effect
        self.play(FadeOut(particle_skull.mobjects[0]), FadeOut(particle_text))
        ghost_text = Text("Ghostly Apparition", font_size=36).to_edge(UP)
        self.play(Write(ghost_text))
        
        ghost = GhostlySkullEffect(
            position=ORIGIN,
            size=1.5,
            color=BLUE_E,
            base_opacity=0.4,
            fade_cycle_time=3.0
        )
        
        ghost_mob = ghost.create()
        ghost.animate(self)
        
        self.wait(4)
        
        # Demo 4: Transformation
        self.play(FadeOut(ghost_mob), FadeOut(ghost_text))
        transform_text = Text("Shape Transformation", font_size=36).to_edge(UP)
        self.play(Write(transform_text))
        
        # Create a circle to transform
        circle = Circle(radius=1, color=YELLOW)
        self.play(Create(circle))
        self.wait()
        
        # Transform into skull
        transform = SkullTransformEffect(
            circle,
            skull_size=1.2,
            skull_style="scary",
            transform_time=2.0,
            intermediate_shapes=True,
            final_color=WHITE
        )
        
        transform.create()
        transform.animate(self)
        
        self.wait(2)
        
        # Finale
        self.play(*[FadeOut(mob) for mob in self.mobjects])
        
        end_text = Text("HAPPY HALLOWEEN!", font_size=60, color=ORANGE)
        end_text.set_stroke(BLACK, width=3)
        self.play(Write(end_text, run_time=2))
        self.wait(2)


if __name__ == "__main__":
    # Configure and render
    from manim import config
    config.pixel_height = 720
    config.pixel_width = 1280
    config.frame_rate = 30
    config.quality = "medium_quality"
    
    scene = SkullEffectsDemo()
    scene.render()