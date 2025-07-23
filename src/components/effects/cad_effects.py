from src.config.manim_config import config
from manim import *
from typing import Dict, Any, Optional, Union, List
import numpy as np
from ..cad_objects import (
    RoundCorners, ChamferCorners, HatchPattern, DashedLine,
    PathMapper, LinearDimension, AngularDimension, PointerLabel
)
from .effect_registry import register_effect
from .base_effect import BaseEffect


class CADEffect(BaseEffect):
    """Base class for CAD-style effects"""
    pass


@register_effect("round_corners")
class RoundCornersEffect(CADEffect):
    """Apply rounded corners to any shape"""
    
    @staticmethod
    def apply(mobject: VMobject, radius: float = 0.2, **kwargs) -> VMobject:
        """
        Apply rounded corners effect to a mobject
        
        Args:
            mobject: The mobject to apply the effect to
            radius: Corner radius
            **kwargs: Additional parameters
            
        Returns:
            The mobject with rounded corners
        """
        return RoundCorners.apply(mobject.copy(), radius)


@register_effect("chamfer_corners")
class ChamferCornersEffect(CADEffect):
    """Apply chamfered corners to any shape"""
    
    @staticmethod
    def apply(mobject: VMobject, offset: float = 0.2, **kwargs) -> VMobject:
        """
        Apply chamfered corners effect to a mobject
        
        Args:
            mobject: The mobject to apply the effect to
            offset: Chamfer offset distance
            **kwargs: Additional parameters
            
        Returns:
            The mobject with chamfered corners
        """
        return ChamferCorners.apply(mobject.copy(), offset)


@register_effect("hatch_fill")
class HatchFillEffect(CADEffect):
    """Add hatching pattern inside a shape"""
    
    @staticmethod
    def apply(mobject: VMobject, angle: float = PI / 6, spacing: float = 0.3,
              color: Optional[str] = None, stroke_width: float = 2, **kwargs) -> VGroup:
        """
        Apply hatching pattern effect to a mobject
        
        Args:
            mobject: The mobject to apply the effect to
            angle: Angle of hatch lines in radians
            spacing: Spacing between hatch lines
            color: Color of hatch lines (if None, matches mobject)
            stroke_width: Width of hatch lines
            **kwargs: Additional parameters
            
        Returns:
            VGroup containing the original mobject and hatch pattern
        """
        hatch = HatchPattern(mobject, angle=angle, spacing=spacing, 
                           stroke_width=stroke_width)
        
        if color:
            hatch.set_color(color)
        else:
            hatch.match_color(mobject)
            
        return VGroup(mobject.copy(), hatch)


@register_effect("cross_hatch")
class CrossHatchEffect(CADEffect):
    """Add cross-hatching pattern inside a shape"""
    
    @staticmethod
    def apply(mobject: VMobject, angle: float = PI / 6, spacing: float = 0.3,
              color: Optional[str] = None, stroke_width: float = 2, **kwargs) -> VGroup:
        """
        Apply cross-hatching pattern effect to a mobject
        
        Args:
            mobject: The mobject to apply the effect to
            angle: Angle of first set of hatch lines in radians
            spacing: Spacing between hatch lines
            color: Color of hatch lines (if None, matches mobject)
            stroke_width: Width of hatch lines
            **kwargs: Additional parameters
            
        Returns:
            VGroup containing the original mobject and cross-hatch pattern
        """
        hatch1 = HatchPattern(mobject, angle=angle, spacing=spacing, 
                            stroke_width=stroke_width)
        hatch2 = HatchPattern(mobject, angle=angle + PI / 2, spacing=spacing,
                            stroke_width=stroke_width)
        
        if color:
            hatch1.set_color(color)
            hatch2.set_color(color)
        else:
            hatch1.match_color(mobject)
            hatch2.match_color(mobject)
            
        return VGroup(mobject.copy(), hatch1, hatch2)


@register_effect("dashed_outline")
class DashedOutlineEffect(CADEffect):
    """Convert solid outline to dashed pattern"""
    
    @staticmethod
    def apply(mobject: VMobject, num_dashes: int = 15, dashed_ratio: float = 0.5,
              dash_offset: float = 0.0, **kwargs) -> DashedLine:
        """
        Apply dashed outline effect to a mobject
        
        Args:
            mobject: The mobject to apply the effect to
            num_dashes: Number of dashes around the shape
            dashed_ratio: Ratio of dash length to total period (0-1)
            dash_offset: Offset for dash pattern
            **kwargs: Additional parameters
            
        Returns:
            DashedLine object
        """
        return DashedLine(mobject, num_dashes=num_dashes, 
                         dashed_ratio=dashed_ratio, dash_offset=dash_offset)


@register_effect("technical_drawing")
class TechnicalDrawingEffect(CADEffect):
    """Apply technical drawing style to a shape"""
    
    @staticmethod
    def apply(mobject: VMobject, style: str = "blueprint", **kwargs) -> VMobject:
        """
        Apply technical drawing style to a mobject
        
        Args:
            mobject: The mobject to apply the effect to
            style: Drawing style ("blueprint", "schematic", "cad")
            **kwargs: Additional parameters
            
        Returns:
            Styled mobject
        """
        result = mobject.copy()
        
        if style == "blueprint":
            result.set_stroke(color=WHITE, width=2)
            result.set_fill(opacity=0)
            # Add grid background effect if needed
        elif style == "schematic":
            result.set_stroke(color=BLACK, width=3)
            result.set_fill(opacity=0)
        elif style == "cad":
            result.set_stroke(color="#FF6B6B", width=2)
            result.set_fill(opacity=0)
            
        return result


@register_effect("dimension_lines")
class DimensionLinesEffect(CADEffect):
    """Add dimension lines to a shape"""
    
    @staticmethod
    def apply(mobject: VMobject, dimensions: List[Dict[str, Any]] = None, **kwargs) -> VGroup:
        """
        Add dimension lines to a mobject
        
        Args:
            mobject: The mobject to add dimensions to
            dimensions: List of dimension configurations
            **kwargs: Additional parameters
            
        Returns:
            VGroup containing mobject and dimension lines
        """
        if dimensions is None:
            # Auto-generate basic dimensions
            dimensions = [
                {
                    "type": "linear",
                    "start": mobject.get_critical_point(LEFT),
                    "end": mobject.get_critical_point(RIGHT),
                    "direction": DOWN,
                    "offset": 1.5
                }
            ]
        
        result = VGroup(mobject.copy())
        
        for dim_config in dimensions:
            dim_type = dim_config.pop("type", "linear")
            
            if dim_type == "linear":
                dim = LinearDimension(**dim_config)
            elif dim_type == "angular":
                dim = AngularDimension(**dim_config)
            else:
                continue
                
            result.add(dim)
            
        return result


@register_effect("pointer_annotation")
class PointerAnnotationEffect(CADEffect):
    """Add pointer annotations to specific points"""
    
    @staticmethod
    def apply(mobject: VMobject, annotations: List[Dict[str, Any]] = None, **kwargs) -> VGroup:
        """
        Add pointer annotations to a mobject
        
        Args:
            mobject: The mobject to annotate
            annotations: List of annotation configurations
            **kwargs: Additional parameters
            
        Returns:
            VGroup containing mobject and annotations
        """
        if annotations is None:
            annotations = [
                {
                    "point": mobject.get_center(),
                    "text": "Center",
                    "offset_vector": UP + RIGHT
                }
            ]
        
        result = VGroup(mobject.copy())
        
        for ann_config in annotations:
            pointer = PointerLabel(**ann_config)
            result.add(pointer)
            
        return result


@register_effect("equalized_animation")
class EqualizedAnimationEffect(CADEffect):
    """Create animations with equalized speed along paths"""
    
    @staticmethod
    def apply(mobject: VMobject, rate_func=smooth, **kwargs) -> VMobject:
        """
        Prepare a mobject for equalized animation
        
        Args:
            mobject: The mobject to prepare
            rate_func: Base rate function to equalize
            **kwargs: Additional parameters
            
        Returns:
            The mobject with attached path mapper
        """
        # Attach path mapper to the mobject for later use
        mobject._path_mapper = PathMapper(mobject)
        mobject._equalized_rate_func = mobject._path_mapper.equalize_rate_func(rate_func)
        return mobject


@register_effect("cad_arrow")
class CADArrowEffect(CADEffect):
    """Add CAD-style arrow indicators"""
    
    @staticmethod
    def apply(mobject: VMobject, arrow_positions: List[float] = None,
              arrow_size: float = DEFAULT_ARROW_TIP_LENGTH, **kwargs) -> VGroup:
        """
        Add CAD-style arrows along a path
        
        Args:
            mobject: The mobject to add arrows to
            arrow_positions: List of positions (0-1) along the path
            arrow_size: Size of arrow heads
            **kwargs: Additional parameters
            
        Returns:
            VGroup containing mobject and arrows
        """
        if arrow_positions is None:
            arrow_positions = [0.25, 0.5, 0.75]
            
        from ..cad_objects import CADArrowHead
        
        result = VGroup(mobject.copy())
        
        for pos in arrow_positions:
            arrow = CADArrowHead(mobject, anchor_point=pos, arrow_size=arrow_size)
            result.add(arrow)
            
        return result


@register_effect("technical_grid")
class TechnicalGridEffect(CADEffect):
    """Add technical grid background"""
    
    @staticmethod
    def apply(mobject: VMobject, grid_spacing: float = 0.5, 
              grid_color: str = "#333333", **kwargs) -> VGroup:
        """
        Add technical grid behind a mobject
        
        Args:
            mobject: The mobject to add grid behind
            grid_spacing: Spacing between grid lines
            grid_color: Color of grid lines
            **kwargs: Additional parameters
            
        Returns:
            VGroup containing grid and mobject
        """
        # Get bounding box
        left = mobject.get_critical_point(LEFT)[0]
        right = mobject.get_critical_point(RIGHT)[0]
        bottom = mobject.get_critical_point(DOWN)[1]
        top = mobject.get_critical_point(UP)[1]
        
        # Add margin
        margin = 1
        left -= margin
        right += margin
        bottom -= margin
        top += margin
        
        # Create grid
        grid = VGroup()
        
        # Vertical lines
        x = left
        while x <= right:
            line = Line([x, bottom, 0], [x, top, 0], 
                       stroke_color=grid_color, stroke_width=1)
            grid.add(line)
            x += grid_spacing
            
        # Horizontal lines
        y = bottom
        while y <= top:
            line = Line([left, y, 0], [right, y, 0],
                       stroke_color=grid_color, stroke_width=1)
            grid.add(line)
            y += grid_spacing
            
        return VGroup(grid, mobject.copy())


# Specialized CAD animation effects
@register_effect("cad_create")
class CADCreateEffect(CADEffect):
    """Special creation animation for CAD objects"""
    
    @staticmethod
    def apply(mobject: VMobject, run_time: float = 3, lag_ratio: float = 0.1, **kwargs) -> Animation:
        """
        Create a CAD-style creation animation
        
        Args:
            mobject: The mobject to animate
            run_time: Duration of animation
            lag_ratio: Lag between creating different parts
            **kwargs: Additional parameters
            
        Returns:
            Animation object
        """
        # Check if mobject has path mapper for equalized animation
        if hasattr(mobject, '_path_mapper'):
            return Create(mobject, rate_func=mobject._equalized_rate_func, 
                         run_time=run_time, **kwargs)
        else:
            return Create(mobject, run_time=run_time, lag_ratio=lag_ratio, **kwargs)


@register_effect("cad_trace")
class CADTraceEffect(CADEffect):
    """Trace along a CAD path with indicators"""
    
    @staticmethod
    def apply(mobject: VMobject, tracer: Optional[VMobject] = None,
              fade_trace: bool = True, **kwargs) -> AnimationGroup:
        """
        Create a tracing animation along a CAD path
        
        Args:
            mobject: The path to trace
            tracer: Object to move along the path (default: dot)
            fade_trace: Whether to fade the trace as it's drawn
            **kwargs: Additional parameters
            
        Returns:
            AnimationGroup with trace animations
        """
        if tracer is None:
            tracer = Dot(color=YELLOW, radius=0.08)
            
        # Create path mapper for smooth motion
        pm = PathMapper(mobject)
        
        # Create animations
        anims = []
        
        # Move tracer along path
        anims.append(MoveAlongPath(tracer, mobject, 
                                  rate_func=pm.equalize_rate_func(smooth)))
        
        # Draw the path
        if fade_trace:
            anims.append(ShowPassingFlash(mobject.copy().set_stroke(width=6)))
        else:
            anims.append(Create(mobject))
            
        return AnimationGroup(*anims, **kwargs)