"""Direct test of composer timeline without circular imports."""

from manim import *
import sys
sys.path.insert(0, 'src')

# Import only what we need
from src.core.timeline.composer_timeline import ComposerTimeline, InterpolationType, Keyframe

class TimelineTest(Scene):
    def construct(self):
        # Create simple shapes
        circle = Circle(radius=1, color=BLUE)
        square = Square(side_length=1.5, color=RED)
        
        circle.shift(LEFT * 3)
        square.shift(RIGHT * 3)
        
        self.add(circle, square)
        
        # Create timeline
        timeline = ComposerTimeline(duration=5.0, fps=30)
        
        # Get main layer and track
        main_layer = timeline.get_layer("Main")
        track = main_layer.get_track("objects")
        
        # Add movement keyframes
        track.add_keyframe("circle_x", Keyframe(0, -3, InterpolationType.LINEAR))
        track.add_keyframe("circle_x", Keyframe(2.5, 3, InterpolationType.EASE_IN_OUT))
        track.add_keyframe("circle_x", Keyframe(5, -3, InterpolationType.EASE_IN_OUT))
        
        # Add rotation keyframes
        track.add_keyframe("square_angle", Keyframe(0, 0, InterpolationType.LINEAR))
        track.add_keyframe("square_angle", Keyframe(5, TAU, InterpolationType.EASE_IN_OUT))
        
        # Animate
        dt = 1 / timeline.fps
        for i in range(int(timeline.duration * timeline.fps)):
            t = i * dt
            
            # Get values
            x = track.get_value_at_time("circle_x", t) or -3
            angle = track.get_value_at_time("square_angle", t) or 0
            
            # Update objects
            circle.move_to(x * RIGHT)
            square.set_angle(angle)
            
            self.wait(dt)

if __name__ == "__main__":
    scene = TimelineTest()
    scene.render()