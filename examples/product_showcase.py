"""Product showcase animation using the enhanced timeline system."""

from manim import *
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.manim_studio.core.timeline_enhanced import (
    EnhancedTimeline, InterpolationType, Keyframe, TrackType
)
from src.manim_studio.components.timeline_visualizer import TimelineVisualizer
from src.manim_studio.core.timeline_presets import TimelinePresets
from src.manim_studio.utils.timeline_debugger import TimelineDebugger

class ProductShowcase(Scene):
    """Professional product showcase using enhanced timeline."""
    
    def construct(self):
        # Create timeline
        timeline = EnhancedTimeline(duration=15.0, fps=60.0)
        
        # === CREATE SCENE OBJECTS ===
        
        # Product name
        product_name = Text("MANIM STUDIO", font_size=72, weight=BOLD)
        product_name.set_color_by_gradient(BLUE, PURPLE)
        
        # Tagline
        tagline = Text("Professional Animation Framework", font_size=32)
        tagline.next_to(product_name, DOWN, buff=0.5)
        
        # Feature cards
        features = VGroup()
        feature_texts = [
            ("Timeline System", "Advanced keyframe animation"),
            ("Visual Effects", "Particles, shaders, and more"),
            ("Configuration", "JSON/YAML scene definitions"),
            ("MCP Integration", "AI-powered creation")
        ]
        
        for i, (title, desc) in enumerate(feature_texts):
            card = self.create_feature_card(title, desc)
            card.shift(LEFT * 3 + RIGHT * 2 * i + DOWN * 2)
            features.add(card)
        
        # Logo elements
        logo_circle = Circle(radius=1.5, color=BLUE, stroke_width=4)
        logo_inner = Circle(radius=1.2, color=PURPLE, stroke_width=3)
        logo_text = Text("MS", font_size=48, weight=BOLD)
        logo = VGroup(logo_circle, logo_inner, logo_text)
        logo.shift(UP * 2)
        
        # Background particles (we'll animate these)
        particles = VGroup(*[
            Dot(radius=0.02, color=random_color())
            .move_to([
                np.random.uniform(-7, 7),
                np.random.uniform(-4, 4),
                0
            ])
            for _ in range(50)
        ])
        
        # Add all objects to scene (initially hidden)
        self.add(product_name, tagline, features, logo, particles)
        for obj in self.mobjects:
            obj.set_opacity(0)
        
        # === SETUP TIMELINE LAYERS AND TRACKS ===
        
        # Get layers
        main_layer = timeline.get_layer("Main")
        effects_layer = timeline.get_layer("Effects")
        bg_layer = timeline.get_layer("Background")
        
        # Create specific tracks
        logo_track = main_layer.add_track(TimelineTrack("logo", TrackType.ANIMATION))
        text_track = main_layer.add_track(TimelineTrack("text", TrackType.ANIMATION))
        cards_track = main_layer.add_track(TimelineTrack("cards", TrackType.ANIMATION))
        particle_track = effects_layer.add_track(TimelineTrack("particles", TrackType.EFFECT))
        camera_track = timeline.add_layer("Camera").add_track(TimelineTrack("main_camera", TrackType.CAMERA))
        
        # === ANIMATE LOGO ENTRANCE (0-3s) ===
        
        # Logo scale animation
        logo_track.add_keyframe("scale", Keyframe(0, 0, InterpolationType.EASE_OUT))
        logo_track.add_keyframe("scale", Keyframe(1.5, 1.2, InterpolationType.EASE_OUT))
        logo_track.add_keyframe("scale", Keyframe(2, 1, InterpolationType.SPRING,
                                                 spring_params={"stiffness": 200, "damping": 15}))
        
        # Logo rotation
        logo_track.add_keyframe("rotation", Keyframe(0, -PI/4, InterpolationType.EASE_OUT))
        logo_track.add_keyframe("rotation", Keyframe(2, 0, InterpolationType.EASE_OUT))
        
        # Logo opacity
        logo_track.add_keyframe("opacity", Keyframe(0, 0, InterpolationType.LINEAR))
        logo_track.add_keyframe("opacity", Keyframe(0.5, 1, InterpolationType.EASE_OUT))
        
        # === ANIMATE TEXT (2-5s) ===
        
        # Product name animation
        text_track.add_keyframe("product_y", Keyframe(2, -5, InterpolationType.EASE_OUT))
        text_track.add_keyframe("product_y", Keyframe(3, 0, InterpolationType.EASE_OUT))
        text_track.add_keyframe("product_opacity", Keyframe(2, 0, InterpolationType.LINEAR))
        text_track.add_keyframe("product_opacity", Keyframe(2.5, 1, InterpolationType.EASE_OUT))
        
        # Tagline animation (staggered)
        text_track.add_keyframe("tagline_y", Keyframe(2.5, -5, InterpolationType.EASE_OUT))
        text_track.add_keyframe("tagline_y", Keyframe(3.5, -1, InterpolationType.EASE_OUT))
        text_track.add_keyframe("tagline_opacity", Keyframe(2.5, 0, InterpolationType.LINEAR))
        text_track.add_keyframe("tagline_opacity", Keyframe(3, 1, InterpolationType.EASE_OUT))
        
        # === ANIMATE FEATURE CARDS (4-8s) ===
        
        for i in range(4):
            start_time = 4 + i * 0.5
            
            # Card entrance with bounce
            cards_track.add_keyframe(f"card_{i}_y", Keyframe(start_time, -5, InterpolationType.EASE_OUT))
            cards_track.add_keyframe(f"card_{i}_y", Keyframe(start_time + 1, -2, InterpolationType.SPRING,
                                                            spring_params={"stiffness": 150, "damping": 12}))
            
            # Card opacity
            cards_track.add_keyframe(f"card_{i}_opacity", Keyframe(start_time, 0, InterpolationType.LINEAR))
            cards_track.add_keyframe(f"card_{i}_opacity", Keyframe(start_time + 0.5, 1, InterpolationType.EASE_OUT))
            
            # Card scale for emphasis
            cards_track.add_keyframe(f"card_{i}_scale", Keyframe(start_time, 0.8, InterpolationType.EASE_OUT))
            cards_track.add_keyframe(f"card_{i}_scale", Keyframe(start_time + 0.5, 1.1, InterpolationType.EASE_OUT))
            cards_track.add_keyframe(f"card_{i}_scale", Keyframe(start_time + 0.7, 1, InterpolationType.EASE_IN_OUT))
        
        # === BACKGROUND PARTICLES (continuous) ===
        
        particle_track.add_keyframe("opacity", Keyframe(0, 0, InterpolationType.LINEAR))
        particle_track.add_keyframe("opacity", Keyframe(3, 0.3, InterpolationType.EASE_OUT))
        particle_track.add_keyframe("drift_amount", Keyframe(0, 0, InterpolationType.LINEAR))
        particle_track.add_keyframe("drift_amount", Keyframe(15, 1, InterpolationType.LINEAR))
        
        # === CAMERA MOVEMENTS (8-12s) ===
        
        camera_track.add_keyframe("zoom", Keyframe(8, 1, InterpolationType.EASE_IN_OUT))
        camera_track.add_keyframe("zoom", Keyframe(10, 1.2, InterpolationType.EASE_IN_OUT))
        camera_track.add_keyframe("zoom", Keyframe(12, 1, InterpolationType.EASE_IN_OUT))
        
        # === FINALE (12-15s) ===
        
        # Logo morph to center
        logo_track.add_keyframe("y_position", Keyframe(12, 2, InterpolationType.EASE_IN_OUT))
        logo_track.add_keyframe("y_position", Keyframe(14, 0, InterpolationType.EASE_IN_OUT))
        logo_track.add_keyframe("final_scale", Keyframe(12, 1, InterpolationType.EASE_IN_OUT))
        logo_track.add_keyframe("final_scale", Keyframe(14, 1.5, InterpolationType.EASE_OUT))
        
        # Fade out other elements
        text_track.add_keyframe("product_opacity", Keyframe(12, 1, InterpolationType.EASE_IN))
        text_track.add_keyframe("product_opacity", Keyframe(13, 0, InterpolationType.EASE_IN))
        cards_track.add_keyframe("all_opacity", Keyframe(12, 1, InterpolationType.EASE_IN))
        cards_track.add_keyframe("all_opacity", Keyframe(13, 0, InterpolationType.EASE_IN))
        
        # === ADD TIMELINE EVENTS ===
        
        # Add effects at key moments
        timeline.add_event(1.5, lambda s: s.play(Flash(logo, color=BLUE, flash_radius=2)), 
                          name="logo_flash", tags=["effect"])
        
        timeline.add_event(3, lambda s: s.play(Write(product_name.copy().set_opacity(0.5), run_time=0.5)), 
                          name="text_glow", tags=["effect"])
        
        # Add markers
        timeline.add_marker(0, "Logo Entrance", color=BLUE)
        timeline.add_marker(2, "Text Reveal", color=GREEN)
        timeline.add_marker(4, "Features", color=YELLOW)
        timeline.add_marker(8, "Camera Move", color=ORANGE)
        timeline.add_marker(12, "Finale", color=RED)
        
        # === SETUP DEBUGGER (optional) ===
        
        debugger = TimelineDebugger(timeline)
        debugger.show_overlay = False  # Set to True to see debug info
        
        # === CREATE TIMELINE VISUALIZER ===
        
        show_timeline_viz = False  # Set to True to see timeline
        if show_timeline_viz:
            viz = TimelineVisualizer(timeline, width=12, height=2)
            viz.to_edge(DOWN, buff=0.1)
            self.add(viz)
        
        # === PLAY THE ANIMATION ===
        
        dt = 1.0 / timeline.fps
        for frame in range(int(timeline.duration * timeline.fps)):
            current_time = frame * dt
            timeline.seek(current_time)
            
            # Update logo
            logo_scale = logo_track.get_value_at_time("scale", current_time) or 0
            logo_rotation = logo_track.get_value_at_time("rotation", current_time) or 0
            logo_opacity = logo_track.get_value_at_time("opacity", current_time) or 0
            logo_y = logo_track.get_value_at_time("y_position", current_time) or 2
            final_scale = logo_track.get_value_at_time("final_scale", current_time) or 1
            
            logo.set_opacity(logo_opacity)
            logo.scale(logo_scale / (logo.width / 3))  # Normalize scale
            logo.rotate(logo_rotation - logo.get_angle())
            logo.move_to(UP * logo_y)
            if current_time >= 12:
                logo.scale(final_scale / (logo.width / 3))
            
            # Update text
            product_y = text_track.get_value_at_time("product_y", current_time) or -5
            product_opacity = text_track.get_value_at_time("product_opacity", current_time) or 0
            product_name.set_opacity(product_opacity)
            product_name.move_to(UP * product_y)
            
            tagline_y = text_track.get_value_at_time("tagline_y", current_time) or -5
            tagline_opacity = text_track.get_value_at_time("tagline_opacity", current_time) or 0
            tagline.set_opacity(tagline_opacity)
            tagline.move_to(UP * tagline_y)
            
            # Update cards
            for i, card in enumerate(features):
                card_y = cards_track.get_value_at_time(f"card_{i}_y", current_time) or -5
                card_opacity = cards_track.get_value_at_time(f"card_{i}_opacity", current_time) or 0
                card_scale = cards_track.get_value_at_time(f"card_{i}_scale", current_time) or 1
                all_opacity = cards_track.get_value_at_time("all_opacity", current_time)
                
                if all_opacity is not None:
                    card_opacity = all_opacity
                
                card.set_opacity(card_opacity)
                card.move_to(LEFT * 3 + RIGHT * 2 * i + UP * card_y)
                card.scale(card_scale / (card.width / 2))  # Normalize scale
            
            # Update particles
            particle_opacity = particle_track.get_value_at_time("opacity", current_time) or 0
            drift = particle_track.get_value_at_time("drift_amount", current_time) or 0
            
            particles.set_opacity(particle_opacity)
            for particle in particles:
                # Add drift motion
                particle.shift(RIGHT * 0.01 * drift + UP * 0.005 * np.sin(current_time))
            
            # Camera effects
            zoom = camera_track.get_value_at_time("zoom", current_time) or 1
            if zoom != 1:
                self.camera.frame.scale(zoom / self.camera.frame.width * 14.2)  # Normalize zoom
            
            # Process timeline events
            timeline.play(self)
            
            # Update visualizer if shown
            if show_timeline_viz:
                viz.update_playhead(current_time)
            
            self.wait(dt)
        
        # Hold final frame
        self.wait(2)
    
    def create_feature_card(self, title: str, description: str) -> VGroup:
        """Create a feature card with title and description."""
        # Card background
        card_bg = RoundedRectangle(
            width=3, height=1.5,
            corner_radius=0.2,
            color=BLUE_D,
            fill_opacity=0.8
        )
        
        # Title
        card_title = Text(title, font_size=20, weight=BOLD, color=BLUE)
        card_title.move_to(card_bg.get_top() + DOWN * 0.3)
        
        # Description
        card_desc = Text(description, font_size=14, color=GREY_A)
        card_desc.move_to(card_bg.get_center() + DOWN * 0.2)
        
        # Icon placeholder
        icon = Circle(radius=0.2, color=BLUE, fill_opacity=0.3)
        icon.next_to(card_title, LEFT, buff=0.2)
        
        return VGroup(card_bg, icon, card_title, card_desc)


class DataVisualizationTimeline(Scene):
    """Data visualization with timeline-driven animations."""
    
    def construct(self):
        # Create timeline with presets
        timeline = EnhancedTimeline(duration=10.0)
        presets = TimelinePresets()
        
        # Apply data reveal preset
        data_preset = presets.get_preset("data_reveal")
        data_preset.apply(timeline, {
            "chart_type": "bar",
            "data_points": 5,
            "reveal_style": "sequential"
        })
        
        # Create chart
        title = Text("Quarterly Revenue 2024", font_size=36)
        title.to_edge(UP)
        
        # Data
        data = [
            ("Q1", 2.5, BLUE),
            ("Q2", 3.2, GREEN),
            ("Q3", 2.8, YELLOW),
            ("Q4", 4.1, RED),
            ("Proj", 4.5, PURPLE)
        ]
        
        # Create bars
        bars = VGroup()
        labels = VGroup()
        values = VGroup()
        
        for i, (label, value, color) in enumerate(data):
            # Bar
            bar = Rectangle(
                width=1,
                height=value,
                color=color,
                fill_opacity=0.8
            )
            bar.move_to(LEFT * 4 + RIGHT * 2 * i + UP * (value/2 - 1))
            bars.add(bar)
            
            # Label
            label_text = Text(label, font_size=24)
            label_text.next_to(bar, DOWN, buff=0.3)
            labels.add(label_text)
            
            # Value
            value_text = Text(f"${value}M", font_size=20)
            value_text.next_to(bar, UP, buff=0.1)
            values.add(value_text)
        
        # Add all to scene
        self.add(title, bars, labels, values)
        
        # Get track for custom animations
        main_track = timeline.get_layer("Main").get_track("objects")
        
        # Animate based on timeline
        dt = 1.0 / timeline.fps
        for frame in range(int(timeline.duration * timeline.fps)):
            current_time = frame * dt
            timeline.seek(current_time)
            
            # Update bars based on timeline
            for i, (bar, label, value) in enumerate(zip(bars, labels, values)):
                # Get scale from timeline
                scale_y = main_track.get_value_at_time(f"data_{i}_scale_y", current_time) or 0
                bar.stretch_to_fit_height(scale_y * data[i][1])
                bar.move_to(LEFT * 4 + RIGHT * 2 * i + UP * (scale_y * data[i][1]/2 - 1))
                
                # Get label opacity
                label_opacity = main_track.get_value_at_time(f"label_{i}_opacity", current_time) or 0
                label.set_opacity(label_opacity)
                value.set_opacity(label_opacity)
            
            self.wait(dt)
        
        self.wait(2)


if __name__ == "__main__":
    # Choose which scene to render
    scene = ProductShowcase()
    # scene = DataVisualizationTimeline()
    scene.render()