#!/usr/bin/env python
"""Test the improved timeline layer system with proper z-indexing."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from manim import *
from src.core.timeline import ComposerTimeline, create_layered_scene, LayerManager
from src.components.effects import (
    ImprovedSkullEffect, GlowEffect, BokehEffect, 
    RippleEffect, ParticleSystemEffect
)


class ImprovedLayerDemo(Scene):
    def construct(self):
        # Create timeline with improved layer support
        timeline = ComposerTimeline(duration=20.0)
        
        # Create layers with explicit z-indices
        bg_layer = timeline.add_layer("DeepBackground", ["stars"], z_index=0)
        fog_layer = timeline.add_layer("Fog", ["atmosphere"], z_index=50)
        back_layer = timeline.add_layer("Background", ["environment"], z_index=100)
        mid_layer = timeline.add_layer("Midground", ["skulls"], z_index=200)
        fx_layer = timeline.add_layer("Effects", ["particles", "glows"], z_index=300)
        front_layer = timeline.add_layer("Foreground", ["ui"], z_index=400)
        
        # Create layer manager
        layer_manager = LayerManager(timeline)
        
        # Title
        title = Text("Timeline Layer System", font_size=48, weight=BOLD)
        title.to_edge(UP)
        self.add(title)
        layer_manager.register_mobject("Foreground", title)
        
        # Deep background: starfield
        stars = VGroup()
        for _ in range(100):
            star = Dot(
                point=np.random.uniform(-7, 7, 3),
                radius=np.random.uniform(0.01, 0.03),
                color=WHITE
            ).set_opacity(np.random.uniform(0.3, 0.8))
            stars.add(star)
        
        self.add(stars)
        layer_manager.register_mobject("DeepBackground", stars)
        
        # Fog layer: atmospheric effect
        fog_circles = VGroup()
        for i in range(5):
            fog = Circle(
                radius=np.random.uniform(2, 4),
                color=GREY,
                fill_opacity=0.1,
                stroke_opacity=0
            ).shift(np.random.uniform(-4, 4, 3))
            fog_circles.add(fog)
        
        self.add(fog_circles)
        layer_manager.register_mobject("Fog", fog_circles)
        
        # Background: Bokeh effect
        bokeh = BokehEffect(
            num_bokeh=30,
            bokeh_sizes=(0.5, 2.0),
            bokeh_colors=[BLUE_E, PURPLE_E, TEAL_E],
            bokeh_opacity=(0.1, 0.3)
        )
        bokeh_mob = bokeh.create()
        self.add(bokeh_mob)
        layer_manager.register_mobject("Background", bokeh_mob)
        
        # Midground: Multiple skulls at different positions
        skull_positions = [LEFT * 3, ORIGIN, RIGHT * 3]
        skull_styles = ["minimal", "realistic", "stylized"]
        
        for pos, style in zip(skull_positions, skull_styles):
            skull = ImprovedSkullEffect(
                position=pos,
                size=1.5,
                style=style,
                color=WHITE,
                eye_glow=True,
                eye_color=RED if style == "realistic" else BLUE
            )
            skull_mob = skull.create()
            self.add(skull_mob)
            layer_manager.register_mobject("Midground", skull_mob)
        
        # Effects layer: Glows and particles
        for i, pos in enumerate(skull_positions):
            # Create glow effect
            glow = Circle(
                radius=2,
                color=YELLOW if i == 1 else BLUE,
                fill_opacity=0.2,
                stroke_opacity=0
            ).move_to(pos)
            self.add(glow)
            layer_manager.register_mobject("Effects", glow)
        
        # Apply initial ordering
        layer_manager.apply_layer_ordering(self)
        
        # UI overlay
        info_text = VGroup(
            Text("Z-Index Demo", font_size=24),
            Text("Layers are properly ordered", font_size=18, color=GREY)
        ).arrange(DOWN, buff=0.2).to_corner(DL)
        self.add(info_text)
        layer_manager.register_mobject("Foreground", info_text)
        
        self.wait()
        
        # Demonstrate layer reordering
        demo_text = Text("Moving skulls to front...", font_size=20).next_to(info_text, UP)
        self.play(FadeIn(demo_text))
        layer_manager.register_mobject("Foreground", demo_text)
        
        # Move midground to top
        timeline.move_layer_to_top("Midground")
        layer_manager.apply_layer_ordering(self)
        self.wait(2)
        
        # Move back to original position
        self.play(FadeOut(demo_text))
        demo_text = Text("Restoring original order...", font_size=20).next_to(info_text, UP)
        self.play(FadeIn(demo_text))
        layer_manager.register_mobject("Foreground", demo_text)
        
        timeline.set_layer_z_index("Midground", 200)
        layer_manager.apply_layer_ordering(self)
        self.wait(2)
        
        # Hide/show layers
        self.play(FadeOut(demo_text))
        demo_text = Text("Hiding fog layer...", font_size=20).next_to(info_text, UP)
        self.play(FadeIn(demo_text))
        layer_manager.register_mobject("Foreground", demo_text)
        
        layer_manager.hide_layer(self, "Fog")
        self.wait(2)
        
        self.play(FadeOut(demo_text))
        demo_text = Text("Showing fog layer...", font_size=20).next_to(info_text, UP)
        self.play(FadeIn(demo_text))
        layer_manager.register_mobject("Foreground", demo_text)
        
        layer_manager.show_layer(self, "Fog")
        self.wait(2)
        
        # Solo mode
        self.play(FadeOut(demo_text))
        demo_text = Text("Solo mode: Only skulls...", font_size=20).next_to(info_text, UP)
        self.play(FadeIn(demo_text))
        layer_manager.register_mobject("Foreground", demo_text)
        
        layer_manager.solo_layer(self, "Midground")
        self.wait(2)
        
        layer_manager.unsolo_all_layers(self)
        self.wait()
        
        # Final message
        final_text = VGroup(
            Text("Layer System Complete!", font_size=36, weight=BOLD),
            Text("Z-ordering, visibility, and solo modes working", font_size=24)
        ).arrange(DOWN).set_color_by_gradient(GREEN, BLUE)
        
        self.play(
            FadeOut(demo_text),
            Transform(title, final_text)
        )
        self.wait(2)


class LayeredSceneDemo(Scene):
    """Demo using the create_layered_scene factory."""
    
    def construct(self):
        # Create timeline
        timeline = ComposerTimeline(duration=15.0)
        
        # Use factory to create layered scene class
        LayeredSceneClass = create_layered_scene(timeline)
        
        # Create instance and demonstrate
        scene = LayeredSceneClass()
        scene.camera = self.camera
        scene.renderer = self.renderer
        
        # Add content to layers
        scene.add_to_layer("Background", 
            Rectangle(width=14, height=8, color=BLUE_E, fill_opacity=0.2))
        
        scene.add_to_layer("Midground",
            Circle(radius=2, color=RED),
            Square(side_length=3, color=GREEN).shift(RIGHT * 3),
            Triangle(color=YELLOW).shift(LEFT * 3))
        
        scene.add_to_layer("Foreground",
            Text("Layered Scene Demo", font_size=48).to_edge(UP))
        
        # Transfer to main scene
        self.add(*scene.mobjects)
        self.wait(2)
        
        # Demo layer operations
        info = Text("Bringing Background to front...", font_size=24).to_edge(DOWN)
        self.play(Write(info))
        
        scene.bring_layer_to_front("Background")
        self.remove(*self.mobjects)
        self.add(*scene.mobjects)
        self.add(info)
        self.wait(2)
        
        self.play(info.animate.become(
            Text("Sending Background to back...", font_size=24).to_edge(DOWN)
        ))
        
        scene.send_layer_to_back("Background")
        self.remove(*self.mobjects)
        self.add(*scene.mobjects)
        self.add(info)
        self.wait(2)
        
        self.play(FadeOut(info))
        self.wait()


if __name__ == "__main__":
    from manim import config
    config.pixel_height = 1080
    config.pixel_width = 1920
    config.frame_rate = 60
    config.quality = "high_quality"
    
    # Run improved layer demo
    scene = ImprovedLayerDemo()
    scene.render()
    
    # Run layered scene factory demo
    scene2 = LayeredSceneDemo()
    scene2.render()