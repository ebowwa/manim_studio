"""
Demo showcasing enhanced easing functions in timeline animations.

This example demonstrates how the math3d utilities have been integrated
into the timeline system to create smooth, professional animations.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from manim import *
from src.core.timeline import ComposerTimeline, InterpolationType
from src.core.timeline.timeline_presets import TimelinePresets
from src.core.timeline.easing import EasingFunction, EasingPresets
from src.components.effects import EffectTransitions, WaveEffect, RippleEffect


class EnhancedEasingDemo(Scene):
    """Demonstrates various easing functions and their visual impact."""
    
    def construct(self):
        # Create title
        title = Text("Enhanced Easing Functions", font_size=48)
        subtitle = Text("Powered by Math3D Utilities", font_size=24, color=GRAY)
        subtitle.next_to(title, DOWN)
        
        self.play(
            Write(title),
            FadeIn(subtitle, shift=UP*0.3),
            run_time=2
        )
        self.wait(1)
        self.play(FadeOut(VGroup(title, subtitle)))
        
        # Demo 1: Smooth Step Variations
        self.demo_smooth_steps()
        self.wait(1)
        
        # Demo 2: Elastic and Bounce Easing
        self.demo_elastic_bounce()
        self.wait(1)
        
        # Demo 3: Material Design Preset
        self.demo_material_design()
        self.wait(1)
        
        # Demo 4: Complex Timeline Animation
        self.demo_complex_timeline()
    
    def demo_smooth_steps(self):
        """Demonstrate smooth step easing variations."""
        header = Text("Smooth Step Variations", font_size=36).to_edge(UP)
        self.play(Write(header))
        
        # Create objects for comparison
        labels = ["Linear", "Smooth", "Smoother", "Smoothest"]
        colors = [RED, BLUE, GREEN, PURPLE]
        
        dots = VGroup()
        paths = VGroup()
        
        for i, (label, color) in enumerate(zip(labels, colors)):
            # Create dot
            dot = Dot(radius=0.15, color=color)
            dot.move_to(LEFT * 5 + UP * (1.5 - i))
            
            # Create path line
            path = Line(
                start=LEFT * 5 + UP * (1.5 - i),
                end=RIGHT * 5 + UP * (1.5 - i),
                stroke_width=1,
                color=color
            )
            
            # Add label
            text = Text(label, font_size=20, color=color)
            text.next_to(path, LEFT, buff=0.5)
            
            dots.add(dot)
            paths.add(VGroup(path, text))
        
        self.play(
            *[Create(path) for path in paths],
            *[FadeIn(dot) for dot in dots],
            run_time=1
        )
        
        # Create timeline with different easing functions
        timeline = ComposerTimeline(duration=3.0)
        
        # Add keyframes for each dot with different easing
        easings = [
            InterpolationType.LINEAR,
            InterpolationType.SMOOTH_STEP,
            InterpolationType.EASE_IN_OUT,  # Using smoother as ease in out
            InterpolationType.SMOOTH_STEP   # Will use smoothest via params
        ]
        
        for i, (dot, easing) in enumerate(zip(dots, easings)):
            if i == 3:  # Smoothest
                timeline.add_keyframe("Main", "objects", f"dot_{i}_x",
                                    0, dot.get_x(), InterpolationType.SMOOTH_STEP,
                                    easing_params={'smoothness': 3})
                timeline.add_keyframe("Main", "objects", f"dot_{i}_x",
                                    3, 5, InterpolationType.SMOOTH_STEP,
                                    easing_params={'smoothness': 3})
            else:
                timeline.add_keyframe("Main", "objects", f"dot_{i}_x",
                                    0, dot.get_x(), easing)
                timeline.add_keyframe("Main", "objects", f"dot_{i}_x",
                                    3, 5, easing)
        
        # Animate dots moving
        def update_dots(dt):
            nonlocal timeline
            timeline.current_time += dt
            for i, dot in enumerate(dots):
                x = timeline.get_layer("Main").get_track("objects").get_value_at_time(
                    f"dot_{i}_x", timeline.current_time
                )
                if x is not None:
                    dot.move_to([x, dot.get_y(), 0])
        
        # Reset timeline
        timeline.current_time = 0
        self.add(dots)
        
        # Play animation
        self.play(UpdateFromFunc(dots, update_dots), run_time=3)
        
        self.play(FadeOut(VGroup(dots, paths, header)))
    
    def demo_elastic_bounce(self):
        """Demonstrate elastic and bounce easing."""
        header = Text("Elastic & Bounce Easing", font_size=36).to_edge(UP)
        self.play(Write(header))
        
        # Create squares for different effects
        effects = [
            ("Elastic In", EasingFunction.EASE_IN_ELASTIC, BLUE),
            ("Elastic Out", EasingFunction.EASE_OUT_ELASTIC, GREEN),
            ("Bounce Out", EasingFunction.EASE_OUT_BOUNCE, ORANGE),
            ("Back (Overshoot)", EasingFunction.EASE_OUT_BACK, PURPLE)
        ]
        
        squares = VGroup()
        for i, (name, easing, color) in enumerate(effects):
            square = Square(side_length=1, color=color)
            square.move_to(LEFT * 6 + RIGHT * i * 4 + DOWN)
            
            label = Text(name, font_size=16, color=color)
            label.next_to(square, DOWN)
            
            squares.add(VGroup(square, label))
        
        self.play(*[FadeIn(sq) for sq in squares])
        
        # Create timeline animations
        timeline = ComposerTimeline(duration=2.0)
        
        for i, (_, easing, _) in enumerate(effects):
            # Scale animation
            timeline.add_keyframe("Main", "objects", f"square_{i}_scale",
                                0, 0, InterpolationType.LINEAR)
            
            # Map EasingFunction to InterpolationType
            interp_type = InterpolationType.ELASTIC if "elastic" in easing.value else \
                         InterpolationType.BOUNCE if "bounce" in easing.value else \
                         InterpolationType.BACK
            
            timeline.add_keyframe("Main", "objects", f"square_{i}_scale",
                                2, 1, interp_type,
                                easing_params={'amplitude': 1.5, 'period': 0.3})
        
        # Animate squares
        animations = []
        for i, square_group in enumerate(squares):
            square = square_group[0]
            if i == 0:  # Elastic In
                animations.append(square.animate(run_time=2).scale(1))
            elif i == 1:  # Elastic Out
                animations.append(
                    square.animate(run_time=2, rate_func=elastic_ease_out).scale(1)
                )
            elif i == 2:  # Bounce Out
                animations.append(
                    square.animate(run_time=2, rate_func=bounce_ease_out).scale(1)
                )
            else:  # Back
                animations.append(
                    square.animate(run_time=2, rate_func=ease_out_back).scale(1)
                )
        
        # First scale to 0
        for square_group in squares:
            square_group[0].scale(0)
        
        self.play(*animations)
        self.wait(1)
        
        self.play(FadeOut(VGroup(squares, header)))
    
    def demo_material_design(self):
        """Demonstrate Material Design presets."""
        header = Text("Material Design Animations", font_size=36).to_edge(UP)
        self.play(Write(header))
        
        # Create UI elements
        cards = VGroup()
        for i in range(3):
            card = RoundedRectangle(
                width=3, height=2, corner_radius=0.2,
                fill_color=BLUE_E, fill_opacity=0.8
            )
            card.move_to(LEFT * 4 + RIGHT * i * 4)
            
            # Add content
            title = Text(f"Card {i+1}", font_size=20, color=WHITE)
            title.move_to(card.get_center() + UP * 0.5)
            
            content = Line(LEFT, RIGHT, color=WHITE, stroke_width=2)
            content.scale(0.8)
            content.move_to(card.get_center())
            
            card_group = VGroup(card, title, content)
            cards.add(card_group)
        
        # Use Material Design preset from timeline
        presets = TimelinePresets()
        timeline = ComposerTimeline(duration=5.0)
        
        # Apply Material Design preset
        material_preset = presets.get_preset("material_design")
        if material_preset:
            material_preset.apply(timeline, {
                'element_count': 3,
                'stagger_delay': 0.1,
                'elevation_effect': True,
                'ripple_effect': True
            })
        
        # Animate cards appearing with Material Design timing
        for i, card in enumerate(cards):
            card.shift(DOWN * 5)
            card.set_opacity(0)
        
        animations = []
        for i, card in enumerate(cards):
            # Material standard easing
            animations.append(
                AnimationGroup(
                    card.animate(
                        run_time=0.3,
                        rate_func=bezier([0.4, 0.0, 0.2, 1.0])  # Material standard
                    ).shift(UP * 5).set_opacity(1),
                    lag_ratio=0
                )
            )
        
        self.play(LaggedStart(*animations, lag_ratio=0.1))
        
        # Add ripple effect on click simulation
        for i, card in enumerate(cards):
            ripple = RippleEffect(
                center=card[0].get_center(),
                num_ripples=1,
                max_radius=1.5,
                ripple_color=WHITE,
                ripple_width=2,
                lifetime=0.5
            )
            ripple.create()
            self.add(ripple._mobjects)
            self.play(
                ripple._mobjects[0].animate(run_time=0.5).scale(150).set_stroke(opacity=0),
                rate_func=bezier([0.4, 0.0, 1.0, 1.0])  # Material accelerated
            )
            self.remove(ripple._mobjects)
        
        self.play(FadeOut(VGroup(cards, header)))
    
    def demo_complex_timeline(self):
        """Demonstrate complex timeline with multiple easing types."""
        title = Text("Complex Timeline Animation", font_size=36).to_edge(UP)
        self.play(Write(title))
        
        # Create a complex scene
        circle = Circle(radius=1, color=BLUE)
        square = Square(side_length=1.5, color=RED)
        triangle = Triangle(color=GREEN)
        
        shapes = VGroup(circle, square, triangle)
        shapes.arrange(RIGHT, buff=2)
        
        self.play(*[FadeIn(shape) for shape in shapes])
        
        # Create complex timeline
        timeline = ComposerTimeline(duration=6.0)
        presets = TimelinePresets()
        
        # Apply elastic pop preset to circle
        elastic_preset = presets.get_preset("elastic_pop")
        if elastic_preset:
            # Manually add elastic animations for circle
            timeline.add_keyframe("Main", "objects", "circle_scale",
                                0, 0, InterpolationType.ELASTIC,
                                easing_params={'amplitude': 1.5, 'period': 0.4})
            timeline.add_keyframe("Main", "objects", "circle_scale",
                                1.5, 1, InterpolationType.ELASTIC,
                                easing_params={'amplitude': 1.5, 'period': 0.4})
        
        # Square with smooth morph
        timeline.add_keyframe("Main", "objects", "square_rotation",
                            0, 0, InterpolationType.SMOOTH_STEP)
        timeline.add_keyframe("Main", "objects", "square_rotation",
                            3, TAU, InterpolationType.SMOOTH_STEP)
        
        # Triangle with wave effect
        wave_effect = WaveEffect(
            triangle,
            wave_direction=UP,
            wavelength=0.5,
            amplitude=0.2,
            frequency=2,
            wave_speed=1
        )
        
        # Create transition effect
        transition = EffectTransitions(
            duration=1.0,
            particles_enabled=True,
            color_scheme=PURPLE
        )
        
        # Animate everything
        circle.scale(0)
        self.play(
            circle.animate(run_time=1.5, rate_func=elastic_ease_out).scale(1),
            Rotate(square, TAU, run_time=3, rate_func=smooth),
            run_time=3
        )
        
        # Add wave effect to triangle
        wave_effect.create()
        wave_effect.animate(self)
        
        self.wait(2)
        
        # Final transition
        self.play(
            *[FadeOut(shape, scale=0.5) for shape in shapes],
            FadeOut(title),
            run_time=1
        )


class TimelinePresetsDemo(Scene):
    """Demonstrates the timeline preset system."""
    
    def construct(self):
        # Title
        title = Text("Timeline Presets Showcase", font_size=48)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))
        
        # Create timeline and presets
        timeline = ComposerTimeline(duration=20.0)
        presets = TimelinePresets()
        
        # Demo each preset
        preset_names = [
            "fade_in_out",
            "title_sequence",
            "kinetic_typography",
            "material_design",
            "elastic_pop",
            "smooth_morph"
        ]
        
        for preset_name in preset_names:
            self.demo_preset(preset_name, presets, timeline)
            self.wait(1)
    
    def demo_preset(self, preset_name: str, presets: TimelinePresets, timeline: ComposerTimeline):
        """Demo a specific preset."""
        # Get preset
        preset = presets.get_preset(preset_name)
        if not preset:
            return
        
        # Show preset info
        info = VGroup(
            Text(preset.name.replace("_", " ").title(), font_size=36),
            Text(preset.description, font_size=20, color=GRAY)
        ).arrange(DOWN)
        info.to_edge(UP)
        
        self.play(FadeIn(info))
        
        # Create demo objects based on preset
        if preset_name == "fade_in_out":
            obj = Circle(radius=1, color=BLUE)
            self.add(obj)
            
            # Apply fade preset
            self.play(
                obj.animate(run_time=1).set_opacity(1),
                rate_func=smooth
            )
            self.wait(1)
            self.play(
                obj.animate(run_time=1).set_opacity(0),
                rate_func=smooth
            )
            
        elif preset_name == "material_design":
            # Create material cards
            cards = VGroup(*[
                RoundedRectangle(width=2, height=3, corner_radius=0.2)
                .set_fill(BLUE_E, 0.8)
                .shift(LEFT * 3 + RIGHT * i * 3)
                for i in range(3)
            ])
            
            for card in cards:
                card.shift(DOWN * 5).set_opacity(0)
            
            self.play(
                LaggedStart(*[
                    card.animate(
                        run_time=0.3,
                        rate_func=bezier([0.4, 0.0, 0.2, 1.0])
                    ).shift(UP * 5).set_opacity(1)
                    for card in cards
                ], lag_ratio=0.1)
            )
            
            self.play(FadeOut(cards))
        
        elif preset_name == "elastic_pop":
            shapes = VGroup(
                Circle(radius=0.5, color=RED),
                Square(side_length=1, color=GREEN),
                Triangle(color=BLUE)
            ).arrange(RIGHT, buff=1)
            
            for shape in shapes:
                shape.scale(0)
            
            self.play(
                LaggedStart(*[
                    shape.animate(
                        run_time=1,
                        rate_func=elastic_ease_out
                    ).scale(1)
                    for shape in shapes
                ], lag_ratio=0.2)
            )
            
            self.play(FadeOut(shapes))
        
        self.play(FadeOut(info))


# Utility functions for custom easing
def bezier(control_points):
    """Create a bezier easing function."""
    x1, y1, x2, y2 = control_points
    
    def bezier_ease(t):
        # Simplified bezier calculation
        return 3 * (1-t)**2 * t * y1 + 3 * (1-t) * t**2 * y2 + t**3
    
    return bezier_ease


def elastic_ease_out(t):
    """Elastic ease out function."""
    if t == 0:
        return 0
    if t == 1:
        return 1
    
    p = 0.3
    s = p / 4
    return np.power(2, -10 * t) * np.sin((t - s) * 2 * PI / p) + 1


def bounce_ease_out(t):
    """Bounce ease out function."""
    if t < 1/2.75:
        return 7.5625 * t * t
    elif t < 2/2.75:
        t -= 1.5/2.75
        return 7.5625 * t * t + 0.75
    elif t < 2.5/2.75:
        t -= 2.25/2.75
        return 7.5625 * t * t + 0.9375
    else:
        t -= 2.625/2.75
        return 7.5625 * t * t + 0.984375


def ease_out_back(t):
    """Back (overshoot) ease out."""
    s = 1.70158
    t = t - 1
    return t * t * ((s + 1) * t + s) + 1


if __name__ == "__main__":
    # Run the enhanced easing demo
    from manim import config
    config.pixel_height = 1080
    config.pixel_width = 1920
    config.frame_rate = 60
    
    scene = EnhancedEasingDemo()
    scene.render()