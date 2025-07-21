"""
4x4 Matrix Transformations

This module provides comprehensive 4x4 matrix operations for 3D transformations including:
- Translation, rotation, and scaling matrices
- Perspective and orthographic projection matrices
- Look-at matrices for camera transformations
- Matrix operations (multiplication, inverse, transpose)
- Matrix decomposition into translation, rotation, and scale
"""

import numpy as np
from typing import Tuple
from .vector3d import Vector3D


class Matrix4x4:
    """4x4 Matrix for 3D transformations."""

    def __init__(self, matrix: np.ndarray = None):
        if matrix is None:
            self.matrix = np.eye(4, dtype=np.float64)
        else:
            self.matrix = np.array(matrix, dtype=np.float64)

    @classmethod
    def identity(cls) -> 'Matrix4x4':
        """Create identity matrix."""
        return cls()

    @classmethod
    def translation(cls, x: float, y: float, z: float) -> 'Matrix4x4':
        """Create translation matrix."""
        matrix = np.eye(4, dtype=np.float64)
        matrix[0, 3] = x
        matrix[1, 3] = y
        matrix[2, 3] = z
        return cls(matrix)

    @classmethod
    def translation_from_vector(cls, vector: Vector3D) -> 'Matrix4x4':
        """Create translation matrix from Vector3D."""
        return cls.translation(vector.x, vector.y, vector.z)

    @classmethod
    def scale(cls, x: float, y: float, z: float) -> 'Matrix4x4':
        """Create scale matrix."""
        matrix = np.eye(4, dtype=np.float64)
        matrix[0, 0] = x
        matrix[1, 1] = y
        matrix[2, 2] = z
        return cls(matrix)

    @classmethod
    def uniform_scale(cls, scale: float) -> 'Matrix4x4':
        """Create uniform scale matrix."""
        return cls.scale(scale, scale, scale)

    @classmethod
    def scale_from_vector(cls, vector: Vector3D) -> 'Matrix4x4':
        """Create scale matrix from Vector3D."""
        return cls.scale(vector.x, vector.y, vector.z)

    @classmethod
    def rotation_x(cls, angle: float) -> 'Matrix4x4':
        """Create rotation matrix around X-axis."""
        cos_a = np.cos(angle)
        sin_a = np.sin(angle)
        matrix = np.eye(4, dtype=np.float64)
        matrix[1, 1] = cos_a
        matrix[1, 2] = -sin_a
        matrix[2, 1] = sin_a
        matrix[2, 2] = cos_a
        return cls(matrix)

    @classmethod
    def rotation_y(cls, angle: float) -> 'Matrix4x4':
        """Create rotation matrix around Y-axis."""
        cos_a = np.cos(angle)
        sin_a = np.sin(angle)
        matrix = np.eye(4, dtype=np.float64)
        matrix[0, 0] = cos_a
        matrix[0, 2] = sin_a
        matrix[2, 0] = -sin_a
        matrix[2, 2] = cos_a
        return cls(matrix)

    @classmethod
    def rotation_z(cls, angle: float) -> 'Matrix4x4':
        """Create rotation matrix around Z-axis."""
        cos_a = np.cos(angle)
        sin_a = np.sin(angle)
        matrix = np.eye(4, dtype=np.float64)
        matrix[0, 0] = cos_a
        matrix[0, 1] = -sin_a
        matrix[1, 0] = sin_a
        matrix[1, 1] = cos_a
        return cls(matrix)

    @classmethod
    def rotation_euler(cls, x_angle: float, y_angle: float, z_angle: float, 
                      order: str = "XYZ") -> 'Matrix4x4':
        """Create rotation matrix from Euler angles."""
        rx = cls.rotation_x(x_angle)
        ry = cls.rotation_y(y_angle)
        rz = cls.rotation_z(z_angle)
        
        if order == "XYZ":
            return rz * ry * rx
        elif order == "XZY":
            return ry * rz * rx
        elif order == "YXZ":
            return rz * rx * ry
        elif order == "YZX":
            return rx * rz * ry
        elif order == "ZXY":
            return ry * rx * rz
        elif order == "ZYX":
            return rx * ry * rz
        else:
            raise ValueError(f"Invalid rotation order: {order}")

    @classmethod
    def rotation_euler_from_vector(cls, euler: Vector3D, order: str = "XYZ") -> 'Matrix4x4':
        """Create rotation matrix from Euler angles in Vector3D."""
        return cls.rotation_euler(euler.x, euler.y, euler.z, order)

    @classmethod
    def rotation_axis_angle(cls, axis: Vector3D, angle: float) -> 'Matrix4x4':
        """Create rotation matrix around arbitrary axis."""
        axis = axis.normalize()
        cos_a = np.cos(angle)
        sin_a = np.sin(angle)
        x, y, z = axis.x, axis.y, axis.z

        matrix = np.eye(4, dtype=np.float64)
        matrix[0, 0] = cos_a + x*x*(1 - cos_a)
        matrix[0, 1] = x*y*(1 - cos_a) - z*sin_a
        matrix[0, 2] = x*z*(1 - cos_a) + y*sin_a
        matrix[1, 0] = y*x*(1 - cos_a) + z*sin_a
        matrix[1, 1] = cos_a + y*y*(1 - cos_a)
        matrix[1, 2] = y*z*(1 - cos_a) - x*sin_a
        matrix[2, 0] = z*x*(1 - cos_a) - y*sin_a
        matrix[2, 1] = z*y*(1 - cos_a) + x*sin_a
        matrix[2, 2] = cos_a + z*z*(1 - cos_a)
        return cls(matrix)

    @classmethod
    def look_at(cls, eye: Vector3D, target: Vector3D, up: Vector3D) -> 'Matrix4x4':
        """Create look-at view matrix."""
        forward = (target - eye).normalize()
        right = forward.cross(up.normalize()).normalize()
        new_up = right.cross(forward)

        matrix = np.eye(4, dtype=np.float64)
        matrix[0, 0:3] = right.array
        matrix[1, 0:3] = new_up.array
        matrix[2, 0:3] = -forward.array
        matrix[0, 3] = -right.dot(eye)
        matrix[1, 3] = -new_up.dot(eye)
        matrix[2, 3] = forward.dot(eye)
        return cls(matrix)

    @classmethod
    def perspective(cls, fov: float, aspect: float, near: float, far: float) -> 'Matrix4x4':
        """Create perspective projection matrix."""
        f = 1.0 / np.tan(fov / 2)
        matrix = np.zeros((4, 4), dtype=np.float64)
        matrix[0, 0] = f / aspect
        matrix[1, 1] = f
        matrix[2, 2] = (far + near) / (near - far)
        matrix[2, 3] = (2 * far * near) / (near - far)
        matrix[3, 2] = -1
        return cls(matrix)

    @classmethod
    def perspective_fov(cls, fov_y: float, width: float, height: float, 
                       near: float, far: float) -> 'Matrix4x4':
        """Create perspective projection matrix with field of view."""
        aspect = width / height
        return cls.perspective(fov_y, aspect, near, far)

    @classmethod
    def orthographic(cls, left: float, right: float, bottom: float, top: float, 
                    near: float, far: float) -> 'Matrix4x4':
        """Create orthographic projection matrix."""
        matrix = np.eye(4, dtype=np.float64)
        matrix[0, 0] = 2 / (right - left)
        matrix[1, 1] = 2 / (top - bottom)
        matrix[2, 2] = -2 / (far - near)
        matrix[0, 3] = -(right + left) / (right - left)
        matrix[1, 3] = -(top + bottom) / (top - bottom)
        matrix[2, 3] = -(far + near) / (far - near)
        return cls(matrix)

    @classmethod
    def orthographic_centered(cls, width: float, height: float, 
                             near: float, far: float) -> 'Matrix4x4':
        """Create centered orthographic projection matrix."""
        return cls.orthographic(-width/2, width/2, -height/2, height/2, near, far)

    def transform_point(self, point: Vector3D) -> Vector3D:
        """Transform a 3D point."""
        homogeneous = np.array([point.x, point.y, point.z, 1.0])
        result = self.matrix @ homogeneous
        if result[3] != 0:
            result = result / result[3]  # Perspective division
        return Vector3D(result[0], result[1], result[2])

    def transform_direction(self, direction: Vector3D) -> Vector3D:
        """Transform a 3D direction (ignores translation)."""
        homogeneous = np.array([direction.x, direction.y, direction.z, 0.0])
        result = self.matrix @ homogeneous
        return Vector3D(result[0], result[1], result[2])

    def transform_points(self, points: list) -> list:
        """Transform multiple 3D points efficiently."""
        if not points:
            return []
        
        # Convert to homogeneous coordinates
        homogeneous = np.array([[p.x, p.y, p.z, 1.0] for p in points])
        # Transform all points at once
        results = (self.matrix @ homogeneous.T).T
        # Convert back to Vector3D
        return [Vector3D(r[0], r[1], r[2]) for r in results]

    def inverse(self) -> 'Matrix4x4':
        """Calculate matrix inverse."""
        try:
            return Matrix4x4(np.linalg.inv(self.matrix))
        except np.linalg.LinAlgError:
            raise ValueError("Matrix is not invertible")

    def transpose(self) -> 'Matrix4x4':
        """Calculate matrix transpose."""
        return Matrix4x4(self.matrix.T)

    def determinant(self) -> float:
        """Calculate matrix determinant."""
        return np.linalg.det(self.matrix)

    def is_orthogonal(self, tolerance: float = 1e-6) -> bool:
        """Check if matrix is orthogonal."""
        product = self.matrix @ self.matrix.T
        identity = np.eye(4)
        return np.allclose(product, identity, atol=tolerance)

    def decompose(self) -> Tuple[Vector3D, Vector3D, Vector3D]:
        """Decompose matrix into translation, rotation, and scale."""
        # Extract translation
        translation = Vector3D(self.matrix[0, 3], self.matrix[1, 3], self.matrix[2, 3])
        
        # Extract scale
        scale_x = Vector3D(self.matrix[0, 0], self.matrix[1, 0], self.matrix[2, 0]).magnitude()
        scale_y = Vector3D(self.matrix[0, 1], self.matrix[1, 1], self.matrix[2, 1]).magnitude()
        scale_z = Vector3D(self.matrix[0, 2], self.matrix[1, 2], self.matrix[2, 2]).magnitude()
        scale = Vector3D(scale_x, scale_y, scale_z)
        
        # Extract rotation (simplified - returns Euler angles)
        rotation_matrix = self.matrix[:3, :3] / np.array([scale_x, scale_y, scale_z])
        sy = np.sqrt(rotation_matrix[0, 0]**2 + rotation_matrix[1, 0]**2)
        
        singular = sy < 1e-6
        if not singular:
            x = np.arctan2(rotation_matrix[2, 1], rotation_matrix[2, 2])
            y = np.arctan2(-rotation_matrix[2, 0], sy)
            z = np.arctan2(rotation_matrix[1, 0], rotation_matrix[0, 0])
        else:
            x = np.arctan2(-rotation_matrix[1, 2], rotation_matrix[1, 1])
            y = np.arctan2(-rotation_matrix[2, 0], sy)
            z = 0
        
        rotation = Vector3D(x, y, z)
        
        return translation, rotation, scale

    def __mul__(self, other: 'Matrix4x4') -> 'Matrix4x4':
        return Matrix4x4(self.matrix @ other.matrix)

    def __eq__(self, other: 'Matrix4x4') -> bool:
        if not isinstance(other, Matrix4x4):
            return False
        return np.allclose(self.matrix, other.matrix)

    def __str__(self) -> str:
        return f"Matrix4x4:\n{self.matrix}"

    def __repr__(self) -> str:
        return self.__str__()


# Convenience functions for matrix operations
def create_transform_matrix(translation: Vector3D = None, 
                          rotation: Vector3D = None, 
                          scale: Vector3D = None,
                          rotation_order: str = "XYZ") -> Matrix4x4:
    """Create transformation matrix from translation, rotation, and scale."""
    result = Matrix4x4.identity()
    
    if scale:
        result = result * Matrix4x4.scale_from_vector(scale)
    
    if rotation:
        result = result * Matrix4x4.rotation_euler_from_vector(rotation, rotation_order)
    
    if translation:
        result = result * Matrix4x4.translation_from_vector(translation)
    
    return result


def create_trs_matrix(translation: Vector3D, rotation: Vector3D, scale: Vector3D,
                     rotation_order: str = "XYZ") -> Matrix4x4:
    """Create TRS (Translation-Rotation-Scale) transformation matrix."""
    return create_transform_matrix(translation, rotation, scale, rotation_order)


def create_view_matrix(position: Vector3D, target: Vector3D, up: Vector3D = None) -> Matrix4x4:
    """Create view matrix for camera."""
    if up is None:
        up = Vector3D.up()
    return Matrix4x4.look_at(position, target, up)


def create_projection_matrix(fov: float, aspect: float, near: float, far: float, 
                           orthographic: bool = False) -> Matrix4x4:
    """Create projection matrix (perspective or orthographic)."""
    if orthographic:
        # Convert FOV to orthographic bounds
        height = 2 * near * np.tan(fov / 2)
        width = height * aspect
        return Matrix4x4.orthographic_centered(width, height, near, far)
    else:
        return Matrix4x4.perspective(fov, aspect, near, far)


def invert_transform_matrix(matrix: Matrix4x4) -> Matrix4x4:
    """Efficiently invert a transformation matrix."""
    return matrix.inverse()


def combine_transforms(*transforms: Matrix4x4) -> Matrix4x4:
    """Combine multiple transformation matrices."""
    result = Matrix4x4.identity()
    for transform in transforms:
        result = result * transform
    return result