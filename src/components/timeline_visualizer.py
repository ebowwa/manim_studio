"""Timeline visualizer component for visual timeline editing."""

from manim import *
from typing import Dict, List, Any, Optional
from core.timeline.composer_timeline import ComposerTimeline, TimelineLayer, TimelineTrack, TrackType

class TimelineVisualizer(VGroup):
    """Visual representation of the timeline for debugging and editing."""
    
    def __init__(self, timeline: ComposerTimeline, width: float = 12, height: float = 6, **kwargs):
        super().__init__(**kwargs)
        self.timeline = timeline
        self.width = width
        self.height = height
        self.time_scale = width / timeline.duration
        
        # Colors for different track types
        self.track_colors = {
            TrackType.ANIMATION: "#4ECDC4",
            TrackType.AUDIO: "#FF6B6B",
            TrackType.EFFECT: "#9B59B6",
            TrackType.CAMERA: "#F39C12",
            TrackType.SUBTITLE: "#1ABC9C",
            TrackType.MARKER: "#E74C3C"
        }
        
        self._create_timeline_visual()
    
    def _create_timeline_visual(self):
        """Create the visual timeline representation."""
        # Background
        bg = Rectangle(width=self.width, height=self.height, 
                      color=GREY_E, fill_opacity=0.1)
        self.add(bg)
        
        # Time ruler
        ruler = self._create_time_ruler()
        ruler.to_edge(UP, buff=0.1)
        self.add(ruler)
        
        # Layers and tracks
        layer_group = self._create_layers_visual()
        self.add(layer_group)
        
        # Playhead
        self.playhead = self._create_playhead()
        self.add(self.playhead)
        
        # Markers
        markers_group = self._create_markers_visual()
        self.add(markers_group)
        
        # Regions
        regions_group = self._create_regions_visual()
        self.add(regions_group)
    
    def _create_time_ruler(self) -> VGroup:
        """Create time ruler with tick marks."""
        ruler = VGroup()
        
        # Main line
        line = Line(
            start=LEFT * self.width/2,
            end=RIGHT * self.width/2,
            color=WHITE
        )
        ruler.add(line)
        
        # Time marks
        tick_interval = 1.0  # 1 second intervals
        num_ticks = int(self.timeline.duration / tick_interval) + 1
        
        for i in range(num_ticks):
            time = i * tick_interval
            x_pos = self._time_to_x(time)
            
            # Major tick every 5 seconds
            if time % 5 == 0:
                tick = Line(
                    start=x_pos * RIGHT + UP * 0.1,
                    end=x_pos * RIGHT + DOWN * 0.2,
                    color=WHITE
                )
                label = Text(f"{int(time)}s", font_size=16).next_to(tick, DOWN)
                ruler.add(tick, label)
            else:
                # Minor tick
                tick = Line(
                    start=x_pos * RIGHT + UP * 0.05,
                    end=x_pos * RIGHT + DOWN * 0.1,
                    color=GREY_B
                )
                ruler.add(tick)
        
        return ruler
    
    def _create_layers_visual(self) -> VGroup:
        """Create visual representation of layers and tracks."""
        layers_group = VGroup()
        
        if not self.timeline.layers:
            return layers_group
        
        # Calculate dimensions
        layer_height = (self.height - 1.5) / len(self.timeline.layers)
        y_offset = self.height/2 - 1.0
        
        for i, layer in enumerate(self.timeline.layers):
            layer_visual = self._create_layer_visual(layer, layer_height)
            layer_visual.move_to(UP * (y_offset - i * layer_height - layer_height/2))
            layers_group.add(layer_visual)
        
        return layers_group
    
    def _create_layer_visual(self, layer: TimelineLayer, height: float) -> VGroup:
        """Create visual for a single layer."""
        layer_group = VGroup()
        
        # Layer background
        bg = Rectangle(
            width=self.width,
            height=height * 0.9,
            color=GREY_D if layer.locked else GREY_E,
            fill_opacity=0.3 if layer.visible else 0.1
        )
        layer_group.add(bg)
        
        # Layer name
        name_text = Text(layer.name, font_size=14, color=WHITE)
        name_text.to_edge(LEFT, buff=0.2)
        layer_group.add(name_text)
        
        # Solo indicator
        if layer.solo:
            solo_dot = Dot(color=YELLOW, radius=0.05)
            solo_dot.next_to(name_text, RIGHT, buff=0.1)
            layer_group.add(solo_dot)
        
        # Tracks
        if layer.tracks:
            track_height = height * 0.8 / len(layer.tracks)
            tracks_group = VGroup()
            
            for j, track in enumerate(layer.tracks):
                track_visual = self._create_track_visual(track, track_height)
                track_visual.shift(DOWN * (j * track_height))
                tracks_group.add(track_visual)
            
            tracks_group.shift(RIGHT * 1.5)
            layer_group.add(tracks_group)
        
        return layer_group
    
    def _create_track_visual(self, track: TimelineTrack, height: float) -> VGroup:
        """Create visual for a single track."""
        track_group = VGroup()
        
        # Track color
        track_color = self.track_colors.get(track.track_type, WHITE)
        
        # Events
        for event in track.events:
            if event.enabled:
                event_visual = self._create_event_visual(event, height * 0.7, track_color)
                track_group.add(event_visual)
        
        # Keyframes
        for prop_name, keyframes in track.keyframes.items():
            for kf in keyframes:
                kf_visual = self._create_keyframe_visual(kf, prop_name, track_color)
                track_group.add(kf_visual)
        
        return track_group
    
    def _create_event_visual(self, event, height: float, color: str) -> Rectangle:
        """Create visual for an event."""
        x_pos = self._time_to_x(event.time)
        width = self._duration_to_width(event.duration) if event.duration > 0 else 0.1
        
        rect = Rectangle(
            width=width,
            height=height,
            color=color,
            fill_opacity=0.7
        )
        rect.move_to(RIGHT * x_pos)
        
        # Add label if event has name
        if event.name:
            label = Text(event.name[:10], font_size=10, color=BLACK)
            label.move_to(rect)
            rect_with_label = VGroup(rect, label)
            return rect_with_label
        
        return rect
    
    def _create_keyframe_visual(self, keyframe, prop_name: str, color: str) -> VGroup:
        """Create visual for a keyframe."""
        x_pos = self._time_to_x(keyframe.time)
        
        # Diamond shape for keyframe
        diamond = Square(side_length=0.1, color=color, fill_opacity=1.0)
        diamond.rotate(PI/4)
        diamond.move_to(RIGHT * x_pos)
        
        return diamond
    
    def _create_playhead(self) -> Line:
        """Create playhead indicator."""
        playhead = Line(
            start=UP * self.height/2,
            end=DOWN * self.height/2,
            color=RED,
            stroke_width=3
        )
        playhead.move_to(self._time_to_x(self.timeline.current_time) * RIGHT)
        return playhead
    
    def _create_markers_visual(self) -> VGroup:
        """Create visual representation of markers."""
        markers_group = VGroup()
        
        for marker in self.timeline.markers:
            x_pos = self._time_to_x(marker.time)
            
            # Marker line
            line = DashedLine(
                start=UP * self.height/2,
                end=DOWN * self.height/2,
                color=marker.color,
                stroke_width=2
            )
            line.move_to(RIGHT * x_pos)
            
            # Marker label
            label = Text(marker.label, font_size=12, color=marker.color)
            label.next_to(line, UP)
            
            markers_group.add(line, label)
        
        return markers_group
    
    def _create_regions_visual(self) -> VGroup:
        """Create visual representation of regions."""
        regions_group = VGroup()
        
        for region in self.timeline.regions:
            start_x = self._time_to_x(region["start"])
            end_x = self._time_to_x(region["end"])
            width = end_x - start_x
            
            rect = Rectangle(
                width=width,
                height=self.height,
                color=region["color"],
                fill_opacity=0.2,
                stroke_width=0
            )
            rect.move_to(RIGHT * (start_x + width/2))
            
            # Region label
            label = Text(region["name"], font_size=14, color=region["color"])
            label.to_edge(UP, buff=0.3)
            label.shift(RIGHT * (start_x + width/2))
            
            regions_group.add(rect, label)
        
        return regions_group
    
    def _time_to_x(self, time: float) -> float:
        """Convert time to x coordinate."""
        return (time / self.timeline.duration - 0.5) * self.width
    
    def _duration_to_width(self, duration: float) -> float:
        """Convert duration to width."""
        return duration * self.time_scale
    
    def update_playhead(self, time: float):
        """Update playhead position."""
        self.timeline.current_time = time
        self.playhead.move_to(self._time_to_x(time) * RIGHT)
    
    def animate_playhead(self, scene, start_time: float = None, end_time: float = None):
        """Animate playhead across timeline."""
        start = start_time or 0
        end = end_time or self.timeline.duration
        
        scene.play(
            self.playhead.animate.move_to(self._time_to_x(end) * RIGHT),
            run_time=end - start,
            rate_func=linear
        )