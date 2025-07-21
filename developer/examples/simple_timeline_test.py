"""Simple test of the composer timeline system."""

from manim import *
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.manim_studio.core.composer_timeline import (
    ComposerTimeline, InterpolationType, Keyframe
)

class SimpleTimelineTest(Scene):
    """Simple demonstration of timeline features."""
    
    def construct(self):
        # Create timeline
        timeline = ComposerTimeline(duration=6.0, fps=30.0)
        
        # Create objects
        circle = Circle(radius=1, color=BLUE, fill_opacity=0.5)
        square = Square(side_length=2, color=RED, fill_opacity=0.5)
        text = Text("Timeline Demo", font_size=36)
        
        # Position objects
        circle.shift(LEFT * 3)
        square.shift(RIGHT * 3)
        text.shift(UP * 2)
        
        # Add to scene
        self.add(circle, square, text)
        
        # Get main track
        main_layer = timeline.get_layer("Main")
        main_track = main_layer.get_track("objects")
        
        # Add keyframes for circle movement
        main_track.add_keyframe("circle_x", Keyframe(0, -3, InterpolationType.LINEAR))
        main_track.add_keyframe("circle_x", Keyframe(2, 3, InterpolationType.EASE_IN_OUT))
        main_track.add_keyframe("circle_x", Keyframe(4, -3, InterpolationType.EASE_IN_OUT))
        
        # Add keyframes for square rotation
        main_track.add_keyframe("square_rotation", Keyframe(0, 0, InterpolationType.LINEAR))
        main_track.add_keyframe("square_rotation", Keyframe(3, TAU, InterpolationType.EASE_IN_OUT))
        
        # Add keyframes for text opacity
        main_track.add_keyframe("text_opacity", Keyframe(0, 1, InterpolationType.LINEAR))
        main_track.add_keyframe("text_opacity", Keyframe(1, 0.2, InterpolationType.EASE_IN))
        main_track.add_keyframe("text_opacity", Keyframe(2, 1, InterpolationType.EASE_OUT))
        
        # Animate
        dt = 1.0 / timeline.fps
        for frame in range(int(timeline.duration * timeline.fps)):
            current_time = frame * dt
            timeline.seek(current_time)
            
            # Update circle position
            circle_x = main_track.get_value_at_time("circle_x", current_time)
            if circle_x is not None:
                circle.move_to(circle_x * RIGHT)
            
            # Update square rotation
            square_rot = main_track.get_value_at_time("square_rotation", current_time)
            if square_rot is not None:
                square.set_angle(square_rot)
            
            # Update text opacity
            text_opacity = main_track.get_value_at_time("text_opacity", current_time)
            if text_opacity is not None:
                text.set_opacity(text_opacity)
            
            self.wait(dt)
        
        self.wait()

if __name__ == "__main__":
    scene = SimpleTimelineTest()
    scene.render()