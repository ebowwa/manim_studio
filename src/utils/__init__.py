"""Utility modules for Manim Studio."""

# Import these lazily to avoid circular imports
# from .timeline_debugger import TimelineDebugger
# from .frame_extractor import FrameExtractor, FrameExtractionConfig, extract_frames_from_video
# from .frame_analyzer import FrameAnalyzer, FrameAnalysisResult, analyze_video_frames

# Import 3D math utilities from the math3d package
from .math3d import (
    Vector3D, Matrix4x4, SpatialUtils,
    lerp_3d, slerp_3d, dot_product, cross_product,
    distance_between, angle_between_vectors, reflect_vector, project_vector,
    create_transform_matrix, create_trs_matrix, create_view_matrix, create_projection_matrix,
    invert_transform_matrix, combine_transforms,
    point_to_line_distance, point_to_plane_distance, ray_sphere_hit,
    triangle_contains_point, calculate_triangle_area, calculate_centroid, get_bounding_box,
    euler_to_quaternion, quaternion_to_euler
)

__all__ = [
    # Timeline and debugging utilities
    # 'TimelineDebugger',
    
    # Frame processing utilities
    # 'FrameExtractor', 'FrameExtractionConfig', 'extract_frames_from_video',
    # 'FrameAnalyzer', 'FrameAnalysisResult', 'analyze_video_frames',
    
    # 3D Math - Core classes
    'Vector3D', 'Matrix4x4', 'SpatialUtils',
    
    # 3D Math - Vector operations
    'lerp_3d', 'slerp_3d', 'dot_product', 'cross_product',
    'distance_between', 'angle_between_vectors', 'reflect_vector', 'project_vector',
    
    # 3D Math - Matrix operations
    'create_transform_matrix', 'create_trs_matrix', 'create_view_matrix', 'create_projection_matrix',
    'invert_transform_matrix', 'combine_transforms',
    
    # 3D Math - Spatial utilities
    'point_to_line_distance', 'point_to_plane_distance', 'ray_sphere_hit',
    'triangle_contains_point', 'calculate_triangle_area', 'calculate_centroid', 'get_bounding_box',
    
    # 3D Math - Quaternion utilities
    'euler_to_quaternion', 'quaternion_to_euler'
]