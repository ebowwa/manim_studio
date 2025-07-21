"""Timeline debugging tools for development and troubleshooting."""

from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass
from datetime import datetime
import json
import time
from pathlib import Path

from manim import *
from core.timeline.composer_timeline import (
    ComposerTimeline, TimelineEvent, TimelineLayer, 
    TimelineTrack, Keyframe, InterpolationType
)

@dataclass
class TimelineBreakpoint:
    """Breakpoint for timeline debugging."""
    time: float
    condition: Optional[Callable[[ComposerTimeline], bool]] = None
    enabled: bool = True
    hit_count: int = 0
    label: str = ""
    
    def should_break(self, timeline: ComposerTimeline) -> bool:
        """Check if should break at this point."""
        if not self.enabled:
            return False
        
        if abs(timeline.current_time - self.time) < 0.01:
            if self.condition is None or self.condition(timeline):
                self.hit_count += 1
                return True
        return False

@dataclass
class TimelineLog:
    """Log entry for timeline events."""
    timestamp: float
    event_type: str
    details: Dict[str, Any]
    timeline_time: float
    
    def __str__(self) -> str:
        return f"[{self.timestamp:.3f}] {self.event_type} at {self.timeline_time:.3f}s: {self.details}"

class TimelineDebugger:
    """Debugger for timeline development and troubleshooting."""
    
    def __init__(self, timeline: ComposerTimeline):
        self.timeline = timeline
        self.breakpoints: List[TimelineBreakpoint] = []
        self.logs: List[TimelineLog] = []
        self.step_mode = False
        self.playback_speed = 1.0
        self.performance_metrics: Dict[str, List[float]] = {}
        self.watches: Dict[str, Callable[[ComposerTimeline], Any]] = {}
        self.start_time = time.time()
        
        # Debug overlay
        self.debug_overlay: Optional[VGroup] = None
        self.show_overlay = True
        
        # Event tracking
        self.event_history: List[TimelineEvent] = []
        self.skipped_events: List[TimelineEvent] = []
        
        # State snapshots
        self.snapshots: Dict[float, Dict[str, Any]] = {}
    
    def add_breakpoint(self, time: float, condition: Optional[Callable] = None, 
                      label: str = "") -> TimelineBreakpoint:
        """Add a breakpoint at specific time."""
        bp = TimelineBreakpoint(time, condition, label=label)
        self.breakpoints.append(bp)
        self.breakpoints.sort(key=lambda b: b.time)
        return bp
    
    def remove_breakpoint(self, breakpoint: TimelineBreakpoint):
        """Remove a breakpoint."""
        if breakpoint in self.breakpoints:
            self.breakpoints.remove(breakpoint)
    
    def add_watch(self, name: str, expression: Callable[[ComposerTimeline], Any]):
        """Add a watch expression."""
        self.watches[name] = expression
    
    def log_event(self, event_type: str, details: Dict[str, Any]):
        """Log a timeline event."""
        log = TimelineLog(
            timestamp=time.time() - self.start_time,
            event_type=event_type,
            details=details,
            timeline_time=self.timeline.current_time
        )
        self.logs.append(log)
    
    def step_forward(self, delta: float = 0.1):
        """Step forward in timeline."""
        new_time = min(self.timeline.current_time + delta, self.timeline.duration)
        self.timeline.seek(new_time)
        self._update_debug_info()
    
    def step_backward(self, delta: float = 0.1):
        """Step backward in timeline."""
        new_time = max(self.timeline.current_time - delta, 0)
        self.timeline.seek(new_time)
        self._update_debug_info()
    
    def play_with_debugging(self, scene):
        """Play timeline with debugging features."""
        self.log_event("playback_start", {"speed": self.playback_speed})
        
        # Check for breakpoints
        for bp in self.breakpoints:
            if bp.should_break(self.timeline):
                self.log_event("breakpoint_hit", {"time": bp.time, "label": bp.label})
                self._pause_for_debugging(scene, bp)
        
        # Track performance
        start = time.perf_counter()
        
        # Play timeline
        self.timeline.play(scene)
        
        # Record performance
        duration = time.perf_counter() - start
        self._record_performance("frame_time", duration)
        
        # Update overlay
        if self.show_overlay and self.debug_overlay:
            self._update_overlay(scene)
    
    def _pause_for_debugging(self, scene, breakpoint: TimelineBreakpoint):
        """Pause execution at breakpoint."""
        print(f"\n🔴 Breakpoint hit at {breakpoint.time}s: {breakpoint.label}")
        print(f"Timeline state:")
        print(f"  Current time: {self.timeline.current_time}")
        print(f"  Active tracks: {len(self.timeline.get_active_tracks())}")
        
        # Show watches
        if self.watches:
            print("\nWatches:")
            for name, expr in self.watches.items():
                try:
                    value = expr(self.timeline)
                    print(f"  {name}: {value}")
                except Exception as e:
                    print(f"  {name}: <Error: {e}>")
        
        # Wait for user input in step mode
        if self.step_mode:
            input("\nPress Enter to continue...")
    
    def create_debug_overlay(self, scene) -> VGroup:
        """Create debug overlay for scene."""
        overlay = VGroup()
        
        # Background
        bg = Rectangle(
            width=4, height=3,
            color=BLACK, fill_opacity=0.8,
            stroke_width=1, stroke_color=WHITE
        )
        bg.to_corner(UL, buff=0.2)
        overlay.add(bg)
        
        # Timeline info
        info_text = VGroup()
        
        # Current time
        time_text = Text(f"Time: {self.timeline.current_time:.2f}s", font_size=16)
        time_text.to_edge(LEFT, buff=0.3).shift(UP * 1.2)
        info_text.add(time_text)
        
        # FPS
        fps = self._calculate_fps()
        fps_text = Text(f"FPS: {fps:.1f}", font_size=16)
        fps_text.next_to(time_text, DOWN, aligned_edge=LEFT)
        info_text.add(fps_text)
        
        # Active events
        active_count = len([e for e in self.timeline.event_queue if e.enabled])
        events_text = Text(f"Events: {active_count}", font_size=16)
        events_text.next_to(fps_text, DOWN, aligned_edge=LEFT)
        info_text.add(events_text)
        
        # Memory usage (if available)
        try:
            import psutil
            process = psutil.Process()
            mem_mb = process.memory_info().rss / 1024 / 1024
            mem_text = Text(f"Memory: {mem_mb:.1f} MB", font_size=16)
            mem_text.next_to(events_text, DOWN, aligned_edge=LEFT)
            info_text.add(mem_text)
        except ImportError:
            pass
        
        overlay.add(info_text)
        
        # Breakpoint indicators
        for bp in self.breakpoints:
            if bp.enabled:
                bp_indicator = Dot(color=RED, radius=0.05)
                bp_x = -6 + (bp.time / self.timeline.duration) * 12
                bp_indicator.move_to(np.array([bp_x, -3.5, 0]))
                overlay.add(bp_indicator)
        
        # Timeline progress bar
        progress_bg = Rectangle(width=12, height=0.2, color=GREY_D, fill_opacity=1)
        progress_bg.move_to(DOWN * 3.5)
        overlay.add(progress_bg)
        
        progress = Rectangle(
            width=12 * (self.timeline.current_time / self.timeline.duration),
            height=0.2, color=GREEN, fill_opacity=1
        )
        progress.move_to(progress_bg, aligned_edge=LEFT)
        overlay.add(progress)
        
        self.debug_overlay = overlay
        return overlay
    
    def _update_overlay(self, scene):
        """Update debug overlay with current info."""
        if not self.debug_overlay:
            return
        
        # Update text values
        texts = self.debug_overlay[1]  # Info text group
        if len(texts) > 0:
            texts[0].become(Text(f"Time: {self.timeline.current_time:.2f}s", font_size=16))
            texts[0].to_edge(LEFT, buff=0.3).shift(UP * 1.2)
        
        if len(texts) > 1:
            fps = self._calculate_fps()
            texts[1].become(Text(f"FPS: {fps:.1f}", font_size=16))
            texts[1].next_to(texts[0], DOWN, aligned_edge=LEFT)
        
        # Update progress bar
        progress = self.debug_overlay[-1]
        new_width = 12 * (self.timeline.current_time / self.timeline.duration)
        progress.become(Rectangle(
            width=new_width, height=0.2, color=GREEN, fill_opacity=1
        ))
        progress.move_to(self.debug_overlay[-2], aligned_edge=LEFT)
    
    def _record_performance(self, metric: str, value: float):
        """Record performance metric."""
        if metric not in self.performance_metrics:
            self.performance_metrics[metric] = []
        self.performance_metrics[metric].append(value)
        
        # Keep only last 100 samples
        if len(self.performance_metrics[metric]) > 100:
            self.performance_metrics[metric].pop(0)
    
    def _calculate_fps(self) -> float:
        """Calculate current FPS."""
        if "frame_time" not in self.performance_metrics:
            return 0.0
        
        frame_times = self.performance_metrics["frame_time"]
        if not frame_times:
            return 0.0
        
        avg_frame_time = sum(frame_times) / len(frame_times)
        return 1.0 / avg_frame_time if avg_frame_time > 0 else 0.0
    
    def take_snapshot(self, label: Optional[str] = None):
        """Take a snapshot of current timeline state."""
        snapshot_time = self.timeline.current_time
        
        snapshot = {
            "time": snapshot_time,
            "label": label or f"snapshot_{len(self.snapshots)}",
            "timestamp": datetime.now().isoformat(),
            "layers": {},
            "events": [],
            "performance": dict(self.performance_metrics)
        }
        
        # Capture layer states
        for layer in self.timeline.layers:
            layer_data = {
                "visible": layer.visible,
                "locked": layer.locked,
                "solo": layer.solo,
                "tracks": {}
            }
            
            for track in layer.tracks:
                track_data = {
                    "enabled": track.enabled,
                    "keyframe_values": {}
                }
                
                # Capture current keyframe values
                for prop_name in track.keyframes:
                    value = track.get_value_at_time(prop_name, snapshot_time)
                    track_data["keyframe_values"][prop_name] = value
                
                layer_data["tracks"][track.name] = track_data
            
            snapshot["layers"][layer.name] = layer_data
        
        # Capture pending events
        for event in self.timeline.event_queue:
            if event.time >= snapshot_time:
                snapshot["events"].append({
                    "name": event.name,
                    "time": event.time,
                    "enabled": event.enabled,
                    "tags": event.tags
                })
        
        self.snapshots[snapshot_time] = snapshot
        self.log_event("snapshot_taken", {"label": snapshot["label"]})
        
        return snapshot
    
    def compare_snapshots(self, time1: float, time2: float) -> Dict[str, Any]:
        """Compare two timeline snapshots."""
        if time1 not in self.snapshots or time2 not in self.snapshots:
            raise ValueError("Snapshot times not found")
        
        snap1 = self.snapshots[time1]
        snap2 = self.snapshots[time2]
        
        differences = {
            "time_diff": time2 - time1,
            "layer_changes": {},
            "event_changes": {},
            "performance_changes": {}
        }
        
        # Compare layers
        for layer_name in snap1["layers"]:
            if layer_name in snap2["layers"]:
                layer1 = snap1["layers"][layer_name]
                layer2 = snap2["layers"][layer_name]
                
                if layer1 != layer2:
                    differences["layer_changes"][layer_name] = {
                        "before": layer1,
                        "after": layer2
                    }
        
        return differences
    
    def export_debug_report(self, filepath: Path):
        """Export comprehensive debug report."""
        report = {
            "timeline_info": {
                "duration": self.timeline.duration,
                "fps": self.timeline.fps,
                "current_time": self.timeline.current_time,
                "layers": len(self.timeline.layers),
                "total_events": len(self.event_history)
            },
            "logs": [
                {
                    "timestamp": log.timestamp,
                    "type": log.event_type,
                    "details": log.details,
                    "time": log.timeline_time
                }
                for log in self.logs
            ],
            "performance": {
                metric: {
                    "samples": len(values),
                    "average": sum(values) / len(values) if values else 0,
                    "min": min(values) if values else 0,
                    "max": max(values) if values else 0
                }
                for metric, values in self.performance_metrics.items()
            },
            "breakpoints": [
                {
                    "time": bp.time,
                    "label": bp.label,
                    "hit_count": bp.hit_count,
                    "enabled": bp.enabled
                }
                for bp in self.breakpoints
            ],
            "snapshots": list(self.snapshots.values())
        }
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Debug report exported to: {filepath}")
    
    def validate_timeline(self) -> List[str]:
        """Validate timeline for common issues."""
        issues = []
        
        # Check for overlapping events
        events = sorted(self.timeline.event_queue, key=lambda e: e.time)
        for i in range(len(events) - 1):
            if events[i].time == events[i+1].time and events[i].track_name == events[i+1].track_name:
                issues.append(f"Overlapping events at {events[i].time}s on track {events[i].track_name}")
        
        # Check for invalid keyframes
        for layer in self.timeline.layers:
            for track in layer.tracks:
                for prop_name, keyframes in track.keyframes.items():
                    if not keyframes:
                        issues.append(f"Empty keyframe list for {prop_name} in track {track.name}")
                    
                    # Check keyframe order
                    for i in range(len(keyframes) - 1):
                        if keyframes[i].time >= keyframes[i+1].time:
                            issues.append(f"Keyframes out of order for {prop_name} in track {track.name}")
        
        # Check for disabled layers with active tracks
        for layer in self.timeline.layers:
            if not layer.visible:
                active_tracks = [t for t in layer.tracks if t.enabled]
                if active_tracks:
                    issues.append(f"Hidden layer '{layer.name}' has {len(active_tracks)} active tracks")
        
        return issues
    
    def _update_debug_info(self):
        """Update debug information after timeline change."""
        self.log_event("timeline_seek", {"new_time": self.timeline.current_time})
        
        # Evaluate watches
        for name, expr in self.watches.items():
            try:
                value = expr(self.timeline)
                self.log_event("watch_update", {"name": name, "value": str(value)})
            except Exception as e:
                self.log_event("watch_error", {"name": name, "error": str(e)})