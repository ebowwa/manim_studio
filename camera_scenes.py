#!/usr/bin/env python3
"""
Camera configuration demonstration scenes
"""

from manim import *
import json
import yaml

# Load configuration data
def load_config(file_path):
    if file_path.endswith('.yaml') or file_path.endswith('.yml'):
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    elif file_path.endswith('.json'):
        with open(file_path, 'r') as f:
            return json.load(f)

# Simple Test Scene
class SimpleTest(Scene):
    def construct(self):
        # Load config
        config = load_config("configs/simple_test.json")
        
        # Set background
        self.camera.background_color = config["background_color"]
        
        # Camera info display
        camera_info = Text(f"Camera: zoom={config['camera']['zoom']}, fov={config['camera']['fov']}", 
                          font_size=24).to_edge(UP)
        self.add(camera_info)
        
        # Create title with gradient effect
        title = Text("Manim Studio v2.0", font_size=60)
        title.set_color_by_gradient("#4A90E2", "#9B59B6")
        title.move_to([0, 0, 0])
        
        # Create subtitle
        subtitle = Text("Configuration-Driven Animation", 
                       color=WHITE, font_size=32)
        subtitle.move_to([0, -1.5, 0])
        
        # Animations based on config
        self.play(Write(title), run_time=2.0)
        self.wait(0.5)
        self.play(FadeIn(subtitle), run_time=1.5)
        self.wait(1.0)


class CinematicShowcase(Scene):
    def construct(self):
        # Load config
        config = load_config("configs/cinematic_showcase.json")
        
        # Set background
        self.camera.background_color = config["background_color"]
        
        # Camera technique labels
        techniques = [
            "Wide Establishing Shot",
            "Close-up Shot", 
            "Tracking Shot",
            "Final Composition"
        ]
        
        # Scene elements
        title = Text("Camera Techniques Showcase", font_size=48)
        title.set_color_by_gradient("#667eea", "#764ba2")
        title.to_edge(UP)
        
        # Main subject
        main_subject = Circle(radius=0.8, color="#ff6b6b", fill_opacity=0.9)
        
        # Supporting elements
        element1 = Rectangle(width=1.5, height=0.5, color="#4ecdc4", fill_opacity=0.8)
        element1.move_to([-3, 1, 0])
        
        element2 = RegularPolygon(5, color="#feca57", fill_opacity=0.7)
        element2.move_to([3, -1, 0])
        
        # Grid background
        grid = VGroup()
        for i in range(-4, 5):
            grid.add(Line([-4, i, 0], [4, i, 0], stroke_width=1, color="#2c2c54", stroke_opacity=0.3))
            grid.add(Line([i, -4, 0], [i, 4, 0], stroke_width=1, color="#2c2c54", stroke_opacity=0.3))
        
        # Technique label
        technique_label = Text(techniques[0], font_size=32).to_edge(DOWN)
        
        # Scene 1: Wide shot - everything appears
        self.play(Write(title), run_time=2.0)
        self.play(FadeIn(technique_label), run_time=1.0)
        self.play(Create(grid), run_time=1.5)
        self.play(FadeIn(main_subject), run_time=1.0)
        self.play(FadeIn(element1), FadeIn(element2), run_time=1.0)
        self.wait(1.0)
        
        # Scene 2: Close-up
        self.play(Transform(technique_label, Text(techniques[1], font_size=32).to_edge(DOWN)))
        self.play(main_subject.animate.scale(1.8), run_time=2.0)
        self.wait(1.0)
        
        # Scene 3: Tracking shot
        self.play(Transform(technique_label, Text(techniques[2], font_size=32).to_edge(DOWN)))
        self.play(main_subject.animate.move_to([3, 0, 0]), run_time=3.0)
        self.play(main_subject.animate.move_to([0, 2, 0]), run_time=2.0)
        self.wait(1.0)
        
        # Scene 4: Final composition
        self.play(Transform(technique_label, Text(techniques[3], font_size=32).to_edge(DOWN)))
        self.play(
            main_subject.animate.scale(0.4).move_to([0, 0, 0]),
            element1.animate.move_to([-2, 0, 0]),
            element2.animate.move_to([2, 0, 0]),
            run_time=2.0
        )
        self.wait(2.0)


class Camera2DShowcase(Scene):
    def construct(self):
        # Load config
        config = load_config("configs/camera_2d_showcase.yaml")
        
        # Set background
        self.camera.background_color = config["background_color"]
        
        # Camera info display
        camera_config = config["camera"]
        camera_info = Text(
            f"2D Camera: pos={camera_config['position']}, zoom={camera_config['zoom']}, fov={camera_config['fov']}°",
            font_size=18
        ).to_edge(UP)
        self.add(camera_info)
        
        # Create title and subtitle
        main_title = Text("2D Camera System", font_size=80)
        main_title.set_color_by_gradient("#667eea", "#764ba2")
        main_title.move_to([0, 3, 0])
        
        subtitle = Text("Position • Zoom • Visual Control", 
                       color=WHITE, font_size=40)
        subtitle.move_to([0, 2, 0])
        
        # Demo labels that change
        demo_label = Text("Standard View", color="#ffd700", font_size=36)
        demo_label.move_to([0, -3.5, 0])
        
        # Reference markers
        center_marker = Circle(radius=0.1, color="#ff6b6b", fill_opacity=1.0)
        center_marker.move_to([0, 0, 0])
        
        nw_marker = Circle(radius=0.3, color="#4ecdc4", fill_opacity=0.8)
        nw_marker.move_to([-4, 2, 0])
        
        ne_marker = Rectangle(width=0.6, height=0.6, color="#45b7b8", fill_opacity=0.8)
        ne_marker.move_to([4, 2, 0])
        
        sw_marker = RegularPolygon(5, color="#feca57", fill_opacity=0.8)
        sw_marker.move_to([-4, -2, 0])
        
        se_marker = Triangle(color="#ff9ff3", fill_opacity=0.8)
        se_marker.move_to([4, -2, 0])
        
        # Grid background
        grid = VGroup()
        # Horizontal lines
        for y in [-3, 0, 3]:
            grid.add(Line([-6, y, 0], [6, y, 0], stroke_width=1, color="#2c2c54", stroke_opacity=0.3))
        # Vertical lines
        for x in [-4, 0, 4]:
            grid.add(Line([x, -4, 0], [x, 4, 0], stroke_width=1, color="#2c2c54", stroke_opacity=0.3))
        
        # === INTRO: Standard View (0-3s) ===
        self.play(Write(main_title), run_time=2.0)
        self.play(FadeIn(subtitle), run_time=1.5)
        self.wait(0.5)
        self.play(FadeIn(demo_label), run_time=1.0)
        self.play(Create(grid), run_time=1.5)
        self.play(FadeIn(center_marker), run_time=0.5)
        
        # === DEMO 1: Show positioning markers (3-6s) ===
        new_label = Text("2D Positioning Demo", color="#ffd700", font_size=36)
        new_label.move_to([0, -3.5, 0])
        self.play(Transform(demo_label, new_label), run_time=0.5)
        
        self.play(FadeIn(nw_marker), run_time=0.5)
        self.wait(0.5)
        self.play(FadeIn(ne_marker), run_time=0.5)
        self.wait(0.5)
        self.play(FadeIn(sw_marker), run_time=0.5)
        self.wait(0.5)
        self.play(FadeIn(se_marker), run_time=0.5)
        self.wait(0.5)
        
        # === DEMO 2: Focus on different quadrants (6-12s) ===
        nw_label = Text("Camera Focus: Northwest", color="#4ecdc4", font_size=36)
        nw_label.move_to([0, -3.5, 0])
        self.play(Transform(demo_label, nw_label), run_time=0.5)
        self.play(nw_marker.animate.scale(2.0), run_time=1.0)
        self.wait(0.5)
        
        se_label = Text("Camera Focus: Southeast", color="#ff9ff3", font_size=36)
        se_label.move_to([0, -3.5, 0])
        self.play(Transform(demo_label, se_label), run_time=0.5)
        self.play(nw_marker.animate.scale(0.5), run_time=0.5)
        self.play(se_marker.animate.scale(2.5), run_time=1.5)
        self.wait(0.5)
        
        # === DEMO 3: Zoom capabilities (12-16s) ===
        zoom_label = Text("2D Camera Zoom: Close-up", color="#ff6b6b", font_size=36)
        zoom_label.move_to([0, -3.5, 0])
        self.play(Transform(demo_label, zoom_label), run_time=0.5)
        self.play(se_marker.animate.scale(0.4), run_time=0.5)
        
        # Simulate zoom by scaling center marker
        self.play(center_marker.animate.scale(3.0), run_time=2.0)
        
        wide_label = Text("2D Camera Zoom: Wide View", color="#feca57", font_size=36)
        wide_label.move_to([0, -3.5, 0])
        self.play(Transform(demo_label, wide_label), run_time=0.5)
        self.play(center_marker.animate.scale(0.2), run_time=1.5)
        
        # === FINALE: Show system capabilities (16-20s) ===
        final_label = Text("2D Camera System: Position + Zoom + Visual Control", 
                          color=WHITE, font_size=30)
        final_label.move_to([0, -3.5, 0])
        self.play(Transform(demo_label, final_label), run_time=0.5)
        self.play(center_marker.animate.scale(5.0), run_time=0.5)
        
        # Final celebration - all markers pulse
        self.play(
            nw_marker.animate.scale(1.5),
            run_time=1.0
        )
        self.play(
            ne_marker.animate.scale(1.5),
            run_time=1.0
        )
        self.play(
            sw_marker.animate.scale(1.5),
            run_time=1.0
        )
        self.play(
            se_marker.animate.scale(1.5),
            run_time=1.0
        )
        
        # Fade out
        self.play(
            FadeOut(main_title, subtitle, demo_label),
            run_time=1.0
        )
        self.wait(1.0)


class JourneyOfDiscovery(Scene):
    def construct(self):
        # Load config
        config = load_config("configs/camera_story.yaml")
        
        # Set background
        self.camera.background_color = config["background_color"]
        
        # Camera info display
        camera_config = config["camera"]
        camera_info = Text(
            f"Camera: pos={camera_config['position']}, zoom={camera_config['zoom']}, fov={camera_config['fov']}°",
            font_size=20
        ).to_edge(UP)
        self.add(camera_info)
        
        # Story elements
        title = Text("The Journey of Discovery", font_size=60)
        title.set_color_by_gradient("#ff6b6b", "#feca57")
        title.move_to([0, 2, 0])
        
        narrator = Text("In a world of infinite possibilities...", 
                       color=WHITE, font_size=36)
        narrator.move_to([0, -2.5, 0])
        
        # Hero (blue circle)
        hero = Circle(radius=0.3, color="#48cae4", fill_opacity=0.8)
        hero.move_to([-3, 0, 0])
        
        # Mountain (triangle)
        mountain = Triangle(color="#636e72", fill_opacity=0.9)
        mountain.scale(3.0).move_to([5, -1, 0])
        
        # Treasure (golden rectangle)  
        treasure = Rectangle(width=0.5, height=0.3, color="#f39c12", fill_opacity=1.0)
        treasure.move_to([8, 1, 0])
        
        # Path
        path = Rectangle(width=12, height=0.1, color="#bdc3c7", fill_opacity=0.6)
        path.move_to([2, -0.5, 0])
        
        # === ACT I: Introduction ===
        self.play(Write(title), run_time=2.5)
        self.play(FadeIn(narrator, shift=UP*0.3), run_time=1.5)
        self.wait(0.5)
        self.play(FadeOut(title), run_time=1.0)
        
        # === ACT II: The Hero Appears ===
        new_narrator = Text("A brave soul begins their quest...", 
                           color=WHITE, font_size=36).move_to([0, -2.5, 0])
        self.play(Transform(narrator, new_narrator), run_time=1.0)
        self.play(FadeIn(hero, shift=RIGHT*0.5), run_time=1.5)
        self.play(Create(path), run_time=2.0)
        
        # === ACT III: The Journey ===
        journey_narrator = Text("The path ahead stretches far and wide...", 
                               color=WHITE, font_size=32).move_to([0, -2.8, 0])
        self.play(Transform(narrator, journey_narrator), run_time=1.0)
        
        # Hero starts moving and mountain appears
        self.play(
            hero.animate.move_to([1, 0, 0]),
            FadeIn(mountain),
            run_time=3.0
        )
        
        # === ACT IV: The Challenge ===
        challenge_narrator = Text("But every journey has its trials...", 
                                 color="#e17055", font_size=38).move_to([0, -2.5, 0])
        self.play(Transform(narrator, challenge_narrator), run_time=1.0)
        self.play(hero.animate.move_to([3, 0, 0]), run_time=2.0)
        
        # === ACT V: The Triumph ===
        triumph_narrator = Text("And in the end, victory awaits the persistent!", 
                              color="#00b894", font_size=40).move_to([0, -2.3, 0])
        self.play(Transform(narrator, triumph_narrator), run_time=1.0)
        
        # Hero reaches treasure
        self.play(hero.animate.move_to([7.5, 1, 0]), run_time=2.5)
        self.play(FadeIn(treasure), run_time=1.5)
        
        # Celebration
        self.play(treasure.animate.scale(1.5), run_time=1.0)
        self.wait(1.0)
        
        # Fade out
        self.play(
            FadeOut(hero, mountain, treasure, path, narrator),
            run_time=2.0
        )