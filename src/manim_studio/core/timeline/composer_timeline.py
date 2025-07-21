"""Composer timeline system with layers, tracks, and advanced choreography."""

from typing import Any, Callable, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import heapq
import json
import numpy as np
from pathlib import Path

class InterpolationType(Enum):
    """Types of interpolation for keyframes."""
    LINEAR = "linear"
    EASE_IN = "ease_in"
    EASE_OUT = "ease_out"
    EASE_IN_OUT = "ease_in_out"
    CUBIC_BEZIER = "cubic_bezier"
    STEP = "step"
    SPRING = "spring"

class TrackType(Enum):
    """Types of timeline tracks."""
    ANIMATION = "animation"
    AUDIO = "audio"
    EFFECT = "effect"
    CAMERA = "camera"
    SUBTITLE = "subtitle"
    MARKER = "marker"

@dataclass
class Keyframe:
    """Represents a keyframe in the timeline."""
    time: float
    value: Any
    interpolation: InterpolationType = InterpolationType.LINEAR
    bezier_points: Optional[Tuple[float, float, float, float]] = None
    spring_params: Optional[Dict[str, float]] = None
    
    def interpolate_to(self, next_keyframe: 'Keyframe', t: float) -> Any:
        """Interpolate between this keyframe and the next."""
        if self.interpolation == InterpolationType.STEP:
            return self.value
        
        # Normalize t between keyframes
        duration = next_keyframe.time - self.time
        if duration == 0:
            return self.value
        
        normalized_t = (t - self.time) / duration
        normalized_t = max(0, min(1, normalized_t))
        
        # Apply interpolation
        if self.interpolation == InterpolationType.LINEAR:
            return self._linear_interpolate(self.value, next_keyframe.value, normalized_t)
        elif self.interpolation == InterpolationType.EASE_IN:
            eased_t = normalized_t * normalized_t
            return self._linear_interpolate(self.value, next_keyframe.value, eased_t)
        elif self.interpolation == InterpolationType.EASE_OUT:
            eased_t = 1 - (1 - normalized_t) ** 2
            return self._linear_interpolate(self.value, next_keyframe.value, eased_t)
        elif self.interpolation == InterpolationType.EASE_IN_OUT:
            eased_t = 3 * normalized_t**2 - 2 * normalized_t**3
            return self._linear_interpolate(self.value, next_keyframe.value, eased_t)
        elif self.interpolation == InterpolationType.CUBIC_BEZIER and self.bezier_points:
            eased_t = self._cubic_bezier(normalized_t, *self.bezier_points)
            return self._linear_interpolate(self.value, next_keyframe.value, eased_t)
        elif self.interpolation == InterpolationType.SPRING and self.spring_params:
            eased_t = self._spring_interpolation(normalized_t, **self.spring_params)
            return self._linear_interpolate(self.value, next_keyframe.value, eased_t)
        
        return self.value
    
    def _linear_interpolate(self, start: Any, end: Any, t: float) -> Any:
        """Linear interpolation between values."""
        if isinstance(start, (int, float)):
            return start + (end - start) * t
        elif isinstance(start, (list, tuple)):
            return [self._linear_interpolate(s, e, t) for s, e in zip(start, end)]
        elif isinstance(start, dict):
            return {k: self._linear_interpolate(start[k], end[k], t) for k in start}
        return start
    
    def _cubic_bezier(self, t: float, x1: float, y1: float, x2: float, y2: float) -> float:
        """Cubic bezier interpolation."""
        # Simplified cubic bezier for animation curves
        return 3 * (1-t)**2 * t * y1 + 3 * (1-t) * t**2 * y2 + t**3
    
    def _spring_interpolation(self, t: float, stiffness: float = 100, 
                            damping: float = 10, mass: float = 1) -> float:
        """Spring physics interpolation."""
        # Simplified spring physics
        omega = np.sqrt(stiffness / mass)
        zeta = damping / (2 * np.sqrt(stiffness * mass))
        
        if zeta < 1:  # Underdamped
            wd = omega * np.sqrt(1 - zeta**2)
            return 1 - np.exp(-zeta * omega * t) * (
                np.cos(wd * t) + (zeta * omega / wd) * np.sin(wd * t)
            )
        else:  # Critically damped or overdamped
            return 1 - np.exp(-omega * t) * (1 + omega * t)

@dataclass
class TimelineTrack:
    """Represents a track in the timeline."""
    name: str
    track_type: TrackType
    enabled: bool = True
    locked: bool = False
    color: str = "#FFFFFF"
    opacity: float = 1.0
    events: List['TimelineEvent'] = field(default_factory=list)
    keyframes: Dict[str, List[Keyframe]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_keyframe(self, property_name: str, keyframe: Keyframe):
        """Add a keyframe for a property."""
        if property_name not in self.keyframes:
            self.keyframes[property_name] = []
        self.keyframes[property_name].append(keyframe)
        self.keyframes[property_name].sort(key=lambda k: k.time)
    
    def get_value_at_time(self, property_name: str, time: float) -> Any:
        """Get interpolated value for a property at a specific time."""
        if property_name not in self.keyframes:
            return None
        
        keyframes = self.keyframes[property_name]
        if not keyframes:
            return None
        
        # Find surrounding keyframes
        prev_kf = None
        next_kf = None
        
        for kf in keyframes:
            if kf.time <= time:
                prev_kf = kf
            elif kf.time > time and next_kf is None:
                next_kf = kf
                break
        
        if prev_kf is None:
            return keyframes[0].value
        if next_kf is None:
            return prev_kf.value
        
        return prev_kf.interpolate_to(next_kf, time)

@dataclass
class TimelineLayer:
    """Represents a layer containing multiple tracks."""
    name: str
    visible: bool = True
    locked: bool = False
    solo: bool = False
    tracks: List[TimelineTrack] = field(default_factory=list)
    blend_mode: str = "normal"
    opacity: float = 1.0
    z_index: int = 0  # Layer ordering - higher values appear on top
    parent_layer: Optional[str] = None  # For nested layers
    transform: Dict[str, float] = field(default_factory=lambda: {"x": 0, "y": 0, "scale": 1, "rotation": 0})
    
    def add_track(self, track: TimelineTrack):
        """Add a track to this layer."""
        self.tracks.append(track)
    
    def get_track(self, name: str) -> Optional[TimelineTrack]:
        """Get a track by name."""
        for track in self.tracks:
            if track.name == name:
                return track
        return None

@dataclass
class TimelineEvent:
    """Enhanced timeline event with more properties."""
    time: float
    callback: Callable
    name: str = ""
    duration: float = 0.0
    track_name: Optional[str] = None
    layer_name: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    
    def __lt__(self, other):
        return self.time < other.time

@dataclass
class TimelineMarker:
    """Represents a marker on the timeline."""
    time: float
    label: str
    color: str = "#FFFF00"
    duration: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

class ComposerTimeline:
    """Composer timeline with layers, tracks, and advanced features for choreographing animations."""
    
    def __init__(self, duration: float = 10.0, fps: float = 60.0):
        self.duration = duration
        self.fps = fps
        self.current_time = 0.0
        self.playback_speed = 1.0
        self.is_playing = False
        self.loop_enabled = False
        self.loop_start = 0.0
        self.loop_end = duration
        
        # Layers and tracks
        self.layers: List[TimelineLayer] = []
        self.master_track = TimelineTrack("Master", TrackType.ANIMATION)
        
        # Events and markers
        self.event_queue: List[TimelineEvent] = []
        self.markers: List[TimelineMarker] = []
        self.regions: List[Dict[str, Any]] = []
        
        # Playback state
        self.playback_callbacks: List[Callable] = []
        self.time_callbacks: Dict[float, List[Callable]] = {}
        
        # Create default layers
        self._create_default_layers()
    
    def _create_default_layers(self):
        """Create default timeline layers."""
        self.add_layer("Background", ["background", "environment"], z_index=0)
        self.add_layer("Main", ["objects", "text", "shapes"], z_index=100)
        self.add_layer("Effects", ["particles", "shaders", "filters"], z_index=200)
        self.add_layer("Foreground", ["overlays", "UI"], z_index=300)
        self.add_layer("Audio", ["music", "sfx", "voiceover"], z_index=400)
    
    def add_layer(self, name: str, track_names: List[str] = None, z_index: Optional[int] = None,
                  parent_layer: Optional[str] = None, **kwargs) -> TimelineLayer:
        """Add a new layer with optional tracks and z-ordering."""
        # Auto-assign z_index if not provided
        if z_index is None:
            z_index = len(self.layers) * 10  # Leave gaps for insertion
        
        layer = TimelineLayer(name, z_index=z_index, parent_layer=parent_layer, **kwargs)
        
        if track_names:
            for track_name in track_names:
                track_type = self._infer_track_type(track_name)
                track = TimelineTrack(track_name, track_type)
                layer.add_track(track)
        
        self.layers.append(layer)
        self._sort_layers_by_z_index()
        return layer
    
    def _infer_track_type(self, track_name: str) -> TrackType:
        """Infer track type from name."""
        name_lower = track_name.lower()
        if any(word in name_lower for word in ["music", "sfx", "audio", "sound", "voiceover"]):
            return TrackType.AUDIO
        elif any(word in name_lower for word in ["particle", "shader", "filter", "effect"]):
            return TrackType.EFFECT
        elif any(word in name_lower for word in ["camera", "view", "perspective"]):
            return TrackType.CAMERA
        elif any(word in name_lower for word in ["subtitle", "caption", "text"]):
            return TrackType.SUBTITLE
        elif any(word in name_lower for word in ["marker", "cue", "beat"]):
            return TrackType.MARKER
        return TrackType.ANIMATION
    
    def add_event(self, time: float, callback: Callable, **kwargs) -> TimelineEvent:
        """Add an event to the timeline."""
        event = TimelineEvent(time, callback, **kwargs)
        heapq.heappush(self.event_queue, event)
        
        # Add to specific track if specified
        if event.track_name and event.layer_name:
            layer = self.get_layer(event.layer_name)
            if layer:
                track = layer.get_track(event.track_name)
                if track:
                    track.events.append(event)
        
        return event
    
    def add_keyframe(self, layer_name: str, track_name: str, property_name: str,
                    time: float, value: Any, interpolation: InterpolationType = InterpolationType.LINEAR,
                    **kwargs) -> Optional[Keyframe]:
        """Add a keyframe to a specific track property."""
        layer = self.get_layer(layer_name)
        if not layer:
            return None
        
        track = layer.get_track(track_name)
        if not track:
            return None
        
        keyframe = Keyframe(time, value, interpolation, **kwargs)
        track.add_keyframe(property_name, keyframe)
        return keyframe
    
    def add_marker(self, time: float, label: str, **kwargs) -> TimelineMarker:
        """Add a marker to the timeline."""
        marker = TimelineMarker(time, label, **kwargs)
        self.markers.append(marker)
        self.markers.sort(key=lambda m: m.time)
        return marker
    
    def add_region(self, start: float, end: float, name: str, 
                  color: str = "#0000FF", **metadata) -> Dict[str, Any]:
        """Add a region to the timeline."""
        region = {
            "start": start,
            "end": end,
            "name": name,
            "color": color,
            "metadata": metadata
        }
        self.regions.append(region)
        self.regions.sort(key=lambda r: r["start"])
        return region
    
    def get_layer(self, name: str) -> Optional[TimelineLayer]:
        """Get a layer by name."""
        for layer in self.layers:
            if layer.name == name:
                return layer
        return None
    
    def get_active_tracks(self) -> List[TimelineTrack]:
        """Get all active (enabled and visible) tracks."""
        active_tracks = []
        
        for layer in self.layers:
            if not layer.visible:
                continue
            
            # Check if layer is solo
            solo_layers = [l for l in self.layers if l.solo]
            if solo_layers and layer not in solo_layers:
                continue
            
            for track in layer.tracks:
                if track.enabled and not track.locked:
                    active_tracks.append(track)
        
        return active_tracks
    
    def get_events_in_range(self, start: float, end: float, 
                           tags: Optional[List[str]] = None) -> List[TimelineEvent]:
        """Get all events within a time range."""
        events = []
        
        for event in self.event_queue:
            if start <= event.time <= end and event.enabled:
                if tags is None or any(tag in event.tags for tag in tags):
                    events.append(event)
        
        return sorted(events, key=lambda e: e.time)
    
    def seek(self, time: float):
        """Seek to a specific time."""
        self.current_time = max(0, min(time, self.duration))
        self._trigger_time_callbacks()
    
    def play(self, scene):
        """Play the timeline on a scene."""
        # Reset current time if at end
        if self.current_time >= self.duration:
            self.current_time = 0.0
        
        self.is_playing = True
        
        # Process events up to current time
        events_to_process = []
        temp_queue = []
        
        while self.event_queue:
            event = heapq.heappop(self.event_queue)
            if event.time <= self.current_time and event.enabled:
                events_to_process.append(event)
            else:
                temp_queue.append(event)
        
        # Restore unprocessed events
        for event in temp_queue:
            heapq.heappush(self.event_queue, event)
        
        # Process events
        for event in sorted(events_to_process, key=lambda e: e.time):
            try:
                event.callback(scene)
            except Exception as e:
                print(f"Error in timeline event '{event.name}': {e}")
        
        self._trigger_playback_callbacks(scene)
    
    def pause(self):
        """Pause timeline playback."""
        self.is_playing = False
    
    def stop(self):
        """Stop timeline and reset to beginning."""
        self.is_playing = False
        self.current_time = 0.0
    
    def export_to_json(self, filepath: Union[str, Path]):
        """Export timeline to JSON format."""
        data = {
            "duration": self.duration,
            "fps": self.fps,
            "layers": [],
            "markers": [],
            "regions": self.regions
        }
        
        # Export layers and tracks
        for layer in self.layers:
            layer_data = {
                "name": layer.name,
                "visible": layer.visible,
                "locked": layer.locked,
                "solo": layer.solo,
                "z_index": layer.z_index,
                "parent_layer": layer.parent_layer,
                "transform": layer.transform,
                "tracks": []
            }
            
            for track in layer.tracks:
                track_data = {
                    "name": track.name,
                    "type": track.track_type.value,
                    "enabled": track.enabled,
                    "keyframes": {}
                }
                
                # Export keyframes
                for prop_name, keyframes in track.keyframes.items():
                    track_data["keyframes"][prop_name] = [
                        {
                            "time": kf.time,
                            "value": kf.value,
                            "interpolation": kf.interpolation.value
                        }
                        for kf in keyframes
                    ]
                
                layer_data["tracks"].append(track_data)
            
            data["layers"].append(layer_data)
        
        # Export markers
        data["markers"] = [
            {
                "time": marker.time,
                "label": marker.label,
                "color": marker.color,
                "duration": marker.duration
            }
            for marker in self.markers
        ]
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def import_from_json(self, filepath: Union[str, Path]):
        """Import timeline from JSON format."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.duration = data.get("duration", 10.0)
        self.fps = data.get("fps", 60.0)
        self.layers.clear()
        self.markers.clear()
        self.regions = data.get("regions", [])
        
        # Import layers and tracks
        for layer_data in data.get("layers", []):
            layer = TimelineLayer(
                name=layer_data["name"],
                visible=layer_data.get("visible", True),
                locked=layer_data.get("locked", False),
                solo=layer_data.get("solo", False),
                z_index=layer_data.get("z_index", 0),
                parent_layer=layer_data.get("parent_layer"),
                transform=layer_data.get("transform", {"x": 0, "y": 0, "scale": 1, "rotation": 0})
            )
            
            for track_data in layer_data.get("tracks", []):
                track = TimelineTrack(
                    name=track_data["name"],
                    track_type=TrackType(track_data.get("type", "animation")),
                    enabled=track_data.get("enabled", True)
                )
                
                # Import keyframes
                for prop_name, keyframes_data in track_data.get("keyframes", {}).items():
                    for kf_data in keyframes_data:
                        keyframe = Keyframe(
                            time=kf_data["time"],
                            value=kf_data["value"],
                            interpolation=InterpolationType(kf_data.get("interpolation", "linear"))
                        )
                        track.add_keyframe(prop_name, keyframe)
                
                layer.add_track(track)
            
            self.layers.append(layer)
        
        # Import markers
        for marker_data in data.get("markers", []):
            self.add_marker(
                time=marker_data["time"],
                label=marker_data["label"],
                color=marker_data.get("color", "#FFFF00"),
                duration=marker_data.get("duration", 0.0)
            )
    
    def add_playback_callback(self, callback: Callable):
        """Add a callback that's called during playback."""
        self.playback_callbacks.append(callback)
    
    def add_time_callback(self, time: float, callback: Callable):
        """Add a callback for a specific time."""
        if time not in self.time_callbacks:
            self.time_callbacks[time] = []
        self.time_callbacks[time].append(callback)
    
    def _trigger_time_callbacks(self):
        """Trigger callbacks for the current time."""
        for time, callbacks in self.time_callbacks.items():
            if abs(self.current_time - time) < 1.0 / self.fps:
                for callback in callbacks:
                    callback(self.current_time)
    
    def _trigger_playback_callbacks(self, scene):
        """Trigger playback callbacks."""
        for callback in self.playback_callbacks:
            callback(scene, self.current_time)
    
    def _sort_layers_by_z_index(self):
        """Sort layers by z-index for proper rendering order."""
        self.layers.sort(key=lambda layer: layer.z_index)
    
    def set_layer_z_index(self, layer_name: str, z_index: int):
        """Set z-index for a specific layer."""
        layer = self.get_layer(layer_name)
        if layer:
            layer.z_index = z_index
            self._sort_layers_by_z_index()
    
    def move_layer_forward(self, layer_name: str):
        """Move layer one position forward (higher z-index)."""
        layer = self.get_layer(layer_name)
        if not layer:
            return
        
        current_idx = self.layers.index(layer)
        if current_idx < len(self.layers) - 1:
            # Swap z-indices
            next_layer = self.layers[current_idx + 1]
            layer.z_index, next_layer.z_index = next_layer.z_index, layer.z_index
            self._sort_layers_by_z_index()
    
    def move_layer_backward(self, layer_name: str):
        """Move layer one position backward (lower z-index)."""
        layer = self.get_layer(layer_name)
        if not layer:
            return
        
        current_idx = self.layers.index(layer)
        if current_idx > 0:
            # Swap z-indices
            prev_layer = self.layers[current_idx - 1]
            layer.z_index, prev_layer.z_index = prev_layer.z_index, layer.z_index
            self._sort_layers_by_z_index()
    
    def move_layer_to_top(self, layer_name: str):
        """Move layer to the top (highest z-index)."""
        layer = self.get_layer(layer_name)
        if layer:
            max_z = max((l.z_index for l in self.layers), default=0)
            layer.z_index = max_z + 10
            self._sort_layers_by_z_index()
    
    def move_layer_to_bottom(self, layer_name: str):
        """Move layer to the bottom (lowest z-index)."""
        layer = self.get_layer(layer_name)
        if layer:
            min_z = min((l.z_index for l in self.layers), default=0)
            layer.z_index = min_z - 10
            self._sort_layers_by_z_index()
    
    def get_layers_ordered(self) -> List[TimelineLayer]:
        """Get layers in proper rendering order (by z-index)."""
        return sorted(self.layers, key=lambda layer: layer.z_index)
    
    def apply_layer_ordering_to_scene(self, scene, mobjects_by_layer: Dict[str, List]):
        """Apply layer z-ordering to Manim scene objects.
        
        Args:
            scene: The Manim scene
            mobjects_by_layer: Dict mapping layer names to lists of mobjects
        """
        # Clear and re-add mobjects in proper order
        all_mobjects = []
        for layer in self.get_layers_ordered():
            if layer.name in mobjects_by_layer:
                all_mobjects.extend(mobjects_by_layer[layer.name])
        
        # Remove all mobjects
        scene.remove(*scene.mobjects)
        
        # Re-add in proper order
        for mob in all_mobjects:
            scene.add(mob)
    
    def generate_preview_data(self, width: int = 800, height: int = 200) -> Dict[str, Any]:
        """Generate preview data for timeline visualization."""
        preview = {
            "duration": self.duration,
            "fps": self.fps,
            "width": width,
            "height": height,
            "layers": [],
            "markers": [
                {
                    "position": marker.time / self.duration * width,
                    "label": marker.label,
                    "color": marker.color
                }
                for marker in self.markers
            ],
            "regions": [
                {
                    "start": region["start"] / self.duration * width,
                    "end": region["end"] / self.duration * width,
                    "name": region["name"],
                    "color": region["color"]
                }
                for region in self.regions
            ]
        }
        
        # Calculate layer heights
        layer_height = height / len(self.layers) if self.layers else height
        
        for i, layer in enumerate(self.layers):
            layer_preview = {
                "name": layer.name,
                "y": i * layer_height,
                "height": layer_height,
                "tracks": []
            }
            
            track_height = layer_height / len(layer.tracks) if layer.tracks else layer_height
            
            for j, track in enumerate(layer.tracks):
                track_preview = {
                    "name": track.name,
                    "y": i * layer_height + j * track_height,
                    "height": track_height,
                    "events": [],
                    "keyframes": []
                }
                
                # Add events
                for event in track.events:
                    if event.enabled:
                        track_preview["events"].append({
                            "x": event.time / self.duration * width,
                            "width": event.duration / self.duration * width if event.duration > 0 else 2,
                            "name": event.name
                        })
                
                # Add keyframes
                for prop_name, keyframes in track.keyframes.items():
                    for kf in keyframes:
                        track_preview["keyframes"].append({
                            "x": kf.time / self.duration * width,
                            "property": prop_name,
                            "value": str(kf.value)[:20]  # Truncate long values
                        })
                
                layer_preview["tracks"].append(track_preview)
            
            preview["layers"].append(layer_preview)
        
        return preview