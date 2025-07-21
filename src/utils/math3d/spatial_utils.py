"""
Spatial Utilities

This module provides comprehensive spatial utility functions including:
- Point-to-line and point-to-plane distance calculations
- Line-plane intersections
- Ray-sphere intersections
- Barycentric coordinates
- Triangle operations
- Geometric queries and spatial calculations
"""

import numpy as np
from typing import Union, Tuple, List
from .vector3d import Vector3D


class SpatialUtils:
    """Collection of spatial utility functions."""

    @staticmethod
    def distance_point_to_line(point: Vector3D, line_start: Vector3D, line_end: Vector3D) -> float:
        """Calculate distance from point to line segment."""
        line_vec = line_end - line_start
        point_vec = point - line_start
        
        line_len_sq = line_vec.magnitude_squared()
        if line_len_sq == 0:
            return point_vec.magnitude()
        
        t = max(0, min(1, point_vec.dot(line_vec) / line_len_sq))
        projection = line_start + line_vec * t
        return point.distance_to(projection)

    @staticmethod
    def distance_point_to_infinite_line(point: Vector3D, line_point: Vector3D, line_direction: Vector3D) -> float:
        """Calculate distance from point to infinite line."""
        line_direction = line_direction.normalize()
        point_vec = point - line_point
        projection_length = point_vec.dot(line_direction)
        projection = line_point + line_direction * projection_length
        return point.distance_to(projection)

    @staticmethod
    def distance_point_to_plane(point: Vector3D, plane_point: Vector3D, plane_normal: Vector3D) -> float:
        """Calculate distance from point to plane."""
        plane_normal = plane_normal.normalize()
        return abs((point - plane_point).dot(plane_normal))

    @staticmethod
    def signed_distance_point_to_plane(point: Vector3D, plane_point: Vector3D, plane_normal: Vector3D) -> float:
        """Calculate signed distance from point to plane."""
        plane_normal = plane_normal.normalize()
        return (point - plane_point).dot(plane_normal)

    @staticmethod
    def line_plane_intersection(line_start: Vector3D, line_direction: Vector3D, 
                               plane_point: Vector3D, plane_normal: Vector3D) -> Union[Vector3D, None]:
        """Find intersection point between line and plane."""
        plane_normal = plane_normal.normalize()
        line_direction = line_direction.normalize()
        
        denom = line_direction.dot(plane_normal)
        if abs(denom) < 1e-6:
            return None  # Line is parallel to plane
        
        t = (plane_point - line_start).dot(plane_normal) / denom
        return line_start + line_direction * t

    @staticmethod
    def line_segment_plane_intersection(line_start: Vector3D, line_end: Vector3D,
                                       plane_point: Vector3D, plane_normal: Vector3D) -> Union[Vector3D, None]:
        """Find intersection point between line segment and plane."""
        line_direction = line_end - line_start
        intersection = SpatialUtils.line_plane_intersection(line_start, line_direction, plane_point, plane_normal)
        
        if intersection is None:
            return None
        
        # Check if intersection is within line segment
        t = (intersection - line_start).dot(line_direction) / line_direction.magnitude_squared()
        if 0 <= t <= 1:
            return intersection
        return None

    @staticmethod
    def sphere_sphere_intersection(center1: Vector3D, radius1: float, 
                                  center2: Vector3D, radius2: float) -> bool:
        """Check if two spheres intersect."""
        distance = center1.distance_to(center2)
        return distance <= (radius1 + radius2)

    @staticmethod
    def sphere_sphere_overlap_volume(center1: Vector3D, radius1: float,
                                    center2: Vector3D, radius2: float) -> float:
        """Calculate overlap volume between two spheres."""
        d = center1.distance_to(center2)
        
        if d >= radius1 + radius2:
            return 0.0  # No overlap
        
        if d <= abs(radius1 - radius2):
            # One sphere is inside the other
            smaller_radius = min(radius1, radius2)
            return (4/3) * np.pi * smaller_radius**3
        
        # Partial overlap
        h1 = (radius1**2 - radius2**2 + d**2) / (2 * d)
        h2 = d - h1
        
        cap1_volume = (np.pi / 3) * (radius1 - h1)**2 * (2 * radius1 + h1)
        cap2_volume = (np.pi / 3) * (radius2 - h2)**2 * (2 * radius2 + h2)
        
        return cap1_volume + cap2_volume

    @staticmethod
    def ray_sphere_intersection(ray_origin: Vector3D, ray_direction: Vector3D,
                               sphere_center: Vector3D, sphere_radius: float) -> Union[Tuple[float, float], None]:
        """Find intersection distances along ray to sphere. Returns (near, far) or None."""
        ray_direction = ray_direction.normalize()
        oc = ray_origin - sphere_center
        
        a = ray_direction.magnitude_squared()
        b = 2.0 * oc.dot(ray_direction)
        c = oc.magnitude_squared() - sphere_radius**2
        
        discriminant = b**2 - 4*a*c
        if discriminant < 0:
            return None
        
        sqrt_discriminant = np.sqrt(discriminant)
        t1 = (-b - sqrt_discriminant) / (2*a)
        t2 = (-b + sqrt_discriminant) / (2*a)
        
        return (t1, t2)

    @staticmethod
    def ray_sphere_first_intersection(ray_origin: Vector3D, ray_direction: Vector3D,
                                     sphere_center: Vector3D, sphere_radius: float) -> Union[float, None]:
        """Find first intersection distance along ray to sphere."""
        intersections = SpatialUtils.ray_sphere_intersection(ray_origin, ray_direction, sphere_center, sphere_radius)
        
        if intersections is None:
            return None
        
        t1, t2 = intersections
        if t1 > 0:
            return t1
        elif t2 > 0:
            return t2
        else:
            return None

    @staticmethod
    def barycentric_coordinates(point: Vector3D, a: Vector3D, b: Vector3D, c: Vector3D) -> Tuple[float, float, float]:
        """Calculate barycentric coordinates of point in triangle."""
        v0 = c - a
        v1 = b - a
        v2 = point - a
        
        dot00 = v0.dot(v0)
        dot01 = v0.dot(v1)
        dot02 = v0.dot(v2)
        dot11 = v1.dot(v1)
        dot12 = v1.dot(v2)
        
        inv_denom = 1 / (dot00 * dot11 - dot01 * dot01)
        u = (dot11 * dot02 - dot01 * dot12) * inv_denom
        v = (dot00 * dot12 - dot01 * dot02) * inv_denom
        w = 1 - u - v
        
        return w, v, u

    @staticmethod
    def point_in_triangle(point: Vector3D, a: Vector3D, b: Vector3D, c: Vector3D) -> bool:
        """Check if point lies inside triangle."""
        u, v, w = SpatialUtils.barycentric_coordinates(point, a, b, c)
        return (u >= 0) and (v >= 0) and (w >= 0)

    @staticmethod
    def triangle_area(a: Vector3D, b: Vector3D, c: Vector3D) -> float:
        """Calculate area of triangle."""
        return 0.5 * (b - a).cross(c - a).magnitude()

    @staticmethod
    def triangle_normal(a: Vector3D, b: Vector3D, c: Vector3D) -> Vector3D:
        """Calculate normal vector of triangle."""
        return (b - a).cross(c - a).normalize()

    @staticmethod
    def closest_point_on_triangle(point: Vector3D, a: Vector3D, b: Vector3D, c: Vector3D) -> Vector3D:
        """Find closest point on triangle to given point."""
        # Project point onto triangle plane
        normal = SpatialUtils.triangle_normal(a, b, c)
        plane_point = point - normal * (point - a).dot(normal)
        
        # Check if projected point is inside triangle
        if SpatialUtils.point_in_triangle(plane_point, a, b, c):
            return plane_point
        
        # Find closest point on triangle edges
        closest_ab = SpatialUtils.closest_point_on_line_segment(plane_point, a, b)
        closest_bc = SpatialUtils.closest_point_on_line_segment(plane_point, b, c)
        closest_ca = SpatialUtils.closest_point_on_line_segment(plane_point, c, a)
        
        dist_ab = plane_point.distance_to(closest_ab)
        dist_bc = plane_point.distance_to(closest_bc)
        dist_ca = plane_point.distance_to(closest_ca)
        
        if dist_ab <= dist_bc and dist_ab <= dist_ca:
            return closest_ab
        elif dist_bc <= dist_ca:
            return closest_bc
        else:
            return closest_ca

    @staticmethod
    def closest_point_on_line_segment(point: Vector3D, line_start: Vector3D, line_end: Vector3D) -> Vector3D:
        """Find closest point on line segment to given point."""
        line_vec = line_end - line_start
        point_vec = point - line_start
        
        line_len_sq = line_vec.magnitude_squared()
        if line_len_sq == 0:
            return line_start
        
        t = max(0, min(1, point_vec.dot(line_vec) / line_len_sq))
        return line_start + line_vec * t

    @staticmethod
    def closest_points_between_lines(line1_start: Vector3D, line1_end: Vector3D,
                                    line2_start: Vector3D, line2_end: Vector3D) -> Tuple[Vector3D, Vector3D]:
        """Find closest points between two line segments."""
        d1 = line1_end - line1_start
        d2 = line2_end - line2_start
        r = line1_start - line2_start
        
        a = d1.dot(d1)
        b = d1.dot(d2)
        c = d2.dot(d2)
        d = d1.dot(r)
        e = d2.dot(r)
        f = r.dot(r)
        
        denom = a * c - b * b
        
        if abs(denom) < 1e-6:
            # Lines are parallel
            s = 0
            t = d / b if abs(b) > 1e-6 else 0
        else:
            s = (b * e - c * d) / denom
            t = (a * e - b * d) / denom
        
        s = max(0, min(1, s))
        t = max(0, min(1, t))
        
        point1 = line1_start + d1 * s
        point2 = line2_start + d2 * t
        
        return point1, point2

    @staticmethod
    def volume_of_tetrahedron(a: Vector3D, b: Vector3D, c: Vector3D, d: Vector3D) -> float:
        """Calculate volume of tetrahedron formed by four points."""
        return abs((b - a).dot((c - a).cross(d - a))) / 6.0

    @staticmethod
    def centroid_of_points(points: List[Vector3D]) -> Vector3D:
        """Calculate centroid of a list of points."""
        if not points:
            return Vector3D.zero()
        
        total = Vector3D.zero()
        for point in points:
            total = total + point
        
        return total / len(points)

    @staticmethod
    def bounding_box_of_points(points: List[Vector3D]) -> Tuple[Vector3D, Vector3D]:
        """Calculate axis-aligned bounding box of points."""
        if not points:
            return Vector3D.zero(), Vector3D.zero()
        
        min_x = min_y = min_z = float('inf')
        max_x = max_y = max_z = float('-inf')
        
        for point in points:
            min_x = min(min_x, point.x)
            min_y = min(min_y, point.y)
            min_z = min(min_z, point.z)
            max_x = max(max_x, point.x)
            max_y = max(max_y, point.y)
            max_z = max(max_z, point.z)
        
        return Vector3D(min_x, min_y, min_z), Vector3D(max_x, max_y, max_z)

    @staticmethod
    def point_in_sphere(point: Vector3D, sphere_center: Vector3D, sphere_radius: float) -> bool:
        """Check if point is inside sphere."""
        return point.distance_to(sphere_center) <= sphere_radius

    @staticmethod
    def point_in_box(point: Vector3D, box_min: Vector3D, box_max: Vector3D) -> bool:
        """Check if point is inside axis-aligned bounding box."""
        return (box_min.x <= point.x <= box_max.x and
                box_min.y <= point.y <= box_max.y and
                box_min.z <= point.z <= box_max.z)

    @staticmethod
    def line_sphere_intersection(line_start: Vector3D, line_end: Vector3D,
                                sphere_center: Vector3D, sphere_radius: float) -> bool:
        """Check if line segment intersects with sphere."""
        # Find closest point on line segment to sphere center
        closest_point = SpatialUtils.closest_point_on_line_segment(sphere_center, line_start, line_end)
        distance = sphere_center.distance_to(closest_point)
        return distance <= sphere_radius

    @staticmethod
    def plane_from_points(p1: Vector3D, p2: Vector3D, p3: Vector3D) -> Tuple[Vector3D, Vector3D]:
        """Create plane from three points. Returns (point_on_plane, normal)."""
        normal = (p2 - p1).cross(p3 - p1).normalize()
        return p1, normal

    @staticmethod
    def project_point_onto_plane(point: Vector3D, plane_point: Vector3D, plane_normal: Vector3D) -> Vector3D:
        """Project point onto plane."""
        plane_normal = plane_normal.normalize()
        distance = (point - plane_point).dot(plane_normal)
        return point - plane_normal * distance

    @staticmethod
    def reflect_point_across_plane(point: Vector3D, plane_point: Vector3D, plane_normal: Vector3D) -> Vector3D:
        """Reflect point across plane."""
        plane_normal = plane_normal.normalize()
        distance = (point - plane_point).dot(plane_normal)
        return point - plane_normal * (2 * distance)


# Convenience functions for common spatial operations
def point_to_line_distance(point: Vector3D, line_start: Vector3D, line_end: Vector3D) -> float:
    """Calculate distance from point to line segment."""
    return SpatialUtils.distance_point_to_line(point, line_start, line_end)


def point_to_plane_distance(point: Vector3D, plane_point: Vector3D, plane_normal: Vector3D) -> float:
    """Calculate distance from point to plane."""
    return SpatialUtils.distance_point_to_plane(point, plane_point, plane_normal)


def ray_sphere_hit(ray_origin: Vector3D, ray_direction: Vector3D,
                   sphere_center: Vector3D, sphere_radius: float) -> bool:
    """Check if ray hits sphere."""
    return SpatialUtils.ray_sphere_first_intersection(ray_origin, ray_direction, sphere_center, sphere_radius) is not None


def triangle_contains_point(point: Vector3D, a: Vector3D, b: Vector3D, c: Vector3D) -> bool:
    """Check if triangle contains point."""
    return SpatialUtils.point_in_triangle(point, a, b, c)


def calculate_triangle_area(a: Vector3D, b: Vector3D, c: Vector3D) -> float:
    """Calculate area of triangle."""
    return SpatialUtils.triangle_area(a, b, c)


def calculate_centroid(points: List[Vector3D]) -> Vector3D:
    """Calculate centroid of points."""
    return SpatialUtils.centroid_of_points(points)


def get_bounding_box(points: List[Vector3D]) -> Tuple[Vector3D, Vector3D]:
    """Get axis-aligned bounding box of points."""
    return SpatialUtils.bounding_box_of_points(points)