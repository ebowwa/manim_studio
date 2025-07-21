#!/usr/bin/env python
"""Advanced skull animation demo using timeline layers and camera movements."""

# Configure Manim to use user-data directory
from src.config.manim_config import config

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from manim import *
import numpy as np
from src.components.effects import (
    ImprovedSkullEffect,
    SkullParticleEffect,
    GhostlySkullEffect,
    GlowEffect,
    NeonEffect,
    RippleEffect,
    WaveEffect,
    BlurEffect,
    DepthOfFieldEffect,
    BokehEffect
)
from src.core.timeline import Timeline, TimelineLayer, TimelineTrack, Keyframe
from src.core.timeline.composer_timeline import ComposerTimeline, TrackType, InterpolationType


class SkullLayeredShowcase(Scene):
    def construct(self):
        # Initialize timeline system
        timeline = ComposerTimeline(duration=30.0)
        
        # Create layers for different depth levels
        background_layer = timeline.add_layer("background", z_index=-2)
        midground_layer = timeline.add_layer("midground", z_index=0)
        foreground_layer = timeline.add_layer("foreground", z_index=1)
        effects_layer = timeline.add_layer("effects", z_index=2)
        
        # Title with gradient
        title = Text(
            "LAYERED SKULL CINEMATICS",
            font_size=56,
            gradient=(RED, ORANGE, YELLOW)
        )
        title.to_edge(UP)
        
        # Add title to foreground layer
        title_track = foreground_layer.add_track("title", TrackType.TRANSFORM)
        title_track.add_keyframe(0, {"opacity": 0, "scale": 0.5})
        title_track.add_keyframe(1, {"opacity": 1, "scale": 1})
        title_track.add_keyframe(28, {"opacity": 1, "scale": 1})
        title_track.add_keyframe(30, {"opacity": 0, "scale": 1.5})
        
        self.play(Write(title))
        
        # Scene 1: Depth of Field Demo
        self.camera.frame.save_state()
        
        # Create background bokeh
        bokeh = BokehEffect(
            num_bokeh=50,
            bokeh_sizes=(0.2, 0.8),
            bokeh_colors=[PURPLE_E, BLUE_E, TEAL_E],
            bokeh_opacity=(0.1, 0.3),
            animation_type='drift'
        )
        bokeh_mob = bokeh.create()
        bokeh_mob.set_z_index(-3)
        
        # Background track for bokeh
        bokeh_track = background_layer.add_track("bokeh", TrackType.ANIMATION)
        bokeh_track.add_keyframe(0, {"start": True})
        
        self.add(bokeh_mob)
        bokeh.animate(self)
        
        # Create skulls at different depths
        skulls = []
        positions = [
            (LEFT * 4, -1, "Minimal"),
            (LEFT * 2, -0.5, "Stylized"),
            (ORIGIN, 0, "Realistic"),
            (RIGHT * 2, 0.5, "Decorative"),
            (RIGHT * 4, 1, "Minimal")
        ]
        
        skull_styles = ["minimal", "stylized", "realistic", "decorative", "minimal"]
        colors = [GREY_B, BLUE, WHITE, GOLD, GREY_B]
        
        for i, ((pos, z_depth, label), style, color) in enumerate(zip(positions, skull_styles, colors)):
            skull = ImprovedSkullEffect(
                position=pos + DOWN * 0.5,
                size=1.2 - abs(z_depth) * 0.2,  # Size based on depth
                style=style,
                color=color,
                eye_glow=True if style == "realistic" else False,
                eye_color=RED
            )
            skull_mob = skull.create()
            skull_mob.set_z_index(z_depth)
            
            # Apply blur based on depth
            if abs(z_depth) > 0.5:
                blur = BlurEffect(
                    skull_mob,
                    blur_radius=abs(z_depth) * 0.1,
                    blur_samples=5,
                    blur_opacity=0.3
                )
                skull_mob = blur.create()
            
            skulls.append((skull_mob, label))
            
            # Add to appropriate layer based on z_depth
            if z_depth < -0.3:
                layer = background_layer
            elif z_depth > 0.3:
                layer = foreground_layer
            else:
                layer = midground_layer
            
            track = layer.add_track(f"skull_{i}", TrackType.TRANSFORM)
            track.add_keyframe(2 + i * 0.5, {"opacity": 0, "position": pos + UP})
            track.add_keyframe(3 + i * 0.5, {"opacity": 1, "position": pos + DOWN * 0.5})
        
        # Animate skulls appearing with depth
        for i, (skull_mob, label) in enumerate(skulls):
            self.play(
                FadeIn(skull_mob, shift=DOWN),
                run_time=0.5
            )
        
        self.wait()
        
        # Camera movement through layers
        camera_track = timeline.add_track("camera", TrackType.CAMERA)
        camera_track.add_keyframe(5, {"position": ORIGIN, "zoom": 1})
        camera_track.add_keyframe(8, {"position": RIGHT * 2, "zoom": 1.5})
        camera_track.add_keyframe(11, {"position": LEFT * 2, "zoom": 1.5})
        camera_track.add_keyframe(14, {"position": ORIGIN, "zoom": 0.8})
        
        # Animate camera movement
        self.play(
            self.camera.frame.animate.move_to(RIGHT * 2).scale(0.7),
            run_time=3
        )
        self.play(
            self.camera.frame.animate.move_to(LEFT * 2),
            run_time=3
        )
        self.play(
            self.camera.frame.animate.move_to(ORIGIN).scale(1.4),
            run_time=3
        )
        
        # Scene 2: Particle Layer Effects
        self.play(
            *[FadeOut(skull[0]) for skull in skulls],
            self.camera.frame.animate.restore(),
            run_time=2
        )
        
        # Create multi-layered particle effect
        particle_layers = []
        layer_configs = [
            {"color": BLUE, "num": 200, "z": -1, "radius": 3},
            {"color": PURPLE, "num": 300, "z": 0, "radius": 2.5},
            {"color": PINK, "num": 200, "z": 1, "radius": 2}
        ]
        
        for config in layer_configs:
            particles = VGroup()
            for _ in range(config["num"]):
                angle = TAU * np.random.random()
                radius = config["radius"] + np.random.random()
                start_pos = radius * np.array([np.cos(angle), np.sin(angle), 0])
                
                particle = Dot(
                    point=start_pos,
                    radius=0.02,
                    color=config["color"]
                )
                particle.set_z_index(config["z"])
                particles.add(particle)
            
            particle_layers.append(particles)
            self.play(FadeIn(particles), run_time=0.5)
        
        # Form layered skull shape
        target_skull = ImprovedSkullEffect(
            position=ORIGIN,
            size=2,
            style='realistic',
            color=WHITE
        )
        target_shape = target_skull.create()
        
        # Get skull outline points
        skull_points = []
        for mob in target_shape:
            if hasattr(mob, 'get_points'):
                points = mob.get_points()
                skull_points.extend(points[::5])
        
        # Animate particles to form skull at different layers
        for layer_idx, particles in enumerate(particle_layers):
            particle_anims = []
            points_per_layer = len(skull_points) // len(particle_layers)
            start_idx = layer_idx * points_per_layer
            
            for i, particle in enumerate(particles):
                if start_idx + i < len(skull_points):
                    target_point = skull_points[start_idx + i]
                    # Add slight offset for depth
                    offset = (layer_idx - 1) * 0.1 * OUT
                    particle_anims.append(
                        particle.animate.move_to(target_point + offset)
                    )
            
            self.play(
                *particle_anims,
                run_time=2,
                lag_ratio=0.01
            )
        
        # Add ripple effects at different layers
        for i in range(3):
            ripple = RippleEffect(
                center=ORIGIN,
                ripple_color=interpolate_color(BLUE, PINK, i/2),
                num_ripples=3,
                max_radius=3 + i,
                ripple_width=2
            )
            ripple_mob = ripple.create()
            ripple_mob.set_z_index(-1 + i * 0.5)
            
            ripple_track = effects_layer.add_track(f"ripple_{i}", TrackType.ANIMATION)
            ripple_track.add_keyframe(20 + i * 0.5, {"start": True})
            
            ripple.animate(self)
        
        self.wait(2)
        
        # Scene 3: Advanced Layered Effects
        self.play(
            *[FadeOut(layer, scale=2) for layer in particle_layers],
            run_time=2
        )
        
        # Create final composition with multiple layers
        # Background: Ghostly skull
        ghost = GhostlySkullEffect(
            position=ORIGIN,
            size=3,
            color=BLUE_E,
            base_opacity=0.2,
            num_layers=5
        )
        ghost_mob = ghost.create()
        ghost_mob.set_z_index(-1)
        
        # Midground: Main skull with neon
        main_skull = ImprovedSkullEffect(
            position=ORIGIN,
            size=2,
            style='stylized',
            color=WHITE,
            eye_glow=True,
            eye_color=RED
        )
        main_mob = main_skull.create()
        
        neon = NeonEffect(
            main_mob,
            neon_color=PURPLE,
            secondary_color=PINK,
            flicker=True,
            brightness=0.8
        )
        neon_mob = neon.create()
        neon_mob.set_z_index(0.5)
        
        # Foreground: Glowing accents
        glow = GlowEffect(
            main_mob,
            glow_color=YELLOW,
            glow_radius=1,
            num_layers=10,
            pulse=True,
            pulse_rate=0.5
        )
        glow_mob = glow.create()
        glow_mob.set_z_index(1)
        
        # Animate final composition
        self.play(
            FadeIn(ghost_mob, scale=0.8),
            run_time=2
        )
        ghost.animate(self)
        
        self.play(
            FadeIn(main_mob),
            FadeIn(neon_mob),
            run_time=2
        )
        neon.animate(self)
        
        self.play(
            FadeIn(glow_mob),
            run_time=2
        )
        glow.animate(self)
        
        # Final camera movement
        self.play(
            self.camera.frame.animate.scale(0.8).shift(UP * 0.5),
            run_time=2
        )
        
        # Rotate camera around subject
        self.play(
            Rotating(
                self.camera.frame,
                angle=PI/4,
                about_point=ORIGIN,
                run_time=3
            )
        )
        
        # End title
        end_text = VGroup(
            Text("DEPTH", font_size=40, color=BLUE),
            Text("LAYERS", font_size=50, color=WHITE),
            Text("CINEMA", font_size=60, color=RED)
        ).arrange(DOWN)
        end_text.set_z_index(10)
        
        self.play(
            FadeOut(title),
            Write(end_text),
            self.camera.frame.animate.restore(),
            run_time=3
        )
        
        self.wait(2)


if __name__ == "__main__":
    from manim import config
    config.pixel_height = 1080
    config.pixel_width = 1920
    config.frame_rate = 60
    config.quality = "high_quality"
    
    scene = SkullLayeredShowcase()
    scene.render()