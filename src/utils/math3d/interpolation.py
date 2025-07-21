"""
Interpolation Utilities

This module provides advanced interpolation methods including:
- Bezier curves (quadratic, cubic, and n-degree)
- Catmull-Rom splines
- Hermite curves
- B-splines
- Smooth step and smoother step functions
"""

import numpy as np
from typing import List, Union, Callable
from .vector3d import Vector3D


class BezierCurve:
    """Bezier curve implementation for smooth interpolation."""
    
    def __init__(self, control_points: List[Vector3D]):
        """Initialize Bezier curve with control points."""
        if len(control_points) < 2:
            raise ValueError("Bezier curve requires at least 2 control points")
        self.control_points = control_points
        self.degree = len(control_points) - 1
    
    def evaluate(self, t: float) -> Vector3D:
        """Evaluate curve at parameter t (0 to 1)."""
        t = np.clip(t, 0, 1)
        return self._de_casteljau(self.control_points, t)
    
    def _de_casteljau(self, points: List[Vector3D], t: float) -> Vector3D:
        """De Casteljau's algorithm for Bezier curve evaluation."""
        if len(points) == 1:
            return points[0]
        
        new_points = []
        for i in range(len(points) - 1):
            interpolated = points[i].lerp(points[i + 1], t)
            new_points.append(interpolated)
        
        return self._de_casteljau(new_points, t)
    
    def derivative(self, t: float) -> Vector3D:
        """Calculate first derivative (tangent) at parameter t."""
        if self.degree == 0:
            return Vector3D.zero()
        
        # Derivative of Bezier curve is another Bezier curve of degree n-1
        derivative_points = []
        for i in range(self.degree):
            diff = (self.control_points[i + 1] - self.control_points[i]) * self.degree
            derivative_points.append(diff)
        
        if len(derivative_points) == 1:
            return derivative_points[0]
        
        derivative_curve = BezierCurve(derivative_points)
        return derivative_curve.evaluate(t)
    
    def split(self, t: float) -> tuple:
        """Split curve at parameter t into two Bezier curves."""
        left_points = []
        right_points = []
        
        # Build subdivision tree
        levels = [self.control_points]
        for level in range(self.degree):
            new_level = []
            for i in range(len(levels[-1]) - 1):
                interpolated = levels[-1][i].lerp(levels[-1][i + 1], t)
                new_level.append(interpolated)
            levels.append(new_level)
        
        # Extract left and right control points
        for level in levels:
            left_points.append(level[0])
            right_points.append(level[-1])
        
        right_points.reverse()
        
        return BezierCurve(left_points), BezierCurve(right_points)
    
    def get_points(self, num_points: int) -> List[Vector3D]:
        """Get evenly spaced points along the curve."""
        points = []
        for i in range(num_points):
            t = i / (num_points - 1) if num_points > 1 else 0
            points.append(self.evaluate(t))
        return points


class CatmullRomSpline:
    """Catmull-Rom spline for smooth interpolation through points."""
    
    def __init__(self, points: List[Vector3D], tension: float = 0.5):
        """Initialize spline with control points and tension."""
        if len(points) < 2:
            raise ValueError("Catmull-Rom spline requires at least 2 points")
        self.points = points
        self.tension = tension
    
    def evaluate(self, t: float) -> Vector3D:
        """Evaluate spline at parameter t (0 to num_segments)."""
        n = len(self.points) - 1
        segment = int(t)
        local_t = t - segment
        
        if segment >= n:
            return self.points[-1]
        if segment < 0:
            return self.points[0]
        
        # Get the four points for this segment
        p0 = self.points[max(0, segment - 1)]
        p1 = self.points[segment]
        p2 = self.points[min(n, segment + 1)]
        p3 = self.points[min(n, segment + 2)]
        
        return self._catmull_rom_segment(p0, p1, p2, p3, local_t)
    
    def _catmull_rom_segment(self, p0: Vector3D, p1: Vector3D, p2: Vector3D, 
                            p3: Vector3D, t: float) -> Vector3D:
        """Evaluate single segment of Catmull-Rom spline."""
        t2 = t * t
        t3 = t2 * t
        
        # Catmull-Rom basis functions
        h1 = 2*t3 - 3*t2 + 1
        h2 = -2*t3 + 3*t2
        h3 = t3 - 2*t2 + t
        h4 = t3 - t2
        
        # Tangents
        tangent1 = (p2 - p0) * self.tension
        tangent2 = (p3 - p1) * self.tension
        
        return p1 * h1 + p2 * h2 + tangent1 * h3 + tangent2 * h4
    
    def get_points(self, points_per_segment: int = 10) -> List[Vector3D]:
        """Get evenly spaced points along the spline."""
        points = []
        n = len(self.points) - 1
        
        for i in range(n):
            for j in range(points_per_segment):
                t = i + j / points_per_segment
                points.append(self.evaluate(t))
        
        points.append(self.points[-1])
        return points


class HermiteCurve:
    """Hermite curve with position and tangent control."""
    
    def __init__(self, p0: Vector3D, p1: Vector3D, m0: Vector3D, m1: Vector3D):
        """Initialize with start/end positions and tangents."""
        self.p0 = p0  # Start position
        self.p1 = p1  # End position
        self.m0 = m0  # Start tangent
        self.m1 = m1  # End tangent
    
    def evaluate(self, t: float) -> Vector3D:
        """Evaluate curve at parameter t (0 to 1)."""
        t = np.clip(t, 0, 1)
        t2 = t * t
        t3 = t2 * t
        
        # Hermite basis functions
        h00 = 2*t3 - 3*t2 + 1
        h10 = t3 - 2*t2 + t
        h01 = -2*t3 + 3*t2
        h11 = t3 - t2
        
        return self.p0 * h00 + self.m0 * h10 + self.p1 * h01 + self.m1 * h11
    
    def derivative(self, t: float) -> Vector3D:
        """Calculate first derivative at parameter t."""
        t = np.clip(t, 0, 1)
        t2 = t * t
        
        # Derivatives of Hermite basis functions
        dh00 = 6*t2 - 6*t
        dh10 = 3*t2 - 4*t + 1
        dh01 = -6*t2 + 6*t
        dh11 = 3*t2 - 2*t
        
        return self.p0 * dh00 + self.m0 * dh10 + self.p1 * dh01 + self.m1 * dh11


class BSpline:
    """B-spline curve implementation."""
    
    def __init__(self, control_points: List[Vector3D], degree: int = 3):
        """Initialize B-spline with control points and degree."""
        if len(control_points) < degree + 1:
            raise ValueError(f"B-spline of degree {degree} requires at least {degree + 1} control points")
        
        self.control_points = control_points
        self.degree = degree
        self.n = len(control_points) - 1
        
        # Generate uniform knot vector
        self.knots = self._generate_uniform_knots()
    
    def _generate_uniform_knots(self) -> np.ndarray:
        """Generate uniform knot vector."""
        num_knots = self.n + self.degree + 2
        return np.linspace(0, 1, num_knots)
    
    def _basis_function(self, i: int, k: int, t: float) -> float:
        """Cox-de Boor recursion formula for B-spline basis functions."""
        if k == 0:
            return 1.0 if self.knots[i] <= t < self.knots[i + 1] else 0.0
        
        # Handle edge case for last point
        if i + k >= len(self.knots) - 1:
            if t == self.knots[-1] and i + k == len(self.knots) - 1:
                return 1.0
        
        # Recursive calculation
        left = 0.0
        right = 0.0
        
        if self.knots[i + k] - self.knots[i] > 0:
            left = ((t - self.knots[i]) / (self.knots[i + k] - self.knots[i]) * 
                    self._basis_function(i, k - 1, t))
        
        if i + k + 1 < len(self.knots) and self.knots[i + k + 1] - self.knots[i + 1] > 0:
            right = ((self.knots[i + k + 1] - t) / (self.knots[i + k + 1] - self.knots[i + 1]) * 
                     self._basis_function(i + 1, k - 1, t))
        
        return left + right
    
    def evaluate(self, t: float) -> Vector3D:
        """Evaluate B-spline at parameter t (0 to 1)."""
        t = np.clip(t, 0, 1)
        
        # Find the knot span
        if t == 1.0:
            t = 1.0 - 1e-10
        
        result = Vector3D.zero()
        for i in range(len(self.control_points)):
            basis = self._basis_function(i, self.degree, t)
            if basis > 0:
                result = result + self.control_points[i] * basis
        
        return result
    
    def get_points(self, num_points: int) -> List[Vector3D]:
        """Get evenly spaced points along the curve."""
        points = []
        for i in range(num_points):
            t = i / (num_points - 1) if num_points > 1 else 0
            points.append(self.evaluate(t))
        return points


# Smooth interpolation functions
def smooth_step(t: float) -> float:
    """Smooth step function (cubic)."""
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def smoother_step(t: float) -> float:
    """Smoother step function (quintic)."""
    t = np.clip(t, 0, 1)
    return t * t * t * (t * (t * 6 - 15) + 10)


def smoothest_step(t: float) -> float:
    """Smoothest step function (septic)."""
    t = np.clip(t, 0, 1)
    return t * t * t * t * (t * (t * (t * -20 + 70) - 84) + 35)


def ease_in_out(t: float, power: float = 2) -> float:
    """Ease in-out function with configurable power."""
    t = np.clip(t, 0, 1)
    if t < 0.5:
        return 0.5 * (2 * t) ** power
    else:
        return 1 - 0.5 * (2 * (1 - t)) ** power


def bounce_ease_out(t: float) -> float:
    """Bounce easing out function."""
    t = np.clip(t, 0, 1)
    if t < 1 / 2.75:
        return 7.5625 * t * t
    elif t < 2 / 2.75:
        t -= 1.5 / 2.75
        return 7.5625 * t * t + 0.75
    elif t < 2.5 / 2.75:
        t -= 2.25 / 2.75
        return 7.5625 * t * t + 0.9375
    else:
        t -= 2.625 / 2.75
        return 7.5625 * t * t + 0.984375


def elastic_ease_out(t: float, amplitude: float = 1, period: float = 0.3) -> float:
    """Elastic easing out function."""
    t = np.clip(t, 0, 1)
    if t == 0 or t == 1:
        return t
    
    s = period / (2 * np.pi) * np.arcsin(1 / amplitude) if amplitude >= 1 else period / 4
    return amplitude * np.power(2, -10 * t) * np.sin((t - s) * 2 * np.pi / period) + 1


def circular_ease_in_out(t: float) -> float:
    """Circular easing in-out function."""
    t = np.clip(t, 0, 1)
    if t < 0.5:
        return 0.5 * (1 - np.sqrt(1 - 4 * t * t))
    else:
        return 0.5 * (np.sqrt(1 - (2 * t - 2) ** 2) + 1)


# Multi-point interpolation
def multi_lerp(points: List[Vector3D], t: float) -> Vector3D:
    """Linear interpolation through multiple points."""
    if not points:
        return Vector3D.zero()
    if len(points) == 1:
        return points[0]
    
    t = np.clip(t, 0, 1)
    scaled_t = t * (len(points) - 1)
    index = int(scaled_t)
    local_t = scaled_t - index
    
    if index >= len(points) - 1:
        return points[-1]
    
    return points[index].lerp(points[index + 1], local_t)


def cosine_interpolation(a: Vector3D, b: Vector3D, t: float) -> Vector3D:
    """Cosine interpolation between two vectors."""
    t = np.clip(t, 0, 1)
    t2 = (1 - np.cos(t * np.pi)) / 2
    return a.lerp(b, t2)


def cubic_interpolation(p0: Vector3D, p1: Vector3D, p2: Vector3D, p3: Vector3D, t: float) -> Vector3D:
    """Cubic interpolation between p1 and p2, using p0 and p3 for curve shape."""
    t = np.clip(t, 0, 1)
    t2 = t * t
    
    a0 = p3 - p2 - p0 + p1
    a1 = p0 - p1 - a0
    a2 = p2 - p0
    a3 = p1
    
    return a0 * (t * t2) + a1 * t2 + a2 * t + a3


# Convenience functions
def create_bezier_curve(points: List[Vector3D]) -> BezierCurve:
    """Create a Bezier curve from control points."""
    return BezierCurve(points)


def create_quadratic_bezier(start: Vector3D, control: Vector3D, end: Vector3D) -> BezierCurve:
    """Create a quadratic Bezier curve."""
    return BezierCurve([start, control, end])


def create_cubic_bezier(start: Vector3D, control1: Vector3D, 
                       control2: Vector3D, end: Vector3D) -> BezierCurve:
    """Create a cubic Bezier curve."""
    return BezierCurve([start, control1, control2, end])


def create_catmull_rom_spline(points: List[Vector3D], tension: float = 0.5) -> CatmullRomSpline:
    """Create a Catmull-Rom spline."""
    return CatmullRomSpline(points, tension)


def create_hermite_curve(start: Vector3D, end: Vector3D, 
                        start_tangent: Vector3D, end_tangent: Vector3D) -> HermiteCurve:
    """Create a Hermite curve."""
    return HermiteCurve(start, end, start_tangent, end_tangent)


def create_b_spline(points: List[Vector3D], degree: int = 3) -> BSpline:
    """Create a B-spline curve."""
    return BSpline(points, degree)