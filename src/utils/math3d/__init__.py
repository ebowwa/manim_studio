"""
3D Mathematics Package

This package provides comprehensive 3D mathematical operations for spatial computations,
organized into focused modules:

- vector3d: 3D vector operations (magnitude, normalization, dot/cross products, interpolation)
- matrix4x4: 4x4 matrix transformations (translation, rotation, scaling, projection)
- spatial_utils: Spatial utility functions (distances, intersections, geometric queries)
- interpolation: Advanced interpolation methods (Bezier curves, splines, easing functions)
- noise: Noise generation algorithms (Perlin, Simplex, fractal noise)
- curves: Parametric curves and path operations
- collision: Collision detection for various geometric shapes
- color_math: Color space conversions and operations
- polygon_ops: Polygon algorithms (winding numbers, area, triangulation, complex conversions)

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

from .interpolation import (
    BezierCurve,
    CatmullRomSpline,
    HermiteCurve,
    BSpline,
    smooth_step,
    smoother_step,
    smoothest_step,
    ease_in_out,
    bounce_ease_out,
    elastic_ease_out,
    circular_ease_in_out,
    multi_lerp,
    cosine_interpolation,
    cubic_interpolation,
    create_bezier_curve,
    create_quadratic_bezier,
    create_cubic_bezier,
    create_catmull_rom_spline,
    create_hermite_curve,
    create_b_spline
)

from .noise import (
    PerlinNoise,
    SimplexNoise,
    FractalNoise,
    VoronoiNoise,
    perlin_noise_2d,
    perlin_noise_3d,
    simplex_noise_2d,
    simplex_noise_3d,
    fbm_2d,
    fbm_3d,
    turbulence_2d,
    voronoi_2d,
    voronoi_edge_2d,
    noise_vector_field_2d,
    noise_vector_field_3d
)

from .curves import (
    ParametricCurve,
    ArcLengthParameterizedCurve,
    CircleCurve,
    HelixCurve,
    SpiralCurve,
    LissajousCurve,
    PathOperations,
    create_circle,
    create_helix,
    create_spiral,
    create_lissajous,
    evaluate_curve_frenet_frame
)

from .collision import (
    AABB,
    OBB,
    Sphere,
    Capsule,
    Ray,
    CollisionDetection,
    SweepTest,
    SpatialGrid,
    create_aabb,
    create_aabb_from_points,
    create_sphere,
    create_capsule,
    create_obb,
    create_ray
)

from .color_math import (
    Color,
    ColorSpaceConversions,
    ColorOperations,
    ColorHarmonies,
    ColorMetrics,
    ColorTemperature,
    Colors,
    rgb,
    rgb255,
    hex_color,
    hsv,
    hsl,
    interpolate_colors
)

from .polygon_ops import (
    get_winding_number,
    point_in_polygon,
    shoelace,
    polygon_area,
    polygon_orientation,
    polygon_centroid,
    earclip_triangulation,
    point_in_triangle_2d,
    complex_to_R3,
    R3_to_complex,
    complex_func_to_R3_func,
    apply_complex_function
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
    
    # Interpolation module
    'BezierCurve',
    'CatmullRomSpline',
    'HermiteCurve',
    'BSpline',
    'smooth_step',
    'smoother_step',
    'smoothest_step',
    'ease_in_out',
    'bounce_ease_out',
    'elastic_ease_out',
    'circular_ease_in_out',
    'multi_lerp',
    'cosine_interpolation',
    'cubic_interpolation',
    'create_bezier_curve',
    'create_quadratic_bezier',
    'create_cubic_bezier',
    'create_catmull_rom_spline',
    'create_hermite_curve',
    'create_b_spline',
    
    # Noise module
    'PerlinNoise',
    'SimplexNoise',
    'FractalNoise',
    'VoronoiNoise',
    'perlin_noise_2d',
    'perlin_noise_3d',
    'simplex_noise_2d',
    'simplex_noise_3d',
    'fbm_2d',
    'fbm_3d',
    'turbulence_2d',
    'voronoi_2d',
    'voronoi_edge_2d',
    'noise_vector_field_2d',
    'noise_vector_field_3d',
    
    # Curves module
    'ParametricCurve',
    'ArcLengthParameterizedCurve',
    'CircleCurve',
    'HelixCurve',
    'SpiralCurve',
    'LissajousCurve',
    'PathOperations',
    'create_circle',
    'create_helix',
    'create_spiral',
    'create_lissajous',
    'evaluate_curve_frenet_frame',
    
    # Collision module
    'AABB',
    'OBB',
    'Sphere',
    'Capsule',
    'Ray',
    'CollisionDetection',
    'SweepTest',
    'SpatialGrid',
    'create_aabb',
    'create_aabb_from_points',
    'create_sphere',
    'create_capsule',
    'create_obb',
    'create_ray',
    
    # Color math module
    'Color',
    'ColorSpaceConversions',
    'ColorOperations',
    'ColorHarmonies',
    'ColorMetrics',
    'ColorTemperature',
    'Colors',
    'rgb',
    'rgb255',
    'hex_color',
    'hsv',
    'hsl',
    'interpolate_colors',
    
    # Polygon operations module
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
    
    # Quaternion utilities
    'euler_to_quaternion',
    'quaternion_to_euler'
]