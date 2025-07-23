"""
Enhanced easing system for timeline animations.

This module integrates the math3d interpolation utilities to provide
rich easing functions for smooth, professional animations.
"""

from typing import Callable, Dict, Optional, Tuple, Union
from enum import Enum
import numpy as np

# Import our interpolation utilities
from src.utils.math3d.interpolation import (
    smooth_step, smoother_step, smoothest_step,
    ease_in_out, bounce_ease_out, elastic_ease_out,
    circular_ease_in_out, BezierCurve, Vector3D
)


class EasingFunction(Enum):
    """Extended easing function types."""
    # Basic
    LINEAR = "linear"
    STEP = "step"
    
    # Smooth variations
    SMOOTH_STEP = "smooth_step"
    SMOOTHER_STEP = "smoother_step"
    SMOOTHEST_STEP = "smoothest_step"
    
    # Power functions
    EASE_IN_QUAD = "ease_in_quad"
    EASE_OUT_QUAD = "ease_out_quad"
    EASE_IN_OUT_QUAD = "ease_in_out_quad"
    EASE_IN_CUBIC = "ease_in_cubic"
    EASE_OUT_CUBIC = "ease_out_cubic"
    EASE_IN_OUT_CUBIC = "ease_in_out_cubic"
    EASE_IN_QUART = "ease_in_quart"
    EASE_OUT_QUART = "ease_out_quart"
    EASE_IN_OUT_QUART = "ease_in_out_quart"
    EASE_IN_QUINT = "ease_in_quint"
    EASE_OUT_QUINT = "ease_out_quint"
    EASE_IN_OUT_QUINT = "ease_in_out_quint"
    
    # Exponential
    EASE_IN_EXPO = "ease_in_expo"
    EASE_OUT_EXPO = "ease_out_expo"
    EASE_IN_OUT_EXPO = "ease_in_out_expo"
    
    # Circular
    EASE_IN_CIRC = "ease_in_circ"
    EASE_OUT_CIRC = "ease_out_circ"
    EASE_IN_OUT_CIRC = "ease_in_out_circ"
    
    # Elastic
    EASE_IN_ELASTIC = "ease_in_elastic"
    EASE_OUT_ELASTIC = "ease_out_elastic"
    EASE_IN_OUT_ELASTIC = "ease_in_out_elastic"
    
    # Bounce
    EASE_IN_BOUNCE = "ease_in_bounce"
    EASE_OUT_BOUNCE = "ease_out_bounce"
    EASE_IN_OUT_BOUNCE = "ease_in_out_bounce"
    
    # Back (overshoot)
    EASE_IN_BACK = "ease_in_back"
    EASE_OUT_BACK = "ease_out_back"
    EASE_IN_OUT_BACK = "ease_in_out_back"
    
    # Custom
    CUBIC_BEZIER = "cubic_bezier"
    SPRING = "spring"
    
    # Manim-specific rate functions
    THERE_AND_BACK = "there_and_back"
    THERE_AND_BACK_WITH_PAUSE = "there_and_back_with_pause"
    RUSH_INTO = "rush_into"
    RUSH_FROM = "rush_from"
    SLOW_INTO = "slow_into"
    DOUBLE_SMOOTH = "double_smooth"
    TRIPLE_SMOOTH = "triple_smooth"
    NOT_QUITE_THERE = "not_quite_there"
    WIGGLE = "wiggle"
    SQUISH_RATE_FUNC = "squish_rate_func"
    LINGERING = "lingering"
    EXPONENTIAL_DECAY = "exponential_decay"
    # Distinguish Manim's smooth from our smooth_step
    MANIM_SMOOTH = "manim_smooth"


class EasingLibrary:
    """Library of easing functions for timeline animations."""
    
    @staticmethod
    def get_easing_function(easing_type: EasingFunction, 
                          params: Optional[Dict] = None) -> Callable[[float], float]:
        """Get an easing function by type with optional parameters."""
        
        # Basic functions
        if easing_type == EasingFunction.LINEAR:
            return lambda t: t
        
        elif easing_type == EasingFunction.STEP:
            return lambda t: 0 if t < 0.5 else 1
        
        # Smooth step variations
        elif easing_type == EasingFunction.SMOOTH_STEP:
            return smooth_step
        
        elif easing_type == EasingFunction.SMOOTHER_STEP:
            return smoother_step
        
        elif easing_type == EasingFunction.SMOOTHEST_STEP:
            return smoothest_step
        
        # Power functions
        elif easing_type == EasingFunction.EASE_IN_QUAD:
            return lambda t: t * t
        
        elif easing_type == EasingFunction.EASE_OUT_QUAD:
            return lambda t: 1 - (1 - t) ** 2
        
        elif easing_type == EasingFunction.EASE_IN_OUT_QUAD:
            return lambda t: ease_in_out(t, power=2)
        
        elif easing_type == EasingFunction.EASE_IN_CUBIC:
            return lambda t: t ** 3
        
        elif easing_type == EasingFunction.EASE_OUT_CUBIC:
            return lambda t: 1 - (1 - t) ** 3
        
        elif easing_type == EasingFunction.EASE_IN_OUT_CUBIC:
            return lambda t: ease_in_out(t, power=3)
        
        elif easing_type == EasingFunction.EASE_IN_QUART:
            return lambda t: t ** 4
        
        elif easing_type == EasingFunction.EASE_OUT_QUART:
            return lambda t: 1 - (1 - t) ** 4
        
        elif easing_type == EasingFunction.EASE_IN_OUT_QUART:
            return lambda t: ease_in_out(t, power=4)
        
        elif easing_type == EasingFunction.EASE_IN_QUINT:
            return lambda t: t ** 5
        
        elif easing_type == EasingFunction.EASE_OUT_QUINT:
            return lambda t: 1 - (1 - t) ** 5
        
        elif easing_type == EasingFunction.EASE_IN_OUT_QUINT:
            return lambda t: ease_in_out(t, power=5)
        
        # Exponential
        elif easing_type == EasingFunction.EASE_IN_EXPO:
            return lambda t: 0 if t == 0 else 2 ** (10 * (t - 1))
        
        elif easing_type == EasingFunction.EASE_OUT_EXPO:
            return lambda t: 1 if t == 1 else 1 - 2 ** (-10 * t)
        
        elif easing_type == EasingFunction.EASE_IN_OUT_EXPO:
            return lambda t: EasingLibrary._ease_in_out_expo(t)
        
        # Circular
        elif easing_type == EasingFunction.EASE_IN_CIRC:
            return lambda t: 1 - np.sqrt(1 - t * t)
        
        elif easing_type == EasingFunction.EASE_OUT_CIRC:
            return lambda t: np.sqrt(1 - (t - 1) ** 2)
        
        elif easing_type == EasingFunction.EASE_IN_OUT_CIRC:
            return circular_ease_in_out
        
        # Elastic
        elif easing_type == EasingFunction.EASE_IN_ELASTIC:
            amplitude = params.get('amplitude', 1) if params else 1
            period = params.get('period', 0.3) if params else 0.3
            return lambda t: EasingLibrary._ease_in_elastic(t, amplitude, period)
        
        elif easing_type == EasingFunction.EASE_OUT_ELASTIC:
            amplitude = params.get('amplitude', 1) if params else 1
            period = params.get('period', 0.3) if params else 0.3
            return lambda t: elastic_ease_out(t, amplitude, period)
        
        elif easing_type == EasingFunction.EASE_IN_OUT_ELASTIC:
            amplitude = params.get('amplitude', 1) if params else 1
            period = params.get('period', 0.3) if params else 0.3
            return lambda t: EasingLibrary._ease_in_out_elastic(t, amplitude, period)
        
        # Bounce
        elif easing_type == EasingFunction.EASE_IN_BOUNCE:
            return lambda t: 1 - bounce_ease_out(1 - t)
        
        elif easing_type == EasingFunction.EASE_OUT_BOUNCE:
            return bounce_ease_out
        
        elif easing_type == EasingFunction.EASE_IN_OUT_BOUNCE:
            return lambda t: EasingLibrary._ease_in_out_bounce(t)
        
        # Back (overshoot)
        elif easing_type == EasingFunction.EASE_IN_BACK:
            overshoot = params.get('overshoot', 1.70158) if params else 1.70158
            return lambda t: t * t * ((overshoot + 1) * t - overshoot)
        
        elif easing_type == EasingFunction.EASE_OUT_BACK:
            overshoot = params.get('overshoot', 1.70158) if params else 1.70158
            return lambda t: 1 + (t - 1) ** 3 + (t - 1) ** 2 * (overshoot + 1)
        
        elif easing_type == EasingFunction.EASE_IN_OUT_BACK:
            overshoot = params.get('overshoot', 1.70158) if params else 1.70158
            return lambda t: EasingLibrary._ease_in_out_back(t, overshoot)
        
        # Custom Bezier
        elif easing_type == EasingFunction.CUBIC_BEZIER:
            if params and 'control_points' in params:
                x1, y1, x2, y2 = params['control_points']
                return lambda t: EasingLibrary._cubic_bezier_easing(t, x1, y1, x2, y2)
            else:
                # Default to ease-in-out
                return lambda t: EasingLibrary._cubic_bezier_easing(t, 0.42, 0, 0.58, 1)
        
        # Spring
        elif easing_type == EasingFunction.SPRING:
            stiffness = params.get('stiffness', 100) if params else 100
            damping = params.get('damping', 10) if params else 10
            mass = params.get('mass', 1) if params else 1
            return lambda t: EasingLibrary._spring_easing(t, stiffness, damping, mass)
        
        # Manim rate functions
        elif easing_type == EasingFunction.THERE_AND_BACK:
            return lambda t: EasingLibrary._there_and_back(t)
        
        elif easing_type == EasingFunction.THERE_AND_BACK_WITH_PAUSE:
            pause_ratio = params.get('pause_ratio', 1/3) if params else 1/3
            return lambda t: EasingLibrary._there_and_back_with_pause(t, pause_ratio)
        
        elif easing_type == EasingFunction.RUSH_INTO:
            return lambda t: 2 * EasingLibrary._manim_smooth(0.5 * t)
        
        elif easing_type == EasingFunction.RUSH_FROM:
            return lambda t: 2 * EasingLibrary._manim_smooth(0.5 * (t + 1)) - 1
        
        elif easing_type == EasingFunction.SLOW_INTO:
            return lambda t: EasingLibrary._manim_smooth(2 * t) / 2 if t < 0.5 else (1 + EasingLibrary._manim_smooth(2 * (t - 0.5))) / 2
        
        elif easing_type == EasingFunction.DOUBLE_SMOOTH:
            return lambda t: EasingLibrary._manim_smooth(EasingLibrary._manim_smooth(t))
        
        elif easing_type == EasingFunction.TRIPLE_SMOOTH:
            return lambda t: EasingLibrary._manim_smooth(EasingLibrary._manim_smooth(EasingLibrary._manim_smooth(t)))
        
        elif easing_type == EasingFunction.NOT_QUITE_THERE:
            cutoff = params.get('cutoff', 0.9) if params else 0.9
            return lambda t: cutoff * EasingLibrary._manim_smooth(t)
        
        elif easing_type == EasingFunction.WIGGLE:
            wiggles = params.get('wiggles', 4) if params else 4
            return lambda t: EasingLibrary._wiggle(t, wiggles)
        
        elif easing_type == EasingFunction.SQUISH_RATE_FUNC:
            squish_start = params.get('squish_start', 0.25) if params else 0.25
            squish_end = params.get('squish_end', 0.75) if params else 0.75
            return lambda t: EasingLibrary._squish_rate_func(t, squish_start, squish_end)
        
        elif easing_type == EasingFunction.LINGERING:
            return lambda t: EasingLibrary._lingering(t)
        
        elif easing_type == EasingFunction.EXPONENTIAL_DECAY:
            decay_rate = params.get('decay_rate', 3) if params else 3
            return lambda t: 1 - np.exp(-decay_rate * t)
        
        elif easing_type == EasingFunction.MANIM_SMOOTH:
            return lambda t: EasingLibrary._manim_smooth(t)
        
        # Default to linear
        return lambda t: t
    
    @staticmethod
    def _ease_in_out_expo(t: float) -> float:
        """Exponential ease in-out."""
        if t == 0:
            return 0
        if t == 1:
            return 1
        if t < 0.5:
            return 2 ** (20 * t - 10) / 2
        else:
            return (2 - 2 ** (-20 * t + 10)) / 2
    
    @staticmethod
    def _ease_in_elastic(t: float, amplitude: float = 1, period: float = 0.3) -> float:
        """Elastic ease in."""
        if t == 0:
            return 0
        if t == 1:
            return 1
        
        s = period / (2 * np.pi) * np.arcsin(1 / amplitude) if amplitude >= 1 else period / 4
        return -(amplitude * np.power(2, 10 * (t - 1)) * 
                np.sin((t - 1 - s) * 2 * np.pi / period))
    
    @staticmethod
    def _ease_in_out_elastic(t: float, amplitude: float = 1, period: float = 0.3) -> float:
        """Elastic ease in-out."""
        if t == 0:
            return 0
        if t == 1:
            return 1
        
        t = t * 2
        s = period / (2 * np.pi) * np.arcsin(1 / amplitude) if amplitude >= 1 else period / 4
        
        if t < 1:
            return -0.5 * (amplitude * np.power(2, 10 * (t - 1)) * 
                          np.sin((t - 1 - s) * 2 * np.pi / period))
        else:
            t -= 1
            return amplitude * np.power(2, -10 * t) * \
                   np.sin((t - s) * 2 * np.pi / period) * 0.5 + 1
    
    @staticmethod
    def _ease_in_out_bounce(t: float) -> float:
        """Bounce ease in-out."""
        if t < 0.5:
            return (1 - bounce_ease_out(1 - 2 * t)) / 2
        else:
            return (1 + bounce_ease_out(2 * t - 1)) / 2
    
    @staticmethod
    def _ease_in_out_back(t: float, overshoot: float = 1.70158) -> float:
        """Back (overshoot) ease in-out."""
        s = overshoot * 1.525
        t = t * 2
        
        if t < 1:
            return 0.5 * (t * t * ((s + 1) * t - s))
        else:
            t -= 2
            return 0.5 * (t * t * ((s + 1) * t + s) + 2)
    
    @staticmethod
    def _cubic_bezier_easing(t: float, x1: float, y1: float, x2: float, y2: float) -> float:
        """Calculate cubic bezier easing using our BezierCurve class."""
        # Create bezier curve with control points
        # Start at (0, 0), control points at (x1, y1) and (x2, y2), end at (1, 1)
        control_points = [
            Vector3D(0, 0, 0),
            Vector3D(x1, y1, 0),
            Vector3D(x2, y2, 0),
            Vector3D(1, 1, 0)
        ]
        
        bezier = BezierCurve(control_points)
        
        # For easing, we need to solve for t given x
        # This is an approximation using binary search
        epsilon = 0.0001
        lower = 0.0
        upper = 1.0
        
        for _ in range(10):  # 10 iterations should be enough
            mid = (lower + upper) / 2
            point = bezier.evaluate(mid)
            x = point.x
            
            if abs(x - t) < epsilon:
                return point.y
            elif x < t:
                lower = mid
            else:
                upper = mid
        
        # Return the y value at the found t
        return bezier.evaluate((lower + upper) / 2).y
    
    @staticmethod
    def _spring_easing(t: float, stiffness: float = 100, 
                      damping: float = 10, mass: float = 1) -> float:
        """Spring physics-based easing."""
        if t == 0:
            return 0
        if t == 1:
            return 1
        
        omega = np.sqrt(stiffness / mass)
        zeta = damping / (2 * np.sqrt(stiffness * mass))
        
        if zeta < 1:  # Underdamped
            wd = omega * np.sqrt(1 - zeta**2)
            return 1 - np.exp(-zeta * omega * t) * (
                np.cos(wd * t) + (zeta * omega / wd) * np.sin(wd * t)
            )
        else:  # Critically damped or overdamped
            return 1 - np.exp(-omega * t) * (1 + omega * t)
    
    @staticmethod
    def _manim_smooth(t: float) -> float:
        """Manim's smooth function with zero first and second derivatives at boundaries."""
        # Manim uses this specific formula for smooth
        s = 1 - t
        return t * t * t * (10 * s * s + 5 * s * t + t * t)
    
    @staticmethod
    def _there_and_back(t: float) -> float:
        """Goes from 0 to 1 and back to 0, using smooth interpolation."""
        new_t = 2 * t if t < 0.5 else 2 * (1 - t)
        return EasingLibrary._manim_smooth(new_t)
    
    @staticmethod
    def _there_and_back_with_pause(t: float, pause_ratio: float = 1/3) -> float:
        """There and back with a pause in the middle."""
        pause_start = (1 - pause_ratio) / 2
        pause_end = (1 + pause_ratio) / 2
        
        if t < pause_start:
            # First half: go there
            return EasingLibrary._manim_smooth(t / pause_start)
        elif t < pause_end:
            # Pause at 1
            return 1
        else:
            # Second half: come back
            return EasingLibrary._manim_smooth((1 - t) / (1 - pause_end))
    
    @staticmethod
    def _wiggle(t: float, wiggles: int = 4) -> float:
        """Creates a wiggling motion."""
        return np.sin(wiggles * np.pi * t) * EasingLibrary._there_and_back(t)
    
    @staticmethod
    def _squish_rate_func(t: float, squish_start: float = 0.25, squish_end: float = 0.75) -> float:
        """Squishes the rate function to a specific interval."""
        if t < squish_start:
            return 0
        elif t > squish_end:
            return 1
        else:
            # Map t from [squish_start, squish_end] to [0, 1]
            normalized_t = (t - squish_start) / (squish_end - squish_start)
            return EasingLibrary._manim_smooth(normalized_t)
    
    @staticmethod
    def _lingering(t: float) -> float:
        """Lingers at the beginning and end."""
        if t < 0.2:
            return EasingLibrary._manim_smooth(t * 2.5) * 0.2
        elif t < 0.8:
            return 0.2 + 0.6 * ((t - 0.2) / 0.6)
        else:
            return 0.8 + 0.2 * EasingLibrary._manim_smooth((t - 0.8) * 5)


class EasingPresets:
    """Predefined easing configurations for common animation patterns."""
    
    # Material Design standard easings
    MATERIAL_STANDARD = {
        'type': EasingFunction.CUBIC_BEZIER,
        'params': {'control_points': (0.4, 0.0, 0.2, 1.0)}
    }
    
    MATERIAL_DECELERATED = {
        'type': EasingFunction.CUBIC_BEZIER,
        'params': {'control_points': (0.0, 0.0, 0.2, 1.0)}
    }
    
    MATERIAL_ACCELERATED = {
        'type': EasingFunction.CUBIC_BEZIER,
        'params': {'control_points': (0.4, 0.0, 1.0, 1.0)}
    }
    
    # iOS-style easings
    IOS_DEFAULT = {
        'type': EasingFunction.CUBIC_BEZIER,
        'params': {'control_points': (0.25, 0.1, 0.25, 1.0)}
    }
    
    IOS_EASE_IN = {
        'type': EasingFunction.CUBIC_BEZIER,
        'params': {'control_points': (0.42, 0.0, 1.0, 1.0)}
    }
    
    IOS_EASE_OUT = {
        'type': EasingFunction.CUBIC_BEZIER,
        'params': {'control_points': (0.0, 0.0, 0.58, 1.0)}
    }
    
    # Playful animations
    BOUNCE = {
        'type': EasingFunction.EASE_OUT_BOUNCE,
        'params': {}
    }
    
    ELASTIC = {
        'type': EasingFunction.EASE_OUT_ELASTIC,
        'params': {'amplitude': 1, 'period': 0.3}
    }
    
    SPRING = {
        'type': EasingFunction.SPRING,
        'params': {'stiffness': 100, 'damping': 10, 'mass': 1}
    }
    
    OVERSHOOT = {
        'type': EasingFunction.EASE_OUT_BACK,
        'params': {'overshoot': 1.70158}
    }
    
    # Smooth transitions
    SMOOTH = {
        'type': EasingFunction.SMOOTH_STEP,
        'params': {}
    }
    
    SMOOTHER = {
        'type': EasingFunction.SMOOTHER_STEP,
        'params': {}
    }
    
    SMOOTHEST = {
        'type': EasingFunction.SMOOTHEST_STEP,
        'params': {}
    }
    
    # Manim rate function presets
    THERE_AND_BACK = {
        'type': EasingFunction.THERE_AND_BACK,
        'params': {}
    }
    
    THERE_AND_BACK_PAUSE = {
        'type': EasingFunction.THERE_AND_BACK_WITH_PAUSE,
        'params': {'pause_ratio': 1/3}
    }
    
    RUSH_INTO = {
        'type': EasingFunction.RUSH_INTO,
        'params': {}
    }
    
    RUSH_FROM = {
        'type': EasingFunction.RUSH_FROM,
        'params': {}
    }
    
    WIGGLE = {
        'type': EasingFunction.WIGGLE,
        'params': {'wiggles': 4}
    }
    
    LINGERING = {
        'type': EasingFunction.LINGERING,
        'params': {}
    }
    
    MANIM_SMOOTH = {
        'type': EasingFunction.MANIM_SMOOTH,
        'params': {}
    }
    
    @classmethod
    def get_preset(cls, preset_name: str) -> Dict:
        """Get a preset configuration by name."""
        return getattr(cls, preset_name.upper(), cls.MATERIAL_STANDARD)
    
    @classmethod
    def create_easing_from_preset(cls, preset_name: str) -> Callable[[float], float]:
        """Create an easing function from a preset name."""
        preset = cls.get_preset(preset_name)
        return EasingLibrary.get_easing_function(preset['type'], preset.get('params'))


def interpolate_with_easing(start: float, end: float, t: float, 
                           easing: Union[EasingFunction, str, Callable[[float], float]]) -> float:
    """Interpolate between two values with easing.
    
    Args:
        start: Start value
        end: End value
        t: Progress (0-1)
        easing: EasingFunction enum, preset name string, or custom function
    
    Returns:
        Interpolated value
    """
    if isinstance(easing, str):
        # Try to get from presets
        easing_func = EasingPresets.create_easing_from_preset(easing)
    elif isinstance(easing, EasingFunction):
        easing_func = EasingLibrary.get_easing_function(easing)
    elif callable(easing):
        easing_func = easing
    else:
        easing_func = lambda x: x  # Linear fallback
    
    eased_t = easing_func(np.clip(t, 0, 1))
    return start + (end - start) * eased_t