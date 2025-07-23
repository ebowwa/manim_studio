from src.config.manim_config import config
import pytest
import numpy as np
from manim import *
from src.components.cad_objects import (
    RoundCorners, ChamferCorners, LinearDimension, AngularDimension,
    PointerLabel, HatchPattern, DashedLine, PathMapper, CADArrowHead,
    angle_between_vectors_signed, create_cad_object
)
from src.components.effects.cad_effects import (
    RoundCornersEffect, ChamferCornersEffect, HatchFillEffect,
    DashedOutlineEffect, TechnicalDrawingEffect
)


class TestCADUtilities:
    """Test CAD utility functions"""
    
    def test_angle_between_vectors_signed(self):
        """Test signed angle calculation"""
        v1 = np.array([1, 0, 0])
        v2 = np.array([0, 1, 0])
        angle = angle_between_vectors_signed(v1, v2)
        assert np.isclose(angle, PI / 2)
        
        # Test negative angle
        v3 = np.array([0, -1, 0])
        angle2 = angle_between_vectors_signed(v1, v3)
        assert np.isclose(angle2, -PI / 2)
        
        # Test same direction
        angle3 = angle_between_vectors_signed(v1, v1)
        assert np.isclose(angle3, 0)


class TestCornerModifications:
    """Test corner rounding and chamfering"""
    
    def test_round_corners_square(self):
        """Test rounding corners on a square"""
        square = Square(side_length=2)
        original_num_curves = square.get_num_curves()
        
        rounded = RoundCorners.apply(square, radius=0.2)
        
        # Should have more curves after rounding
        assert rounded.get_num_curves() > original_num_curves
        
        # Should still be a VMobject
        assert isinstance(rounded, VMobject)
    
    def test_chamfer_corners_triangle(self):
        """Test chamfering corners on a triangle"""
        triangle = Triangle()
        original_num_curves = triangle.get_num_curves()
        
        chamfered = ChamferCorners.apply(triangle, offset=0.2)
        
        # Should have more curves after chamfering
        assert chamfered.get_num_curves() > original_num_curves
        
        # Should still be a VMobject
        assert isinstance(chamfered, VMobject)
    
    def test_round_corners_with_zero_radius(self):
        """Test that zero radius doesn't modify shape"""
        square = Square()
        original_points = square.points.copy()
        
        rounded = RoundCorners.apply(square, radius=0)
        
        # Points should be very close to original
        assert np.allclose(rounded.points, original_points, atol=1e-6)


class TestDimensions:
    """Test dimension objects"""
    
    def test_linear_dimension_creation(self):
        """Test creating a linear dimension"""
        dim = LinearDimension(
            start=np.array([-2, 0, 0]),
            end=np.array([2, 0, 0]),
            text="4.00",
            offset=1
        )
        
        # Should be a VDict with multiple components
        assert isinstance(dim, VDict)
        assert len(dim) > 0
        
        # Should have main line and arrows
        assert any("line" in str(k).lower() for k in dim.keys())
    
    def test_angular_dimension_creation(self):
        """Test creating an angular dimension"""
        dim = AngularDimension(
            start=np.array([1, 0, 0]),
            end=np.array([0, 1, 0]),
            arc_center=np.array([0, 0, 0]),
            text="90°"
        )
        
        # Should be a VDict with arc
        assert isinstance(dim, VDict)
        assert any("arc" in str(k).lower() for k in dim.keys())
    
    def test_pointer_label_creation(self):
        """Test creating a pointer label"""
        pointer = PointerLabel(
            point=np.array([1, 1, 0]),
            text="Point A",
            offset_vector=np.array([1, 1, 0])
        )
        
        # Should have text and line components
        assert isinstance(pointer, VDict)
        assert len(pointer) >= 2


class TestHatchPattern:
    """Test hatching patterns"""
    
    def test_hatch_pattern_circle(self):
        """Test creating hatch pattern in a circle"""
        circle = Circle(radius=2)
        hatch = HatchPattern(circle, angle=PI / 4, spacing=0.3)
        
        # Should be a VGroup with lines
        assert isinstance(hatch, VGroup)
        assert len(hatch) > 0
        
        # All elements should be lines
        for elem in hatch:
            assert isinstance(elem, Line)
    
    def test_hatch_pattern_square(self):
        """Test creating hatch pattern in a square"""
        square = Square(side_length=3)
        hatch = HatchPattern(square, angle=0, spacing=0.2)
        
        # Should create horizontal lines
        assert isinstance(hatch, VGroup)
        assert len(hatch) > 0
        
        # Check that lines are roughly horizontal
        for line in hatch:
            start_y = line.get_start()[1]
            end_y = line.get_end()[1]
            assert np.isclose(start_y, end_y, atol=1e-6)


class TestPathMapper:
    """Test path mapping utilities"""
    
    def test_path_mapper_circle(self):
        """Test path mapper on a circle"""
        circle = Circle(radius=2)
        mapper = PathMapper(circle)
        
        # Should calculate correct path length
        expected_length = 2 * PI * 2  # circumference
        assert np.isclose(mapper.get_path_length(), expected_length, rtol=0.1)
        
        # Test point from proportion
        point_at_quarter = mapper.point_from_proportion(0.25)
        assert np.isclose(np.linalg.norm(point_at_quarter), 2, atol=0.1)
    
    def test_path_mapper_line(self):
        """Test path mapper on a line"""
        line = Line(start=[-2, 0, 0], end=[2, 0, 0])
        mapper = PathMapper(line)
        
        # Should calculate correct length
        assert np.isclose(mapper.get_path_length(), 4, atol=0.1)
        
        # Test midpoint
        midpoint = mapper.point_from_proportion(0.5)
        assert np.allclose(midpoint, [0, 0, 0], atol=0.1)
    
    def test_equalized_rate_function(self):
        """Test rate function equalization"""
        # Create a path with non-uniform parametrization
        arc = Arc(radius=2, angle=PI)
        mapper = PathMapper(arc)
        
        # Create equalized rate function
        eq_func = mapper.equalize_rate_func(smooth)
        
        # Test that it returns values in [0, 1]
        for t in np.linspace(0, 1, 10):
            val = eq_func(t)
            assert 0 <= val <= 1


class TestDashedLine:
    """Test dashed line creation"""
    
    def test_dashed_line_circle(self):
        """Test creating dashed circle"""
        circle = Circle(radius=2)
        dashed = DashedLine(circle, num_dashes=12, dashed_ratio=0.5)
        
        # Should be a VDict with dashes
        assert isinstance(dashed, VDict)
        assert len(dashed) > 0
        
        # Should have multiple dash segments
        dashes = list(dashed.values())[0]
        assert isinstance(dashes, VGroup)
        assert len(dashes) > 1
    
    def test_dashed_line_custom_pattern(self):
        """Test dashed line with custom pattern"""
        line = Line(start=[-3, 0, 0], end=[3, 0, 0])
        dashed = DashedLine(line, num_dashes=6, dashed_ratio=0.7)
        
        dashes = list(dashed.values())[0]
        # Should create appropriate number of dashes
        assert len(dashes) <= 6


class TestCADEffects:
    """Test CAD effects integration"""
    
    def test_round_corners_effect(self):
        """Test round corners effect"""
        square = Square()
        result = RoundCornersEffect.apply(square, radius=0.3)
        
        # Should return a modified mobject
        assert isinstance(result, VMobject)
        assert result.get_num_curves() > square.get_num_curves()
    
    def test_hatch_fill_effect(self):
        """Test hatch fill effect"""
        circle = Circle(radius=2)
        result = HatchFillEffect.apply(circle, angle=PI / 6, spacing=0.2)
        
        # Should return a VGroup with original and hatching
        assert isinstance(result, VGroup)
        assert len(result) == 2  # Original + hatch pattern
    
    def test_dashed_outline_effect(self):
        """Test dashed outline effect"""
        triangle = Triangle()
        result = DashedOutlineEffect.apply(triangle, num_dashes=9)
        
        # Should return a DashedLine object
        assert isinstance(result, DashedLine)
    
    def test_technical_drawing_effect(self):
        """Test technical drawing style effect"""
        rect = Rectangle()
        result = TechnicalDrawingEffect.apply(rect, style="blueprint")
        
        # Should modify stroke and fill
        assert result.get_stroke_color() == Color(WHITE)
        assert result.get_fill_opacity() == 0


class TestCADObjectFactory:
    """Test CAD object factory function"""
    
    def test_create_rounded_shape(self):
        """Test creating rounded shape via factory"""
        obj = create_cad_object(
            "rounded_shape",
            shape="square",
            side_length=2,
            corner_radius=0.3
        )
        
        assert isinstance(obj, VMobject)
        # Should have rounded corners (more curves)
        plain_square = Square(side_length=2)
        assert obj.get_num_curves() > plain_square.get_num_curves()
    
    def test_create_linear_dimension(self):
        """Test creating linear dimension via factory"""
        obj = create_cad_object(
            "linear_dimension",
            start=[-1, 0, 0],
            end=[1, 0, 0],
            text="2.00"
        )
        
        assert isinstance(obj, LinearDimension)
    
    def test_create_hatched_shape(self):
        """Test creating hatched shape via factory"""
        obj = create_cad_object(
            "hatched_shape",
            shape="circle",
            radius=1.5,
            hatch_angle=PI / 4,
            hatch_spacing=0.2
        )
        
        assert isinstance(obj, VGroup)
        assert len(obj) == 2  # Shape + hatching


class TestCADArrowHead:
    """Test CAD arrow head"""
    
    def test_arrow_head_creation(self):
        """Test creating CAD arrow head"""
        line = Line(start=[-2, 0, 0], end=[2, 0, 0])
        arrow = CADArrowHead(line, anchor_point=1, arrow_size=0.3)
        
        assert isinstance(arrow, VMobject)
        
        # Should be positioned at end of line
        arrow_pos = arrow.get_center()
        line_end = line.get_end()
        assert np.allclose(arrow_pos, line_end, atol=0.5)
    
    def test_arrow_head_reversed(self):
        """Test reversed arrow head"""
        arc = Arc(radius=2, angle=PI / 2)
        arrow = CADArrowHead(arc, anchor_point=0, reversed_arrow=True)
        
        assert isinstance(arrow, VMobject)
        assert arrow._reversed_arrow == True


class TestIntegration:
    """Integration tests for CAD components"""
    
    def test_technical_drawing_workflow(self):
        """Test complete technical drawing workflow"""
        # Create base shape
        base = Rectangle(width=4, height=2)
        
        # Apply rounded corners
        rounded = RoundCorners.apply(base, radius=0.3)
        
        # Add dimensions
        dim = LinearDimension(
            start=rounded.get_critical_point(LEFT),
            end=rounded.get_critical_point(RIGHT),
            text="4.00",
            direction=DOWN,
            offset=1
        )
        
        # Add hatching
        hatch = HatchPattern(rounded, angle=PI / 4, spacing=0.2)
        
        # Group everything
        drawing = VGroup(rounded, dim, hatch)
        
        assert isinstance(drawing, VGroup)
        assert len(drawing) == 3
    
    def test_animated_cad_path(self):
        """Test animated path with equalization"""
        # Create complex path
        path = Circle(radius=2).append_points(
            Square(side_length=2).shift(RIGHT * 3).points
        )
        
        # Create path mapper
        mapper = PathMapper(path)
        
        # Test equalized movement
        eq_func = mapper.equalize_rate_func(linear)
        
        # Sample points should be evenly distributed by arc length
        points = [mapper.point_from_proportion(eq_func(t)) 
                 for t in np.linspace(0, 1, 10)]
        
        # Calculate distances between consecutive points
        distances = [np.linalg.norm(points[i+1] - points[i]) 
                    for i in range(len(points)-1)]
        
        # Distances should be roughly equal
        mean_dist = np.mean(distances)
        assert all(abs(d - mean_dist) < mean_dist * 0.3 for d in distances)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])