"""Simple demonstration of the ComposerTimeline system."""

from manim import *
import sys
sys.path.insert(0, 'src')

from src.core.timeline.composer_timeline import (
    ComposerTimeline, InterpolationType, Keyframe, TimelineTrack, TrackType
)
from src.core.timeline.timeline_presets import TimelinePresets

class ComposerDemo(Scene):
    def construct(self):
        # Create composer timeline
        timeline = ComposerTimeline(duration=8.0, fps=30)
        presets = TimelinePresets()
        
        # Create scene elements
        title = Text("COMPOSER TIMELINE", font_size=48, weight=BOLD)
        title.set_color_by_gradient(BLUE, PURPLE)
        
        subtitle = Text("Professional Animation System", font_size=24)
        subtitle.next_to(title, DOWN, buff=0.5)
        
        # Feature list
        features = VGroup(
            Text("• Layered Timeline", font_size=20),
            Text("• Keyframe Animation", font_size=20),
            Text("• Multiple Interpolation Types", font_size=20),
            Text("• Timeline Presets", font_size=20),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        features.shift(DOWN * 1.5)
        
        # Add all elements
        self.add(title, subtitle, features)
        
        # === SETUP TIMELINE ===
        
        # Get main layer and create tracks
        main_layer = timeline.get_layer("Main")
        
        title_track = TimelineTrack("title", TrackType.ANIMATION)
        main_layer.add_track(title_track)
        
        features_track = TimelineTrack("features", TrackType.ANIMATION)
        main_layer.add_track(features_track)
        
        # === TITLE ANIMATION ===
        
        # Title entrance with spring
        title_track.add_keyframe("title_scale", Keyframe(0, 0, InterpolationType.EASE_OUT))
        title_track.add_keyframe("title_scale", Keyframe(1, 1.2, InterpolationType.EASE_OUT))
        title_track.add_keyframe("title_scale", Keyframe(1.5, 1, InterpolationType.SPRING,
                                                       spring_params={"stiffness": 200, "damping": 15}))
        
        # Title color shift
        title_track.add_keyframe("title_opacity", Keyframe(0, 0, InterpolationType.LINEAR))
        title_track.add_keyframe("title_opacity", Keyframe(0.5, 1, InterpolationType.EASE_OUT))
        
        # Subtitle fade in
        title_track.add_keyframe("subtitle_opacity", Keyframe(0, 0, InterpolationType.LINEAR))
        title_track.add_keyframe("subtitle_opacity", Keyframe(1, 0, InterpolationType.LINEAR))
        title_track.add_keyframe("subtitle_opacity", Keyframe(2, 1, InterpolationType.EASE_OUT))
        
        # === FEATURES ANIMATION ===
        
        # Staggered feature reveal
        for i in range(4):
            start_time = 2.5 + i * 0.3
            
            features_track.add_keyframe(f"feature_{i}_x", 
                Keyframe(start_time, -5, InterpolationType.EASE_OUT))
            features_track.add_keyframe(f"feature_{i}_x", 
                Keyframe(start_time + 0.8, 0, InterpolationType.EASE_OUT))
            
            features_track.add_keyframe(f"feature_{i}_opacity", 
                Keyframe(start_time, 0, InterpolationType.LINEAR))
            features_track.add_keyframe(f"feature_{i}_opacity", 
                Keyframe(start_time + 0.5, 1, InterpolationType.EASE_OUT))
        
        # === APPLY FADE PRESET AT END ===
        
        # Create a fade out preset
        fade_params = {
            "fade_in_duration": 0,
            "hold_duration": 6,
            "fade_out_duration": 1.5
        }
        fade_preset = presets.get_preset("fade_in_out")
        fade_preset.apply(timeline, fade_params)
        
        # === PLAY ANIMATION ===
        
        dt = 1.0 / timeline.fps
        for frame in range(int(timeline.duration * timeline.fps)):
            current_time = frame * dt
            timeline.seek(current_time)
            
            # Update title animations
            title_scale = title_track.get_value_at_time("title_scale", current_time) or 0
            title_opacity = title_track.get_value_at_time("title_opacity", current_time) or 0
            subtitle_opacity = title_track.get_value_at_time("subtitle_opacity", current_time) or 0
            
            title.scale_to_fit_width(title_scale * 10 if title_scale > 0 else 0.001)
            title.set_opacity(title_opacity)
            subtitle.set_opacity(subtitle_opacity)
            
            # Update features
            for i in range(4):
                feature = features[i]
                x_offset = features_track.get_value_at_time(f"feature_{i}_x", current_time) or -5
                opacity = features_track.get_value_at_time(f"feature_{i}_opacity", current_time) or 0
                
                feature.set_x(x_offset)
                feature.set_opacity(opacity)
            
            # Apply global fade from preset
            global_opacity = main_layer.tracks[0].get_value_at_time("opacity", current_time)
            if global_opacity is not None:
                for mob in self.mobjects:
                    try:
                        mob.set_opacity(global_opacity)
                    except:
                        pass
            
            self.wait(dt)
        
        self.wait()

if __name__ == "__main__":
    scene = ComposerDemo()
    scene.render()