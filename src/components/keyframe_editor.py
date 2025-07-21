"""Keyframe editor for advanced animation control."""

from typing import Any, Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass
import numpy as np
from manim import *
from core.timeline.composer_timeline import Keyframe, InterpolationType, TimelineTrack

@dataclass
class AnimationCurve:
    """Represents an animation curve for visualizing keyframe interpolation."""
    keyframes: List[Keyframe]
    property_name: str
    color: str = "#4ECDC4"
    samples: int = 100
    
    def evaluate_at_time(self, time: float) -> Any:
        """Evaluate the curve at a specific time."""
        if not self.keyframes:
            return None
        
        # Find surrounding keyframes
        prev_kf = None
        next_kf = None
        
        for kf in self.keyframes:
            if kf.time <= time:
                prev_kf = kf
            elif kf.time > time and next_kf is None:
                next_kf = kf
                break
        
        if prev_kf is None:
            return self.keyframes[0].value
        if next_kf is None:
            return prev_kf.value
        
        return prev_kf.interpolate_to(next_kf, time)
    
    def get_curve_points(self, start_time: float = 0, end_time: float = 10) -> List[np.ndarray]:
        """Get points for drawing the curve."""
        if not self.keyframes:
            return []
        
        points = []
        time_step = (end_time - start_time) / self.samples
        
        for i in range(self.samples + 1):
            time = start_time + i * time_step
            value = self.evaluate_at_time(time)
            
            # Handle different value types
            if isinstance(value, (int, float)):
                points.append(np.array([time, value, 0]))
            elif isinstance(value, (list, tuple)) and len(value) >= 2:
                points.append(np.array([time, value[0], 0]))  # Use first component
            else:
                # Skip non-numeric values
                continue
        
        return points

class KeyframeEditor(VGroup):
    """Visual keyframe editor for timeline properties."""
    
    def __init__(self, track: TimelineTrack, width: float = 10, height: float = 6, **kwargs):
        super().__init__(**kwargs)
        self.track = track
        self.width = width
        self.height = height
        self.selected_keyframe: Optional[Keyframe] = None
        self.selected_property: Optional[str] = None
        self.curves: Dict[str, AnimationCurve] = {}
        
        # Interpolation colors
        self.interp_colors = {
            InterpolationType.LINEAR: "#4ECDC4",
            InterpolationType.EASE_IN: "#FF6B6B",
            InterpolationType.EASE_OUT: "#95E1D3",
            InterpolationType.EASE_IN_OUT: "#F38181",
            InterpolationType.CUBIC_BEZIER: "#9B59B6",
            InterpolationType.STEP: "#E74C3C",
            InterpolationType.SPRING: "#F39C12"
        }
        
        self._create_editor()
    
    def _create_editor(self):
        """Create the keyframe editor interface."""
        # Background grid
        grid = self._create_grid()
        self.add(grid)
        
        # Axes
        axes = self._create_axes()
        self.add(axes)
        
        # Property curves
        curves_group = self._create_curves()
        self.add(curves_group)
        
        # Keyframe handles
        handles = self._create_keyframe_handles()
        self.add(handles)
        
        # Interpolation legend
        legend = self._create_interpolation_legend()
        legend.to_corner(UR, buff=0.5)
        self.add(legend)
    
    def _create_grid(self) -> VGroup:
        """Create background grid."""
        grid = VGroup()
        
        # Vertical lines
        for i in range(11):
            x = -self.width/2 + i * self.width/10
            line = DashedLine(
                start=np.array([x, -self.height/2, 0]),
                end=np.array([x, self.height/2, 0]),
                color=GREY_D,
                stroke_width=0.5
            )
            grid.add(line)
        
        # Horizontal lines
        for i in range(7):
            y = -self.height/2 + i * self.height/6
            line = DashedLine(
                start=np.array([-self.width/2, y, 0]),
                end=np.array([self.width/2, y, 0]),
                color=GREY_D,
                stroke_width=0.5
            )
            grid.add(line)
        
        return grid
    
    def _create_axes(self) -> VGroup:
        """Create axes for the editor."""
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[-1, 1, 0.5],
            x_length=self.width,
            y_length=self.height,
            axis_config={
                "color": WHITE,
                "include_numbers": True,
                "font_size": 16
            }
        )
        
        # Labels
        x_label = Text("Time (s)", font_size=20).next_to(axes.x_axis, DOWN)
        y_label = Text("Value", font_size=20).next_to(axes.y_axis, LEFT).rotate(PI/2)
        
        axes.add(x_label, y_label)
        return axes
    
    def _create_curves(self) -> VGroup:
        """Create animation curves for each property."""
        curves_group = VGroup()
        
        # Create curve for each property with keyframes
        for i, (prop_name, keyframes) in enumerate(self.track.keyframes.items()):
            if not keyframes:
                continue
            
            # Create animation curve
            curve = AnimationCurve(
                keyframes=keyframes,
                property_name=prop_name,
                color=self._get_property_color(i)
            )
            self.curves[prop_name] = curve
            
            # Draw curve
            curve_visual = self._draw_curve(curve)
            curves_group.add(curve_visual)
        
        return curves_group
    
    def _draw_curve(self, curve: AnimationCurve) -> VGroup:
        """Draw an animation curve."""
        curve_group = VGroup()
        
        # Get curve points
        points = curve.get_curve_points()
        if len(points) < 2:
            return curve_group
        
        # Scale points to fit editor
        scaled_points = []
        for point in points:
            x = (point[0] / 10) * self.width - self.width/2  # Assuming 10s duration
            y = point[1] * self.height/2  # Assuming -1 to 1 value range
            scaled_points.append(np.array([x, y, 0]))
        
        # Draw curve segments based on interpolation
        for i in range(len(curve.keyframes) - 1):
            kf = curve.keyframes[i]
            next_kf = curve.keyframes[i + 1]
            
            # Find points for this segment
            segment_points = []
            for j, point in enumerate(points):
                if kf.time <= point[0] <= next_kf.time:
                    segment_points.append(scaled_points[j])
            
            if len(segment_points) >= 2:
                # Create path with interpolation-specific style
                color = self.interp_colors.get(kf.interpolation, curve.color)
                
                if kf.interpolation == InterpolationType.STEP:
                    # Step interpolation - draw horizontal then vertical lines
                    for j in range(len(segment_points) - 1):
                        h_line = Line(
                            segment_points[j],
                            np.array([segment_points[j+1][0], segment_points[j][1], 0]),
                            color=color,
                            stroke_width=2
                        )
                        v_line = Line(
                            np.array([segment_points[j+1][0], segment_points[j][1], 0]),
                            segment_points[j+1],
                            color=color,
                            stroke_width=2
                        )
                        curve_group.add(h_line, v_line)
                else:
                    # Smooth interpolation
                    path = VMobject()
                    path.set_points_as_corners(segment_points)
                    path.set_stroke(color, width=2)
                    curve_group.add(path)
        
        # Add property label
        label = Text(curve.property_name, font_size=14, color=curve.color)
        if curve.keyframes:
            last_point = scaled_points[-1]
            label.next_to(last_point, RIGHT, buff=0.1)
            curve_group.add(label)
        
        return curve_group
    
    def _create_keyframe_handles(self) -> VGroup:
        """Create interactive handles for keyframes."""
        handles_group = VGroup()
        
        for prop_name, keyframes in self.track.keyframes.items():
            curve_color = self.curves.get(prop_name, AnimationCurve([], "")).color
            
            for kf in keyframes:
                handle = self._create_keyframe_handle(kf, prop_name, curve_color)
                handles_group.add(handle)
        
        return handles_group
    
    def _create_keyframe_handle(self, keyframe: Keyframe, prop_name: str, color: str) -> VGroup:
        """Create a single keyframe handle."""
        # Scale position
        x = (keyframe.time / 10) * self.width - self.width/2
        y = 0  # Default to center, should be based on value
        
        if isinstance(keyframe.value, (int, float)):
            y = keyframe.value * self.height/2
        
        # Create handle shape based on interpolation type
        if keyframe.interpolation == InterpolationType.STEP:
            handle = Square(side_length=0.15, color=color, fill_opacity=1)
        elif keyframe.interpolation in [InterpolationType.EASE_IN, InterpolationType.EASE_OUT, InterpolationType.EASE_IN_OUT]:
            handle = Circle(radius=0.08, color=color, fill_opacity=1)
        elif keyframe.interpolation == InterpolationType.CUBIC_BEZIER:
            handle = RegularPolygon(n=6, color=color, fill_opacity=1).scale(0.1)
        else:
            handle = Dot(color=color, radius=0.06)
        
        handle.move_to(np.array([x, y, 0]))
        
        # Add selection indicator
        if self.selected_keyframe == keyframe:
            selection = Circle(radius=0.12, color=YELLOW, stroke_width=2)
            selection.move_to(handle.get_center())
            return VGroup(handle, selection)
        
        return handle
    
    def _create_interpolation_legend(self) -> VGroup:
        """Create legend for interpolation types."""
        legend = VGroup()
        
        # Background
        bg = Rectangle(width=3, height=2, color=GREY_E, fill_opacity=0.2)
        legend.add(bg)
        
        # Title
        title = Text("Interpolation Types", font_size=16, weight=BOLD)
        title.to_edge(UP, buff=0.1)
        legend.add(title)
        
        # Interpolation entries
        entries = VGroup()
        for i, (interp_type, color) in enumerate(self.interp_colors.items()):
            # Icon
            if interp_type == InterpolationType.STEP:
                icon = Square(side_length=0.1, color=color, fill_opacity=1)
            elif interp_type in [InterpolationType.EASE_IN, InterpolationType.EASE_OUT, InterpolationType.EASE_IN_OUT]:
                icon = Circle(radius=0.05, color=color, fill_opacity=1)
            elif interp_type == InterpolationType.CUBIC_BEZIER:
                icon = RegularPolygon(n=6, color=color, fill_opacity=1).scale(0.05)
            else:
                icon = Dot(color=color, radius=0.03)
            
            # Label
            label = Text(interp_type.value.replace("_", " ").title(), font_size=12)
            label.next_to(icon, RIGHT, buff=0.1)
            
            entry = VGroup(icon, label)
            entry.shift(DOWN * (i * 0.25))
            entries.add(entry)
        
        entries.next_to(title, DOWN, buff=0.2)
        legend.add(entries)
        
        return legend
    
    def _get_property_color(self, index: int) -> str:
        """Get color for property based on index."""
        colors = ["#4ECDC4", "#FF6B6B", "#95E1D3", "#F38181", "#9B59B6", "#F39C12"]
        return colors[index % len(colors)]
    
    def select_keyframe(self, keyframe: Keyframe, property_name: str):
        """Select a keyframe for editing."""
        self.selected_keyframe = keyframe
        self.selected_property = property_name
        self._update_display()
    
    def add_keyframe(self, time: float, value: Any, property_name: str, 
                    interpolation: InterpolationType = InterpolationType.LINEAR):
        """Add a new keyframe."""
        keyframe = Keyframe(time, value, interpolation)
        self.track.add_keyframe(property_name, keyframe)
        self._update_display()
    
    def delete_selected_keyframe(self):
        """Delete the selected keyframe."""
        if self.selected_keyframe and self.selected_property:
            keyframes = self.track.keyframes.get(self.selected_property, [])
            if self.selected_keyframe in keyframes:
                keyframes.remove(self.selected_keyframe)
                self.selected_keyframe = None
                self._update_display()
    
    def change_interpolation(self, interpolation: InterpolationType):
        """Change interpolation type of selected keyframe."""
        if self.selected_keyframe:
            self.selected_keyframe.interpolation = interpolation
            self._update_display()
    
    def _update_display(self):
        """Update the visual display."""
        # Remove old curves and handles
        self.remove(*self.submobjects[2:])  # Keep grid and axes
        
        # Recreate curves and handles
        curves_group = self._create_curves()
        self.add(curves_group)
        
        handles = self._create_keyframe_handles()
        self.add(handles)
        
        # Re-add legend
        legend = self._create_interpolation_legend()
        legend.to_corner(UR, buff=0.5)
        self.add(legend)
    
    def export_curve_data(self, property_name: str, num_samples: int = 100) -> List[Tuple[float, Any]]:
        """Export curve data as time-value pairs."""
        curve = self.curves.get(property_name)
        if not curve:
            return []
        
        data = []
        for i in range(num_samples + 1):
            time = i * 10.0 / num_samples  # Assuming 10s duration
            value = curve.evaluate_at_time(time)
            data.append((time, value))
        
        return data