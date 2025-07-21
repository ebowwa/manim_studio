"""
Curve Utilities

This module provides utilities for working with parametric curves including:
- Parametric curve representations
- Arc length parameterization
- Curve analysis (curvature, torsion)
- Path operations (trimming, joining, offsetting)
- Common curve types (circle, spiral, helix, etc.)
"""

import numpy as np
from typing import Callable, List, Tuple, Optional
from .vector3d import Vector3D
from .interpolation import BezierCurve, CatmullRomSpline


class ParametricCurve:
    """Base class for parametric curves."""
    
    def __init__(self, func: Callable[[float], Vector3D], 
                 t_min: float = 0, t_max: float = 1):
        """Initialize parametric curve with function and parameter range."""
        self.func = func
        self.t_min = t_min
        self.t_max = t_max
    
    def evaluate(self, t: float) -> Vector3D:
        """Evaluate curve at parameter t."""
        t = np.clip(t, self.t_min, self.t_max)
        return self.func(t)
    
    def derivative(self, t: float, h: float = 1e-6) -> Vector3D:
        """Calculate first derivative (velocity) using finite differences."""
        t = np.clip(t, self.t_min, self.t_max)
        
        # Use central difference when possible
        if t - h >= self.t_min and t + h <= self.t_max:
            return (self.evaluate(t + h) - self.evaluate(t - h)) / (2 * h)
        # Forward difference at start
        elif t - h < self.t_min:
            return (self.evaluate(t + h) - self.evaluate(t)) / h
        # Backward difference at end
        else:
            return (self.evaluate(t) - self.evaluate(t - h)) / h
    
    def second_derivative(self, t: float, h: float = 1e-6) -> Vector3D:
        """Calculate second derivative (acceleration)."""
        t = np.clip(t, self.t_min, self.t_max)
        
        if t - h >= self.t_min and t + h <= self.t_max:
            return (self.evaluate(t + h) - 2 * self.evaluate(t) + self.evaluate(t - h)) / (h * h)
        else:
            # Fallback to derivative of derivative
            return (self.derivative(t + h/2) - self.derivative(t - h/2)) / h
    
    def tangent(self, t: float) -> Vector3D:
        """Get unit tangent vector at parameter t."""
        velocity = self.derivative(t)
        return velocity.normalize()
    
    def normal(self, t: float) -> Vector3D:
        """Get principal normal vector at parameter t."""
        velocity = self.derivative(t)
        acceleration = self.second_derivative(t)
        
        # Project acceleration onto plane perpendicular to velocity
        tangent = velocity.normalize()
        normal_component = acceleration - tangent * acceleration.dot(tangent)
        
        if normal_component.magnitude() < 1e-10:
            # Find any perpendicular vector
            if abs(tangent.x) < 0.9:
                perp = Vector3D(1, 0, 0)
            else:
                perp = Vector3D(0, 1, 0)
            normal_component = perp - tangent * perp.dot(tangent)
        
        return normal_component.normalize()
    
    def binormal(self, t: float) -> Vector3D:
        """Get binormal vector at parameter t."""
        tangent = self.tangent(t)
        normal = self.normal(t)
        return tangent.cross(normal).normalize()
    
    def curvature(self, t: float) -> float:
        """Calculate curvature at parameter t."""
        velocity = self.derivative(t)
        acceleration = self.second_derivative(t)
        
        cross = velocity.cross(acceleration)
        speed = velocity.magnitude()
        
        if speed < 1e-10:
            return 0
        
        return cross.magnitude() / (speed ** 3)
    
    def torsion(self, t: float, h: float = 1e-6) -> float:
        """Calculate torsion at parameter t."""
        velocity = self.derivative(t)
        acceleration = self.second_derivative(t)
        
        # Third derivative approximation
        if t - h >= self.t_min and t + h <= self.t_max:
            jerk = (self.second_derivative(t + h) - self.second_derivative(t - h)) / (2 * h)
        else:
            jerk = (self.second_derivative(t + h/2) - self.second_derivative(t - h/2)) / h
        
        cross = velocity.cross(acceleration)
        cross_mag_sq = cross.magnitude_squared()
        
        if cross_mag_sq < 1e-20:
            return 0
        
        return cross.dot(jerk) / cross_mag_sq
    
    def arc_length(self, t0: float, t1: float, num_samples: int = 100) -> float:
        """Calculate arc length between t0 and t1 using numerical integration."""
        if t1 < t0:
            t0, t1 = t1, t0
        
        t_values = np.linspace(t0, t1, num_samples)
        length = 0
        
        for i in range(len(t_values) - 1):
            p1 = self.evaluate(t_values[i])
            p2 = self.evaluate(t_values[i + 1])
            length += p1.distance_to(p2)
        
        return length
    
    def arc_length_parameterization(self, num_samples: int = 100) -> 'ArcLengthParameterizedCurve':
        """Create arc-length parameterized version of curve."""
        return ArcLengthParameterizedCurve(self, num_samples)
    
    def sample_points(self, num_points: int) -> List[Vector3D]:
        """Sample evenly spaced points in parameter space."""
        t_values = np.linspace(self.t_min, self.t_max, num_points)
        return [self.evaluate(t) for t in t_values]
    
    def sample_points_uniform(self, spacing: float) -> List[Vector3D]:
        """Sample points with uniform spacing along curve."""
        arc_param = self.arc_length_parameterization()
        total_length = arc_param.total_length
        num_points = int(total_length / spacing) + 1
        
        points = []
        for i in range(num_points):
            s = i * spacing
            if s <= total_length:
                points.append(arc_param.evaluate_by_arc_length(s))
        
        return points


class ArcLengthParameterizedCurve:
    """Curve parameterized by arc length for uniform speed traversal."""
    
    def __init__(self, curve: ParametricCurve, num_samples: int = 100):
        """Create arc-length parameterization of curve."""
        self.curve = curve
        
        # Build lookup table
        t_values = np.linspace(curve.t_min, curve.t_max, num_samples)
        arc_lengths = [0]
        
        for i in range(1, len(t_values)):
            p1 = curve.evaluate(t_values[i-1])
            p2 = curve.evaluate(t_values[i])
            arc_lengths.append(arc_lengths[-1] + p1.distance_to(p2))
        
        self.t_values = t_values
        self.arc_lengths = np.array(arc_lengths)
        self.total_length = arc_lengths[-1]
    
    def evaluate_by_arc_length(self, s: float) -> Vector3D:
        """Evaluate curve at arc length s."""
        s = np.clip(s, 0, self.total_length)
        
        # Binary search for interval
        idx = np.searchsorted(self.arc_lengths, s)
        
        if idx == 0:
            return self.curve.evaluate(self.t_values[0])
        if idx >= len(self.arc_lengths):
            return self.curve.evaluate(self.t_values[-1])
        
        # Linear interpolation
        s0 = self.arc_lengths[idx - 1]
        s1 = self.arc_lengths[idx]
        t0 = self.t_values[idx - 1]
        t1 = self.t_values[idx]
        
        if s1 - s0 < 1e-10:
            t = t0
        else:
            t = t0 + (t1 - t0) * (s - s0) / (s1 - s0)
        
        return self.curve.evaluate(t)
    
    def t_from_arc_length(self, s: float) -> float:
        """Get parameter t corresponding to arc length s."""
        s = np.clip(s, 0, self.total_length)
        
        # Binary search for interval
        idx = np.searchsorted(self.arc_lengths, s)
        
        if idx == 0:
            return self.t_values[0]
        if idx >= len(self.arc_lengths):
            return self.t_values[-1]
        
        # Linear interpolation
        s0 = self.arc_lengths[idx - 1]
        s1 = self.arc_lengths[idx]
        t0 = self.t_values[idx - 1]
        t1 = self.t_values[idx]
        
        if s1 - s0 < 1e-10:
            return t0
        else:
            return t0 + (t1 - t0) * (s - s0) / (s1 - s0)


# Common curve types
class CircleCurve(ParametricCurve):
    """Circular curve in 3D space."""
    
    def __init__(self, center: Vector3D, radius: float, 
                 normal: Vector3D = None, start_angle: float = 0, end_angle: float = 2*np.pi):
        """Create circular curve."""
        self.center = center
        self.radius = radius
        self.normal = normal.normalize() if normal else Vector3D.up()
        
        # Create orthonormal basis
        if abs(self.normal.dot(Vector3D.up())) < 0.9:
            self.u = Vector3D.up().cross(self.normal).normalize()
        else:
            self.u = Vector3D.right().cross(self.normal).normalize()
        self.v = self.normal.cross(self.u)
        
        def circle_func(t):
            angle = start_angle + t * (end_angle - start_angle)
            local_x = self.radius * np.cos(angle)
            local_y = self.radius * np.sin(angle)
            return self.center + self.u * local_x + self.v * local_y
        
        super().__init__(circle_func, 0, 1)


class HelixCurve(ParametricCurve):
    """Helical curve."""
    
    def __init__(self, center: Vector3D, radius: float, pitch: float,
                 axis: Vector3D = None, turns: float = 1):
        """Create helix curve."""
        self.center = center
        self.radius = radius
        self.pitch = pitch
        self.axis = axis.normalize() if axis else Vector3D.up()
        
        # Create orthonormal basis
        if abs(self.axis.dot(Vector3D.up())) < 0.9:
            self.u = Vector3D.up().cross(self.axis).normalize()
        else:
            self.u = Vector3D.right().cross(self.axis).normalize()
        self.v = self.axis.cross(self.u)
        
        def helix_func(t):
            angle = t * 2 * np.pi * turns
            local_x = self.radius * np.cos(angle)
            local_y = self.radius * np.sin(angle)
            local_z = t * pitch * turns
            return self.center + self.u * local_x + self.v * local_y + self.axis * local_z
        
        super().__init__(helix_func, 0, 1)


class SpiralCurve(ParametricCurve):
    """Archimedean spiral curve."""
    
    def __init__(self, center: Vector3D, a: float, b: float,
                 normal: Vector3D = None, max_angle: float = 4*np.pi):
        """Create spiral curve with r = a + b*theta."""
        self.center = center
        self.a = a
        self.b = b
        self.normal = normal.normalize() if normal else Vector3D.up()
        
        # Create orthonormal basis
        if abs(self.normal.dot(Vector3D.up())) < 0.9:
            self.u = Vector3D.up().cross(self.normal).normalize()
        else:
            self.u = Vector3D.right().cross(self.normal).normalize()
        self.v = self.normal.cross(self.u)
        
        def spiral_func(t):
            angle = t * max_angle
            r = self.a + self.b * angle
            local_x = r * np.cos(angle)
            local_y = r * np.sin(angle)
            return self.center + self.u * local_x + self.v * local_y
        
        super().__init__(spiral_func, 0, 1)


class LissajousCurve(ParametricCurve):
    """Lissajous curve."""
    
    def __init__(self, center: Vector3D, a: float, b: float,
                 freq_x: float, freq_y: float, phase: float = 0):
        """Create Lissajous curve."""
        self.center = center
        self.a = a
        self.b = b
        self.freq_x = freq_x
        self.freq_y = freq_y
        self.phase = phase
        
        def lissajous_func(t):
            angle = t * 2 * np.pi
            x = self.a * np.sin(self.freq_x * angle + self.phase)
            y = self.b * np.sin(self.freq_y * angle)
            return self.center + Vector3D(x, y, 0)
        
        super().__init__(lissajous_func, 0, 1)


# Path operations
class PathOperations:
    """Utilities for path operations on curves."""
    
    @staticmethod
    def offset_curve(curve: ParametricCurve, distance: float, 
                    num_samples: int = 100) -> List[Vector3D]:
        """Create offset curve at fixed distance."""
        points = []
        t_values = np.linspace(curve.t_min, curve.t_max, num_samples)
        
        for t in t_values:
            point = curve.evaluate(t)
            normal = curve.normal(t)
            offset_point = point + normal * distance
            points.append(offset_point)
        
        return points
    
    @staticmethod
    def trim_curve(curve: ParametricCurve, t_start: float, t_end: float) -> ParametricCurve:
        """Trim curve to parameter range."""
        t_start = max(t_start, curve.t_min)
        t_end = min(t_end, curve.t_max)
        
        def trimmed_func(t):
            actual_t = t_start + t * (t_end - t_start)
            return curve.evaluate(actual_t)
        
        return ParametricCurve(trimmed_func, 0, 1)
    
    @staticmethod
    def join_curves(curves: List[ParametricCurve], 
                   continuity: str = 'C0') -> ParametricCurve:
        """Join multiple curves with specified continuity."""
        if not curves:
            raise ValueError("No curves to join")
        
        if continuity == 'C0':
            # Position continuity only
            def joined_func(t):
                n = len(curves)
                segment = int(t * n)
                if segment >= n:
                    segment = n - 1
                local_t = t * n - segment
                return curves[segment].evaluate(local_t)
            
            return ParametricCurve(joined_func, 0, 1)
        
        elif continuity == 'C1':
            # Tangent continuity - use Hermite interpolation
            points = []
            tangents = []
            
            for curve in curves:
                points.append(curve.evaluate(curve.t_min))
                tangents.append(curve.derivative(curve.t_min))
            points.append(curves[-1].evaluate(curves[-1].t_max))
            tangents.append(curves[-1].derivative(curves[-1].t_max))
            
            # Create smooth interpolation
            spline = CatmullRomSpline(points)
            
            def smooth_func(t):
                return spline.evaluate(t * (len(points) - 1))
            
            return ParametricCurve(smooth_func, 0, 1)
    
    @staticmethod
    def reverse_curve(curve: ParametricCurve) -> ParametricCurve:
        """Reverse the direction of a curve."""
        def reversed_func(t):
            return curve.evaluate(curve.t_max - t + curve.t_min)
        
        return ParametricCurve(reversed_func, curve.t_min, curve.t_max)
    
    @staticmethod
    def reparameterize_by_speed(curve: ParametricCurve, 
                               speed_func: Callable[[float], float]) -> ParametricCurve:
        """Reparameterize curve with custom speed function."""
        # Integrate speed function
        num_samples = 100
        t_old = np.linspace(0, 1, num_samples)
        speeds = [speed_func(t) for t in t_old]
        
        # Cumulative integral
        dt = 1.0 / (num_samples - 1)
        s_values = [0]
        for i in range(1, num_samples):
            s_values.append(s_values[-1] + speeds[i] * dt)
        
        # Normalize
        s_values = np.array(s_values)
        s_values /= s_values[-1]
        
        def reparam_func(t):
            # Inverse lookup
            idx = np.searchsorted(s_values, t)
            if idx == 0:
                old_t = 0
            elif idx >= len(s_values):
                old_t = 1
            else:
                # Linear interpolation
                s0 = s_values[idx - 1]
                s1 = s_values[idx]
                t0 = t_old[idx - 1]
                t1 = t_old[idx]
                
                if s1 - s0 < 1e-10:
                    old_t = t0
                else:
                    old_t = t0 + (t1 - t0) * (t - s0) / (s1 - s0)
            
            return curve.evaluate(curve.t_min + old_t * (curve.t_max - curve.t_min))
        
        return ParametricCurve(reparam_func, 0, 1)


# Convenience functions
def create_circle(center: Vector3D, radius: float, normal: Vector3D = None) -> CircleCurve:
    """Create a circle curve."""
    return CircleCurve(center, radius, normal)


def create_helix(center: Vector3D, radius: float, pitch: float, 
                 turns: float = 1, axis: Vector3D = None) -> HelixCurve:
    """Create a helix curve."""
    return HelixCurve(center, radius, pitch, axis, turns)


def create_spiral(center: Vector3D, inner_radius: float, 
                 growth_rate: float, turns: float = 2) -> SpiralCurve:
    """Create an Archimedean spiral."""
    return SpiralCurve(center, inner_radius, growth_rate / (2 * np.pi), 
                      max_angle=2 * np.pi * turns)


def create_lissajous(center: Vector3D, width: float, height: float,
                    freq_x: float, freq_y: float, phase: float = 0) -> LissajousCurve:
    """Create a Lissajous curve."""
    return LissajousCurve(center, width/2, height/2, freq_x, freq_y, phase)


def evaluate_curve_frenet_frame(curve: ParametricCurve, t: float) -> Tuple[Vector3D, Vector3D, Vector3D]:
    """Get Frenet frame (tangent, normal, binormal) at parameter t."""
    tangent = curve.tangent(t)
    normal = curve.normal(t)
    binormal = curve.binormal(t)
    return tangent, normal, binormal