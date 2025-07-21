"""Timeline system for choreographing animations."""

from typing import Any, Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import heapq
from manim import *


@dataclass
class TimelineEvent:
    """Represents a single event in the timeline."""
    time: float
    action: Callable
    args: tuple = ()
    kwargs: dict = field(default_factory=dict)
    name: str = ""
    
    def __lt__(self, other):
        return self.time < other.time
    
    def execute(self, scene: Scene) -> Any:
        """Execute the event action."""
        return self.action(scene, *self.args, **self.kwargs)


class Timeline:
    """Manages and executes a sequence of timed events."""
    
    def __init__(self):
        self.events: List[TimelineEvent] = []
        self.current_time: float = 0.0
        self._is_playing: bool = False
    
    def add_event(
        self,
        time: float,
        action: Callable,
        args: tuple = (),
        kwargs: dict = None,
        name: str = ""
    ) -> None:
        """Add an event to the timeline."""
        event = TimelineEvent(time, action, args, kwargs or {}, name)
        heapq.heappush(self.events, event)
    
    def add_animation(
        self,
        time: float,
        animation: Animation,
        name: str = ""
    ) -> None:
        """Add an animation to the timeline."""
        def play_animation(scene: Scene, anim: Animation):
            scene.play(anim)
        
        self.add_event(time, play_animation, (animation,), name=name)
    
    def add_wait(self, time: float, duration: float) -> None:
        """Add a wait/pause to the timeline."""
        def wait(scene: Scene, duration: float):
            scene.wait(duration)
        
        self.add_event(time, wait, (duration,), name=f"wait_{duration}s")
    
    def add_sequence(
        self,
        start_time: float,
        events: List[Tuple[float, Callable, tuple, dict]],
        name_prefix: str = ""
    ) -> None:
        """Add a sequence of events starting at a specific time."""
        for i, (offset, action, args, kwargs) in enumerate(events):
            event_name = f"{name_prefix}_{i}" if name_prefix else ""
            self.add_event(
                start_time + offset,
                action,
                args,
                kwargs,
                event_name
            )
    
    def play(self, scene: Scene) -> None:
        """Play the timeline on the given scene."""
        self._is_playing = True
        self.current_time = 0.0
        
        # Sort events by time
        sorted_events = sorted(self.events)
        
        for event in sorted_events:
            if not self._is_playing:
                break
            
            # Wait until event time
            if event.time > self.current_time:
                wait_time = event.time - self.current_time
                scene.wait(wait_time)
                self.current_time = event.time
            
            # Execute event
            event.execute(scene)
    
    def stop(self) -> None:
        """Stop timeline playback."""
        self._is_playing = False
    
    def clear(self) -> None:
        """Clear all events from the timeline."""
        self.events.clear()
        self.current_time = 0.0
    
    def get_duration(self) -> float:
        """Get the total duration of the timeline."""
        if not self.events:
            return 0.0
        return max(event.time for event in self.events)
    
    def get_events_between(self, start: float, end: float) -> List[TimelineEvent]:
        """Get all events between two time points."""
        return [e for e in self.events if start <= e.time <= end]
    
    @classmethod
    def from_config(cls, config: List[Dict[str, Any]]) -> 'Timeline':
        """Create timeline from configuration."""
        timeline = cls()
        
        for event_config in config:
            event_type = event_config.get('type', 'custom')
            time = event_config.get('time', 0.0)
            
            if event_type == 'animation':
                # Handle animation events
                target = event_config.get('target')
                anim_type = event_config.get('animation')
                params = event_config.get('params', {})
                
                # This would need to be connected to actual scene objects
                # For now, we'll store the configuration
                timeline.add_event(
                    time,
                    lambda s, t=target, a=anim_type, p=params: None,
                    name=f"{anim_type}_{target}"
                )
            
            elif event_type == 'wait':
                duration = event_config.get('duration', 1.0)
                timeline.add_wait(time, duration)
        
        return timeline