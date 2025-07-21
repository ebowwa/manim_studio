"""
3D Mathematics Package

This package provides comprehensive 3D mathematical operations for spatial computations,
organized into focused modules:

- vector3d: 3D vector operations (magnitude, normalization, dot/cross products, interpolation)
- matrix4x4: 4x4 matrix transformations (translation, rotation, scaling, projection)
- spatial_utils: Spatial utility functions (distances, intersections, geometric queries)

Each module can be used independently or together for complex 3D mathematical operations.
"""

from .vector3d import (
    Vector3D,
    lerp_3d,
    slerp_3d,
    dot_product,
    cross_product,
    distance_between,
    angle_between_vectors,
    reflect_vector,
    project_vector
)

from .matrix4x4 import (
    Matrix4x4,
    create_transform_matrix,
    create_trs_matrix,
    create_view_matrix,
    create_projection_matrix,
    invert_transform_matrix,
    combine_transforms
)

from .spatial_utils import (
    SpatialUtils,
    point_to_line_distance,
    point_to_plane_distance,
    ray_sphere_hit,
    triangle_contains_point,
    calculate_triangle_area,
    calculate_centroid,
    get_bounding_box
)

# Additional convenience functions for common operations
def euler_to_quaternion(euler: Vector3D) -> tuple:
    """Convert Euler angles to quaternion (x, y, z, w)."""
    import numpy as np
    
    cx = np.cos(euler.x * 0.5)
    sx = np.sin(euler.x * 0.5)
    cy = np.cos(euler.y * 0.5)
    sy = np.sin(euler.y * 0.5)
    cz = np.cos(euler.z * 0.5)
    sz = np.sin(euler.z * 0.5)
    
    w = cx * cy * cz + sx * sy * sz
    x = sx * cy * cz - cx * sy * sz
    y = cx * sy * cz + sx * cy * sz
    z = cx * cy * sz - sx * sy * cz
    
    return (x, y, z, w)


def quaternion_to_euler(x: float, y: float, z: float, w: float) -> Vector3D:
    """Convert quaternion to Euler angles."""
    import numpy as np
    
    # Roll (x-axis rotation)
    sinr_cosp = 2 * (w * x + y * z)
    cosr_cosp = 1 - 2 * (x * x + y * y)
    roll = np.arctan2(sinr_cosp, cosr_cosp)
    
    # Pitch (y-axis rotation)
    sinp = 2 * (w * y - z * x)
    if abs(sinp) >= 1:
        pitch = np.copysign(np.pi / 2, sinp)
    else:
        pitch = np.arcsin(sinp)
    
    # Yaw (z-axis rotation)
    siny_cosp = 2 * (w * z + x * y)
    cosy_cosp = 1 - 2 * (y * y + z * z)
    yaw = np.arctan2(siny_cosp, cosy_cosp)
    
    return Vector3D(roll, pitch, yaw)


# Export all public classes and functions
__all__ = [
    # Vector3D module
    'Vector3D',
    'lerp_3d',
    'slerp_3d', 
    'dot_product',
    'cross_product',
    'distance_between',
    'angle_between_vectors',
    'reflect_vector',
    'project_vector',
    
    # Matrix4x4 module
    'Matrix4x4',
    'create_transform_matrix',
    'create_trs_matrix',
    'create_view_matrix',
    'create_projection_matrix',
    'invert_transform_matrix',
    'combine_transforms',
    
    # Spatial utilities module
    'SpatialUtils',
    'point_to_line_distance',
    'point_to_plane_distance',
    'ray_sphere_hit',
    'triangle_contains_point',
    'calculate_triangle_area',
    'calculate_centroid',
    'get_bounding_box',
    
    # Quaternion utilities
    'euler_to_quaternion',
    'quaternion_to_euler'
]