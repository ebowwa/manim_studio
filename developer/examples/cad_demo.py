from src.config.manim_config import config
from manim import *
from src.components.cad_objects import (
    RoundCorners, ChamferCorners, LinearDimension, AngularDimension,
    PointerLabel, HatchPattern, DashedLine, PathMapper, CADArrowHead
)


class CADBasicDemo(Scene):
    """Basic demonstration of CAD drawing utilities"""
    
    def construct(self):
        # Create title
        title = Text("CAD Drawing Utilities Demo", font_size=48)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait()
        
        # Create a rounded rectangle
        rect = Rectangle(width=4, height=2.5, color=BLUE)
        rounded_rect = RoundCorners.apply(rect, radius=0.4)
        rounded_rect.shift(LEFT * 3.5)
        
        # Create a chamfered hexagon
        hex = RegularPolygon(n=6, radius=1.3, color=GREEN)
        chamfered_hex = ChamferCorners.apply(hex, offset=0.3)
        chamfered_hex.shift(RIGHT * 3.5)
        
        # Animate creation with equalized speed
        pm1 = PathMapper(rounded_rect)
        pm2 = PathMapper(chamfered_hex)
        
        self.play(
            Create(rounded_rect, rate_func=pm1.equalize_rate_func(smooth)),
            Create(chamfered_hex, rate_func=pm2.equalize_rate_func(smooth)),
            run_time=3
        )
        self.wait()
        
        # Add labels
        label1 = PointerLabel(
            point=rounded_rect.get_corner(UR),
            text="R = 0.4",
            offset_vector=UR * 0.7,
            color=YELLOW
        )
        
        label2 = PointerLabel(
            point=chamfered_hex.get_top(),
            text="Chamfer",
            offset_vector=UP * 0.7,
            color=YELLOW
        )
        
        self.play(
            FadeIn(label1),
            FadeIn(label2)
        )
        self.wait()
        
        # Clear and show next demo
        self.play(
            FadeOut(VGroup(rounded_rect, chamfered_hex, label1, label2))
        )
        
        # Dimension demo
        self.show_dimensions_demo()
        
        # Clear for next
        self.clear()
        self.add(title)
        
        # Hatching demo
        self.show_hatching_demo()
        
        # Clear for next
        self.clear()
        self.add(title)
        
        # Dashed lines demo
        self.show_dashed_demo()
        
        self.wait(2)
    
    def show_dimensions_demo(self):
        """Demonstrate dimension annotations"""
        # Create a part with dimensions
        part = Rectangle(width=5, height=3, color=WHITE, stroke_width=3)
        part = RoundCorners.apply(part, radius=0.5)
        
        # Add linear dimensions
        width_dim = LinearDimension(
            start=part.get_corner(DL),
            end=part.get_corner(DR),
            text="5.00",
            direction=DOWN,
            offset=1.2,
            color=RED
        )
        
        height_dim = LinearDimension(
            start=part.get_corner(DR),
            end=part.get_corner(UR),
            text="3.00",
            direction=RIGHT,
            offset=1.2,
            color=RED
        )
        
        # Add angular dimension
        center = part.get_center()
        angle_dim = AngularDimension(
            start=center + RIGHT * 2,
            end=center + UP * 1.5,
            arc_center=center,
            text="37°",
            offset=0.5,
            color=BLUE
        )
        
        # Animate
        self.play(Create(part))
        self.play(
            Create(width_dim),
            Create(height_dim),
            run_time=2
        )
        self.play(Create(angle_dim))
        self.wait(2)
        
        self.play(
            FadeOut(VGroup(part, width_dim, height_dim, angle_dim))
        )
    
    def show_hatching_demo(self):
        """Demonstrate hatching patterns"""
        # Create shapes with different hatch patterns
        circle = Circle(radius=1.5, color=GREEN, stroke_width=3)
        circle.shift(LEFT * 4)
        hatch1 = HatchPattern(circle, angle=PI/4, spacing=0.2)
        hatch1.set_color(GREEN)
        
        square = Square(side_length=2.5, color=BLUE, stroke_width=3)
        hatch2 = HatchPattern(square, angle=0, spacing=0.15)
        hatch2.set_color(BLUE)
        
        triangle = Triangle(radius=1.8, color=RED, stroke_width=3)
        triangle.shift(RIGHT * 4)
        # Cross hatch
        hatch3a = HatchPattern(triangle, angle=PI/6, spacing=0.2)
        hatch3b = HatchPattern(triangle, angle=-PI/6, spacing=0.2)
        hatch3 = VGroup(hatch3a, hatch3b).set_color(RED)
        
        # Animate
        self.play(
            Create(circle),
            Create(square),
            Create(triangle),
            run_time=2
        )
        
        self.play(
            Create(hatch1),
            Create(hatch2),
            Create(hatch3),
            run_time=3
        )
        
        self.wait(2)
        
        self.play(
            FadeOut(VGroup(circle, square, triangle, hatch1, hatch2, hatch3))
        )
    
    def show_dashed_demo(self):
        """Demonstrate dashed lines"""
        # Create various dashed patterns
        shapes = VGroup()
        
        # Dashed circle
        circle = Circle(radius=1.2, color=YELLOW)
        circle.shift(LEFT * 4 + UP * 1.5)
        dashed_circle = DashedLine(circle, num_dashes=16, dashed_ratio=0.6)
        dashed_circle.set_color(YELLOW)
        shapes.add(dashed_circle)
        
        # Dashed rectangle
        rect = Rectangle(width=3, height=2, color=PURPLE)
        rect.shift(UP * 1.5)
        dashed_rect = DashedLine(rect, num_dashes=20, dashed_ratio=0.5)
        dashed_rect.set_color(PURPLE)
        shapes.add(dashed_rect)
        
        # Dashed bezier curve
        curve = VMobject(color=ORANGE)
        curve.set_points_smoothly([
            LEFT * 3 + DOWN * 1.5,
            LEFT * 1 + DOWN * 2,
            RIGHT * 1 + DOWN * 1,
            RIGHT * 3 + DOWN * 1.5
        ])
        dashed_curve = DashedLine(curve, num_dashes=12, dashed_ratio=0.7)
        dashed_curve.set_color(ORANGE)
        shapes.add(dashed_curve)
        
        # Animate with staggered creation
        for i, shape in enumerate(shapes):
            self.play(Create(shape), run_time=1.5)
            self.wait(0.5)
        
        # Animate dash offset to show movement
        t = ValueTracker(0)
        
        def update_dashes(mob, dt):
            offset = t.get_value() % 1
            # Recreate with new offset
            if isinstance(mob, DashedLine):
                # This is a simplified update - in production you'd update the actual dashes
                pass
        
        # Show rotation
        self.play(
            Rotate(shapes[0], angle=TAU, about_point=shapes[0].get_center()),
            Rotate(shapes[1], angle=TAU/2, about_point=shapes[1].get_center()),
            run_time=4,
            rate_func=linear
        )
        
        self.wait()


class CADTechnicalDrawing(Scene):
    """Create a technical drawing with full annotations"""
    
    def construct(self):
        # Set up technical style
        self.camera.background_color = "#1a1a1a"
        
        # Create grid background
        grid = NumberPlane(
            x_range=[-8, 8, 0.5],
            y_range=[-4.5, 4.5, 0.5],
            background_line_style={
                "stroke_color": "#333333",
                "stroke_width": 1,
            },
            axis_config={
                "stroke_color": "#666666",
                "stroke_width": 2,
            }
        )
        grid.set_z_index(-2)
        self.add(grid)
        
        # Create main part
        main_body = Rectangle(width=6, height=3, color="#00ff00", stroke_width=2.5)
        main_body = RoundCorners.apply(main_body, radius=0.4)
        
        # Create center cutout
        cutout = Rectangle(width=3, height=1.5, color="#00ff00", stroke_width=2.5)
        cutout = ChamferCorners.apply(cutout, offset=0.3)
        
        # Add mounting holes
        holes = VGroup()
        hole_positions = [
            [-2.3, 1.1, 0], [2.3, 1.1, 0],
            [-2.3, -1.1, 0], [2.3, -1.1, 0]
        ]
        for pos in hole_positions:
            hole = Circle(radius=0.25, color="#00ff00", stroke_width=2)
            hole.move_to(pos)
            holes.add(hole)
        
        # Add hatching to cutout
        hatch = HatchPattern(cutout, angle=PI/4, spacing=0.15)
        hatch.set_color("#00ff00").set_stroke_width(1)
        
        # Create all parts group
        technical_drawing = VGroup(main_body, cutout, holes, hatch)
        
        # Animate assembly
        self.play(Create(main_body, run_time=2))
        self.play(Create(cutout), Create(hatch), run_time=2)
        self.play(LaggedStart(*[Create(h) for h in holes], lag_ratio=0.1))
        
        # Add dimensions
        dims = VGroup()
        
        # Overall width
        width_dim = LinearDimension(
            start=main_body.get_corner(DL) + DOWN * 0.3,
            end=main_body.get_corner(DR) + DOWN * 0.3,
            text="6.00",
            direction=DOWN,
            offset=1.2,
            color="#ff6b6b",
            stroke_width=1.5
        )
        dims.add(width_dim)
        
        # Overall height
        height_dim = LinearDimension(
            start=main_body.get_corner(DR) + RIGHT * 0.3,
            end=main_body.get_corner(UR) + RIGHT * 0.3,
            text="3.00",
            direction=RIGHT,
            offset=1.2,
            color="#ff6b6b",
            stroke_width=1.5
        )
        dims.add(height_dim)
        
        # Hole spacing
        hole_spacing_dim = LinearDimension(
            start=holes[0].get_center(),
            end=holes[1].get_center(),
            text="4.60",
            direction=UP,
            offset=0.8,
            color="#ff6b6b",
            stroke_width=1.5,
            outside_arrow=True
        )
        dims.add(hole_spacing_dim)
        
        # Add pointer annotations
        annotations = VGroup()
        
        # Radius callout
        radius_pointer = PointerLabel(
            point=main_body.get_corner(UR) + LEFT * 0.4 + DOWN * 0.4,
            text="R0.40",
            offset_vector=UR * 0.8,
            color=YELLOW,
            stroke_width=1.5
        )
        annotations.add(radius_pointer)
        
        # Hole diameter
        hole_pointer = PointerLabel(
            point=holes[0].get_right(),
            text="⌀0.50",
            offset_vector=UL * 0.8,
            color=YELLOW,
            stroke_width=1.5
        )
        annotations.add(hole_pointer)
        
        # Animate dimensions and annotations
        self.play(LaggedStart(*[Create(d) for d in dims], lag_ratio=0.3, run_time=3))
        self.play(LaggedStart(*[FadeIn(a) for a in annotations], lag_ratio=0.2))
        
        # Add title block
        title_block = Rectangle(width=4, height=1.5, color=WHITE, stroke_width=1)
        title_block.to_corner(DR).shift(UP * 0.3 + LEFT * 0.3)
        title_text = VGroup(
            Text("PART: CAD-001", font_size=20),
            Text("Technical Drawing Demo", font_size=16),
            Text("Scale: 1:1", font_size=16)
        ).arrange(DOWN, buff=0.15)
        title_text.move_to(title_block)
        
        self.play(
            Create(title_block),
            Write(title_text),
            run_time=2
        )
        
        # Final camera movement
        self.play(
            self.camera.frame.animate.scale(1.2).shift(DOWN * 0.5),
            run_time=2
        )
        
        self.wait(3)


if __name__ == "__main__":
    # Run basic demo
    with tempconfig({"quality": "medium_quality", "preview": True}):
        scene = CADBasicDemo()
        scene.render()
        
    # Run technical drawing
    with tempconfig({"quality": "high_quality", "preview": True}):
        scene2 = CADTechnicalDrawing()
        scene2.render()