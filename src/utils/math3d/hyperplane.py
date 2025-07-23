"""
N-Dimensional Hyperplane Utilities

This module provides comprehensive hyperplane functionality for:
- N-dimensional hyperplane representation and operations
- Distance calculations and projections
- Hyperplane intersections and classification
- Support for machine learning applications (SVM, decision boundaries)
- Integration with existing 3D spatial utilities
"""

import numpy as np
from typing import Union, List, Tuple, Optional, Any
from .vector3d import Vector3D
from .spatial_utils import SpatialUtils


class Hyperplane:
    """
    Represents a hyperplane in n-dimensional space.
    
    A hyperplane is defined by the equation: w·x + b = 0
    where w is the normal vector and b is the bias term.
    
    For 2D: ax + by + c = 0 (line)
    For 3D: ax + by + cz + d = 0 (plane)
    For nD: w₁x₁ + w₂x₂ + ... + wₙxₙ + b = 0
    """
    
    def __init__(self, normal: Union[np.ndarray, List[float], Vector3D], bias: float = 0.0):
        """
        Initialize hyperplane with normal vector and bias.
        
        Args:
            normal: Normal vector to the hyperplane
            bias: Bias term (signed distance from origin)
        """
        if isinstance(normal, Vector3D):
            self.normal = np.array([normal.x, normal.y, normal.z])
        else:
            self.normal = np.array(normal, dtype=float)
        
        self.bias = float(bias)
        self.dimension = len(self.normal)
        
        # Normalize the normal vector
        norm = np.linalg.norm(self.normal)
        if norm > 1e-10:
            self.normal = self.normal / norm
            self.bias = self.bias / norm
    
    @classmethod
    def from_point_and_normal(cls, point: Union[np.ndarray, List[float], Vector3D], 
                             normal: Union[np.ndarray, List[float], Vector3D]) -> 'Hyperplane':
        """Create hyperplane from a point on the plane and normal vector."""
        if isinstance(point, Vector3D):
            point = np.array([point.x, point.y, point.z])
        else:
            point = np.array(point)
        
        if isinstance(normal, Vector3D):
            normal = np.array([normal.x, normal.y, normal.z])
        else:
            normal = np.array(normal)
        
        # Calculate bias: -normal·point
        bias = -np.dot(normal, point)
        return cls(normal, bias)
    
    @classmethod
    def from_points(cls, points: List[Union[np.ndarray, List[float]]]) -> 'Hyperplane':
        """
        Create hyperplane from n points in n-dimensional space.
        For n+1 points, creates hyperplane that best fits them.
        """
        points = [np.array(p) for p in points]
        n_points = len(points)
        dimension = len(points[0])
        
        if n_points < dimension:
            raise ValueError(f"Need at least {dimension} points for {dimension}D hyperplane")
        
        if n_points == dimension:
            # Exact fit - solve for hyperplane through n points
            # Create matrix where each row is [point, 1]
            A = np.column_stack([points, np.ones(n_points)])
            
            # Find null space (hyperplane coefficients)
            _, _, vh = np.linalg.svd(A)
            coeffs = vh[-1]
            
            normal = coeffs[:-1]
            bias = coeffs[-1]
            
        else:
            # Overdetermined - use least squares fit
            # Fit plane to minimize sum of squared distances
            A = np.column_stack([points, np.ones(n_points)])
            
            # Use SVD for robust fitting
            _, s, vh = np.linalg.svd(A, full_matrices=False)
            
            # Choose solution with smallest singular value
            coeffs = vh[-1]
            normal = coeffs[:-1]
            bias = coeffs[-1]
        
        return cls(normal, bias)
    
    @classmethod
    def from_svm_weights(cls, weights: np.ndarray, bias: float) -> 'Hyperplane':
        """Create hyperplane from SVM decision boundary weights."""
        return cls(weights, bias)
    
    def distance_to_point(self, point: Union[np.ndarray, List[float], Vector3D]) -> float:
        """Calculate signed distance from point to hyperplane."""
        if isinstance(point, Vector3D):
            point = np.array([point.x, point.y, point.z])
        else:
            point = np.array(point)
        
        return np.dot(self.normal, point) + self.bias
    
    def unsigned_distance_to_point(self, point: Union[np.ndarray, List[float], Vector3D]) -> float:
        """Calculate unsigned distance from point to hyperplane."""
        return abs(self.distance_to_point(point))
    
    def project_point(self, point: Union[np.ndarray, List[float], Vector3D]) -> np.ndarray:
        """Project point onto hyperplane."""
        if isinstance(point, Vector3D):
            point = np.array([point.x, point.y, point.z])
        else:
            point = np.array(point)
        
        distance = self.distance_to_point(point)
        return point - distance * self.normal
    
    def reflect_point(self, point: Union[np.ndarray, List[float], Vector3D]) -> np.ndarray:
        """Reflect point across hyperplane."""
        if isinstance(point, Vector3D):
            point = np.array([point.x, point.y, point.z])
        else:
            point = np.array(point)
        
        distance = self.distance_to_point(point)
        return point - 2 * distance * self.normal
    
    def classify_point(self, point: Union[np.ndarray, List[float], Vector3D]) -> int:
        """
        Classify point relative to hyperplane.
        Returns: 1 if on positive side, -1 if on negative side, 0 if on plane.
        """
        distance = self.distance_to_point(point)
        if abs(distance) < 1e-10:
            return 0
        return 1 if distance > 0 else -1
    
    def classify_points(self, points: List[Union[np.ndarray, List[float]]]) -> np.ndarray:
        """Classify multiple points at once."""
        if isinstance(points, np.ndarray):
            points_array = points
        else:
            points_array = np.array([np.array(p) for p in points])
        
        distances = points_array @ self.normal + self.bias
        return np.sign(distances)
    
    def is_on_hyperplane(self, point: Union[np.ndarray, List[float], Vector3D], 
                        tolerance: float = 1e-10) -> bool:
        """Check if point lies on hyperplane within tolerance."""
        return abs(self.distance_to_point(point)) < tolerance
    
    def get_parallel_hyperplane(self, distance: float) -> 'Hyperplane':
        """Get parallel hyperplane at specified signed distance."""
        return Hyperplane(self.normal.copy(), self.bias - distance)
    
    def translate(self, offset: Union[np.ndarray, List[float], Vector3D]) -> 'Hyperplane':
        """Translate hyperplane by offset vector."""
        if isinstance(offset, Vector3D):
            offset = np.array([offset.x, offset.y, offset.z])
        else:
            offset = np.array(offset)
        
        # Translation changes bias by -normal·offset
        new_bias = self.bias - np.dot(self.normal, offset)
        return Hyperplane(self.normal.copy(), new_bias)
    
    def flip_normal(self) -> 'Hyperplane':
        """Return hyperplane with flipped normal direction."""
        return Hyperplane(-self.normal, -self.bias)
    
    def to_vector3d_plane(self) -> Tuple[Vector3D, Vector3D]:
        """Convert to 3D plane representation (point, normal) for spatial_utils."""
        if self.dimension != 3:
            raise ValueError("Can only convert 3D hyperplanes to Vector3D representation")
        
        # Find a point on the plane
        # Use the point closest to origin
        point_on_plane = -self.bias * self.normal
        
        normal_vec = Vector3D(self.normal[0], self.normal[1], self.normal[2])
        point_vec = Vector3D(point_on_plane[0], point_on_plane[1], point_on_plane[2])
        
        return point_vec, normal_vec
    
    def __str__(self) -> str:
        """String representation of hyperplane equation."""
        terms = []
        for i, coeff in enumerate(self.normal):
            if abs(coeff) > 1e-10:
                if i == 0:
                    terms.append(f"{coeff:.3f}x{i+1}")
                else:
                    sign = "+" if coeff >= 0 else ""
                    terms.append(f"{sign}{coeff:.3f}x{i+1}")
        
        if abs(self.bias) > 1e-10:
            sign = "+" if self.bias >= 0 else ""
            terms.append(f"{sign}{self.bias:.3f}")
        
        return " ".join(terms) + " = 0"
    
    def __repr__(self) -> str:
        return f"Hyperplane(normal={self.normal}, bias={self.bias})"


class HyperplaneIntersection:
    """Utilities for hyperplane intersection operations."""
    
    @staticmethod
    def intersect_two_hyperplanes(h1: Hyperplane, h2: Hyperplane) -> Optional['Hyperplane']:
        """
        Find intersection of two hyperplanes.
        Returns a hyperplane of dimension n-1, or None if parallel.
        """
        if h1.dimension != h2.dimension:
            raise ValueError("Hyperplanes must have same dimension")
        
        # Check if parallel
        cross_product = np.cross(h1.normal, h2.normal) if h1.dimension == 2 else None
        dot_product = np.dot(h1.normal, h2.normal)
        
        if h1.dimension == 2:
            # 2D case: intersection is a point or line
            if abs(cross_product) < 1e-10:
                return None  # Parallel lines
            
            # Solve 2x2 system for intersection point
            A = np.array([h1.normal, h2.normal])
            b = np.array([-h1.bias, -h2.bias])
            point = np.linalg.solve(A, b)
            
            # Return as 0D "hyperplane" (point)
            return point
        
        else:
            # Higher dimensional case
            if abs(abs(dot_product) - 1.0) < 1e-10:
                return None  # Parallel hyperplanes
            
            # Create system of equations
            A = np.array([h1.normal, h2.normal])
            b = np.array([-h1.bias, -h2.bias])
            
            # Find null space of A (direction of intersection)
            _, _, vh = np.linalg.svd(A)
            null_space = vh[2:].T  # Columns are basis vectors for null space
            
            # Find particular solution
            particular = np.linalg.pinv(A) @ b
            
            # The intersection is an affine subspace
            # For visualization, we might return the null space basis
            return {
                'particular_solution': particular,
                'direction_basis': null_space,
                'dimension': h1.dimension - 2
            }
    
    @staticmethod
    def intersect_multiple_hyperplanes(hyperplanes: List[Hyperplane]) -> Optional[dict]:
        """
        Find intersection of multiple hyperplanes.
        Returns intersection subspace information or None if no intersection.
        """
        if not hyperplanes:
            return None
        
        dimension = hyperplanes[0].dimension
        if not all(h.dimension == dimension for h in hyperplanes):
            raise ValueError("All hyperplanes must have same dimension")
        
        # Create system of linear equations
        A = np.array([h.normal for h in hyperplanes])
        b = np.array([-h.bias for h in hyperplanes])
        
        # Solve using SVD for numerical stability
        u, s, vh = np.linalg.svd(A, full_matrices=False)
        
        # Check rank to determine if solution exists
        rank = np.sum(s > 1e-10)
        
        if rank > len(hyperplanes):
            return None  # Inconsistent system
        
        # Find particular solution
        s_inv = np.zeros_like(s)
        s_inv[s > 1e-10] = 1.0 / s[s > 1e-10]
        particular = vh.T @ (s_inv[:, None] * (u.T @ b))
        
        # Find null space (free directions)
        null_space = vh[rank:].T if rank < dimension else np.empty((dimension, 0))
        
        return {
            'particular_solution': particular,
            'direction_basis': null_space,
            'intersection_dimension': dimension - rank,
            'rank': rank
        }


class HyperplaneRegion:
    """Represents a region defined by multiple hyperplane constraints."""
    
    def __init__(self, hyperplanes: List[Hyperplane] = None):
        """Initialize with list of bounding hyperplanes."""
        self.hyperplanes = hyperplanes or []
        self.dimension = hyperplanes[0].dimension if hyperplanes else None
    
    def add_hyperplane(self, hyperplane: Hyperplane) -> None:
        """Add a hyperplane constraint to the region."""
        if self.dimension is None:
            self.dimension = hyperplane.dimension
        elif hyperplane.dimension != self.dimension:
            raise ValueError(f"Hyperplane dimension {hyperplane.dimension} doesn't match region dimension {self.dimension}")
        
        self.hyperplanes.append(hyperplane)
    
    def contains_point(self, point: Union[np.ndarray, List[float], Vector3D], 
                      tolerance: float = 1e-10) -> bool:
        """Check if point is inside the region (satisfies all constraints)."""
        for hyperplane in self.hyperplanes:
            if hyperplane.distance_to_point(point) > tolerance:
                return False
        return True
    
    def classify_points(self, points: List[Union[np.ndarray, List[float]]]) -> np.ndarray:
        """
        Classify points as inside (1) or outside (0) the region.
        Returns boolean array indicating membership.
        """
        if not points:
            return np.array([])
        
        points_array = np.array([np.array(p) for p in points])
        n_points = len(points_array)
        
        # Check each hyperplane constraint
        inside = np.ones(n_points, dtype=bool)
        
        for hyperplane in self.hyperplanes:
            distances = points_array @ hyperplane.normal + hyperplane.bias
            inside &= (distances <= 1e-10)
        
        return inside.astype(int)
    
    def get_vertices(self) -> List[np.ndarray]:
        """
        Find vertices of the polytope defined by hyperplanes.
        Only works for bounded regions in low dimensions.
        """
        if self.dimension > 3 or len(self.hyperplanes) < self.dimension:
            raise NotImplementedError("Vertex finding only implemented for 2D/3D bounded regions")
        
        vertices = []
        n = len(self.hyperplanes)
        
        # Check all combinations of d hyperplanes for d-dimensional intersections
        from itertools import combinations
        
        for combo in combinations(range(n), self.dimension):
            # Solve system of d equations in d unknowns
            A = np.array([self.hyperplanes[i].normal for i in combo])
            b = np.array([-self.hyperplanes[i].bias for i in combo])
            
            try:
                vertex = np.linalg.solve(A, b)
                
                # Check if vertex satisfies all constraints
                if self.contains_point(vertex):
                    vertices.append(vertex)
                    
            except np.linalg.LinAlgError:
                # Singular matrix - hyperplanes don't intersect at unique point
                continue
        
        return vertices
    
    def get_center(self) -> Optional[np.ndarray]:
        """Get geometric center of the region (centroid of vertices)."""
        try:
            vertices = self.get_vertices()
            if vertices:
                return np.mean(vertices, axis=0)
        except NotImplementedError:
            pass
        
        return None


# Integration with existing spatial utilities for 3D cases
class Hyperplane3DAdapter:
    """Adapter to integrate hyperplanes with existing 3D spatial utilities."""
    
    @staticmethod
    def from_spatial_plane(plane_point: Vector3D, plane_normal: Vector3D) -> Hyperplane:
        """Create hyperplane from existing spatial utils plane representation."""
        return Hyperplane.from_point_and_normal(plane_point, plane_normal)
    
    @staticmethod
    def distance_to_point_3d(hyperplane: Hyperplane, point: Vector3D) -> float:
        """Wrapper for 3D distance calculation using existing spatial utils."""
        if hyperplane.dimension != 3:
            raise ValueError("Only works with 3D hyperplanes")
        
        plane_point, plane_normal = hyperplane.to_vector3d_plane()
        return SpatialUtils.signed_distance_point_to_plane(point, plane_point, plane_normal)
    
    @staticmethod
    def project_point_3d(hyperplane: Hyperplane, point: Vector3D) -> Vector3D:
        """Project 3D point onto hyperplane using spatial utils."""
        if hyperplane.dimension != 3:
            raise ValueError("Only works with 3D hyperplanes")
        
        plane_point, plane_normal = hyperplane.to_vector3d_plane()
        projected = SpatialUtils.project_point_onto_plane(point, plane_point, plane_normal)
        return projected
    
    @staticmethod
    def reflect_point_3d(hyperplane: Hyperplane, point: Vector3D) -> Vector3D:
        """Reflect 3D point across hyperplane using spatial utils."""
        if hyperplane.dimension != 3:
            raise ValueError("Only works with 3D hyperplanes")
        
        plane_point, plane_normal = hyperplane.to_vector3d_plane()
        reflected = SpatialUtils.reflect_point_across_plane(point, plane_point, plane_normal)
        return reflected


# Convenience functions for common operations
def create_hyperplane_2d(a: float, b: float, c: float) -> Hyperplane:
    """Create 2D hyperplane from equation ax + by + c = 0."""
    return Hyperplane([a, b], c)


def create_hyperplane_3d(a: float, b: float, c: float, d: float) -> Hyperplane:
    """Create 3D hyperplane from equation ax + by + cz + d = 0."""
    return Hyperplane([a, b, c], d)


def hyperplane_from_points_2d(p1: Tuple[float, float], p2: Tuple[float, float]) -> Hyperplane:
    """Create 2D hyperplane (line) from two points."""
    return Hyperplane.from_points([p1, p2])


def hyperplane_from_points_3d(p1: Tuple[float, float, float], 
                             p2: Tuple[float, float, float], 
                             p3: Tuple[float, float, float]) -> Hyperplane:
    """Create 3D hyperplane from three points."""
    return Hyperplane.from_points([p1, p2, p3])


def svm_decision_boundary(weights: np.ndarray, bias: float) -> Hyperplane:
    """Create hyperplane representing SVM decision boundary."""
    return Hyperplane.from_svm_weights(weights, bias)