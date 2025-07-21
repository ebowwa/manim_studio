"""Advanced custom animations ported from xiaoxiae's videos."""
from manim import *
from typing import Optional, Callable, Any
import numpy as np


class MoveAndFadeThereBack(Animation):
    """Move an object along a path while fading out and back in."""
    
    def __init__(
        self,
        mobject: Mobject,
        shift: np.ndarray = RIGHT,
        **kwargs
    ):
        self.original = mobject.copy()
        self.shift = shift
        super().__init__(mobject, **kwargs)
    
    def interpolate_mobject(self, alpha: float) -> None:
        new_alpha = self.rate_func(alpha)
        
        if new_alpha < 0.5:
            # First half: move and fade out
            self.mobject.move_to(
                self.original.get_center() + self.shift * (new_alpha * 2)
            )
            self.mobject.set_opacity(1 - new_alpha * 2)
        else:
            # Second half: move back and fade in
            self.mobject.move_to(
                self.original.get_center() + self.shift * (2 - new_alpha * 2)
            )
            self.mobject.set_opacity((new_alpha - 0.5) * 2)


class Increment(Animation):
    """Animate incrementing a number with upward movement."""
    
    def __init__(
        self,
        mobject: Mobject,
        number: int,
        distance: float = 1.0,
        **kwargs
    ):
        super().__init__(mobject, **kwargs)
        self.number = number
        self.distance = distance
        self.became = False
        self.start = mobject.get_center()
    
    def interpolate_mobject(self, alpha: float) -> None:
        # Change number at midpoint
        if alpha > 0.5 and not self.became:
            self.mobject.become(
                Tex(r"\textbf{" + str(self.number) + "}").move_to(self.mobject)
            )
            self.became = True
        
        # Move upward
        new_alpha = self.rate_func(alpha)
        self.mobject.move_to(self.start + UP * self.distance * new_alpha)


class Wiggle(Animation):
    """Wiggle animation for objects."""
    
    def __init__(
        self,
        mobject: Mobject,
        scale_factor: float = 1.2,
        n_wiggles: int = 6,
        rotation_angle: float = 0.015,
        scale_about_point: Optional[np.ndarray] = None,
        rotate_about_point: Optional[np.ndarray] = None,
        **kwargs
    ):
        self.scale_factor = scale_factor
        self.n_wiggles = n_wiggles
        self.rotation_angle = rotation_angle
        self.scale_about_point = scale_about_point
        self.rotate_about_point = rotate_about_point
        super().__init__(mobject, **kwargs)
    
    def interpolate_mobject(self, alpha: float) -> None:
        # Calculate wiggle phase
        wiggle_phase = np.sin(alpha * self.n_wiggles * 2 * PI)
        
        # Apply scaling
        scale = 1 + (self.scale_factor - 1) * abs(wiggle_phase) * (1 - alpha)
        self.mobject.scale(
            scale,
            about_point=self.scale_about_point or self.mobject.get_center()
        )
        
        # Apply rotation
        self.mobject.rotate(
            self.rotation_angle * wiggle_phase,
            about_point=self.rotate_about_point or self.mobject.get_center()
        )


class MoveAlongPathShow(Animation):
    """Move object along a path while revealing it."""
    
    def __init__(
        self,
        mobject: Mobject,
        path: VMobject,
        **kwargs
    ):
        self.path = path
        super().__init__(mobject, **kwargs)
    
    def interpolate_mobject(self, alpha: float) -> None:
        point = self.path.point_from_proportion(alpha)
        self.mobject.move_to(point)
        self.mobject.set_opacity(alpha)


class SwitchZIndex(Animation):
    """Animation to switch z-index ordering."""
    
    def __init__(
        self,
        mobject: Mobject,
        new_z_index: float,
        **kwargs
    ):
        self.new_z_index = new_z_index
        self.original_z_index = mobject.get_z_index()
        super().__init__(mobject, **kwargs)
    
    def interpolate_mobject(self, alpha: float) -> None:
        if alpha < 0.5:
            self.mobject.set_z_index(self.original_z_index)
        else:
            self.mobject.set_z_index(self.new_z_index)


class FlashWithColor(Flash):
    """Enhanced Flash animation with customizable parameters."""
    
    def __init__(
        self,
        point: Mobject,
        color: str = YELLOW,
        flash_radius: float = 0.5,
        line_length: float = 0.3,
        num_lines: int = 12,
        flash_up: bool = True,
        **kwargs
    ):
        super().__init__(
            point,
            color=color,
            flash_radius=flash_radius,
            line_length=line_length,
            num_lines=num_lines,
            **kwargs
        )


# Custom rate functions for complex animations
def rush_into_with_pause(t: float, pause_ratio: float = 0.1) -> float:
    """Rush into animation with pause at the end."""
    if t < 1 - pause_ratio:
        return rush_into(t / (1 - pause_ratio))
    return 1


def rush_from_with_pause(t: float, pause_ratio: float = 0.1) -> float:
    """Rush from animation with pause at the beginning."""
    if t < pause_ratio:
        return 0
    return rush_from((t - pause_ratio) / (1 - pause_ratio))


def there_and_back_with_pause(t: float, pause_ratio: float = 0.2) -> float:
    """There and back animation with pause in the middle."""
    if t < 0.5 - pause_ratio/2:
        return 2 * t / (1 - pause_ratio)
    elif t < 0.5 + pause_ratio/2:
        return 1
    else:
        return 2 * (1 - t) / (1 - pause_ratio)


# Animation composition helpers
class AnimationSequence:
    """Helper for creating complex animation sequences."""
    
    def __init__(self, scene: Scene):
        self.scene = scene
        self.animations = []
    
    def add(
        self,
        *animations: Animation,
        lag_ratio: float = 0,
        run_time: Optional[float] = None
    ) -> 'AnimationSequence':
        """Add animations to the sequence."""
        if lag_ratio > 0:
            group = AnimationGroup(*animations, lag_ratio=lag_ratio)
            if run_time:
                group.run_time = run_time
            self.animations.append(group)
        else:
            self.animations.extend(animations)
        return self
    
    def wait(self, duration: float) -> 'AnimationSequence':
        """Add a wait to the sequence."""
        self.animations.append(Wait(duration))
        return self
    
    def play(self) -> None:
        """Play the entire sequence."""
        for anim in self.animations:
            if isinstance(anim, Wait):
                self.scene.wait(anim.duration)
            else:
                self.scene.play(anim)


class ComplexAnimationBuilder:
    """Builder for complex multi-phase animations."""
    
    def __init__(self):
        self.phases = []
        self.current_phase = []
    
    def add_animation(self, animation: Animation) -> 'ComplexAnimationBuilder':
        """Add animation to current phase."""
        self.current_phase.append(animation)
        return self
    
    def add_group(
        self,
        *animations: Animation,
        lag_ratio: float = 0.1
    ) -> 'ComplexAnimationBuilder':
        """Add animation group to current phase."""
        self.current_phase.append(
            AnimationGroup(*animations, lag_ratio=lag_ratio)
        )
        return self
    
    def next_phase(self) -> 'ComplexAnimationBuilder':
        """Start a new phase."""
        if self.current_phase:
            self.phases.append(self.current_phase)
            self.current_phase = []
        return self
    
    def build(self) -> Succession:
        """Build the final animation."""
        if self.current_phase:
            self.phases.append(self.current_phase)
        
        return Succession(
            *[AnimationGroup(*phase) for phase in self.phases]
        )