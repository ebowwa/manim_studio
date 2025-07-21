"""
Indication Effects for Manim Studio
Adapted from manimlib.animation.indication for compatibility with manim_studio
"""

from __future__ import annotations
import numpy as np
from typing import Callable, TYPE_CHECKING

# Manim imports
from manim import *
from manim import Animation, AnimationGroup, Succession, Transform
from manim import FadeOut, FadeIn, Write, ShowCreation
from manim import VMobject, VGroup, Circle, Dot, Line, Mobject
from manim import GREY, YELLOW, ORIGIN, RIGHT, UP, SMALL_BUFF
from manim import interpolate, there_and_back, smooth

# Manim Studio imports
from .base_effect import BaseEffect
from .effect_registry import register_effect

if TYPE_CHECKING:
    from manim.typing import Vector3D


@register_effect("focus_on")
class FocusOn(Transform, BaseEffect):
    """Creates a focus spotlight effect on a point or object"""
    
    def __init__(
        self,
        focus_point: Vector3D | Mobject,
        opacity: float = 0.2,
        color: str = GREY,
        run_time: float = 2,
        remover: bool = True,
        **kwargs
    ):
        self.focus_point = focus_point
        self.opacity = opacity
        self.color = color
        
        # Initialize with blank mobject
        super().__init__(VMobject(), run_time=run_time, remover=remover, **kwargs)

    def create_target(self) -> Dot:
        little_dot = Dot(radius=0)
        little_dot.set_fill(self.color, opacity=self.opacity)
        little_dot.add_updater(lambda d: d.move_to(self.focus_point))
        return little_dot

    def create_starting_mobject(self) -> Dot:
        return Dot(
            radius=config.frame_x_radius + config.frame_y_radius,
            stroke_width=0,
            fill_color=self.color,
            fill_opacity=0,
        )


@register_effect("indicate")
class Indicate(Transform, BaseEffect):
    """Scales and colors an object to indicate attention"""
    
    def __init__(
        self,
        mobject: Mobject,
        scale_factor: float = 1.2,
        color: str = YELLOW,
        rate_func: Callable[[float], float] = there_and_back,
        **kwargs
    ):
        self.scale_factor = scale_factor
        self.color = color
        super().__init__(mobject, rate_func=rate_func, **kwargs)

    def create_target(self) -> Mobject:
        target = self.mobject.copy()
        target.scale(self.scale_factor)
        target.set_color(self.color)
        return target


@register_effect("flash")
class Flash(AnimationGroup, BaseEffect):
    """Creates a flash effect with radiating lines"""
    
    def __init__(
        self,
        point: Vector3D | Mobject,
        color: str = YELLOW,
        line_length: float = 0.2,
        num_lines: int = 12,
        flash_radius: float = 0.3,
        line_stroke_width: float = 3.0,
        run_time: float = 1.0,
        **kwargs
    ):
        self.point = point
        self.color = color
        self.line_length = line_length
        self.num_lines = num_lines
        self.flash_radius = flash_radius
        self.line_stroke_width = line_stroke_width

        self.lines = self.create_lines()
        animations = self.create_line_anims()
        super().__init__(
            *animations,
            group=self.lines,
            run_time=run_time,
            **kwargs,
        )

    def create_lines(self) -> VGroup:
        lines = VGroup()
        for angle in np.arange(0, TAU, TAU / self.num_lines):
            line = Line(ORIGIN, self.line_length * RIGHT)
            line.shift((self.flash_radius - self.line_length) * RIGHT)
            line.rotate(angle, about_point=ORIGIN)
            lines.add(line)
        lines.set_stroke(
            color=self.color,
            width=self.line_stroke_width
        )
        lines.add_updater(lambda l: l.move_to(self.point))
        return lines

    def create_line_anims(self) -> list[Animation]:
        return [
            ShowCreationThenDestruction(line)
            for line in self.lines
        ]


@register_effect("circle_indicate")
class CircleIndicate(Transform, BaseEffect):
    """Creates a circle around an object that scales in and out"""
    
    def __init__(
        self,
        mobject: Mobject,
        scale_factor: float = 1.2,
        rate_func: Callable[[float], float] = there_and_back,
        stroke_color: str = YELLOW,
        stroke_width: float = 3.0,
        remover: bool = True,
        **kwargs
    ):
        circle = Circle(stroke_color=stroke_color, stroke_width=stroke_width)
        circle.surround(mobject)
        pre_circle = circle.copy().set_stroke(width=0)
        pre_circle.scale(1 / scale_factor)
        super().__init__(
            pre_circle, circle,
            rate_func=rate_func,
            remover=remover,
            **kwargs
        )


@register_effect("show_passing_flash")
class ShowPassingFlash(Animation, BaseEffect):
    """Shows a flash that passes along an object"""
    
    def __init__(
        self,
        mobject: Mobject,
        time_width: float = 0.1,
        remover: bool = True,
        **kwargs
    ):
        self.time_width = time_width
        super().__init__(
            mobject,
            remover=remover,
            **kwargs
        )

    def interpolate_mobject(self, alpha: float) -> None:
        lower, upper = self.get_bounds(alpha)
        self.mobject.pointwise_become_partial(
            self.starting_mobject, lower, upper
        )

    def get_bounds(self, alpha: float) -> tuple[float, float]:
        tw = self.time_width
        upper = interpolate(0, 1 + tw, alpha)
        lower = upper - tw
        upper = min(upper, 1)
        lower = max(lower, 0)
        return (lower, upper)

    def finish(self) -> None:
        super().finish()
        self.mobject.pointwise_become_partial(self.starting_mobject, 0, 1)


@register_effect("wiggle_out_then_in")
class WiggleOutThenIn(Animation, BaseEffect):
    """Wiggles an object by scaling and rotating"""
    
    def __init__(
        self,
        mobject: Mobject,
        scale_value: float = 1.1,
        rotation_angle: float = 0.01 * TAU,
        n_wiggles: int = 6,
        scale_about_point: Vector3D | None = None,
        rotate_about_point: Vector3D | None = None,
        run_time: float = 2,
        **kwargs
    ):
        self.scale_value = scale_value
        self.rotation_angle = rotation_angle
        self.n_wiggles = n_wiggles
        self.scale_about_point = scale_about_point
        self.rotate_about_point = rotate_about_point
        super().__init__(mobject, run_time=run_time, **kwargs)

    def get_scale_about_point(self) -> Vector3D:
        return self.scale_about_point or self.mobject.get_center()

    def get_rotate_about_point(self) -> Vector3D:
        return self.rotate_about_point or self.mobject.get_center()

    def interpolate_mobject(self, alpha: float) -> None:
        self.mobject.restore()
        self.mobject.scale(
            interpolate(1, self.scale_value, there_and_back(alpha)),
            about_point=self.get_scale_about_point()
        )
        # Simple wiggle function
        wiggle_alpha = np.sin(alpha * self.n_wiggles * TAU) * there_and_back(alpha)
        self.mobject.rotate(
            wiggle_alpha * self.rotation_angle,
            about_point=self.get_rotate_about_point()
        )


@register_effect("show_creation_then_destruction")
class ShowCreationThenDestruction(ShowPassingFlash):
    """Shows creation of an object then destroys it"""
    
    def __init__(self, vmobject: VMobject, time_width: float = 2.0, **kwargs):
        super().__init__(vmobject, time_width=time_width, **kwargs)


@register_effect("show_creation_then_fade_out")
class ShowCreationThenFadeOut(Succession, BaseEffect):
    """Shows creation of an object then fades it out"""
    
    def __init__(self, mobject: Mobject, remover: bool = True, **kwargs):
        super().__init__(
            ShowCreation(mobject),
            FadeOut(mobject),
            remover=remover,
            **kwargs
        )


@register_effect("apply_wave")
class ApplyWave(Animation, BaseEffect):
    """Applies a wave effect across an object"""
    
    def __init__(
        self,
        mobject: Mobject,
        direction: Vector3D = UP,
        amplitude: float = 0.2,
        run_time: float = 1.0,
        **kwargs
    ):
        self.direction = direction
        self.amplitude = amplitude
        self.left_x = mobject.get_left()[0]
        self.right_x = mobject.get_right()[0]
        self.vect = amplitude * direction
        super().__init__(mobject, run_time=run_time, **kwargs)

    def interpolate_mobject(self, alpha: float) -> None:
        def wave_function(point):
            x, y, z = point
            if self.right_x == self.left_x:
                relative_x = 0
            else:
                relative_x = (x - self.left_x) / (self.right_x - self.left_x)
            power = np.exp(2.0 * (relative_x - 0.5))
            nudge = there_and_back(alpha**power)
            return point + nudge * self.vect
        
        self.mobject.restore()
        self.mobject.apply_function(wave_function)


# Export all effects
__all__ = [
    "FocusOn",
    "Indicate", 
    "Flash",
    "CircleIndicate",
    "ShowPassingFlash",
    "WiggleOutThenIn",
    "ShowCreationThenDestruction",
    "ShowCreationThenFadeOut",
    "ApplyWave",
]