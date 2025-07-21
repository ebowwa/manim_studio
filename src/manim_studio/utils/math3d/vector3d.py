"""
3D Vector Operations

This module provides comprehensive 3D vector operations including:
- Basic vector arithmetic
- Magnitude and normalization
- Dot and cross products
- Linear and spherical interpolation
- Reflection and projection
- Angle calculations
"""

import numpy as np
from typing import Union
from dataclasses import dataclass


@dataclass
class Vector3D:
    """3D Vector with comprehensive operations."""
    x: float
    y: float
    z: float

    def __post_init__(self):
        self._array = np.array([self.x, self.y, self.z], dtype=np.float64)

    @property
    def array(self) -> np.ndarray:
        """Get numpy array representation."""
        return self._array

    @classmethod
    def from_array(cls, arr: np.ndarray) -> 'Vector3D':
        """Create Vector3D from numpy array."""
        return cls(float(arr[0]), float(arr[1]), float(arr[2]))

    @classmethod
    def zero(cls) -> 'Vector3D':
        """Create zero vector."""
        return cls(0, 0, 0)

    @classmethod
    def up(cls) -> 'Vector3D':
        """Create unit vector pointing up (Y-axis)."""
        return cls(0, 1, 0)

    @classmethod
    def right(cls) -> 'Vector3D':
        """Create unit vector pointing right (X-axis)."""
        return cls(1, 0, 0)

    @classmethod
    def forward(cls) -> 'Vector3D':
        """Create unit vector pointing forward (Z-axis)."""
        return cls(0, 0, 1)

    def magnitude(self) -> float:
        """Calculate vector magnitude."""
        return np.linalg.norm(self._array)

    def magnitude_squared(self) -> float:
        """Calculate squared magnitude (faster than magnitude)."""
        return np.dot(self._array, self._array)

    def normalize(self) -> 'Vector3D':
        """Return normalized vector."""
        mag = self.magnitude()
        if mag == 0:
            return Vector3D.zero()
        return Vector3D.from_array(self._array / mag)

    def dot(self, other: 'Vector3D') -> float:
        """Calculate dot product."""
        return np.dot(self._array, other._array)

    def cross(self, other: 'Vector3D') -> 'Vector3D':
        """Calculate cross product."""
        return Vector3D.from_array(np.cross(self._array, other._array))

    def distance_to(self, other: 'Vector3D') -> float:
        """Calculate distance to another vector."""
        return (self - other).magnitude()

    def lerp(self, other: 'Vector3D', t: float) -> 'Vector3D':
        """Linear interpolation between vectors."""
        return self + (other - self) * t

    def slerp(self, other: 'Vector3D', t: float) -> 'Vector3D':
        """Spherical linear interpolation between normalized vectors."""
        dot_product = self.dot(other)
        dot_product = np.clip(dot_product, -1.0, 1.0)
        
        if abs(dot_product) > 0.9995:
            return self.lerp(other, t).normalize()
        
        theta = np.arccos(abs(dot_product))
        sin_theta = np.sin(theta)
        
        a = np.sin((1 - t) * theta) / sin_theta
        b = np.sin(t * theta) / sin_theta
        
        return Vector3D.from_array(a * self._array + b * other._array)

    def reflect(self, normal: 'Vector3D') -> 'Vector3D':
        """Reflect vector across surface normal."""
        return self - normal * (2 * self.dot(normal))

    def project_onto(self, other: 'Vector3D') -> 'Vector3D':
        """Project this vector onto another vector."""
        return other * (self.dot(other) / other.magnitude_squared())

    def angle_between(self, other: 'Vector3D') -> float:
        """Calculate angle between vectors in radians."""
        dot_product = self.dot(other)
        mags = self.magnitude() * other.magnitude()
        if mags == 0:
            return 0
        cos_angle = np.clip(dot_product / mags, -1.0, 1.0)
        return np.arccos(cos_angle)

    def __add__(self, other: 'Vector3D') -> 'Vector3D':
        return Vector3D.from_array(self._array + other._array)

    def __sub__(self, other: 'Vector3D') -> 'Vector3D':
        return Vector3D.from_array(self._array - other._array)

    def __mul__(self, scalar: float) -> 'Vector3D':
        return Vector3D.from_array(self._array * scalar)

    def __rmul__(self, scalar: float) -> 'Vector3D':
        return self.__mul__(scalar)

    def __truediv__(self, scalar: float) -> 'Vector3D':
        return Vector3D.from_array(self._array / scalar)

    def __neg__(self) -> 'Vector3D':
        return Vector3D.from_array(-self._array)

    def __eq__(self, other: 'Vector3D') -> bool:
        if not isinstance(other, Vector3D):
            return False
        return np.allclose(self._array, other._array)

    def __str__(self) -> str:
        return f"Vector3D({self.x:.3f}, {self.y:.3f}, {self.z:.3f})"

    def __repr__(self) -> str:
        return self.__str__()


# Convenience functions for vector operations
def lerp_3d(a: Vector3D, b: Vector3D, t: float) -> Vector3D:
    """Linear interpolation between two 3D vectors."""
    return a.lerp(b, t)


def slerp_3d(a: Vector3D, b: Vector3D, t: float) -> Vector3D:
    """Spherical linear interpolation between two 3D vectors."""
    return a.slerp(b, t)


def dot_product(a: Vector3D, b: Vector3D) -> float:
    """Calculate dot product of two vectors."""
    return a.dot(b)


def cross_product(a: Vector3D, b: Vector3D) -> Vector3D:
    """Calculate cross product of two vectors."""
    return a.cross(b)


def distance_between(a: Vector3D, b: Vector3D) -> float:
    """Calculate distance between two points."""
    return a.distance_to(b)


def angle_between_vectors(a: Vector3D, b: Vector3D) -> float:
    """Calculate angle between two vectors in radians."""
    return a.angle_between(b)


def reflect_vector(vector: Vector3D, normal: Vector3D) -> Vector3D:
    """Reflect vector across surface normal."""
    return vector.reflect(normal)


def project_vector(vector: Vector3D, onto: Vector3D) -> Vector3D:
    """Project vector onto another vector."""
    return vector.project_onto(onto)