#!/usr/bin/env python
"""Test improved skull designs."""

# Configure Manim to use user-data directory
from src.config.manim_config import config

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from manim import *
from src.components.effects import (
    ImprovedSkullEffect,
    GlowEffect,
    NeonEffect,
    RippleEffect,
    ParticleSystem,
    WaveEffect
)


class ImprovedSkullShowcase(Scene):
    def construct(self):
        # Title
        title = Text("IMPROVED SKULL DESIGNS", font_size=48, gradient=(RED, WHITE))
        title.to_edge(UP)
        self.play(Write(title))
        self.wait()
        
        # Scene 1: Compare old vs new realistic skull
        self.play(title.animate.set_opacity(0.3))
        
        # Show realistic skull with details
        realistic_skull = ImprovedSkullEffect(
            position=ORIGIN,
            size=2,
            style='realistic',
            color=WHITE,
            detail_level='high',
            add_shadows=True,
            eye_glow=True,
            eye_color=ORANGE
        )
        
        skull_mob = realistic_skull.create()
        
        # Add dramatic lighting
        spotlight = Circle(radius=3, color=YELLOW)
        spotlight.set_fill(YELLOW, opacity=0.1)
        spotlight.move_to(skull_mob.get_center())
        
        self.play(
            FadeIn(spotlight),
            FadeIn(skull_mob, scale=0.5),
            run_time=2
        )
        
        # Rotate to show 3D-like quality
        self.play(
            Rotate(skull_mob, angle=PI/6, axis=UP),
            run_time=2
        )
        self.play(
            Rotate(skull_mob, angle=-PI/3, axis=UP),
            run_time=2
        )
        self.play(
            Rotate(skull_mob, angle=PI/6, axis=UP),
            run_time=2
        )
        
        self.wait(2)
        
        # Scene 2: Show all skull styles
        self.play(
            FadeOut(skull_mob),
            FadeOut(spotlight),
            title.animate.set_opacity(1)
        )
        
        styles_text = Text("Skull Style Variations", font_size=36).to_edge(UP)
        self.play(Transform(title, styles_text))
        
        # Create skull style grid
        styles = [
            ("Realistic", "realistic", WHITE),
            ("Stylized", "stylized", BLUE_E),
            ("Minimal", "minimal", GREY_A),
            ("Decorative", "decorative", GOLD)
        ]
        
        skull_grid = VGroup()
        positions = [
            UP * 1.5 + LEFT * 3,
            UP * 1.5 + RIGHT * 3,
            DOWN * 1.5 + LEFT * 3,
            DOWN * 1.5 + RIGHT * 3
        ]
        
        for (name, style, color), pos in zip(styles, positions):
            skull = ImprovedSkullEffect(
                position=pos,
                size=1,
                style=style,
                color=color,
                detail_level='medium',
                eye_glow=(style in ['realistic', 'stylized']),
                eye_color=RED if style == 'realistic' else YELLOW
            )
            skull_mob = skull.create()
            
            label = Text(name, font_size=24, color=color)
            label.next_to(pos + DOWN * 1.8, DOWN)
            
            skull_grid.add(VGroup(skull_mob, label))
        
        self.play(
            LaggedStart(*[
                AnimationGroup(
                    FadeIn(group[0], scale=0.5),
                    Write(group[1])
                ) for group in skull_grid
            ], lag_ratio=0.2),
            run_time=3
        )
        
        self.wait(3)
        
        # Scene 3: Particle skull with improved design
        self.play(
            FadeOut(skull_grid),
            title.animate.set_opacity(0.3)
        )
        
        particle_text = Text("Enhanced Particle Formation", font_size=36).to_edge(UP)
        self.play(Transform(title, particle_text))
        
        # Create a simple particle effect that forms a skull
        num_particles = 300
        particles = VGroup()
        
        # Create target skull for particle positions
        target_skull = ImprovedSkullEffect(
            position=ORIGIN,
            size=1.5,
            style='minimal',  # Use minimal for clearer outline
            color=PURPLE
        )
        target_shape = target_skull.create()
        
        # Get points from skull outline
        skull_points = []
        for mob in target_shape:
            if hasattr(mob, 'get_points'):
                points = mob.get_points()
                skull_points.extend(points[::10])  # Sample every 10th point
        
        # Create particles at random positions
        for i in range(min(num_particles, len(skull_points))):
            angle = TAU * np.random.random()
            radius = 3 + np.random.random()
            start_pos = radius * np.array([np.cos(angle), np.sin(angle), 0])
            
            particle = Dot(
                point=start_pos,
                radius=0.03,
                color=interpolate_color(BLUE, PURPLE, i/num_particles)
            )
            particle.set_glow_factor(0.5)
            particles.add(particle)
        
        self.play(FadeIn(particles))
        
        # Animate particles to skull points
        if len(skull_points) > 0:
            particle_anims = []
            for i, particle in enumerate(particles):
                if i < len(skull_points):
                    particle_anims.append(
                        particle.animate.move_to(skull_points[i])
                    )
            
            self.play(
                *particle_anims,
                run_time=3,
                rate_func=smooth
            )
        
        self.wait(2)
        
        # Scene 4: Animated features
        self.play(
            FadeOut(particles),
            title.animate.set_opacity(1)
        )
        
        animated_text = Text("Animated Skull Effects", font_size=36).to_edge(UP)
        self.play(Transform(title, animated_text))
        
        # Create animated skull with wave effect
        animated_skull = ImprovedSkullEffect(
            position=ORIGIN,
            size=1.5,
            style='stylized',
            color=GREEN,
            eye_glow=True,
            eye_color=YELLOW
        )
        
        skull_mob = animated_skull.create()
        self.play(FadeIn(skull_mob))
        
        # Apply wave effect
        wave = WaveEffect(
            skull_mob,
            wave_direction=RIGHT,
            wavelength=1.0,
            amplitude=0.1,
            frequency=1.0,
            wave_speed=1.0
        )
        wave_mob = wave.create()
        wave.animate(self)
        
        # Add pulsing glow
        glow = GlowEffect(
            skull_mob,
            glow_color=GREEN,
            glow_radius=0.5,
            num_layers=5,
            pulse=True,
            pulse_rate=0.5
        )
        glow_mob = glow.create()
        glow.animate(self)
        
        self.wait(3)
        
        # Finale
        self.play(
            *[FadeOut(mob) for mob in self.mobjects]
        )
        
        final_text = VGroup(
            Text("ANATOMICALLY", font_size=40, color=RED),
            Text("IMPROVED", font_size=50, color=WHITE),
            Text("SKULLS", font_size=60, color=RED)
        ).arrange(DOWN)
        
        self.play(
            LaggedStart(*[
                Write(text, run_time=1) for text in final_text
            ], lag_ratio=0.3)
        )
        
        # Add final skull behind text
        final_skull = ImprovedSkullEffect(
            position=ORIGIN,
            size=3,
            style='realistic',
            color=RED,
            detail_level='high',
            add_shadows=True,
            eye_glow=True,
            eye_color=WHITE
        )
        
        final_skull_mob = final_skull.create()
        final_skull_mob.set_opacity(0.3)
        final_skull_mob.set_z_index(-1)
        
        self.play(
            FadeIn(final_skull_mob, scale=2),
            final_text.animate.set_fill(WHITE, opacity=1).set_stroke(BLACK, width=3),
            run_time=2
        )
        
        self.wait(3)


if __name__ == "__main__":
    from manim import config
    config.pixel_height = 1080
    config.pixel_width = 1920
    config.frame_rate = 60
    config.quality = "high_quality"
    
    scene = ImprovedSkullShowcase()
    scene.render()