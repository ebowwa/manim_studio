#!/usr/bin/env python
"""Advanced skull animation demo using timeline layers and camera movements."""

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
    BokehEffect
)
from src.core.timeline.composer_timeline import (
    ComposerTimeline, TimelineLayer, TimelineTrack, 
    Keyframe, TrackType, InterpolationType
)


class SkullCinematicShowcase(Scene):
    def construct(self):
        # Initialize timeline system
        timeline = ComposerTimeline(duration=30.0)
        
        # Create layers for organization
        background_layer = timeline.add_layer("Background", ["bokeh", "ambient"])
        midground_layer = timeline.add_layer("Midground", ["skulls", "particles"])
        foreground_layer = timeline.add_layer("Foreground", ["title", "ui"])
        effects_layer = timeline.add_layer("Effects", ["glow", "ripples"])
        
        # Cinematic title with depth
        title = VGroup(
            Text("SKULL", font_size=72, weight=BOLD).set_color(RED),
            Text("CINEMATICS", font_size=48).set_color(WHITE)
        ).arrange(DOWN, buff=0.3)
        title.to_edge(UP).shift(DOWN * 0.5)
        
        # Add metallic shine to title
        shine = Rectangle(
            width=title.width * 1.5,
            height=title.height * 0.1,
            color=WHITE
        ).move_to(title).shift(LEFT * title.width)
        shine.set_sheen_direction(RIGHT)
        
        self.play(
            Write(title),
            shine.animate.shift(RIGHT * title.width * 2),
            run_time=2
        )
        self.wait()
        
        # Scene 1: Depth Showcase with Camera Movement
        subtitle = Text("Depth & Layers", font_size=24).to_edge(DOWN)
        self.play(FadeIn(subtitle))
        
        # Create background atmosphere
        bokeh = BokehEffect(
            num_bokeh=40,
            bokeh_sizes=(0.3, 1.0),
            bokeh_colors=[PURPLE_E, BLUE_E, TEAL_E],
            bokeh_opacity=(0.1, 0.4),
            animation_type='drift'
        )
        bokeh_mob = bokeh.create()
        self.bring_to_back(bokeh_mob)
        self.add(bokeh_mob)
        bokeh.animate(self)
        
        # Create layered skull arrangement
        skull_configs = [
            {"pos": LEFT * 5, "size": 0.8, "style": "minimal", "color": GREY_B, "blur": 0.15},
            {"pos": LEFT * 2.5, "size": 1.0, "style": "stylized", "color": BLUE_C, "blur": 0.08},
            {"pos": ORIGIN, "size": 1.5, "style": "realistic", "color": WHITE, "blur": 0},
            {"pos": RIGHT * 2.5, "size": 1.0, "style": "decorative", "color": GOLD, "blur": 0.08},
            {"pos": RIGHT * 5, "size": 0.8, "style": "minimal", "color": GREY_B, "blur": 0.15}
        ]
        
        skulls = VGroup()
        for i, config in enumerate(skull_configs):
            skull = ImprovedSkullEffect(
                position=config["pos"] + DOWN,
                size=config["size"],
                style=config["style"],
                color=config["color"],
                eye_glow=(config["style"] == "realistic"),
                eye_color=ORANGE
            )
            skull_mob = skull.create()
            
            # Apply depth blur
            if config["blur"] > 0:
                blur = BlurEffect(
                    skull_mob,
                    blur_radius=config["blur"],
                    blur_samples=6,
                    blur_opacity=0.4,
                    preserve_original=True
                )
                skull_mob = blur.create()
            
            skulls.add(skull_mob)
        
        # Staggered appearance
        self.play(
            LaggedStart(*[
                FadeIn(skull, shift=DOWN * 0.5)
                for skull in skulls
            ], lag_ratio=0.2),
            run_time=2
        )
        
        # Camera dolly shot
        # Store original camera state
        original_camera_pos = self.camera.get_frame_center()
        original_camera_width = self.camera.get_frame_width()
        
        # Track from left to right with focus changes
        self.play(
            self.camera.animate.move_to(LEFT * 3).set_width(original_camera_width * 0.7),
            run_time=2
        )
        
        for pos in [LEFT * 2.5, ORIGIN, RIGHT * 2.5, RIGHT * 3]:
            self.play(
                self.camera.animate.move_to(pos + DOWN * 0.5),
                run_time=1.5,
                rate_func=smooth
            )
        
        self.play(
            self.camera.animate.move_to(original_camera_pos).set_width(original_camera_width),
            run_time=2
        )
        
        # Scene 2: Particle Formation with Layers
        self.play(
            FadeOut(skulls),
            FadeOut(subtitle),
            run_time=1
        )
        
        subtitle = Text("Particle Layers", font_size=24).to_edge(DOWN)
        self.play(FadeIn(subtitle))
        
        # Create multi-layer particle system
        particle_groups = []
        colors = [BLUE, PURPLE, PINK]
        radii = [3.5, 3.0, 2.5]
        
        for i, (color, radius) in enumerate(zip(colors, radii)):
            particles = VGroup()
            num_particles = 250 - i * 50
            
            for j in range(num_particles):
                angle = TAU * j / num_particles + i * PI / 6
                r = radius + 0.5 * np.random.random()
                pos = r * np.array([np.cos(angle), np.sin(angle), 0])
                
                particle = Dot(
                    point=pos,
                    radius=0.02 + i * 0.005,
                    color=color
                ).set_opacity(0.8 - i * 0.1)
                
                particles.add(particle)
            
            particle_groups.append(particles)
            self.play(FadeIn(particles), run_time=0.3)
        
        # Form layered skull
        target_skull = ImprovedSkullEffect(
            position=ORIGIN,
            size=2,
            style='realistic'
        )
        target_points = []
        target_mob = target_skull.create()
        
        # Extract points from skull
        for submob in target_mob:
            if hasattr(submob, 'get_points'):
                points = submob.get_points()
                target_points.extend(points[::8])
        
        # Animate particles to skull shape in layers
        all_anims = []
        for i, particles in enumerate(particle_groups):
            layer_offset = (i - 1) * 0.2 * OUT
            for j, particle in enumerate(particles):
                if j < len(target_points) // len(particle_groups):
                    idx = i * (len(target_points) // len(particle_groups)) + j
                    if idx < len(target_points):
                        all_anims.append(
                            particle.animate.move_to(target_points[idx] + layer_offset)
                        )
        
        self.play(*all_anims, run_time=3, lag_ratio=0.001)
        
        # Add ripple effects
        for i in range(3):
            ripple = RippleEffect(
                center=ORIGIN,
                ripple_color=colors[i],
                num_ripples=2,
                max_radius=3 + i * 0.5,
                fade_out=True
            )
            ripple.create()
            ripple.animate(self)
        
        self.wait(2)
        
        # Scene 3: Advanced Composition
        self.play(
            *[FadeOut(group, scale=2) for group in particle_groups],
            FadeOut(subtitle),
            run_time=2
        )
        
        subtitle = Text("Layered Composition", font_size=24).to_edge(DOWN)
        self.play(FadeIn(subtitle))
        
        # Background: Ghostly atmosphere
        ghost_skull = GhostlySkullEffect(
            position=ORIGIN,
            size=4,
            color=BLUE_E,
            base_opacity=0.15,
            num_layers=6,
            fade_cycle_time=6.0
        )
        ghost_mob = ghost_skull.create()
        self.add(ghost_mob)
        self.bring_to_back(ghost_mob)
        ghost_skull.animate(self)
        
        # Midground: Main skull
        main_skull = ImprovedSkullEffect(
            position=ORIGIN,
            size=2,
            style='stylized',
            color=WHITE,
            eye_glow=True,
            eye_color=RED
        )
        main_mob = main_skull.create()
        
        # Add neon effect
        neon = NeonEffect(
            main_mob,
            neon_color=PURPLE,
            secondary_color=PINK,
            flicker=True,
            flicker_probability=0.02
        )
        neon_mob = neon.create()
        
        self.play(
            FadeIn(main_mob, scale=0.8),
            FadeIn(neon_mob),
            run_time=2
        )
        neon.animate(self)
        
        # Foreground: Dynamic glow
        glow = GlowEffect(
            main_mob,
            glow_color=YELLOW,
            glow_radius=0.8,
            num_layers=12,
            pulse=True,
            pulse_rate=0.5
        )
        glow_mob = glow.create()
        
        self.play(FadeIn(glow_mob), run_time=1)
        glow.animate(self)
        
        # Camera orbit effect (simulate with movement)
        self.play(
            self.camera.animate.move_to(RIGHT * 2),
            title.animate.set_opacity(0.3),
            run_time=2
        )
        self.play(
            self.camera.animate.move_to(LEFT * 2),
            run_time=2
        )
        
        # Add floating particles
        ambient_particles = VGroup()
        for _ in range(50):
            pos = np.random.uniform(-4, 4, 3)
            pos[2] = 0
            particle = Dot(
                point=pos,
                radius=0.01,
                color=random_color()
            ).set_opacity(0.5)
            ambient_particles.add(particle)
        
        self.play(FadeIn(ambient_particles))
        
        # Float particles
        for particle in ambient_particles:
            particle.add_updater(
                lambda m, dt: m.shift(UP * 0.02 * dt + RIGHT * 0.01 * np.sin(self.renderer.time))
            )
        
        self.wait(3)
        
        # Grand Finale
        self.play(
            FadeOut(subtitle),
            title.animate.set_opacity(1).scale(1.2),
            self.camera.animate.set_width(self.camera.get_frame_width() * 1.5),
            run_time=2
        )
        
        # Final title card
        final_text = VGroup(
            Text("MANIM STUDIO", font_size=60, weight=BOLD),
            Text("Advanced Visual Effects", font_size=30, slant=ITALIC)
        ).arrange(DOWN, buff=0.5)
        final_text.set_color_by_gradient(RED, ORANGE, YELLOW)
        
        self.play(
            *[FadeOut(mob) for mob in self.mobjects if mob != title and mob != final_text],
            Transform(title, final_text),
            run_time=3
        )
        
        self.wait(2)


if __name__ == "__main__":
    from manim import config
    config.pixel_height = 1080
    config.pixel_width = 1920
    config.frame_rate = 60
    config.quality = "high_quality"
    
    scene = SkullCinematicShowcase()
    scene.render()