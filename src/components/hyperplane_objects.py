"""Hyperplane visualization objects for Manim Studio."""

from manim import *
import numpy as np
from typing import List, Tuple, Optional, Union
from ..utils.math3d.hyperplane import Hyperplane, HyperplaneRegion
from ..utils.math3d.vector3d import Vector3D


class HyperplaneVisualization2D(VMobject):
    """2D hyperplane (line) visualization with support regions and classification."""
    
    def __init__(
        self,
        hyperplane: Hyperplane,
        length: float = 20,
        show_normal: bool = True,
        show_positive_region: bool = False,
        show_negative_region: bool = False,
        line_color: ManimColor = WHITE,
        normal_color: ManimColor = YELLOW,
        positive_region_color: ManimColor = GREEN,
        negative_region_color: ManimColor = RED,
        region_opacity: float = 0.3,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        if hyperplane.dimension != 2:
            raise ValueError("HyperplaneVisualization2D only works with 2D hyperplanes")
        
        self.hyperplane = hyperplane
        self.length = length
        
        # Create the line
        self.line = self._create_line(line_color)
        self.add(self.line)
        
        # Create normal vector arrow
        if show_normal:
            self.normal_arrow = self._create_normal_arrow(normal_color)
            self.add(self.normal_arrow)
        
        # Create region fills
        if show_positive_region:
            self.positive_region = self._create_half_plane(1, positive_region_color, region_opacity)
            self.add(self.positive_region)
        
        if show_negative_region:
            self.negative_region = self._create_half_plane(-1, negative_region_color, region_opacity)
            self.add(self.negative_region)
    
    def _create_line(self, color: ManimColor) -> Line:
        """Create the hyperplane line."""
        a, b = self.hyperplane.normal
        c = self.hyperplane.bias
        
        if abs(b) < 1e-6:
            # Vertical line: x = -c/a
            x = -c / a if abs(a) > 1e-6 else 0
            start = np.array([x, -self.length/2, 0])
            end = np.array([x, self.length/2, 0])
        else:
            # Non-vertical line: solve for two points
            # At x = -length/2: y = (-c - a*(-length/2))/b
            x1 = -self.length/2
            y1 = (-c - a * x1) / b
            
            # At x = length/2: y = (-c - a*(length/2))/b
            x2 = self.length/2
            y2 = (-c - a * x2) / b
            
            start = np.array([x1, y1, 0])
            end = np.array([x2, y2, 0])
        
        return Line(start, end, color=color, stroke_width=3)
    
    def _create_normal_arrow(self, color: ManimColor) -> Arrow:
        """Create normal vector arrow."""
        # Place arrow at center of line
        center = self.line.get_center()
        
        # Normal direction
        normal_2d = self.hyperplane.normal
        arrow_end = center + np.array([normal_2d[0], normal_2d[1], 0])
        
        return Arrow(center, arrow_end, color=color, buff=0)
    
    def _create_half_plane(self, sign: int, color: ManimColor, opacity: float) -> Polygon:
        """Create half-plane region (sign: 1 for positive, -1 for negative)."""
        # Create large rectangle for the half-plane
        size = 50
        
        # Get line center and normal
        center = self.line.get_center()[:2]  # 2D center
        normal = self.hyperplane.normal * sign
        
        # Create rectangle vertices
        vertices = []
        
        # Extend in normal direction
        offset = normal * size
        base_center = center + offset
        
        # Create rectangle around the offset center
        vertices = [
            [base_center[0] - size, base_center[1] - size, 0],
            [base_center[0] + size, base_center[1] - size, 0],
            [base_center[0] + size, base_center[1] + size, 0],
            [base_center[0] - size, base_center[1] + size, 0],
        ]
        
        half_plane = Polygon(*vertices, fill_opacity=opacity, color=color, stroke_width=0)
        half_plane.set_z_index(-1)  # Behind other objects
        
        return half_plane
    
    def add_classification_points(self, points: List[Tuple[float, float]], 
                                 point_colors: List[ManimColor] = None) -> VGroup:
        """Add classified points to the visualization."""
        if point_colors is None:
            point_colors = [GREEN if self.hyperplane.classify_point(p) > 0 else RED for p in points]
        
        dots = VGroup()
        for i, (point, color) in enumerate(zip(points, point_colors)):
            dot = Dot(point=[point[0], point[1], 0], color=color)
            dots.add(dot)
        
        self.add(dots)
        return dots
    
    def get_distance_line(self, point: Tuple[float, float], 
                         color: ManimColor = BLUE) -> VGroup:
        """Create line showing distance from point to hyperplane."""
        point_3d = np.array([point[0], point[1], 0])
        projected = self.hyperplane.project_point(point)
        projected_3d = np.array([projected[0], projected[1], 0])
        
        distance_line = Line(point_3d, projected_3d, color=color, stroke_width=2)
        distance_dot = Dot(projected_3d, color=color, radius=0.05)
        
        return VGroup(distance_line, distance_dot)


class HyperplaneVisualization3D(VMobject):
    """3D hyperplane (plane) visualization."""
    
    def __init__(
        self,
        hyperplane: Hyperplane,
        size: float = 10,
        resolution: Tuple[int, int] = (20, 20),
        show_normal: bool = True,
        plane_color: ManimColor = BLUE,
        normal_color: ManimColor = YELLOW,
        plane_opacity: float = 0.5,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        if hyperplane.dimension != 3:
            raise ValueError("HyperplaneVisualization3D only works with 3D hyperplanes")
        
        self.hyperplane = hyperplane
        self.size = size
        
        # Create the plane surface
        self.plane_surface = self._create_plane_surface(plane_color, plane_opacity, resolution)
        self.add(self.plane_surface)
        
        # Create normal vector arrow
        if show_normal:
            self.normal_arrow = self._create_normal_arrow(normal_color)
            self.add(self.normal_arrow)
    
    def _create_plane_surface(self, color: ManimColor, opacity: float, 
                            resolution: Tuple[int, int]) -> Surface:
        """Create 3D plane surface."""
        # Find two orthogonal vectors in the plane
        normal = self.hyperplane.normal
        
        # Find first tangent vector
        if abs(normal[0]) < 0.9:
            tangent1 = np.array([1, 0, 0])
        else:
            tangent1 = np.array([0, 1, 0])
        
        # Make orthogonal to normal
        tangent1 = tangent1 - np.dot(tangent1, normal) * normal
        tangent1 = tangent1 / np.linalg.norm(tangent1)
        
        # Second tangent vector
        tangent2 = np.cross(normal, tangent1)
        
        # Point on plane (closest to origin)
        plane_center = -self.hyperplane.bias * normal
        
        def plane_func(u, v):
            point = (plane_center + 
                    u * self.size * tangent1 + 
                    v * self.size * tangent2)
            return point
        
        surface = Surface(
            plane_func,
            u_range=[-1, 1],
            v_range=[-1, 1],
            resolution=resolution,
            fill_color=color,
            fill_opacity=opacity
        )
        
        return surface
    
    def _create_normal_arrow(self, color: ManimColor) -> Arrow3D:
        """Create 3D normal vector arrow."""
        # Place at plane center
        plane_center = -self.hyperplane.bias * self.hyperplane.normal
        arrow_end = plane_center + self.hyperplane.normal * 2
        
        return Arrow3D(
            start=plane_center,
            end=arrow_end,
            color=color
        )
    
    def add_classification_points(self, points: List[Tuple[float, float, float]], 
                                 point_colors: List[ManimColor] = None) -> VGroup:
        """Add 3D classified points to the visualization."""
        if point_colors is None:
            point_colors = [GREEN if self.hyperplane.classify_point(p) > 0 else RED for p in points]
        
        dots = VGroup()
        for point, color in zip(points, point_colors):
            dot = Dot3D(point=point, color=color)
            dots.add(dot)
        
        self.add(dots)
        return dots


class SVMVisualization2D(HyperplaneVisualization2D):
    """Specialized visualization for SVM decision boundaries."""
    
    def __init__(
        self,
        decision_hyperplane: Hyperplane,
        margin: float = 1.0,
        show_support_vectors: bool = True,
        show_margin_lines: bool = True,
        support_vector_color: ManimColor = ORANGE,
        margin_line_color: ManimColor = GRAY,
        **kwargs
    ):
        super().__init__(
            decision_hyperplane,
            show_positive_region=True,
            show_negative_region=True,
            **kwargs
        )
        
        self.margin = margin
        
        # Add margin lines
        if show_margin_lines:
            self.margin_lines = self._create_margin_lines(margin_line_color)
            self.add(self.margin_lines)
    
    def _create_margin_lines(self, color: ManimColor) -> VGroup:
        """Create SVM margin boundary lines."""
        # Create hyperplanes at ±margin distance
        positive_margin = self.hyperplane.get_parallel_hyperplane(-self.margin)
        negative_margin = self.hyperplane.get_parallel_hyperplane(self.margin)
        
        # Create line visualizations
        pos_line = HyperplaneVisualization2D(
            positive_margin, 
            length=self.length,
            show_normal=False,
            line_color=color
        ).line
        
        neg_line = HyperplaneVisualization2D(
            negative_margin,
            length=self.length,
            show_normal=False,
            line_color=color
        ).line
        
        # Make them dashed
        pos_line.set_style(stroke_width=2, stroke_opacity=0.7)
        neg_line.set_style(stroke_width=2, stroke_opacity=0.7)
        
        return VGroup(pos_line, neg_line)
    
    def add_support_vectors(self, support_points: List[Tuple[float, float]], 
                          support_vector_color: ManimColor = ORANGE) -> VGroup:
        """Add support vector points with special highlighting."""
        dots = VGroup()
        for point in support_points:
            # Create larger, highlighted dot for support vectors
            dot = Dot(
                point=[point[0], point[1], 0], 
                color=support_vector_color,
                radius=0.08
            )
            
            # Add circle around support vector
            circle = Circle(
                radius=0.12,
                color=support_vector_color,
                stroke_width=2
            ).move_to(dot)
            
            dots.add(VGroup(dot, circle))
        
        self.add(dots)
        return dots


class HyperplaneRegionVisualization2D(VMobject):
    """Visualization for regions defined by multiple hyperplanes (polytopes)."""
    
    def __init__(
        self,
        region: HyperplaneRegion,
        show_hyperplanes: bool = True,
        show_region: bool = True,
        show_vertices: bool = True,
        region_color: ManimColor = BLUE,
        region_opacity: float = 0.3,
        vertex_color: ManimColor = RED,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        if region.dimension != 2:
            raise ValueError("HyperplaneRegionVisualization2D only works with 2D regions")
        
        self.region = region
        
        # Add hyperplane lines
        if show_hyperplanes:
            self.hyperplane_lines = VGroup()
            for hyperplane in region.hyperplanes:
                line_viz = HyperplaneVisualization2D(
                    hyperplane,
                    show_normal=False,
                    line_color=WHITE
                )
                self.hyperplane_lines.add(line_viz.line)
            self.add(self.hyperplane_lines)
        
        # Add feasible region
        if show_region:
            self.region_fill = self._create_region_fill(region_color, region_opacity)
            if self.region_fill:
                self.add(self.region_fill)
        
        # Add vertices
        if show_vertices:
            self.vertex_dots = self._create_vertex_dots(vertex_color)
            if self.vertex_dots:
                self.add(self.vertex_dots)
    
    def _create_region_fill(self, color: ManimColor, opacity: float) -> Optional[Polygon]:
        """Create filled polygon for the feasible region."""
        try:
            vertices = self.region.get_vertices()
            if len(vertices) < 3:
                return None
            
            # Sort vertices in counterclockwise order
            center = np.mean(vertices, axis=0)
            angles = [np.arctan2(v[1] - center[1], v[0] - center[0]) for v in vertices]
            sorted_vertices = [v for _, v in sorted(zip(angles, vertices))]
            
            # Convert to 3D points for Manim
            points_3d = [[v[0], v[1], 0] for v in sorted_vertices]
            
            return Polygon(
                *points_3d,
                fill_color=color,
                fill_opacity=opacity,
                stroke_width=0
            )
            
        except (NotImplementedError, np.linalg.LinAlgError):
            return None
    
    def _create_vertex_dots(self, color: ManimColor) -> Optional[VGroup]:
        """Create dots at region vertices."""
        try:
            vertices = self.region.get_vertices()
            if not vertices:
                return None
            
            dots = VGroup()
            for vertex in vertices:
                dot = Dot(
                    point=[vertex[0], vertex[1], 0],
                    color=color,
                    radius=0.06
                )
                dots.add(dot)
            
            return dots
            
        except (NotImplementedError, np.linalg.LinAlgError):
            return None


# Convenience functions for quick visualization creation
def visualize_hyperplane_2d(hyperplane: Hyperplane, **kwargs) -> HyperplaneVisualization2D:
    """Create 2D hyperplane visualization."""
    return HyperplaneVisualization2D(hyperplane, **kwargs)


def visualize_hyperplane_3d(hyperplane: Hyperplane, **kwargs) -> HyperplaneVisualization3D:
    """Create 3D hyperplane visualization.""" 
    return HyperplaneVisualization3D(hyperplane, **kwargs)


def visualize_svm_2d(decision_boundary: Hyperplane, margin: float = 1.0, **kwargs) -> SVMVisualization2D:
    """Create SVM decision boundary visualization."""
    return SVMVisualization2D(decision_boundary, margin=margin, **kwargs)


def visualize_polytope_2d(region: HyperplaneRegion, **kwargs) -> HyperplaneRegionVisualization2D:
    """Create 2D polytope visualization."""
    return HyperplaneRegionVisualization2D(region, **kwargs)


# Integration helpers for creating hyperplanes from existing mathematical objects
def hyperplane_from_inequality_2d(inequality) -> Hyperplane:
    """Convert Inequality2D object to Hyperplane."""
    # Assuming inequality has a, b, c attributes representing ax + by <= c
    # Convert to hyperplane form: ax + by - c = 0
    from ..utils.math3d.hyperplane import Hyperplane
    return Hyperplane([inequality.a, inequality.b], -inequality.c)


def hyperplane_region_from_feasible_area(feasible_area) -> HyperplaneRegion:
    """Convert FeasibleArea2D to HyperplaneRegion."""
    hyperplanes = []
    for inequality in feasible_area.inequalities:
        hyperplane = hyperplane_from_inequality_2d(inequality)
        hyperplanes.append(hyperplane)
    
    return HyperplaneRegion(hyperplanes)