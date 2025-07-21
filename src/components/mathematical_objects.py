"""Mathematical visualization objects for linear programming and geometry."""
from manim import *
from typing import List, Tuple, Optional, Callable
import numpy as np
from shapely import geometry
import math


# Constants
LINE_STROKE = 3
NORMAL_DOT_SCALE = 0.75
OPTIMUM_DOT_SCALE = 1.0


def get_infinite_square(size: float = 100) -> Square:
    """Create a large square for representing infinite planes."""
    return Square(side_length=size, fill_opacity=0.3, stroke_opacity=0)


def crop_line_to_screen(
    line_to_crop: Line,
    screen: Rectangle = None,
    buffer: float = 0
) -> None:
    """Crop a line to fit within screen boundaries."""
    if screen is None:
        screen = ScreenRectangle()
    
    # Get screen boundaries
    min_x = screen.get_left()[0] - buffer
    max_x = screen.get_right()[0] + buffer
    min_y = screen.get_bottom()[1] - buffer
    max_y = screen.get_top()[1] + buffer
    
    # Get line equation
    start = line_to_crop.get_start()
    end = line_to_crop.get_end()
    
    # Handle vertical lines
    if abs(end[0] - start[0]) < 1e-6:
        x = start[0]
        if min_x <= x <= max_x:
            line_to_crop.put_start_and_end_on(
                [x, min_y, 0],
                [x, max_y, 0]
            )
        return
    
    # Calculate line parameters
    m = (end[1] - start[1]) / (end[0] - start[0])
    b = start[1] - m * start[0]
    
    # Find intersection points
    points = []
    
    # Left boundary
    y = m * min_x + b
    if min_y <= y <= max_y:
        points.append([min_x, y, 0])
    
    # Right boundary
    y = m * max_x + b
    if min_y <= y <= max_y:
        points.append([max_x, y, 0])
    
    # Top boundary
    if m != 0:
        x = (max_y - b) / m
        if min_x <= x <= max_x:
            points.append([x, max_y, 0])
    
    # Bottom boundary
    if m != 0:
        x = (min_y - b) / m
        if min_x <= x <= max_x:
            points.append([x, min_y, 0])
    
    if len(points) >= 2:
        line_to_crop.put_start_and_end_on(points[0], points[1])


class AffineLine2D(VMobject):
    """Represents an infinite line in 2D with direction and offset."""
    
    def __init__(
        self,
        direction: Tuple[float, float],
        offset: Tuple[float, float] = (0, 0),
        length: float = 100,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.direction = direction
        
        # Create line from origin along direction
        p1 = np.array([0, 0, 0])
        p2 = np.array([*direction, 0])
        
        self.line = Line(
            p1, p2,
            color=WHITE,
            stroke_width=LINE_STROKE
        ).scale(length / np.linalg.norm(p2 - p1)).move_to((*offset, 0))
        
        self.add(self.line)
    
    def crop_to_screen(self, screen: Rectangle = None, buffer: float = 0) -> None:
        """Crop the line to screen boundaries."""
        crop_line_to_screen(self.line, screen, buffer)
    
    def get_area_border_intersection(self, area: 'FeasibleArea2D') -> VGroup:
        """Find intersection points with feasible area borders."""
        possible_points = []
        
        # Check intersection with each inequality
        for inequality in area.inequalities:
            # Calculate intersection point
            # Using line-line intersection formula
            p1, p2 = self.line.get_start(), self.line.get_end()
            p3, p4 = inequality.line.get_start(), inequality.line.get_end()
            
            # Convert to 2D
            x1, y1 = p1[0], p1[1]
            x2, y2 = p2[0], p2[1]
            x3, y3 = p3[0], p3[1]
            x4, y4 = p4[0], p4[1]
            
            denom = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
            if abs(denom) > 1e-6:
                t = ((x1-x3)*(y3-y4) - (y1-y3)*(x3-x4)) / denom
                x = x1 + t*(x2-x1)
                y = y1 + t*(y2-y1)
                possible_points.append((x, y))
        
        # Filter points that satisfy all inequalities
        dots = VGroup()
        for point in possible_points:
            if all(ineq.satisfies(*point, epsilon=0.01) for ineq in area.inequalities):
                dot = Dot().move_to([*point, 0]).scale(OPTIMUM_DOT_SCALE)
                dots.add(dot)
        
        return dots


class Inequality2D(VMobject):
    """Represents a linear inequality in 2D: ax + by <= c."""
    
    def __init__(
        self,
        a: float,
        b: float,
        operation: str = "<=",
        c: float = 0,
        length: float = 100,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.a = a
        self.b = b
        self.operation = operation
        self.c = c
        
        # Calculate line points
        if abs(b) < 1e-6:
            # Vertical line
            x = c / a if abs(a) > 1e-6 else 0
            p1 = np.array([x, -length/2, 0])
            p2 = np.array([x, length/2, 0])
        else:
            # Non-vertical line
            # Use two points: (0, c/b) and (c/a, 0)
            x1, y1 = 0, c/b
            x2, y2 = c/a if abs(a) > 1e-6 else 1, 0 if abs(a) > 1e-6 else (c-a)/b
            
            # Extend line
            dx, dy = x2 - x1, y2 - y1
            norm = np.sqrt(dx**2 + dy**2)
            dx, dy = dx/norm * length/2, dy/norm * length/2
            
            p1 = np.array([x1 - dx, y1 - dy, 0])
            p2 = np.array([x1 + dx, y1 + dy, 0])
        
        self.line = Line(p1, p2, color=WHITE, stroke_width=LINE_STROKE)
        self.add(self.line)
        
        # Calculate angle for half-plane orientation
        center = self.line.get_center()
        direction = p2 - p1
        self.angle = np.arctan2(direction[1], direction[0]) + np.pi/2
    
    @classmethod
    def from_points(
        cls,
        p1: Tuple[float, float],
        p2: Tuple[float, float],
        operation: str = "<="
    ) -> 'Inequality2D':
        """Create inequality from two points on the line."""
        x1, y1 = p1
        x2, y2 = p2
        
        if abs(x1 - x2) < 1e-6:
            # Vertical line
            a, b = 1, 0
            c = x1
        else:
            # Non-vertical line
            a = (y2 - y1) / (x1 - x2)
            b = 1
            c = a * x1 + b * y1
        
        return cls(a, b, operation, c)
    
    def crop_to_screen(self, screen: Rectangle = None, buffer: float = 0) -> None:
        """Crop the inequality line to screen boundaries."""
        crop_line_to_screen(self.line, screen, buffer)
    
    def satisfies(self, x: float, y: float, epsilon: float = 0) -> bool:
        """Check if a point satisfies the inequality."""
        value = self.a * x + self.b * y
        if self.operation == "<=":
            return value <= self.c + epsilon
        else:
            return value >= self.c - epsilon
    
    def get_half_plane(self) -> Polygon:
        """Get the half-plane representing the feasible region."""
        half_plane = get_infinite_square()
        half_plane.set_color(self.get_color())
        
        # Position half-plane on correct side of line
        half_plane.move_to(self.line)
        normal = np.array([self.a, self.b, 0])
        normal = normal / np.linalg.norm(normal)
        
        # Check which side is feasible
        test_point = self.line.get_center() + normal * 0.1
        if not self.satisfies(test_point[0], test_point[1]):
            normal = -normal
        
        half_plane.shift(normal * half_plane.width/2)
        return half_plane


class FeasibleArea2D(VMobject):
    """Represents the feasible region for a 2D linear program."""
    
    def __init__(
        self,
        fill_opacity: float = 0.3,
        stroke_width: float = 0,
        dots_z_index: float = 1000,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.inequalities: List[Inequality2D] = []
        self.dots = VGroup()  # Corner points
        self.dots_z_index = dots_z_index
        
        # Start with infinite area
        self.area = get_infinite_square()
        self.area.set_fill_opacity(fill_opacity)
        self.area.set_stroke_width(stroke_width)
        
        self.add(self.area, self.dots)
    
    def add_inequality(self, inequality: Inequality2D) -> None:
        """Add a single inequality to the feasible region."""
        self.inequalities.append(inequality)
        self._update_area()
    
    def add_inequalities(self, inequalities: List[Inequality2D]) -> None:
        """Add multiple inequalities to the feasible region."""
        self.inequalities.extend(inequalities)
        self._update_area()
    
    def remove_inequality(self, inequality: Inequality2D) -> None:
        """Remove an inequality from the feasible region."""
        if inequality in self.inequalities:
            self.inequalities.remove(inequality)
            self._update_area()
    
    def clear_inequalities(self) -> None:
        """Remove all inequalities."""
        self.inequalities.clear()
        self._update_area()
    
    def _update_area(self) -> None:
        """Update the feasible area based on current inequalities."""
        # Start with infinite area
        new_area = get_infinite_square()
        new_area.set_color(self.area.get_color())
        new_area.set_fill_opacity(self.area.get_fill_opacity())
        new_area.set_stroke_width(self.area.get_stroke_width())
        
        # Intersect with each half-plane
        for inequality in self.inequalities:
            half_plane = inequality.get_half_plane()
            new_area = Intersection(
                new_area,
                half_plane,
                color=new_area.get_color(),
                fill_opacity=new_area.get_fill_opacity(),
                stroke_width=new_area.get_stroke_width()
            )
        
        self.area.become(new_area)
        
        # Update corner points
        self._update_corner_points()
    
    def _update_corner_points(self) -> None:
        """Find and update corner points of the feasible region."""
        possible_points = []
        
        # Find all intersection points
        n = len(self.inequalities)
        for i in range(n):
            for j in range(i + 1, n):
                # Calculate intersection of two lines
                ineq1, ineq2 = self.inequalities[i], self.inequalities[j]
                
                # Solve system: a1*x + b1*y = c1, a2*x + b2*y = c2
                det = ineq1.a * ineq2.b - ineq1.b * ineq2.a
                if abs(det) > 1e-6:
                    x = (ineq1.c * ineq2.b - ineq1.b * ineq2.c) / det
                    y = (ineq1.a * ineq2.c - ineq1.c * ineq2.a) / det
                    possible_points.append((x, y))
        
        # Filter points that satisfy all inequalities
        new_dots = VGroup()
        for point in possible_points:
            if all(ineq.satisfies(*point, epsilon=0.01) for ineq in self.inequalities):
                dot = Dot().move_to([*point, 0]).scale(NORMAL_DOT_SCALE)
                new_dots.add(dot)
        
        self.dots.become(new_dots).set_z_index(self.dots_z_index)
    
    def get_vertices(self) -> List[np.ndarray]:
        """Get the vertices of the feasible region."""
        return [dot.get_center() for dot in self.dots]
    
    def get_optimal_point(
        self,
        objective_direction: Tuple[float, float]
    ) -> Optional[np.ndarray]:
        """Find the optimal point for a given objective direction."""
        vertices = self.get_vertices()
        if not vertices:
            return None
        
        # Maximize objective_direction · vertex
        best_vertex = None
        best_value = -float('inf')
        
        for vertex in vertices:
            value = objective_direction[0] * vertex[0] + objective_direction[1] * vertex[1]
            if value > best_value:
                best_value = value
                best_vertex = vertex
        
        return best_vertex