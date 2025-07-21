"""Improved skull effects with better anatomical accuracy and visual design."""

from typing import Optional, List, Tuple
import numpy as np
from manim import *
from .base_effect import BaseEffect


class ImprovedSkullEffect(BaseEffect):
    """Creates anatomically improved skull designs."""
    
    def __init__(self, position: np.ndarray = ORIGIN, **kwargs):
        super().__init__()
        self.position = position
        self.update_config(
            size=kwargs.get('size', 1.0),
            style=kwargs.get('style', 'realistic'),  # 'realistic', 'stylized', 'minimal', 'decorative'
            color=kwargs.get('color', WHITE),
            detail_level=kwargs.get('detail_level', 'high'),  # 'low', 'medium', 'high'
            add_shadows=kwargs.get('add_shadows', True),
            eye_glow=kwargs.get('eye_glow', False),
            eye_color=kwargs.get('eye_color', RED)
        )
    
    def create(self) -> VGroup:
        """Create improved skull design."""
        skull = VGroup()
        size = self.get_config('size')
        style = self.get_config('style')
        
        if style == 'realistic':
            skull = self._create_realistic_skull(size)
        elif style == 'stylized':
            skull = self._create_stylized_skull(size)
        elif style == 'minimal':
            skull = self._create_minimal_skull(size)
        elif style == 'decorative':
            skull = self._create_decorative_skull(size)
        
        skull.move_to(self.position)
        base_color = self.get_config('color')
        
        # Apply color gradient for depth
        if self.get_config('add_shadows'):
            for i, part in enumerate(skull):
                if hasattr(part, 'set_fill'):
                    # Create subtle shading
                    shade_factor = 1 - (i * 0.05)
                    shaded_color = interpolate_color(BLACK, base_color, shade_factor)
                    part.set_color(shaded_color)
        else:
            skull.set_color(base_color)
        
        if self.get_config('eye_glow'):
            self._add_improved_eye_glow(skull)
        
        self.add_mobjects(skull)
        return self._mobjects
    
    def _create_realistic_skull(self, size: float) -> VGroup:
        """Create anatomically accurate skull."""
        skull = VGroup()
        
        # Cranium - more realistic shape using bezier curves
        cranium_points = [
            [0, 1.2, 0],      # Top
            [0.7, 1.0, 0],    # Upper right
            [0.9, 0.5, 0],    # Mid right
            [0.8, 0, 0],      # Lower right
            [0.5, -0.3, 0],   # Jaw right
            [0, -0.4, 0],     # Chin
            [-0.5, -0.3, 0],  # Jaw left
            [-0.8, 0, 0],     # Lower left
            [-0.9, 0.5, 0],   # Mid left
            [-0.7, 1.0, 0],   # Upper left
            [0, 1.2, 0]       # Back to top
        ]
        cranium_points = [size * np.array(p) for p in cranium_points]
        
        cranium = VMobject()
        cranium.set_points_as_corners(cranium_points)
        cranium.make_smooth()
        cranium.set_fill(WHITE, opacity=1)
        cranium.set_stroke(WHITE, width=2)
        
        # Eye sockets - realistic shapes
        left_eye = self._create_eye_socket(size * 0.35, LEFT * size * 0.35 + UP * size * 0.3)
        right_eye = self._create_eye_socket(size * 0.35, RIGHT * size * 0.35 + UP * size * 0.3)
        
        # Nasal cavity - anatomically correct
        nose = self._create_nasal_cavity(size * 0.25)
        nose.move_to(DOWN * size * 0.05)
        
        # Cheekbones
        left_cheek = Arc(
            start_angle=PI * 0.7,
            angle=PI * 0.4,
            radius=size * 0.6
        ).shift(LEFT * size * 0.4 + DOWN * size * 0.1)
        left_cheek.set_stroke(WHITE, width=2)
        
        right_cheek = Arc(
            start_angle=PI * 1.9,
            angle=PI * 0.4,
            radius=size * 0.6
        ).shift(RIGHT * size * 0.4 + DOWN * size * 0.1)
        right_cheek.set_stroke(WHITE, width=2)
        
        # Upper teeth
        upper_teeth = self._create_teeth_row(
            num_teeth=8,
            tooth_width=size * 0.12,
            tooth_height=size * 0.2,
            position=DOWN * size * 0.4
        )
        
        # Lower jaw with teeth
        lower_jaw = self._create_lower_jaw(size)
        lower_jaw.move_to(DOWN * size * 0.7)
        
        # Temporal lines (side of skull)
        left_temporal = Arc(
            radius=size * 0.8,
            start_angle=PI * 0.5,
            angle=PI * 0.3
        ).shift(LEFT * size * 0.6 + UP * size * 0.5)
        left_temporal.set_stroke(WHITE, width=1, opacity=0.5)
        
        right_temporal = Arc(
            radius=size * 0.8,
            start_angle=PI * 0.2,
            angle=PI * 0.3
        ).shift(RIGHT * size * 0.6 + UP * size * 0.5)
        right_temporal.set_stroke(WHITE, width=1, opacity=0.5)
        
        skull.add(
            cranium, left_eye, right_eye, nose,
            left_cheek, right_cheek,
            upper_teeth, lower_jaw,
            left_temporal, right_temporal
        )
        
        return skull
    
    def _create_eye_socket(self, size: float, position: np.ndarray) -> VMobject:
        """Create realistic eye socket."""
        # Irregular eye socket shape
        eye_points = [
            [0, 0.5, 0],      # Top
            [0.5, 0.3, 0],    # Upper right
            [0.6, 0, 0],      # Right
            [0.5, -0.3, 0],   # Lower right
            [0, -0.4, 0],     # Bottom
            [-0.5, -0.3, 0],  # Lower left
            [-0.6, 0, 0],     # Left
            [-0.5, 0.3, 0],   # Upper left
            [0, 0.5, 0]       # Back to top
        ]
        eye_points = [size * np.array(p) + position for p in eye_points]
        
        eye = VMobject()
        eye.set_points_as_corners(eye_points)
        eye.make_smooth()
        eye.set_fill(BLACK, opacity=1)
        eye.set_stroke(WHITE, width=2)
        
        # Add orbital ridge detail
        ridge = Arc(
            radius=size * 1.1,
            start_angle=PI * 0.2,
            angle=PI * 0.6
        ).move_to(position + UP * size * 0.1)
        ridge.set_stroke(WHITE, width=1, opacity=0.7)
        
        socket = VGroup(eye, ridge)
        return socket
    
    def _create_nasal_cavity(self, size: float) -> VMobject:
        """Create anatomically correct nasal cavity."""
        # Nasal opening shape
        nose_points = [
            [0, 0.8, 0],      # Top (nasal spine)
            [0.3, 0.5, 0],    # Upper right
            [0.4, 0, 0],      # Right
            [0.3, -0.5, 0],   # Lower right
            [0, -0.6, 0],     # Bottom
            [-0.3, -0.5, 0],  # Lower left
            [-0.4, 0, 0],     # Left
            [-0.3, 0.5, 0],   # Upper left
            [0, 0.8, 0]       # Back to top
        ]
        nose_points = [size * np.array(p) for p in nose_points]
        
        nose = VMobject()
        nose.set_points_as_corners(nose_points)
        nose.make_smooth()
        nose.set_fill(BLACK, opacity=1)
        nose.set_stroke(WHITE, width=2)
        
        # Add nasal septum
        septum = Line(
            UP * size * 0.8,
            DOWN * size * 0.6,
            stroke_width=1,
            stroke_opacity=0.5
        )
        
        cavity = VGroup(nose, septum)
        return cavity
    
    def _create_teeth_row(self, num_teeth: int, tooth_width: float, 
                          tooth_height: float, position: np.ndarray) -> VGroup:
        """Create a row of anatomically shaped teeth."""
        teeth = VGroup()
        total_width = num_teeth * tooth_width * 0.9
        
        for i in range(num_teeth):
            # Vary tooth shapes
            if i < 2 or i >= num_teeth - 2:
                # Molars - wider and flatter
                tooth = self._create_molar(tooth_width * 1.2, tooth_height * 0.8)
            elif i == num_teeth // 2 or i == num_teeth // 2 - 1:
                # Incisors - thinner and taller
                tooth = self._create_incisor(tooth_width * 0.8, tooth_height)
            else:
                # Canines/premolars
                tooth = self._create_canine(tooth_width, tooth_height * 0.9)
            
            x_pos = -total_width/2 + (i + 0.5) * tooth_width * 0.9
            tooth.move_to(position + RIGHT * x_pos)
            teeth.add(tooth)
        
        return teeth
    
    def _create_incisor(self, width: float, height: float) -> VMobject:
        """Create incisor tooth shape."""
        points = [
            [-width/2, 0, 0],
            [-width/2, height * 0.7, 0],
            [-width/3, height * 0.9, 0],
            [0, height, 0],
            [width/3, height * 0.9, 0],
            [width/2, height * 0.7, 0],
            [width/2, 0, 0]
        ]
        
        tooth = VMobject()
        tooth.set_points_as_corners(points)
        tooth.make_smooth()
        tooth.set_fill(WHITE, opacity=0.9)
        tooth.set_stroke(GREY, width=1)
        
        return tooth
    
    def _create_canine(self, width: float, height: float) -> VMobject:
        """Create canine tooth shape."""
        points = [
            [-width/2, 0, 0],
            [-width/2, height * 0.6, 0],
            [0, height, 0],
            [width/2, height * 0.6, 0],
            [width/2, 0, 0]
        ]
        
        tooth = VMobject()
        tooth.set_points_as_corners(points)
        tooth.make_smooth()
        tooth.set_fill(WHITE, opacity=0.9)
        tooth.set_stroke(GREY, width=1)
        
        return tooth
    
    def _create_molar(self, width: float, height: float) -> VMobject:
        """Create molar tooth shape."""
        tooth = RoundedRectangle(
            width=width,
            height=height,
            corner_radius=width * 0.2
        )
        tooth.set_fill(WHITE, opacity=0.9)
        tooth.set_stroke(GREY, width=1)
        
        # Add cusps (bumps on molars)
        cusp1 = Circle(radius=width * 0.1)
        cusp1.move_to(tooth.get_top() + DOWN * height * 0.2 + LEFT * width * 0.2)
        cusp1.set_fill(WHITE, opacity=0.9)
        cusp1.set_stroke(width=0)
        
        cusp2 = Circle(radius=width * 0.1)
        cusp2.move_to(tooth.get_top() + DOWN * height * 0.2 + RIGHT * width * 0.2)
        cusp2.set_fill(WHITE, opacity=0.9)
        cusp2.set_stroke(width=0)
        
        return VGroup(tooth, cusp1, cusp2)
    
    def _create_lower_jaw(self, size: float) -> VGroup:
        """Create lower jaw with mandible shape."""
        jaw = VGroup()
        
        # Mandible curve
        jaw_points = [
            [-size * 0.6, 0, 0],
            [-size * 0.7, -size * 0.1, 0],
            [-size * 0.5, -size * 0.2, 0],
            [0, -size * 0.25, 0],
            [size * 0.5, -size * 0.2, 0],
            [size * 0.7, -size * 0.1, 0],
            [size * 0.6, 0, 0]
        ]
        
        mandible = VMobject()
        mandible.set_points_as_corners(jaw_points)
        mandible.make_smooth()
        mandible.set_stroke(WHITE, width=3)
        
        # Lower teeth
        lower_teeth = self._create_teeth_row(
            num_teeth=8,
            tooth_width=size * 0.11,
            tooth_height=size * 0.15,
            position=UP * size * 0.05
        )
        
        jaw.add(mandible, lower_teeth)
        return jaw
    
    def _create_stylized_skull(self, size: float) -> VGroup:
        """Create a stylized, artistic skull."""
        skull = VGroup()
        
        # Stylized cranium with exaggerated features
        cranium = Circle(radius=size)
        cranium.stretch(1.3, 1)  # Elongate vertically
        cranium.set_fill(WHITE, opacity=1)
        cranium.set_stroke(WHITE, width=3)
        
        # Large dramatic eye sockets
        left_eye = Ellipse(width=size * 0.6, height=size * 0.5)
        left_eye.move_to(LEFT * size * 0.35 + UP * size * 0.2)
        left_eye.rotate(PI/8)
        left_eye.set_fill(BLACK, opacity=1)
        left_eye.set_stroke(WHITE, width=2)
        
        right_eye = Ellipse(width=size * 0.6, height=size * 0.5)
        right_eye.move_to(RIGHT * size * 0.35 + UP * size * 0.2)
        right_eye.rotate(-PI/8)
        right_eye.set_fill(BLACK, opacity=1)
        right_eye.set_stroke(WHITE, width=2)
        
        # Stylized nose
        nose = Triangle()
        nose.scale(size * 0.3)
        nose.move_to(DOWN * size * 0.1)
        nose.set_fill(BLACK, opacity=1)
        nose.set_stroke(WHITE, width=2)
        
        # Decorative jaw design
        jaw_curve = ParametricFunction(
            lambda t: np.array([
                size * 0.8 * np.sin(t),
                -size * 0.5 - size * 0.2 * np.cos(2*t),
                0
            ]),
            t_range=[-PI/2, PI/2]
        )
        jaw_curve.set_stroke(WHITE, width=3)
        
        # Stylized teeth pattern
        teeth_pattern = VGroup()
        for i in range(5):
            tooth = RegularPolygon(n=3, radius=size * 0.15)
            tooth.move_to(
                DOWN * size * 0.6 + 
                RIGHT * (i - 2) * size * 0.25
            )
            teeth_pattern.add(tooth)
        teeth_pattern.set_fill(WHITE, opacity=0.9)
        teeth_pattern.set_stroke(GREY, width=1)
        
        # Add decorative elements
        swirl_left = ParametricFunction(
            lambda t: np.array([
                -size * 0.8 - size * 0.2 * np.cos(3*t),
                size * 0.3 * np.sin(2*t),
                0
            ]),
            t_range=[0, PI]
        )
        swirl_left.set_stroke(WHITE, width=2, opacity=0.7)
        
        swirl_right = swirl_left.copy()
        swirl_right.flip(RIGHT)
        swirl_right.shift(RIGHT * size * 1.6)
        
        skull.add(
            cranium, left_eye, right_eye, nose,
            jaw_curve, teeth_pattern,
            swirl_left, swirl_right
        )
        
        return skull
    
    def _create_minimal_skull(self, size: float) -> VGroup:
        """Create minimalist skull design."""
        skull = VGroup()
        
        # Simple curved cranium
        cranium = Circle(radius=size)
        cranium.stretch(1.2, 1)
        cranium.set_stroke(WHITE, width=4)
        cranium.set_fill(opacity=0)
        
        # Minimal eye sockets
        left_eye = Circle(radius=size * 0.2)
        left_eye.move_to(LEFT * size * 0.3 + UP * size * 0.2)
        left_eye.set_stroke(WHITE, width=3)
        left_eye.set_fill(opacity=0)
        
        right_eye = Circle(radius=size * 0.2)
        right_eye.move_to(RIGHT * size * 0.3 + UP * size * 0.2)
        right_eye.set_stroke(WHITE, width=3)
        right_eye.set_fill(opacity=0)
        
        # Simple nose
        nose = Line(
            DOWN * size * 0.05,
            DOWN * size * 0.25,
            stroke_width=3
        )
        
        # Minimal jaw indication
        jaw_line = Arc(
            radius=size * 0.7,
            start_angle=PI + PI/4,
            angle=-PI/2
        )
        jaw_line.move_to(DOWN * size * 0.5)
        jaw_line.set_stroke(WHITE, width=3)
        
        skull.add(cranium, left_eye, right_eye, nose, jaw_line)
        
        return skull
    
    def _create_decorative_skull(self, size: float) -> VGroup:
        """Create Day of the Dead style decorative skull."""
        skull = VGroup()
        
        # Base skull shape
        base = self._create_stylized_skull(size * 0.8)
        
        # Floral patterns around eyes
        for eye_pos in [LEFT * size * 0.35 + UP * size * 0.2, 
                        RIGHT * size * 0.35 + UP * size * 0.2]:
            for i in range(8):
                angle = i * TAU / 8
                petal = Ellipse(width=size * 0.1, height=size * 0.2)
                petal.move_to(eye_pos + size * 0.35 * np.array([
                    np.cos(angle), np.sin(angle), 0
                ]))
                petal.rotate(angle)
                petal.set_fill(PINK, opacity=0.8)
                petal.set_stroke(WHITE, width=1)
                skull.add(petal)
        
        # Decorative forehead design
        mandala = VGroup()
        for i in range(3):
            circle = Circle(radius=size * (0.15 - i * 0.05))
            circle.move_to(UP * size * 0.7)
            circle.set_stroke(GOLD, width=2)
            mandala.add(circle)
        
        # Chin decoration
        chin_design = RegularPolygon(n=6, radius=size * 0.2)
        chin_design.move_to(DOWN * size * 0.8)
        chin_design.set_fill(PURPLE, opacity=0.7)
        chin_design.set_stroke(WHITE, width=2)
        
        # Side swirls
        for side in [LEFT, RIGHT]:
            swirl = ParametricFunction(
                lambda t: np.array([
                    side[0] * size * (0.9 + 0.2 * np.sin(3*t)),
                    size * 0.3 * np.cos(2*t),
                    0
                ]),
                t_range=[0, PI]
            )
            swirl.set_stroke(GOLD, width=3)
            skull.add(swirl)
        
        skull.add(base, mandala, chin_design)
        
        return skull
    
    def _add_improved_eye_glow(self, skull: VGroup) -> None:
        """Add improved glowing effect to eye sockets."""
        eye_color = self.get_config('eye_color')
        
        # Find eye sockets in the skull
        for mob in skull:
            if isinstance(mob, VGroup):
                for submob in mob:
                    if self._is_eye_socket(submob):
                        self._add_glow_to_socket(submob, eye_color)
            elif self._is_eye_socket(mob):
                self._add_glow_to_socket(mob, eye_color)
    
    def _is_eye_socket(self, mob: Mobject) -> bool:
        """Check if a mobject is an eye socket."""
        # Check if it's black and roughly circular/elliptical
        if hasattr(mob, 'get_fill_color'):
            fill_color = mob.get_fill_color()
            if fill_color == BLACK or fill_color.to_hex() == '#000000':
                # Check if it's in the upper half of the skull
                if mob.get_center()[1] > 0:
                    return True
        return False
    
    def _add_glow_to_socket(self, socket: Mobject, color) -> None:
        """Add glow effect to a single eye socket."""
        center = socket.get_center()
        
        # Create multiple glow layers
        glow_group = VGroup()
        
        # Inner bright core
        core = Dot(radius=0.05, color=WHITE)
        core.move_to(center)
        core.set_glow_factor(1.0)
        
        # Middle glow
        middle = Circle(radius=0.15, color=color)
        middle.move_to(center)
        middle.set_fill(color, opacity=0.6)
        middle.set_stroke(width=0)
        
        # Outer glow
        outer = Circle(radius=0.25, color=color)
        outer.move_to(center)
        outer.set_fill(color, opacity=0.3)
        outer.set_stroke(width=0)
        
        socket.add(outer, middle, core)
    
    def animate(self, scene: Scene) -> None:
        """Animate the skull (optional animations)."""
        skull = self._mobjects[0]
        
        # Default: just add to scene
        # Subclasses can override for specific animations
        if not scene.mobjects.__contains__(skull):
            scene.add(skull)