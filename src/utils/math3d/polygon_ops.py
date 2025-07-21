"""
Polygon Operations

This module provides polygon-specific algorithms including:
- Winding number calculation for point-in-polygon tests
- Shoelace formula for area calculation
- Ear clipping triangulation for converting polygons to triangles
- Complex number conversions for complex plane animations
"""

import numpy as np
from typing import List, Tuple, Sequence, Union, Callable
import itertools as it
from .vector3d import Vector3D


def get_winding_number(points: Sequence[np.ndarray]) -> float:
    """
    Determine the number of times a polygon winds around the origin.
    
    The orientation is measured mathematically positively, i.e.,
    counterclockwise.
    
    Parameters
    ----------
    points : Sequence[np.ndarray]
        The vertices of the polygon being queried.
        
    Returns
    -------
    float
        The winding number. 1.0 means one complete counterclockwise rotation,
        -1.0 means one clockwise rotation, 0.0 means the origin is outside.
        
    Examples
    --------
    >>> square_points = np.array([[1, 1, 0], [-1, 1, 0], [-1, -1, 0], [1, -1, 0]])
    >>> get_winding_number(square_points)  # Origin is inside
    1.0
    >>> shifted_square = square_points + np.array([3, 0, 0])
    >>> get_winding_number(shifted_square)  # Origin is outside
    0.0
    """
    total_angle = 0.0
    points = list(points) + [points[0]]  # Close the polygon
    
    for i in range(len(points) - 1):
        p1 = points[i]
        p2 = points[i + 1]
        
        # Calculate angle from p1 to p2 around origin
        angle1 = np.arctan2(p1[1], p1[0])
        angle2 = np.arctan2(p2[1], p2[0])
        
        d_angle = angle2 - angle1
        
        # Normalize angle to [-π, π]
        while d_angle > np.pi:
            d_angle -= 2 * np.pi
        while d_angle < -np.pi:
            d_angle += 2 * np.pi
            
        total_angle += d_angle
    
    return total_angle / (2 * np.pi)


def point_in_polygon(point: np.ndarray, polygon: Sequence[np.ndarray]) -> bool:
    """
    Test if a point is inside a polygon using the winding number algorithm.
    
    Parameters
    ----------
    point : np.ndarray
        The point to test (2D or 3D, but only x,y coordinates are used)
    polygon : Sequence[np.ndarray]
        The vertices of the polygon
        
    Returns
    -------
    bool
        True if the point is inside the polygon
    """
    # Translate polygon so point is at origin
    translated_polygon = [p - point for p in polygon]
    winding = get_winding_number(translated_polygon)
    
    # Point is inside if winding number is non-zero
    return abs(winding) > 0.5


def shoelace(points: Sequence[np.ndarray]) -> float:
    """
    Calculate the signed area of a polygon using the shoelace formula.
    
    Parameters
    ----------
    points : Sequence[np.ndarray]
        The vertices of the polygon in order. Each point should have at least
        x and y coordinates (z will be ignored).
        
    Returns
    -------
    float
        The signed area. Positive for counterclockwise, negative for clockwise.
        
    Notes
    -----
    The actual area is the absolute value of the result divided by 2.
    """
    points = np.array(points)
    x = points[:, 0]
    y = points[:, 1]
    
    # Add the first point at the end to close the polygon
    x = np.append(x, x[0])
    y = np.append(y, y[0])
    
    # Shoelace formula
    area = 0.0
    for i in range(len(x) - 1):
        area += x[i] * y[i + 1] - x[i + 1] * y[i]
    
    return area / 2.0


def polygon_area(points: Sequence[np.ndarray]) -> float:
    """
    Calculate the unsigned area of a polygon.
    
    Parameters
    ----------
    points : Sequence[np.ndarray]
        The vertices of the polygon
        
    Returns
    -------
    float
        The area of the polygon (always positive)
    """
    return abs(shoelace(points))


def polygon_orientation(points: Sequence[np.ndarray]) -> str:
    """
    Determine if a polygon is oriented clockwise or counterclockwise.
    
    Parameters
    ----------
    points : Sequence[np.ndarray]
        The vertices of the polygon
        
    Returns
    -------
    str
        "CCW" for counterclockwise, "CW" for clockwise
    """
    area = shoelace(points)
    return "CCW" if area > 0 else "CW"


def polygon_centroid(points: Sequence[np.ndarray]) -> np.ndarray:
    """
    Calculate the centroid of a polygon using the shoelace formula.
    
    Parameters
    ----------
    points : Sequence[np.ndarray]
        The vertices of the polygon
        
    Returns
    -------
    np.ndarray
        The centroid point
    """
    points = np.array(points)
    n = len(points)
    
    # Close the polygon
    x = np.append(points[:, 0], points[0, 0])
    y = np.append(points[:, 1], points[0, 1])
    
    # Calculate signed area
    signed_area = 0.0
    cx = 0.0
    cy = 0.0
    
    for i in range(n):
        cross = x[i] * y[i + 1] - x[i + 1] * y[i]
        signed_area += cross
        cx += (x[i] + x[i + 1]) * cross
        cy += (y[i] + y[i + 1]) * cross
    
    signed_area *= 0.5
    
    if abs(signed_area) < 1e-10:
        # Degenerate polygon, return average of points
        return np.mean(points, axis=0)
    
    factor = 1.0 / (6.0 * signed_area)
    cx *= factor
    cy *= factor
    
    # Return with original z-coordinate if 3D
    if points.shape[1] >= 3:
        return np.array([cx, cy, np.mean(points[:, 2])])
    else:
        return np.array([cx, cy])


def earclip_triangulation(vertices: np.ndarray, holes: List[List[int]] = None) -> List[Tuple[int, int, int]]:
    """
    Triangulate a polygon (potentially with holes) using the ear clipping algorithm.
    
    Parameters
    ----------
    vertices : np.ndarray
        Array of vertices, shape (n, 2) or (n, 3)
    holes : List[List[int]], optional
        List of hole polygons, where each hole is a list of vertex indices
        
    Returns
    -------
    List[Tuple[int, int, int]]
        List of triangles, each as a tuple of three vertex indices
        
    Notes
    -----
    This is a simplified version that handles simple polygons without holes.
    For polygons with holes, consider using the mapbox_earcut library.
    """
    if holes is not None:
        raise NotImplementedError("Holes are not yet supported in this implementation")
    
    n = len(vertices)
    if n < 3:
        return []
    
    # Work with 2D projection
    verts_2d = vertices[:, :2].copy()
    
    # Create a list of vertex indices
    indices = list(range(n))
    triangles = []
    
    # Helper function to check if a triangle is valid (no points inside)
    def is_ear(i: int, j: int, k: int, remaining_indices: List[int]) -> bool:
        # Get the triangle vertices
        a = verts_2d[i]
        b = verts_2d[j]
        c = verts_2d[k]
        
        # Check if triangle has correct orientation
        area = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
        if area <= 0:  # Wrong orientation or degenerate
            return False
        
        # Check if any other vertex is inside this triangle
        for idx in remaining_indices:
            if idx in (i, j, k):
                continue
            
            p = verts_2d[idx]
            if point_in_triangle_2d(p, a, b, c):
                return False
        
        return True
    
    # Main ear clipping loop
    while len(indices) > 3:
        ear_found = False
        
        for i in range(len(indices)):
            prev_idx = (i - 1) % len(indices)
            next_idx = (i + 1) % len(indices)
            
            if is_ear(indices[prev_idx], indices[i], indices[next_idx], indices):
                # Found an ear, clip it
                triangles.append((indices[prev_idx], indices[i], indices[next_idx]))
                indices.pop(i)
                ear_found = True
                break
        
        if not ear_found:
            # Fallback: just create a fan triangulation from the first vertex
            for i in range(1, len(indices) - 1):
                triangles.append((indices[0], indices[i], indices[i + 1]))
            break
    
    # Add the last triangle
    if len(indices) == 3:
        triangles.append(tuple(indices))
    
    return triangles


def point_in_triangle_2d(p: np.ndarray, a: np.ndarray, b: np.ndarray, c: np.ndarray) -> bool:
    """
    Check if a 2D point is inside a triangle using barycentric coordinates.
    
    Parameters
    ----------
    p : np.ndarray
        The point to test
    a, b, c : np.ndarray
        The triangle vertices
        
    Returns
    -------
    bool
        True if point is inside the triangle
    """
    # Compute vectors
    v0 = c - a
    v1 = b - a
    v2 = p - a
    
    # Compute dot products
    dot00 = np.dot(v0, v0)
    dot01 = np.dot(v0, v1)
    dot02 = np.dot(v0, v2)
    dot11 = np.dot(v1, v1)
    dot12 = np.dot(v1, v2)
    
    # Compute barycentric coordinates
    inv_denom = 1 / (dot00 * dot11 - dot01 * dot01)
    u = (dot11 * dot02 - dot01 * dot12) * inv_denom
    v = (dot00 * dot12 - dot01 * dot02) * inv_denom
    
    # Check if point is in triangle
    return (u >= 0) and (v >= 0) and (u + v <= 1)


# Complex number conversions
def complex_to_R3(z: complex) -> np.ndarray:
    """
    Convert a complex number to a 3D point in the xy-plane.
    
    Parameters
    ----------
    z : complex
        The complex number
        
    Returns
    -------
    np.ndarray
        3D point [real, imag, 0]
    """
    return np.array([z.real, z.imag, 0.0])


def R3_to_complex(point: Union[np.ndarray, Vector3D]) -> complex:
    """
    Convert a 3D point to a complex number (using x and y coordinates).
    
    Parameters
    ----------
    point : Union[np.ndarray, Vector3D]
        The 3D point
        
    Returns
    -------
    complex
        The complex number x + yi
    """
    if isinstance(point, Vector3D):
        return complex(point.x, point.y)
    else:
        return complex(point[0], point[1])


def complex_func_to_R3_func(
    complex_func: Callable[[complex], complex]
) -> Callable[[np.ndarray], np.ndarray]:
    """
    Convert a complex function to a function on 3D points.
    
    Parameters
    ----------
    complex_func : Callable[[complex], complex]
        A function that takes and returns complex numbers
        
    Returns
    -------
    Callable[[np.ndarray], np.ndarray]
        A function that takes and returns 3D points
        
    Examples
    --------
    >>> # Create a function that squares complex numbers
    >>> f = lambda z: z**2
    >>> f_3d = complex_func_to_R3_func(f)
    >>> f_3d(np.array([1, 1, 0]))  # (1+i)^2 = 2i
    array([0., 2., 0.])
    """
    def R3_func(point: np.ndarray) -> np.ndarray:
        z = R3_to_complex(point)
        result = complex_func(z)
        return complex_to_R3(result)
    
    return R3_func


def apply_complex_function(
    points: np.ndarray,
    complex_func: Callable[[complex], complex]
) -> np.ndarray:
    """
    Apply a complex function to an array of 3D points.
    
    Parameters
    ----------
    points : np.ndarray
        Array of 3D points, shape (n, 3)
    complex_func : Callable[[complex], complex]
        The complex function to apply
        
    Returns
    -------
    np.ndarray
        Transformed points
    """
    R3_func = complex_func_to_R3_func(complex_func)
    return np.array([R3_func(p) for p in points])


# Export all functions
__all__ = [
    'get_winding_number',
    'point_in_polygon',
    'shoelace',
    'polygon_area',
    'polygon_orientation',
    'polygon_centroid',
    'earclip_triangulation',
    'point_in_triangle_2d',
    'complex_to_R3',
    'R3_to_complex',
    'complex_func_to_R3_func',
    'apply_complex_function',
]