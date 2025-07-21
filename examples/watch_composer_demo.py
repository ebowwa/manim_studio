"""Simple ComposerTimeline demo that renders a complete video."""

from manim import *
import sys
sys.path.insert(0, 'src')

from manim_studio.core.timeline.composer_timeline import ComposerTimeline, InterpolationType, Keyframe

class WatchComposerDemo(Scene):
    def construct(self):
        # Create timeline
        timeline = ComposerTimeline(duration=5.0, fps=30)
        
        # Create animated elements
        title = Text("COMPOSER TIMELINE", font_size=48, weight=BOLD)
        title.set_color_by_gradient(BLUE, PURPLE)
        
        circle = Circle(radius=1, color=BLUE, fill_opacity=0.7)
        square = Square(side_length=1.5, color=RED, fill_opacity=0.7)
        
        # Position elements
        circle.shift(LEFT * 3)
        square.shift(RIGHT * 3)
        
        # Add to scene
        self.add(title, circle, square)
        
        # Get main track
        main_layer = timeline.get_layer("Main")
        track = main_layer.get_track("objects")
        
        # === TITLE ANIMATION ===
        # Fade in and scale
        track.add_keyframe("title_opacity", Keyframe(0, 0, InterpolationType.LINEAR))
        track.add_keyframe("title_opacity", Keyframe(1, 1, InterpolationType.EASE_OUT))
        
        track.add_keyframe("title_scale", Keyframe(0, 0.5, InterpolationType.EASE_OUT))
        track.add_keyframe("title_scale", Keyframe(1, 1.2, InterpolationType.EASE_OUT))
        track.add_keyframe("title_scale", Keyframe(1.5, 1, InterpolationType.SPRING))
        
        # === CIRCLE ANIMATION ===
        # Move circle across screen
        track.add_keyframe("circle_x", Keyframe(0, -3, InterpolationType.LINEAR))
        track.add_keyframe("circle_x", Keyframe(2, 3, InterpolationType.EASE_IN_OUT))
        track.add_keyframe("circle_x", Keyframe(4, -3, InterpolationType.EASE_IN_OUT))
        
        # Scale circle
        track.add_keyframe("circle_scale", Keyframe(0, 1, InterpolationType.LINEAR))
        track.add_keyframe("circle_scale", Keyframe(2, 2, InterpolationType.EASE_OUT))
        track.add_keyframe("circle_scale", Keyframe(4, 1, InterpolationType.EASE_IN))
        
        # === SQUARE ANIMATION ===
        # Rotate square
        track.add_keyframe("square_rotation", Keyframe(0, 0, InterpolationType.LINEAR))
        track.add_keyframe("square_rotation", Keyframe(5, TAU, InterpolationType.EASE_IN_OUT))
        
        # Pulse square
        track.add_keyframe("square_scale", Keyframe(0, 1, InterpolationType.LINEAR))
        track.add_keyframe("square_scale", Keyframe(1, 1.3, InterpolationType.EASE_OUT))
        track.add_keyframe("square_scale", Keyframe(2, 1, InterpolationType.EASE_IN))
        track.add_keyframe("square_scale", Keyframe(3, 1.3, InterpolationType.EASE_OUT))
        track.add_keyframe("square_scale", Keyframe(4, 1, InterpolationType.EASE_IN))
        
        # === FADE OUT ALL ===
        track.add_keyframe("all_opacity", Keyframe(4.5, 1, InterpolationType.EASE_IN))
        track.add_keyframe("all_opacity", Keyframe(5, 0, InterpolationType.LINEAR))
        
        # === ANIMATE USING TIMELINE ===
        dt = 1.0 / timeline.fps
        for frame in range(int(timeline.duration * timeline.fps)):
            t = frame * dt
            timeline.seek(t)
            
            # Title animation
            title_opacity = track.get_value_at_time("title_opacity", t) or 0
            title_scale = track.get_value_at_time("title_scale", t) or 1
            title.set_opacity(title_opacity).scale(title_scale / title.height * 1.5)
            
            # Circle animation
            circle_x = track.get_value_at_time("circle_x", t) or -3
            circle_scale = track.get_value_at_time("circle_scale", t) or 1
            circle.move_to(circle_x * RIGHT).scale(circle_scale / circle.width * 2)
            
            # Square animation
            square_rot = track.get_value_at_time("square_rotation", t) or 0
            square_scale = track.get_value_at_time("square_scale", t) or 1
            square.set_angle(square_rot).scale(square_scale / square.width * 1.5)
            
            # Global fade
            all_opacity = track.get_value_at_time("all_opacity", t)
            if all_opacity is not None:
                title.set_opacity(title_opacity * all_opacity)
                circle.set_opacity(0.7 * all_opacity)
                square.set_opacity(0.7 * all_opacity)
            
            self.wait(dt)

if __name__ == "__main__":
    # Render with medium quality for faster processing
    os.system('manim -qm watch_composer_demo.py WatchComposerDemo')