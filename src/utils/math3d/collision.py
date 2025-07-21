"""
Collision Detection Utilities

This module provides collision detection algorithms for various geometric shapes:
- AABB (Axis-Aligned Bounding Box) collisions
- OBB (Oriented Bounding Box) collisions
- Sphere collisions
- Capsule collisions
- Ray casting
- Swept collision detection
- Spatial partitioning (octree, grid)
"""

import numpy as np
from typing import Tuple, Optional, List, Set
from dataclasses import dataclass
from .vector3d import Vector3D
from .matrix4x4 import Matrix4x4
from .spatial_utils import SpatialUtils


@dataclass
class AABB:
    """Axis-Aligned Bounding Box."""
    min_point: Vector3D
    max_point: Vector3D
    
    def center(self) -> Vector3D:
        """Get center of AABB."""
        return (self.min_point + self.max_point) * 0.5
    
    def size(self) -> Vector3D:
        """Get size of AABB."""
        return self.max_point - self.min_point
    
    def half_extents(self) -> Vector3D:
        """Get half extents of AABB."""
        return self.size() * 0.5
    
    def contains_point(self, point: Vector3D) -> bool:
        """Check if point is inside AABB."""
        return (self.min_point.x <= point.x <= self.max_point.x and
                self.min_point.y <= point.y <= self.max_point.y and
                self.min_point.z <= point.z <= self.max_point.z)
    
    def expand(self, amount: float) -> 'AABB':
        """Expand AABB by amount in all directions."""
        expansion = Vector3D(amount, amount, amount)
        return AABB(self.min_point - expansion, self.max_point + expansion)
    
    def merge(self, other: 'AABB') -> 'AABB':
        """Merge two AABBs."""
        return AABB(
            Vector3D(min(self.min_point.x, other.min_point.x),
                    min(self.min_point.y, other.min_point.y),
                    min(self.min_point.z, other.min_point.z)),
            Vector3D(max(self.max_point.x, other.max_point.x),
                    max(self.max_point.y, other.max_point.y),
                    max(self.max_point.z, other.max_point.z))
        )
    
    def intersects(self, other: 'AABB') -> bool:
        """Check if two AABBs intersect."""
        return (self.min_point.x <= other.max_point.x and
                self.max_point.x >= other.min_point.x and
                self.min_point.y <= other.max_point.y and
                self.max_point.y >= other.min_point.y and
                self.min_point.z <= other.max_point.z and
                self.max_point.z >= other.min_point.z)
    
    def intersection(self, other: 'AABB') -> Optional['AABB']:
        """Get intersection of two AABBs."""
        if not self.intersects(other):
            return None
        
        return AABB(
            Vector3D(max(self.min_point.x, other.min_point.x),
                    max(self.min_point.y, other.min_point.y),
                    max(self.min_point.z, other.min_point.z)),
            Vector3D(min(self.max_point.x, other.max_point.x),
                    min(self.max_point.y, other.max_point.y),
                    min(self.max_point.z, other.max_point.z))
        )
    
    def closest_point(self, point: Vector3D) -> Vector3D:
        """Get closest point on AABB to given point."""
        return Vector3D(
            np.clip(point.x, self.min_point.x, self.max_point.x),
            np.clip(point.y, self.min_point.y, self.max_point.y),
            np.clip(point.z, self.min_point.z, self.max_point.z)
        )


@dataclass
class OBB:
    """Oriented Bounding Box."""
    center: Vector3D
    half_extents: Vector3D
    orientation: Matrix4x4  # Rotation matrix
    
    def get_axes(self) -> Tuple[Vector3D, Vector3D, Vector3D]:
        """Get local axes of OBB."""
        return (
            Vector3D.from_array(self.orientation.matrix[:3, 0]),
            Vector3D.from_array(self.orientation.matrix[:3, 1]),
            Vector3D.from_array(self.orientation.matrix[:3, 2])
        )
    
    def get_corners(self) -> List[Vector3D]:
        """Get all 8 corners of OBB."""
        axes = self.get_axes()
        corners = []
        
        for sx in [-1, 1]:
            for sy in [-1, 1]:
                for sz in [-1, 1]:
                    corner = self.center
                    corner = corner + axes[0] * (self.half_extents.x * sx)
                    corner = corner + axes[1] * (self.half_extents.y * sy)
                    corner = corner + axes[2] * (self.half_extents.z * sz)
                    corners.append(corner)
        
        return corners
    
    def contains_point(self, point: Vector3D) -> bool:
        """Check if point is inside OBB."""
        # Transform point to OBB local space
        local_point = self.orientation.inverse().transform_point(point - self.center)
        
        return (abs(local_point.x) <= self.half_extents.x and
                abs(local_point.y) <= self.half_extents.y and
                abs(local_point.z) <= self.half_extents.z)
    
    def closest_point(self, point: Vector3D) -> Vector3D:
        """Get closest point on OBB to given point."""
        # Transform to local space
        local_point = self.orientation.inverse().transform_point(point - self.center)
        
        # Clamp to box
        clamped = Vector3D(
            np.clip(local_point.x, -self.half_extents.x, self.half_extents.x),
            np.clip(local_point.y, -self.half_extents.y, self.half_extents.y),
            np.clip(local_point.z, -self.half_extents.z, self.half_extents.z)
        )
        
        # Transform back to world space
        return self.orientation.transform_point(clamped) + self.center


@dataclass
class Sphere:
    """Sphere collision shape."""
    center: Vector3D
    radius: float
    
    def contains_point(self, point: Vector3D) -> bool:
        """Check if point is inside sphere."""
        return self.center.distance_to(point) <= self.radius
    
    def intersects(self, other: 'Sphere') -> bool:
        """Check if two spheres intersect."""
        return SpatialUtils.sphere_sphere_intersection(
            self.center, self.radius, other.center, other.radius
        )
    
    def closest_point(self, point: Vector3D) -> Vector3D:
        """Get closest point on sphere to given point."""
        direction = (point - self.center).normalize()
        return self.center + direction * self.radius


@dataclass
class Capsule:
    """Capsule collision shape."""
    start: Vector3D
    end: Vector3D
    radius: float
    
    def contains_point(self, point: Vector3D) -> bool:
        """Check if point is inside capsule."""
        closest = SpatialUtils.closest_point_on_line_segment(point, self.start, self.end)
        return point.distance_to(closest) <= self.radius
    
    def closest_point(self, point: Vector3D) -> Vector3D:
        """Get closest point on capsule to given point."""
        closest_on_line = SpatialUtils.closest_point_on_line_segment(
            point, self.start, self.end
        )
        direction = (point - closest_on_line).normalize()
        return closest_on_line + direction * self.radius


@dataclass
class Ray:
    """Ray for casting."""
    origin: Vector3D
    direction: Vector3D  # Should be normalized
    
    def point_at(self, t: float) -> Vector3D:
        """Get point along ray at distance t."""
        return self.origin + self.direction * t


class CollisionDetection:
    """Collection of collision detection algorithms."""
    
    @staticmethod
    def aabb_aabb(a: AABB, b: AABB) -> bool:
        """Check collision between two AABBs."""
        return a.intersects(b)
    
    @staticmethod
    def sphere_sphere(a: Sphere, b: Sphere) -> bool:
        """Check collision between two spheres."""
        return a.intersects(b)
    
    @staticmethod
    def aabb_sphere(box: AABB, sphere: Sphere) -> bool:
        """Check collision between AABB and sphere."""
        closest = box.closest_point(sphere.center)
        return sphere.center.distance_to(closest) <= sphere.radius
    
    @staticmethod
    def obb_obb(a: OBB, b: OBB) -> bool:
        """Check collision between two OBBs using SAT."""
        # Get axes from both OBBs
        axes_a = list(a.get_axes())
        axes_b = list(b.get_axes())
        
        # Also test cross products of axes
        test_axes = axes_a + axes_b
        for i in range(3):
            for j in range(3):
                cross = axes_a[i].cross(axes_b[j])
                if cross.magnitude() > 1e-6:
                    test_axes.append(cross.normalize())
        
        # Separating Axis Test
        for axis in test_axes:
            # Project both OBBs onto axis
            min_a, max_a = CollisionDetection._project_obb_on_axis(a, axis)
            min_b, max_b = CollisionDetection._project_obb_on_axis(b, axis)
            
            # Check for separation
            if max_a < min_b or max_b < min_a:
                return False
        
        return True
    
    @staticmethod
    def _project_obb_on_axis(obb: OBB, axis: Vector3D) -> Tuple[float, float]:
        """Project OBB onto axis and return min/max values."""
        corners = obb.get_corners()
        projections = [corner.dot(axis) for corner in corners]
        return min(projections), max(projections)
    
    @staticmethod
    def obb_sphere(box: OBB, sphere: Sphere) -> bool:
        """Check collision between OBB and sphere."""
        closest = box.closest_point(sphere.center)
        return sphere.center.distance_to(closest) <= sphere.radius
    
    @staticmethod
    def capsule_capsule(a: Capsule, b: Capsule) -> bool:
        """Check collision between two capsules."""
        # Find closest points between line segments
        closest_a, closest_b = SpatialUtils.closest_points_between_lines(
            a.start, a.end, b.start, b.end
        )
        
        # Check if distance is less than sum of radii
        return closest_a.distance_to(closest_b) <= a.radius + b.radius
    
    @staticmethod
    def capsule_sphere(capsule: Capsule, sphere: Sphere) -> bool:
        """Check collision between capsule and sphere."""
        closest = SpatialUtils.closest_point_on_line_segment(
            sphere.center, capsule.start, capsule.end
        )
        return sphere.center.distance_to(closest) <= capsule.radius + sphere.radius
    
    @staticmethod
    def ray_aabb(ray: Ray, box: AABB) -> Optional[float]:
        """Ray-AABB intersection test. Returns distance to intersection."""
        inv_dir = Vector3D(
            1.0 / ray.direction.x if abs(ray.direction.x) > 1e-10 else float('inf'),
            1.0 / ray.direction.y if abs(ray.direction.y) > 1e-10 else float('inf'),
            1.0 / ray.direction.z if abs(ray.direction.z) > 1e-10 else float('inf')
        )
        
        t1 = (box.min_point.x - ray.origin.x) * inv_dir.x
        t2 = (box.max_point.x - ray.origin.x) * inv_dir.x
        t3 = (box.min_point.y - ray.origin.y) * inv_dir.y
        t4 = (box.max_point.y - ray.origin.y) * inv_dir.y
        t5 = (box.min_point.z - ray.origin.z) * inv_dir.z
        t6 = (box.max_point.z - ray.origin.z) * inv_dir.z
        
        tmin = max(min(t1, t2), min(t3, t4), min(t5, t6))
        tmax = min(max(t1, t2), max(t3, t4), max(t5, t6))
        
        if tmax < 0 or tmin > tmax:
            return None
        
        return tmin if tmin >= 0 else tmax
    
    @staticmethod
    def ray_sphere(ray: Ray, sphere: Sphere) -> Optional[float]:
        """Ray-sphere intersection test. Returns distance to intersection."""
        result = SpatialUtils.ray_sphere_intersection(
            ray.origin, ray.direction, sphere.center, sphere.radius
        )
        
        if result is None:
            return None
        
        t1, t2 = result
        if t1 >= 0:
            return t1
        elif t2 >= 0:
            return t2
        else:
            return None
    
    @staticmethod
    def ray_obb(ray: Ray, box: OBB) -> Optional[float]:
        """Ray-OBB intersection test. Returns distance to intersection."""
        # Transform ray to OBB local space
        local_origin = box.orientation.inverse().transform_point(ray.origin - box.center)
        local_direction = box.orientation.inverse().transform_direction(ray.direction)
        
        # Create local AABB
        local_aabb = AABB(-box.half_extents, box.half_extents)
        local_ray = Ray(local_origin, local_direction.normalize())
        
        # Test against local AABB
        return CollisionDetection.ray_aabb(local_ray, local_aabb)


class SweepTest:
    """Swept collision detection for moving objects."""
    
    @staticmethod
    def sphere_sphere_sweep(a: Sphere, velocity_a: Vector3D,
                           b: Sphere, velocity_b: Vector3D,
                           max_time: float = 1.0) -> Optional[float]:
        """Find time of impact between two moving spheres."""
        # Relative motion
        rel_velocity = velocity_a - velocity_b
        rel_position = a.center - b.center
        min_dist = a.radius + b.radius
        
        # Solve quadratic equation
        a_coef = rel_velocity.magnitude_squared()
        b_coef = 2 * rel_position.dot(rel_velocity)
        c_coef = rel_position.magnitude_squared() - min_dist * min_dist
        
        if abs(a_coef) < 1e-10:
            # No relative motion
            if c_coef <= 0:
                return 0  # Already colliding
            else:
                return None
        
        discriminant = b_coef * b_coef - 4 * a_coef * c_coef
        if discriminant < 0:
            return None
        
        sqrt_discriminant = np.sqrt(discriminant)
        t1 = (-b_coef - sqrt_discriminant) / (2 * a_coef)
        t2 = (-b_coef + sqrt_discriminant) / (2 * a_coef)
        
        if t1 >= 0 and t1 <= max_time:
            return t1
        elif t2 >= 0 and t2 <= max_time:
            return t2
        else:
            return None
    
    @staticmethod
    def aabb_aabb_sweep(a: AABB, velocity_a: Vector3D,
                       b: AABB, velocity_b: Vector3D,
                       max_time: float = 1.0) -> Optional[float]:
        """Find time of impact between two moving AABBs."""
        # Relative velocity
        rel_velocity = velocity_a - velocity_b
        
        # Entry and exit times for each axis
        entry_time = Vector3D(float('-inf'), float('-inf'), float('-inf'))
        exit_time = Vector3D(float('inf'), float('inf'), float('inf'))
        
        # X-axis
        if abs(rel_velocity.x) < 1e-10:
            if a.max_point.x < b.min_point.x or a.min_point.x > b.max_point.x:
                return None
        else:
            t1 = (b.min_point.x - a.max_point.x) / rel_velocity.x
            t2 = (b.max_point.x - a.min_point.x) / rel_velocity.x
            entry_time.x = min(t1, t2)
            exit_time.x = max(t1, t2)
        
        # Y-axis
        if abs(rel_velocity.y) < 1e-10:
            if a.max_point.y < b.min_point.y or a.min_point.y > b.max_point.y:
                return None
        else:
            t1 = (b.min_point.y - a.max_point.y) / rel_velocity.y
            t2 = (b.max_point.y - a.min_point.y) / rel_velocity.y
            entry_time.y = min(t1, t2)
            exit_time.y = max(t1, t2)
        
        # Z-axis
        if abs(rel_velocity.z) < 1e-10:
            if a.max_point.z < b.min_point.z or a.min_point.z > b.max_point.z:
                return None
        else:
            t1 = (b.min_point.z - a.max_point.z) / rel_velocity.z
            t2 = (b.max_point.z - a.min_point.z) / rel_velocity.z
            entry_time.z = min(t1, t2)
            exit_time.z = max(t1, t2)
        
        # Find overall entry and exit times
        entry = max(entry_time.x, entry_time.y, entry_time.z)
        exit = min(exit_time.x, exit_time.y, exit_time.z)
        
        if entry > exit or entry > max_time or exit < 0:
            return None
        
        return max(0, entry)


class SpatialGrid:
    """Spatial grid for broad-phase collision detection."""
    
    def __init__(self, cell_size: float, bounds: AABB):
        """Initialize spatial grid."""
        self.cell_size = cell_size
        self.bounds = bounds
        self.grid = {}  # Dict mapping cell coordinates to object sets
        
        # Calculate grid dimensions
        size = bounds.size()
        self.grid_size = Vector3D(
            int(np.ceil(size.x / cell_size)),
            int(np.ceil(size.y / cell_size)),
            int(np.ceil(size.z / cell_size))
        )
    
    def _get_cell_coords(self, position: Vector3D) -> Tuple[int, int, int]:
        """Get grid cell coordinates for position."""
        relative = position - self.bounds.min_point
        return (
            int(relative.x / self.cell_size),
            int(relative.y / self.cell_size),
            int(relative.z / self.cell_size)
        )
    
    def _get_cells_for_aabb(self, aabb: AABB) -> List[Tuple[int, int, int]]:
        """Get all cells that AABB overlaps."""
        min_cell = self._get_cell_coords(aabb.min_point)
        max_cell = self._get_cell_coords(aabb.max_point)
        
        cells = []
        for x in range(min_cell[0], max_cell[0] + 1):
            for y in range(min_cell[1], max_cell[1] + 1):
                for z in range(min_cell[2], max_cell[2] + 1):
                    if 0 <= x < self.grid_size.x and \
                       0 <= y < self.grid_size.y and \
                       0 <= z < self.grid_size.z:
                        cells.append((x, y, z))
        
        return cells
    
    def insert(self, obj_id: int, aabb: AABB):
        """Insert object into grid."""
        cells = self._get_cells_for_aabb(aabb)
        
        for cell in cells:
            if cell not in self.grid:
                self.grid[cell] = set()
            self.grid[cell].add(obj_id)
    
    def remove(self, obj_id: int, aabb: AABB):
        """Remove object from grid."""
        cells = self._get_cells_for_aabb(aabb)
        
        for cell in cells:
            if cell in self.grid:
                self.grid[cell].discard(obj_id)
                if not self.grid[cell]:
                    del self.grid[cell]
    
    def query(self, aabb: AABB) -> Set[int]:
        """Query grid for potential collisions."""
        cells = self._get_cells_for_aabb(aabb)
        result = set()
        
        for cell in cells:
            if cell in self.grid:
                result.update(self.grid[cell])
        
        return result
    
    def clear(self):
        """Clear the grid."""
        self.grid.clear()


# Convenience functions
def create_aabb(min_point: Vector3D, max_point: Vector3D) -> AABB:
    """Create an axis-aligned bounding box."""
    return AABB(min_point, max_point)


def create_aabb_from_points(points: List[Vector3D]) -> AABB:
    """Create AABB from list of points."""
    if not points:
        return AABB(Vector3D.zero(), Vector3D.zero())
    
    min_point = Vector3D(float('inf'), float('inf'), float('inf'))
    max_point = Vector3D(float('-inf'), float('-inf'), float('-inf'))
    
    for point in points:
        min_point.x = min(min_point.x, point.x)
        min_point.y = min(min_point.y, point.y)
        min_point.z = min(min_point.z, point.z)
        max_point.x = max(max_point.x, point.x)
        max_point.y = max(max_point.y, point.y)
        max_point.z = max(max_point.z, point.z)
    
    return AABB(min_point, max_point)


def create_sphere(center: Vector3D, radius: float) -> Sphere:
    """Create a sphere collision shape."""
    return Sphere(center, radius)


def create_capsule(start: Vector3D, end: Vector3D, radius: float) -> Capsule:
    """Create a capsule collision shape."""
    return Capsule(start, end, radius)


def create_obb(center: Vector3D, half_extents: Vector3D, orientation: Matrix4x4) -> OBB:
    """Create an oriented bounding box."""
    return OBB(center, half_extents, orientation)


def create_ray(origin: Vector3D, direction: Vector3D) -> Ray:
    """Create a ray for casting."""
    return Ray(origin, direction.normalize())