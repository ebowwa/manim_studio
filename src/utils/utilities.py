"""Manim utilities ported from xiaoxiae's high-quality video repository."""
from manim import *
from math import *
from random import *
from functools import *
from itertools import *
from typing import List, Tuple, Dict, Optional, Callable, Any


def fade(f: Callable) -> Callable:
    """A decorator for construct method of scenes where all objects should fade at the end."""
    def inner(self):
        f(self)
        self.play(*[FadeOut(mob) for mob in self.mobjects])
    return inner


def fade_all(self) -> None:
    """Fade out all mobjects in the scene."""
    self.play(*[FadeOut(mob) for mob in self.mobjects])


def create_code(self, code: Code) -> List[Animation]:
    """Creates code more evenly with background, code, and line numbers."""
    return [
        Create(code.background_mobject), 
        Write(code.code), 
        Write(code.line_numbers)
    ]


def myCode(*args, **kwargs) -> Code:
    """Declares a nice-looking code block with consistent styling."""
    code = Code(
        *args, **kwargs, 
        font="Fira Mono", 
        line_spacing=0.35, 
        style="Monokai"
    )
    code.background_mobject[0].set_style(fill_opacity=0)
    return code


def myOutput(*args, **kwargs) -> Code:
    """Declares a nice-looking output block without line numbers."""
    code = Code(
        *args, **kwargs, 
        font="Fira Mono", 
        line_spacing=0.35, 
        style="Monokai", 
        insert_line_no=False
    )
    code.background_mobject[0].set_style(fill_opacity=0)
    return code


def highlightText(text: VGroup) -> None:
    """Highlight alternating text elements in yellow."""
    for i in range(1, len(text), 2):
        text[i].set_color(YELLOW)


def createHighlightedParagraph(
    *args, 
    speed: float = 0.04, 
    width: int = 22, 
    size: str = r"\normalsize", 
    splitBy: Optional[str] = None
) -> Tuple[float, Tex]:
    """Create a paragraph with highlighted alternating segments.
    
    Returns:
        Tuple of (animation_time, text_mobject)
    """
    if splitBy is not None:
        args = args[0].split(splitBy)
    
    text = Tex(
        r"\parbox{" + str(width) + "em}{" + size + " " + args[0], 
        *args[1:-1], 
        args[-1] + "}"
    )
    highlightText(text)
    return len("".join(args).replace("$", "")) * speed, text


def visuallyChangeColor(self, color_changes: List[Tuple[VMobject, str]]) -> None:
    """Animate color changes with visual feedback using Flash effects.
    
    Args:
        color_changes: List of (mobject, new_color) tuples
    """
    self.play(
        *[mob.animate.set_color(color) for mob, color in color_changes],
        *[Flash(mob, color=color) for mob, color in color_changes],
    )


def get_fade_rect(
    mobject: VMobject, 
    opacity: float = 0.7, 
    color: str = BLACK
) -> Rectangle:
    """Create a fade overlay rectangle for the given mobject."""
    rect = Rectangle(
        width=mobject.width + 0.1,
        height=mobject.height + 0.1,
        fill_opacity=opacity,
        stroke_opacity=0,
        color=color
    )
    rect.move_to(mobject)
    return rect


def staggered_animation_group(
    animations: List[Animation], 
    lag_ratio: float = 0.1
) -> AnimationGroup:
    """Create a staggered animation group with consistent lag ratio."""
    return AnimationGroup(*animations, lag_ratio=lag_ratio)


def create_title_transition(
    self,
    title: str,
    subtitle: Optional[str] = None,
    fade_time: float = 1.0,
    wait_time: float = 2.0
) -> None:
    """Create a standard title → fade transition."""
    title_tex = Text(title, font_size=48)
    
    if subtitle:
        subtitle_tex = Text(subtitle, font_size=32)
        title_group = VGroup(title_tex, subtitle_tex).arrange(DOWN, buff=0.5)
        self.play(FadeIn(title_group, shift=UP))
    else:
        self.play(FadeIn(title_tex, shift=UP))
    
    self.wait(wait_time)
    self.play(FadeOut(title_tex if not subtitle else title_group))
    self.wait(fade_time)


def hsv_to_rgb(h: float, s: float, v: float) -> Tuple[float, float, float]:
    """Convert HSV to RGB color space (values normalized 0-1)."""
    i = floor(h * 6)
    f = h * 6 - i
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    
    return [
        (v, t, p),
        (q, v, p),
        (p, v, t),
        (p, q, v),
        (t, p, v),
        (v, p, q),
    ][int(i % 6)]


def rainbow_to_rgb(i: float, s: float = 0.7) -> str:
    """Return a color from rainbow gradient as hex string."""
    return rgb_to_hex(hsv_to_rgb(i, s, 1))


class ProgressiveCodeReveal:
    """Helper class for progressive code reveal animations."""
    
    def __init__(self, code: Code):
        self.code = code
        self.lines = code.code.lines
        self.current_line = 0
    
    def reveal_next_line(self, scene: Scene) -> None:
        """Reveal the next line of code."""
        if self.current_line < len(self.lines):
            scene.play(Write(self.lines[self.current_line]))
            self.current_line += 1
    
    def reveal_lines(self, scene: Scene, start: int, end: int) -> None:
        """Reveal a range of lines."""
        for i in range(start, min(end, len(self.lines))):
            if i >= self.current_line:
                scene.play(Write(self.lines[i]))
                self.current_line = i + 1
    
    def highlight_lines(
        self, 
        scene: Scene, 
        lines: List[int], 
        color: str = YELLOW
    ) -> None:
        """Highlight specific lines of code."""
        for line_num in lines:
            if 0 <= line_num < len(self.lines):
                scene.play(
                    self.lines[line_num].animate.set_color(color),
                    Flash(self.lines[line_num], color=color)
                )