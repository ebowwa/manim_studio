"""Demo showcasing the composer timeline system."""

from manim import *
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.manim_studio.core.composer_timeline import (
    ComposerTimeline, InterpolationType, Keyframe
)
from src.manim_studio.components.timeline_visualizer import TimelineVisualizer
from src.manim_studio.components.keyframe_editor import KeyframeEditor
from src.manim_studio.core.timeline_presets import TimelinePresets, PresetCategory
from src.manim_studio.utils.timeline_debugger import TimelineDebugger

class ComposerTimelineDemo(Scene):
    """Demonstrates composer timeline features."""
    
    def construct(self):
        # Create composer timeline
        timeline = ComposerTimeline(duration=10.0, fps=60.0)
        
        # Add some test objects
        title = Text("Composer Timeline Demo", font_size=48)
        subtitle = Text("Layers, Tracks, and Keyframes", font_size=24)
        subtitle.next_to(title, DOWN)
        
        circle = Circle(radius=1, color=BLUE)
        square = Square(side_length=2, color=RED)
        triangle = Triangle(color=GREEN)
        
        # Position objects
        circle.shift(LEFT * 3)
        square.shift(RIGHT * 3)
        triangle.shift(DOWN * 2)
        
        # Add objects to scene
        self.add(title, subtitle, circle, square, triangle)
        
        # Setup timeline layers and tracks
        main_layer = timeline.get_layer("Main")
        shapes_track = main_layer.get_track("shapes")
        text_track = main_layer.get_track("text")
        
        # Add keyframes for circle animation
        shapes_track.add_keyframe("circle_x", Keyframe(0, -3, InterpolationType.EASE_IN_OUT))
        shapes_track.add_keyframe("circle_x", Keyframe(2, 3, InterpolationType.EASE_IN_OUT))
        shapes_track.add_keyframe("circle_x", Keyframe(4, -3, InterpolationType.SPRING,
                                                      spring_params={"stiffness": 150, "damping": 10}))
        
        shapes_track.add_keyframe("circle_scale", Keyframe(0, 1, InterpolationType.LINEAR))
        shapes_track.add_keyframe("circle_scale", Keyframe(2, 2, InterpolationType.EASE_OUT))
        shapes_track.add_keyframe("circle_scale", Keyframe(4, 1, InterpolationType.EASE_IN))
        
        # Add keyframes for square animation
        shapes_track.add_keyframe("square_rotation", Keyframe(0, 0, InterpolationType.LINEAR))
        shapes_track.add_keyframe("square_rotation", Keyframe(5, TAU, InterpolationType.CUBIC_BEZIER,
                                                            bezier_points=(0.4, 0, 0.6, 1)))
        
        # Add keyframes for text fade
        text_track.add_keyframe("title_opacity", Keyframe(0, 1, InterpolationType.LINEAR))
        text_track.add_keyframe("title_opacity", Keyframe(3, 0.2, InterpolationType.EASE_IN))
        text_track.add_keyframe("title_opacity", Keyframe(6, 1, InterpolationType.EASE_OUT))
        
        # Add events
        timeline.add_event(1.0, lambda s: s.play(Flash(circle)), name="circle_flash")
        timeline.add_event(3.0, lambda s: s.play(Indicate(square)), name="square_indicate")
        timeline.add_event(5.0, lambda s: s.play(FadeOut(triangle)), name="triangle_fadeout")
        timeline.add_event(7.0, lambda s: s.play(FadeIn(triangle)), name="triangle_fadein")
        
        # Add markers
        timeline.add_marker(2.0, "Circle reaches right", color=YELLOW)
        timeline.add_marker(5.0, "Square rotation complete", color=ORANGE)
        
        # Add region
        timeline.add_region(3.0, 6.0, "Text fade section", color="#0000FF")
        
        # Create timeline visualizer
        visualizer = TimelineVisualizer(timeline, width=12, height=4)
        visualizer.shift(DOWN * 2)
        self.add(visualizer)
        
        # Setup debugger
        debugger = TimelineDebugger(timeline)
        debugger.add_breakpoint(2.0, label="Circle at right position")
        debugger.add_watch("circle_pos", lambda t: shapes_track.get_value_at_time("circle_x", t.current_time))
        debugger.add_watch("text_opacity", lambda t: text_track.get_value_at_time("title_opacity", t.current_time))
        
        # Create debug overlay
        debug_overlay = debugger.create_debug_overlay(self)
        self.add(debug_overlay)
        
        # Animation loop
        dt = 1.0 / timeline.fps
        for frame in range(int(timeline.duration * timeline.fps)):
            current_time = frame * dt
            timeline.seek(current_time)
            
            # Update object positions based on keyframes
            circle_x = shapes_track.get_value_at_time("circle_x", current_time) or -3
            circle_scale = shapes_track.get_value_at_time("circle_scale", current_time) or 1
            circle.move_to(circle_x * RIGHT).scale_to_fit_width(2 * circle_scale)
            
            square_rot = shapes_track.get_value_at_time("square_rotation", current_time) or 0
            square.rotate(square_rot - square.get_angle())
            
            title_opacity = text_track.get_value_at_time("title_opacity", current_time) or 1
            title.set_opacity(title_opacity)
            
            # Update visualizer playhead
            visualizer.update_playhead(current_time)
            
            # Update debug overlay
            debugger._update_overlay(self)
            
            # Process timeline events
            debugger.play_with_debugging(self)
            
            self.wait(dt)
        
        # Export timeline data
        timeline.export_to_json("timeline_demo.json")
        debugger.export_debug_report(Path("timeline_debug_report.json"))
        
        self.wait(2)

class TimelinePresetsDemo(Scene):
    """Demonstrates timeline presets."""
    
    def construct(self):
        # Create timeline and presets
        timeline = ComposerTimeline(duration=5.0)
        presets = TimelinePresets()
        
        # Create test objects
        title = Text("Timeline Presets Demo", font_size=36)
        objects = VGroup(
            Circle(radius=0.5, color=BLUE).shift(LEFT * 2),
            Square(side_length=1, color=RED),
            Triangle(color=GREEN).shift(RIGHT * 2)
        )
        objects.shift(DOWN)
        
        self.add(title, objects)
        
        # Apply fade in/out preset
        fade_preset = presets.get_preset("fade_in_out")
        fade_preset.apply(timeline, {
            "fade_in_duration": 1.0,
            "hold_duration": 2.0,
            "fade_out_duration": 1.0
        })
        
        # Create timeline visualizer
        visualizer = TimelineVisualizer(timeline, width=10, height=3)
        visualizer.to_edge(DOWN, buff=0.5)
        self.add(visualizer)
        
        # Play timeline with visualization
        dt = 1.0 / timeline.fps
        for frame in range(int(timeline.duration * timeline.fps)):
            current_time = frame * dt
            timeline.seek(current_time)
            
            # Get opacity from timeline
            main_layer = timeline.get_layer("Main")
            if main_layer:
                for track in main_layer.tracks:
                    opacity = track.get_value_at_time("opacity", current_time)
                    if opacity is not None:
                        objects.set_opacity(opacity)
                        title.set_opacity(opacity)
            
            visualizer.update_playhead(current_time)
            self.wait(dt)
        
        self.wait()

class KeyframeEditorDemo(Scene):
    """Demonstrates keyframe editor."""
    
    def construct(self):
        # Create timeline
        timeline = ComposerTimeline()
        track = timeline.get_layer("Main").get_track("objects")
        
        # Add some keyframes
        track.add_keyframe("position_x", Keyframe(0, -3, InterpolationType.LINEAR))
        track.add_keyframe("position_x", Keyframe(2, 0, InterpolationType.EASE_IN_OUT))
        track.add_keyframe("position_x", Keyframe(4, 3, InterpolationType.SPRING))
        track.add_keyframe("position_x", Keyframe(6, 0, InterpolationType.CUBIC_BEZIER,
                                                bezier_points=(0.4, 0, 0.6, 1)))
        track.add_keyframe("position_x", Keyframe(8, -3, InterpolationType.EASE_OUT))
        
        track.add_keyframe("scale", Keyframe(0, 0.5, InterpolationType.EASE_OUT))
        track.add_keyframe("scale", Keyframe(4, 1.5, InterpolationType.EASE_IN_OUT))
        track.add_keyframe("scale", Keyframe(8, 0.5, InterpolationType.EASE_IN))
        
        # Create keyframe editor
        editor = KeyframeEditor(track, width=10, height=5)
        self.add(editor)
        
        # Add title
        title = Text("Keyframe Editor", font_size=24)
        title.to_edge(UP)
        self.add(title)
        
        # Create animated object
        dot = Dot(radius=0.2, color=YELLOW)
        dot.shift(DOWN * 3)
        self.add(dot)
        
        # Animate based on keyframes
        for t in range(0, 80):
            time = t / 10.0
            
            # Get values from track
            pos_x = track.get_value_at_time("position_x", time) or 0
            scale = track.get_value_at_time("scale", time) or 1
            
            # Update object
            dot.move_to(pos_x * RIGHT + DOWN * 3)
            dot.scale_to_fit_width(0.4 * scale)
            
            self.wait(0.1)
        
        self.wait()

if __name__ == "__main__":
    # Run demos
    scene = ComposerTimelineDemo()
    scene.render()