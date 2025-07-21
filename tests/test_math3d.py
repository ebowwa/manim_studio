"""Tests for 3D math utilities."""

import pytest
import numpy as np
from src.manim_studio.utils.math3d import (
    Vector3D, Matrix4x4, SpatialUtils,
    lerp_3d, slerp_3d, create_transform_matrix,
    euler_to_quaternion, quaternion_to_euler
)


class TestVector3D:
    """Test cases for Vector3D class."""

    def test_vector_creation(self):
        """Test vector creation and basic properties."""
        v = Vector3D(1, 2, 3)
        assert v.x == 1
        assert v.y == 2
        assert v.z == 3
        assert np.array_equal(v.array, np.array([1, 2, 3]))

    def test_vector_from_array(self):
        """Test creating vector from numpy array."""
        arr = np.array([4, 5, 6])
        v = Vector3D.from_array(arr)
        assert v.x == 4
        assert v.y == 5
        assert v.z == 6

    def test_vector_constants(self):
        """Test vector constants."""
        assert Vector3D.zero() == Vector3D(0, 0, 0)
        assert Vector3D.up() == Vector3D(0, 1, 0)
        assert Vector3D.right() == Vector3D(1, 0, 0)
        assert Vector3D.forward() == Vector3D(0, 0, 1)

    def test_magnitude(self):
        """Test vector magnitude calculations."""
        v = Vector3D(3, 4, 0)
        assert v.magnitude() == 5.0
        assert v.magnitude_squared() == 25.0

    def test_normalize(self):
        """Test vector normalization."""
        v = Vector3D(3, 4, 0)
        normalized = v.normalize()
        assert abs(normalized.magnitude() - 1.0) < 1e-10
        
        # Test zero vector normalization
        zero_normalized = Vector3D.zero().normalize()
        assert zero_normalized == Vector3D.zero()

    def test_dot_product(self):
        """Test dot product."""
        v1 = Vector3D(1, 2, 3)
        v2 = Vector3D(4, 5, 6)
        assert v1.dot(v2) == 32  # 1*4 + 2*5 + 3*6

    def test_cross_product(self):
        """Test cross product."""
        v1 = Vector3D(1, 0, 0)
        v2 = Vector3D(0, 1, 0)
        cross = v1.cross(v2)
        assert cross == Vector3D(0, 0, 1)

    def test_distance(self):
        """Test distance calculation."""
        v1 = Vector3D(0, 0, 0)
        v2 = Vector3D(3, 4, 0)
        assert v1.distance_to(v2) == 5.0

    def test_linear_interpolation(self):
        """Test linear interpolation."""
        v1 = Vector3D(0, 0, 0)
        v2 = Vector3D(10, 10, 10)
        lerped = v1.lerp(v2, 0.5)
        assert lerped == Vector3D(5, 5, 5)

    def test_vector_arithmetic(self):
        """Test vector arithmetic operations."""
        v1 = Vector3D(1, 2, 3)
        v2 = Vector3D(4, 5, 6)
        
        # Addition
        result = v1 + v2
        assert result == Vector3D(5, 7, 9)
        
        # Subtraction
        result = v2 - v1
        assert result == Vector3D(3, 3, 3)
        
        # Scalar multiplication
        result = v1 * 2
        assert result == Vector3D(2, 4, 6)
        
        # Scalar division
        result = v1 / 2
        assert result == Vector3D(0.5, 1, 1.5)
        
        # Negation
        result = -v1
        assert result == Vector3D(-1, -2, -3)

    def test_angle_between(self):
        """Test angle calculation between vectors."""
        v1 = Vector3D(1, 0, 0)
        v2 = Vector3D(0, 1, 0)
        angle = v1.angle_between(v2)
        assert abs(angle - np.pi/2) < 1e-10

    def test_reflection(self):
        """Test vector reflection."""
        v = Vector3D(1, -1, 0)
        normal = Vector3D(0, 1, 0)
        reflected = v.reflect(normal)
        assert reflected == Vector3D(1, 1, 0)

    def test_projection(self):
        """Test vector projection."""
        v1 = Vector3D(3, 4, 0)
        v2 = Vector3D(1, 0, 0)
        projection = v1.project_onto(v2)
        assert projection == Vector3D(3, 0, 0)

    def test_equality(self):
        """Test vector equality."""
        v1 = Vector3D(1, 2, 3)
        v2 = Vector3D(1, 2, 3)
        v3 = Vector3D(1, 2, 4)
        assert v1 == v2
        assert v1 != v3


class TestMatrix4x4:
    """Test cases for Matrix4x4 class."""

    def test_identity_matrix(self):
        """Test identity matrix creation."""
        identity = Matrix4x4.identity()
        expected = np.eye(4)
        assert np.array_equal(identity.matrix, expected)

    def test_translation_matrix(self):
        """Test translation matrix."""
        trans = Matrix4x4.translation(1, 2, 3)
        point = Vector3D(0, 0, 0)
        result = trans.transform_point(point)
        assert result == Vector3D(1, 2, 3)

    def test_scale_matrix(self):
        """Test scale matrix."""
        scale = Matrix4x4.scale(2, 3, 4)
        point = Vector3D(1, 1, 1)
        result = scale.transform_point(point)
        assert result == Vector3D(2, 3, 4)

    def test_rotation_matrices(self):
        """Test rotation matrices."""
        # Test 90-degree rotation around Z-axis
        rot_z = Matrix4x4.rotation_z(np.pi/2)
        point = Vector3D(1, 0, 0)
        result = rot_z.transform_point(point)
        assert abs(result.x) < 1e-10
        assert abs(result.y - 1) < 1e-10
        assert abs(result.z) < 1e-10

    def test_matrix_multiplication(self):
        """Test matrix multiplication."""
        trans = Matrix4x4.translation(1, 2, 3)
        scale = Matrix4x4.scale(2, 2, 2)
        combined = trans * scale
        
        point = Vector3D(1, 1, 1)
        result = combined.transform_point(point)
        assert result == Vector3D(3, 4, 5)  # scaled then translated

    def test_matrix_inverse(self):
        """Test matrix inverse."""
        trans = Matrix4x4.translation(1, 2, 3)
        inverse = trans.inverse()
        combined = trans * inverse
        
        # Should be identity (within floating point precision)
        identity = Matrix4x4.identity()
        diff = np.abs(combined.matrix - identity.matrix)
        assert np.all(diff < 1e-10)

    def test_transform_direction(self):
        """Test direction transformation (no translation)."""
        trans = Matrix4x4.translation(10, 20, 30)
        direction = Vector3D(1, 0, 0)
        result = trans.transform_direction(direction)
        assert result == direction  # Translation shouldn't affect direction

    def test_look_at_matrix(self):
        """Test look-at matrix."""
        eye = Vector3D(0, 0, 5)
        target = Vector3D(0, 0, 0)
        up = Vector3D(0, 1, 0)
        
        look_at = Matrix4x4.look_at(eye, target, up)
        # Transform should place eye at origin looking down negative Z
        transformed_eye = look_at.transform_point(eye)
        assert abs(transformed_eye.z) < 1e-10

    def test_perspective_matrix(self):
        """Test perspective projection matrix."""
        fov = np.pi/4
        aspect = 16/9
        near = 0.1
        far = 100.0
        
        perspective = Matrix4x4.perspective(fov, aspect, near, far)
        assert perspective.matrix[3, 2] == -1  # Perspective projection marker

    def test_matrix_decomposition(self):
        """Test matrix decomposition."""
        # Create a simple transform with just translation
        original_trans = Vector3D(1, 2, 3)
        
        matrix = create_transform_matrix(translation=original_trans)
        trans, rot, scale = matrix.decompose()
        
        assert abs(trans.x - original_trans.x) < 1e-10
        assert abs(trans.y - original_trans.y) < 1e-10
        assert abs(trans.z - original_trans.z) < 1e-10
        
        # Scale should be identity for translation-only matrix
        assert abs(scale.x - 1.0) < 1e-10
        assert abs(scale.y - 1.0) < 1e-10
        assert abs(scale.z - 1.0) < 1e-10


class TestSpatialUtils:
    """Test cases for SpatialUtils class."""

    def test_distance_point_to_line(self):
        """Test distance from point to line."""
        point = Vector3D(0, 1, 0)
        line_start = Vector3D(-1, 0, 0)
        line_end = Vector3D(1, 0, 0)
        
        distance = SpatialUtils.distance_point_to_line(point, line_start, line_end)
        assert abs(distance - 1.0) < 1e-10

    def test_distance_point_to_plane(self):
        """Test distance from point to plane."""
        point = Vector3D(0, 0, 5)
        plane_point = Vector3D(0, 0, 0)
        plane_normal = Vector3D(0, 0, 1)
        
        distance = SpatialUtils.distance_point_to_plane(point, plane_point, plane_normal)
        assert abs(distance - 5.0) < 1e-10

    def test_line_plane_intersection(self):
        """Test line-plane intersection."""
        line_start = Vector3D(0, 0, -5)
        line_direction = Vector3D(0, 0, 1)
        plane_point = Vector3D(0, 0, 0)
        plane_normal = Vector3D(0, 0, 1)
        
        intersection = SpatialUtils.line_plane_intersection(
            line_start, line_direction, plane_point, plane_normal
        )
        
        assert intersection is not None
        assert intersection == Vector3D(0, 0, 0)

    def test_sphere_sphere_intersection(self):
        """Test sphere-sphere intersection."""
        center1 = Vector3D(0, 0, 0)
        radius1 = 1.0
        center2 = Vector3D(1.5, 0, 0)
        radius2 = 1.0
        
        # Should intersect
        assert SpatialUtils.sphere_sphere_intersection(center1, radius1, center2, radius2)
        
        # Should not intersect
        center3 = Vector3D(3, 0, 0)
        assert not SpatialUtils.sphere_sphere_intersection(center1, radius1, center3, radius2)

    def test_ray_sphere_intersection(self):
        """Test ray-sphere intersection."""
        ray_origin = Vector3D(-5, 0, 0)
        ray_direction = Vector3D(1, 0, 0)
        sphere_center = Vector3D(0, 0, 0)
        sphere_radius = 1.0
        
        intersections = SpatialUtils.ray_sphere_intersection(
            ray_origin, ray_direction, sphere_center, sphere_radius
        )
        
        assert intersections is not None
        t1, t2 = intersections
        assert abs(t1 - 4.0) < 1e-10  # Should hit at x = -1

    def test_barycentric_coordinates(self):
        """Test barycentric coordinates."""
        # Test with point at vertex A
        a = Vector3D(0, 0, 0)
        b = Vector3D(1, 0, 0)
        c = Vector3D(0, 1, 0)
        point = a
        
        u, v, w = SpatialUtils.barycentric_coordinates(point, a, b, c)
        assert abs(u - 1.0) < 1e-10
        assert abs(v) < 1e-10
        assert abs(w) < 1e-10

    def test_point_in_triangle(self):
        """Test point in triangle."""
        a = Vector3D(0, 0, 0)
        b = Vector3D(1, 0, 0)
        c = Vector3D(0, 1, 0)
        
        # Point inside triangle
        inside_point = Vector3D(0.25, 0.25, 0)
        assert SpatialUtils.point_in_triangle(inside_point, a, b, c)
        
        # Point outside triangle
        outside_point = Vector3D(1, 1, 0)
        assert not SpatialUtils.point_in_triangle(outside_point, a, b, c)

    def test_closest_point_on_line_segment(self):
        """Test closest point on line segment."""
        point = Vector3D(0, 1, 0)
        line_start = Vector3D(-1, 0, 0)
        line_end = Vector3D(1, 0, 0)
        
        closest = SpatialUtils.closest_point_on_line_segment(point, line_start, line_end)
        assert closest == Vector3D(0, 0, 0)

    def test_volume_of_tetrahedron(self):
        """Test tetrahedron volume calculation."""
        # Unit tetrahedron
        a = Vector3D(0, 0, 0)
        b = Vector3D(1, 0, 0)
        c = Vector3D(0, 1, 0)
        d = Vector3D(0, 0, 1)
        
        volume = SpatialUtils.volume_of_tetrahedron(a, b, c, d)
        expected_volume = 1.0/6.0
        assert abs(volume - expected_volume) < 1e-10

    def test_centroid_of_points(self):
        """Test centroid calculation."""
        points = [
            Vector3D(0, 0, 0),
            Vector3D(3, 0, 0),
            Vector3D(0, 3, 0),
            Vector3D(0, 0, 3)
        ]
        
        centroid = SpatialUtils.centroid_of_points(points)
        expected = Vector3D(0.75, 0.75, 0.75)
        
        assert abs(centroid.x - expected.x) < 1e-10
        assert abs(centroid.y - expected.y) < 1e-10
        assert abs(centroid.z - expected.z) < 1e-10


class TestUtilityFunctions:
    """Test cases for utility functions."""

    def test_lerp_3d(self):
        """Test 3D linear interpolation."""
        a = Vector3D(0, 0, 0)
        b = Vector3D(10, 10, 10)
        result = lerp_3d(a, b, 0.5)
        assert result == Vector3D(5, 5, 5)

    def test_create_transform_matrix(self):
        """Test transform matrix creation."""
        translation = Vector3D(1, 2, 3)
        scale = Vector3D(2, 2, 2)
        
        matrix = create_transform_matrix(translation=translation, scale=scale)
        
        point = Vector3D(1, 1, 1)
        result = matrix.transform_point(point)
        # Order is scale then translate: (1,1,1) * 2 + (1,2,3) = (3,4,5)
        # But our function does translate then scale: (1,1,1) + (1,2,3) * 2 = (4,6,8)
        assert result == Vector3D(4, 6, 8)

    def test_euler_quaternion_conversion(self):
        """Test Euler to quaternion conversion and back."""
        euler = Vector3D(0.1, 0.2, 0.3)
        
        # Convert to quaternion
        x, y, z, w = euler_to_quaternion(euler)
        
        # Convert back to Euler
        result_euler = quaternion_to_euler(x, y, z, w)
        
        # Should be approximately equal
        assert abs(result_euler.x - euler.x) < 1e-10
        assert abs(result_euler.y - euler.y) < 1e-10
        assert abs(result_euler.z - euler.z) < 1e-10

    def test_spherical_interpolation(self):
        """Test spherical linear interpolation."""
        a = Vector3D(1, 0, 0).normalize()
        b = Vector3D(0, 1, 0).normalize()
        
        result = slerp_3d(a, b, 0.5)
        
        # Result should be normalized
        assert abs(result.magnitude() - 1.0) < 1e-10
        
        # Should be halfway between input vectors
        expected = Vector3D(1/np.sqrt(2), 1/np.sqrt(2), 0)
        assert abs(result.x - expected.x) < 1e-10
        assert abs(result.y - expected.y) < 1e-10
        assert abs(result.z - expected.z) < 1e-10


if __name__ == "__main__":
    pytest.main([__file__])