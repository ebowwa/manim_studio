"""
Vector Space Extensions for Advanced Coordinate Operations

This module provides additional coordinate system abstractions and
specialized transformations for Manim Studio.
"""

from typing import List, Optional, Callable, Tuple, Union
import numpy as np
from manim import *
from .vector_space import VectorSpace, CoordinateSystem, Vector3D
from ..utils.math3d import Matrix4x4


class CoordinateFrame:
    """
    Represents a local coordinate frame within the vector space.
    Useful for hierarchical transformations and local object spaces.
    """
    
    def __init__(self, origin: Vector3D = None, 
                 x_axis: Vector3D = None,
                 y_axis: Vector3D = None,
                 z_axis: Vector3D = None,
                 parent: Optional['CoordinateFrame'] = None):
        self.origin = origin or Vector3D(0, 0, 0)
        self.x_axis = x_axis or Vector3D(1, 0, 0)
        self.y_axis = y_axis or Vector3D(0, 1, 0)
        self.z_axis = z_axis or Vector3D(0, 0, 1)
        self.parent = parent
        
        # Ensure orthonormal basis
        self._orthonormalize()
    
    def _orthonormalize(self):
        """Ensure axes form an orthonormal basis."""
        # Gram-Schmidt orthogonalization
        self.x_axis = self.x_axis.normalize()
        self.y_axis = (self.y_axis - self.y_axis.project_onto(self.x_axis)).normalize()
        self.z_axis = self.x_axis.cross(self.y_axis)
    
    def to_matrix(self) -> Matrix4x4:
        """Convert frame to transformation matrix."""
        matrix = np.eye(4)
        matrix[:3, 0] = self.x_axis.array
        matrix[:3, 1] = self.y_axis.array
        matrix[:3, 2] = self.z_axis.array
        matrix[:3, 3] = self.origin.array
        return Matrix4x4(matrix)
    
    def from_matrix(self, matrix: Matrix4x4):
        """Set frame from transformation matrix."""
        self.x_axis = Vector3D(matrix.matrix[0, 0], matrix.matrix[1, 0], matrix.matrix[2, 0])
        self.y_axis = Vector3D(matrix.matrix[0, 1], matrix.matrix[1, 1], matrix.matrix[2, 1])
        self.z_axis = Vector3D(matrix.matrix[0, 2], matrix.matrix[1, 2], matrix.matrix[2, 2])
        self.origin = Vector3D(matrix.matrix[0, 3], matrix.matrix[1, 3], matrix.matrix[2, 3])
    
    def transform_to_world(self, point: Vector3D) -> Vector3D:
        """Transform point from local frame to world coordinates."""
        world_point = self.origin + (self.x_axis * point.x + 
                                    self.y_axis * point.y + 
                                    self.z_axis * point.z)
        
        if self.parent:
            return self.parent.transform_to_world(world_point)
        return world_point
    
    def transform_from_world(self, world_point: Vector3D) -> Vector3D:
        """Transform point from world coordinates to local frame."""
        if self.parent:
            world_point = self.parent.transform_from_world(world_point)
        
        relative = world_point - self.origin
        return Vector3D(
            relative.dot(self.x_axis),
            relative.dot(self.y_axis),
            relative.dot(self.z_axis)
        )


class SphericalCoordinates:
    """Handler for spherical coordinate system conversions."""
    
    @staticmethod
    def from_cartesian(point: Vector3D) -> Tuple[float, float, float]:
        """Convert Cartesian to spherical (r, theta, phi)."""
        r = point.magnitude()
        if r == 0:
            return (0, 0, 0)
        
        theta = np.arctan2(point.y, point.x)  # Azimuth
        phi = np.arccos(point.z / r)          # Inclination from z-axis
        return (r, theta, phi)
    
    @staticmethod
    def to_cartesian(r: float, theta: float, phi: float) -> Vector3D:
        """Convert spherical (r, theta, phi) to Cartesian."""
        x = r * np.sin(phi) * np.cos(theta)
        y = r * np.sin(phi) * np.sin(theta)
        z = r * np.cos(phi)
        return Vector3D(x, y, z)


class CylindricalCoordinates:
    """Handler for cylindrical coordinate system conversions."""
    
    @staticmethod
    def from_cartesian(point: Vector3D) -> Tuple[float, float, float]:
        """Convert Cartesian to cylindrical (r, theta, z)."""
        r = np.sqrt(point.x**2 + point.y**2)
        theta = np.arctan2(point.y, point.x)
        return (r, theta, point.z)
    
    @staticmethod
    def to_cartesian(r: float, theta: float, z: float) -> Vector3D:
        """Convert cylindrical (r, theta, z) to Cartesian."""
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        return Vector3D(x, y, z)


class BarycentricCoordinates:
    """Handler for barycentric coordinate operations."""
    
    @staticmethod
    def from_cartesian(point: Vector3D, v0: Vector3D, v1: Vector3D, v2: Vector3D) -> Tuple[float, float, float]:
        """
        Convert Cartesian point to barycentric coordinates relative to triangle.
        
        Returns (u, v, w) where point = u*v0 + v*v1 + w*v2 and u + v + w = 1
        """
        # Compute vectors
        v0v1 = v1 - v0
        v0v2 = v2 - v0
        v0p = point - v0
        
        # Compute dot products
        dot00 = v0v2.dot(v0v2)
        dot01 = v0v2.dot(v0v1)
        dot02 = v0v2.dot(v0p)
        dot11 = v0v1.dot(v0v1)
        dot12 = v0v1.dot(v0p)
        
        # Compute barycentric coordinates
        inv_denom = 1 / (dot00 * dot11 - dot01 * dot01)
        v = (dot11 * dot02 - dot01 * dot12) * inv_denom
        w = (dot00 * dot12 - dot01 * dot02) * inv_denom
        u = 1 - v - w
        
        return (u, v, w)
    
    @staticmethod
    def to_cartesian(u: float, v: float, w: float, v0: Vector3D, v1: Vector3D, v2: Vector3D) -> Vector3D:
        """Convert barycentric coordinates to Cartesian point."""
        return v0 * u + v1 * v + v2 * w


class PolarCoordinates:
    """Handler for 2D polar coordinate conversions."""
    
    @staticmethod
    def from_cartesian(x: float, y: float) -> Tuple[float, float]:
        """Convert 2D Cartesian to polar (r, theta)."""
        r = np.sqrt(x**2 + y**2)
        theta = np.arctan2(y, x)
        return (r, theta)
    
    @staticmethod
    def to_cartesian(r: float, theta: float) -> Tuple[float, float]:
        """Convert polar (r, theta) to 2D Cartesian."""
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        return (x, y)


class VectorFieldSpace:
    """
    Manages vector fields in the coordinate space.
    Useful for visualizing gradients, flows, and forces.
    """
    
    def __init__(self, vector_space: VectorSpace):
        self.vector_space = vector_space
        self.fields = {}
    
    def add_field(self, name: str, field_func: Callable[[Vector3D], Vector3D]):
        """Add a vector field defined by a function."""
        self.fields[name] = field_func
    
    def evaluate_field(self, name: str, point: Vector3D) -> Vector3D:
        """Evaluate vector field at a point."""
        if name not in self.fields:
            raise ValueError(f"Field '{name}' not found")
        return self.fields[name](point)
    
    def create_field_visualization(self, name: str, 
                                 bounds: Optional[Tuple[float, float, float, float]] = None,
                                 density: int = 10,
                                 scale: float = 0.5) -> VGroup:
        """Create visual representation of vector field."""
        if bounds is None:
            bounds = self.vector_space.get_scene_bounds()
        
        left, right, bottom, top = bounds
        vectors = VGroup()
        
        x_points = np.linspace(left, right, density)
        y_points = np.linspace(bottom, top, density)
        
        for x in x_points:
            for y in y_points:
                point = Vector3D(x, y, 0)
                field_vector = self.evaluate_field(name, point)
                
                if field_vector.magnitude() > 0:
                    arrow = Arrow(
                        start=point.array,
                        end=(point + field_vector * scale).array,
                        buff=0,
                        stroke_width=2,
                        tip_length=0.1
                    )
                    # Color by magnitude
                    magnitude = field_vector.magnitude()
                    arrow.set_color(interpolate_color(BLUE, RED, min(magnitude / 5, 1)))
                    vectors.add(arrow)
        
        return vectors


class CoordinateSystemVisualizer:
    """Creates visual representations of different coordinate systems."""
    
    @staticmethod
    def create_cartesian_grid(extent: float = 5, spacing: float = 1) -> VGroup:
        """Create a Cartesian coordinate grid."""
        grid = VGroup()
        
        # Grid lines
        for i in np.arange(-extent, extent + spacing, spacing):
            grid.add(Line([i, -extent, 0], [i, extent, 0], stroke_width=0.5, stroke_color=GREY))
            grid.add(Line([-extent, i, 0], [extent, i, 0], stroke_width=0.5, stroke_color=GREY))
        
        # Axes
        x_axis = Arrow([-extent, 0, 0], [extent, 0, 0], color=RED, stroke_width=2)
        y_axis = Arrow([0, -extent, 0], [0, extent, 0], color=GREEN, stroke_width=2)
        
        # Labels
        x_label = MathTex("x").next_to(x_axis, RIGHT)
        y_label = MathTex("y").next_to(y_axis, UP)
        
        grid.add(x_axis, y_axis, x_label, y_label)
        return grid
    
    @staticmethod
    def create_polar_grid(max_radius: float = 5, num_circles: int = 5, num_rays: int = 12) -> VGroup:
        """Create a polar coordinate grid."""
        grid = VGroup()
        
        # Concentric circles
        for i in range(1, num_circles + 1):
            radius = i * max_radius / num_circles
            circle = Circle(radius=radius, stroke_width=0.5, stroke_color=GREY)
            grid.add(circle)
        
        # Radial lines
        for i in range(num_rays):
            angle = i * TAU / num_rays
            end_point = [max_radius * np.cos(angle), max_radius * np.sin(angle), 0]
            line = Line(ORIGIN, end_point, stroke_width=0.5, stroke_color=GREY)
            grid.add(line)
        
        # Origin
        origin = Dot(ORIGIN, color=WHITE, radius=0.05)
        grid.add(origin)
        
        return grid
    
    @staticmethod
    def create_spherical_grid(radius: float = 3, num_parallels: int = 6, num_meridians: int = 8) -> VGroup:
        """Create a spherical coordinate grid visualization."""
        grid = VGroup()
        
        # Parallels (latitude lines)
        for i in range(1, num_parallels):
            phi = i * PI / num_parallels
            circle_radius = radius * np.sin(phi)
            z_height = radius * np.cos(phi)
            circle = Circle(radius=circle_radius, stroke_width=0.5, stroke_color=GREY)
            circle.shift(z_height * OUT)
            grid.add(circle)
        
        # Meridians (longitude lines)
        for i in range(num_meridians):
            theta = i * TAU / num_meridians
            arc = ParametricFunction(
                lambda t: np.array([
                    radius * np.sin(t) * np.cos(theta),
                    radius * np.sin(t) * np.sin(theta),
                    radius * np.cos(t)
                ]),
                t_range=[0, PI],
                stroke_width=0.5,
                stroke_color=GREY
            )
            grid.add(arc)
        
        # Equator
        equator = Circle(radius=radius, stroke_width=1, stroke_color=BLUE)
        grid.add(equator)
        
        # Axes
        x_axis = Arrow(ORIGIN, radius * RIGHT, color=RED, stroke_width=1)
        y_axis = Arrow(ORIGIN, radius * UP, color=GREEN, stroke_width=1)
        z_axis = Arrow(ORIGIN, radius * OUT, color=BLUE, stroke_width=1)
        
        grid.add(x_axis, y_axis, z_axis)
        return grid