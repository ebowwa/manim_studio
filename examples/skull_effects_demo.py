"""Demo animation showcasing all skull effects."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from manim import *
from src.manim_studio.components.effects import (
    SkullEffect,
    SkullParticleEffect,
    GhostlySkullEffect,
    SkullTransformEffect,
    GlowEffect,
    NeonEffect,
    RippleEffect,
    BlurEffect
)


class SkullEffectsShowcase(Scene):
    def construct(self):
        # Title
        title = Text("SKULL EFFECTS SHOWCASE", font_size=48)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait()
        
        # Scene 1: Different skull styles
        self.play(FadeOut(title))
        style_title = Text("Skull Styles", font_size=36).to_edge(UP)
        self.play(Write(style_title))
        
        # Normal skull
        normal_skull = SkullEffect(
            position=LEFT * 4,
            size=1,
            style='normal',
            color=WHITE
        )
        normal_label = Text("Normal", font_size=20).next_to(LEFT * 4, DOWN * 2)
        
        # Cute skull
        cute_skull = SkullEffect(
            position=LEFT * 1.3,
            size=1,
            style='cute',
            color=PINK
        )
        cute_label = Text("Cute", font_size=20).next_to(LEFT * 1.3, DOWN * 2)
        
        # Scary skull
        scary_skull = SkullEffect(
            position=RIGHT * 1.3,
            size=1,
            style='scary',
            color=RED,
            eye_glow=True,
            eye_color=YELLOW
        )
        scary_label = Text("Scary", font_size=20).next_to(RIGHT * 1.3, DOWN * 2)
        
        # Pixelated skull
        pixel_skull = SkullEffect(
            position=RIGHT * 4,
            size=1,
            style='pixelated',
            color=GREEN
        )
        pixel_label = Text("Pixel", font_size=20).next_to(RIGHT * 4, DOWN * 2)
        
        # Animate skulls appearing
        for skull, label in [(normal_skull, normal_label), (cute_skull, cute_label), 
                             (scary_skull, scary_label), (pixel_skull, pixel_label)]:
            skull_mob = skull.create()
            self.play(
                FadeIn(skull_mob, scale=0.5),
                Write(label),
                run_time=0.5
            )
        
        self.wait(2)
        
        # Add animations to skulls
        normal_skull_mob = normal_skull.mobjects[0]
        scary_skull_mob = scary_skull.mobjects[0]
        
        # Make scary skull jaw animate
        scary_skull.update_config(animate_jaw=True)
        scary_skull.animate(self)
        
        self.wait(3)
        
        # Clear scene
        self.play(*[FadeOut(mob) for mob in self.mobjects])
        
        # Scene 2: Skull Particle Formation
        particle_title = Text("Particle Formation", font_size=36).to_edge(UP)
        self.play(Write(particle_title))
        
        skull_particles = SkullParticleEffect(
            position=ORIGIN,
            num_particles=800,
            particle_size=0.03,
            particle_color=BLUE,
            glow=True,
            formation_time=3.0
        )
        
        skull_particles.create()
        skull_particles.animate(self)
        
        # Add ripple effect at center
        ripple = RippleEffect(center=ORIGIN, ripple_color=BLUE, num_ripples=3)
        ripple.create()
        ripple.animate(self)
        
        self.wait(2)
        
        # Clear scene
        self.play(*[FadeOut(mob) for mob in self.mobjects if mob != particle_title])
        
        # Scene 3: Ghostly Skull
        self.play(FadeOut(particle_title))
        ghost_title = Text("Ghostly Apparition", font_size=36).to_edge(UP)
        self.play(Write(ghost_title))
        
        # Dark background for better ghost effect
        dark_bg = Rectangle(width=14, height=8, fill_color=BLACK, fill_opacity=0.8)
        self.play(FadeIn(dark_bg))
        
        ghostly = GhostlySkullEffect(
            position=ORIGIN,
            size=2,
            color=BLUE_E,
            base_opacity=0.4,
            fade_cycle_time=3.0,
            num_layers=4
        )
        
        ghostly.create()
        ghostly.animate(self)
        
        # Add some fog/mist effect using blur
        for i in range(3):
            mist = Circle(radius=1 + i * 0.5, color=GREY, fill_opacity=0.1)
            mist.move_to(DOWN * 2)
            self.add(mist)
        
        self.wait(5)
        
        # Clear scene
        self.play(*[FadeOut(mob) for mob in self.mobjects])
        
        # Scene 4: Transform objects into skulls
        transform_title = Text("Skull Transformation", font_size=36).to_edge(UP)
        self.play(Write(transform_title))
        
        # Create various shapes to transform
        circle = Circle(radius=1, color=YELLOW).shift(LEFT * 3)
        square = Square(side_length=1.5, color=GREEN)
        triangle = Triangle(radius=1, color=RED).shift(RIGHT * 3)
        
        self.play(
            Create(circle),
            Create(square),
            Create(triangle)
        )
        self.wait()
        
        # Transform them into skulls
        transforms = []
        for obj, style in [(circle, 'cute'), (square, 'normal'), (triangle, 'scary')]:
            transform = SkullTransformEffect(
                obj,
                skull_size=1,
                skull_style=style,
                transform_time=2.0,
                intermediate_shapes=True,
                final_color=WHITE
            )
            transforms.append(transform)
        
        # Animate transformations
        for transform in transforms:
            transform.create()
            transform.animate(self)
        
        self.wait(2)
        
        # Scene 5: Grand Finale - Multiple effects combined
        self.play(*[FadeOut(mob) for mob in self.mobjects])
        
        finale_title = Text("GRAND FINALE", font_size=48, color=RED)
        finale_title.to_edge(UP)
        self.play(Write(finale_title), run_time=0.5)
        
        # Create a central glowing skull with neon effect
        main_skull = SkullEffect(
            position=ORIGIN,
            size=1.5,
            style='scary',
            color=WHITE,
            eye_glow=True,
            eye_color=RED,
            floating=True
        )
        main_skull_mob = main_skull.create()
        
        # Add glow effect
        glow = GlowEffect(
            main_skull_mob,
            glow_color=RED,
            glow_radius=0.8,
            num_layers=10,
            pulse=True
        )
        glow_mob = glow.create()
        
        # Add neon effect
        neon = NeonEffect(
            main_skull_mob,
            neon_color=PURPLE,
            flicker=True,
            flicker_probability=0.03
        )
        neon_mob = neon.create()
        
        self.play(
            FadeIn(main_skull_mob),
            FadeIn(glow_mob),
            FadeIn(neon_mob)
        )
        
        main_skull.animate(self)
        glow.animate(self)
        neon.animate(self)
        
        # Create orbiting particle skulls
        mini_skulls = VGroup()
        for i in range(6):
            angle = i * TAU / 6
            pos = 3 * np.array([np.cos(angle), np.sin(angle), 0])
            
            mini = SkullEffect(
                position=pos,
                size=0.5,
                style='pixelated',
                color=HSL_TO_RGB([i/6, 1, 0.5])
            )
            mini_mob = mini.create()
            mini_skulls.add(mini_mob)
        
        self.play(
            LaggedStart(*[FadeIn(skull, scale=0.5) for skull in mini_skulls], lag_ratio=0.1)
        )
        
        # Rotate mini skulls around center
        def rotate_updater(mob, dt):
            mob.rotate(0.5 * dt, about_point=ORIGIN)
        
        mini_skulls.add_updater(rotate_updater)
        
        # Add particle streams
        for i in range(4):
            angle = i * TAU / 4 + TAU / 8
            start_pos = 4 * np.array([np.cos(angle), np.sin(angle), 0])
            
            particles = SkullParticleEffect(
                position=start_pos,
                num_particles=200,
                particle_size=0.02,
                particle_color=YELLOW,
                formation_time=2.0
            )
            particles.create()
            self.play(FadeIn(particles.mobjects[0]), run_time=0.5)
        
        self.wait(3)
        
        # Epic ending
        end_text = Text("HAPPY HALLOWEEN!", font_size=60, color=ORANGE)
        end_text.set_stroke(BLACK, width=3)
        
        self.play(
            *[FadeOut(mob, scale=2) for mob in self.mobjects if mob != finale_title],
            FadeIn(end_text, scale=0.5),
            finale_title.animate.set_color(ORANGE),
            run_time=2
        )
        
        self.wait(2)


# Run the animation
if __name__ == "__main__":
    from manim import config
    config.pixel_height = 1080
    config.pixel_width = 1920
    config.frame_rate = 60
    
    scene = SkullEffectsShowcase()
    scene.render()