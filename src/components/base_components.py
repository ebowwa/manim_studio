from src.config.manim_config import config
from manim import *
import os
from typing import Optional, Union, List, Tuple, Any
from pathlib import Path

class StudioText:
    def __init__(self) -> None:
        self.default_font_size: int = 48
        self.title_scale: float = 1.5
        self.subtitle_scale: float = 1.0
        self.default_color: ManimColor = WHITE
        self.background_opacity: float = 0.7

    def create_title(
        self, 
        text: str, 
        scale: Optional[float] = None, 
        color: Optional[ManimColor] = None
    ) -> VGroup:
        scale = scale or self.title_scale
        color = color or self.default_color
        
        # Create text with proper formatting
        title = Text(
            text,
            font_size=self.default_font_size,
            color=color,
            weight="BOLD"
        ).scale(scale)
        
        # Add subtle background for better readability
        background = Rectangle(
            width=title.width + 0.5,
            height=title.height + 0.3,
            fill_color=BLACK,
            fill_opacity=self.background_opacity,
            stroke_width=0
        )
        
        return VGroup(background, title)
    
    def create_subtitle(
        self, 
        text: str, 
        scale: Optional[float] = None, 
        color: Optional[ManimColor] = None
    ) -> VGroup:
        scale = scale or self.subtitle_scale
        color = color or self.default_color
        
        # Create text with proper formatting
        subtitle = Text(
            text,
            font_size=self.default_font_size,
            color=color
        ).scale(scale)
        
        # Add subtle background for better readability
        background = Rectangle(
            width=subtitle.width + 0.4,
            height=subtitle.height + 0.2,
            fill_color=BLACK,
            fill_opacity=self.background_opacity,
            stroke_width=0
        )
        
        return VGroup(background, subtitle)
    
    def create_paragraph(
        self, 
        text: str, 
        width: float = 6, 
        scale: float = 0.8, 
        color: Optional[ManimColor] = None
    ) -> VGroup:
        color = color or self.default_color
        
        # Create text with proper formatting and wrapping
        paragraph = MarkupText(
            text,
            font_size=self.default_font_size,
            color=color,
            line_spacing=0.5
        ).scale(scale)
        
        # Wrap text to specified width
        paragraph.width = width
        
        # Add subtle background
        background = Rectangle(
            width=paragraph.width + 0.4,
            height=paragraph.height + 0.2,
            fill_color=BLACK,
            fill_opacity=self.background_opacity,
            stroke_width=0
        )
        
        return VGroup(background, paragraph)

class StudioImage:
    @staticmethod
    def load_image(
        image_path: Union[str, Path], 
        scale: float = 1.0
    ) -> Union[Rectangle, ImageMobject]:
        if not os.path.exists(str(image_path)):
            # Create a placeholder rectangle if image doesn't exist
            return Rectangle(height=4, width=6, color=BLUE).scale(scale)
        return ImageMobject(str(image_path)).scale(scale)

class StudioTransitions:
    @staticmethod
    def fade_transform(
        scene: Scene, 
        out_mobjects: Union[Mobject, List[Mobject]], 
        in_mobjects: Union[Mobject, List[Mobject]], 
        duration: float = 1.0
    ) -> None:
        # Ensure all mobjects are lists
        out_mobjects = [out_mobjects] if not isinstance(out_mobjects, list) else out_mobjects
        in_mobjects = [in_mobjects] if not isinstance(in_mobjects, list) else in_mobjects
        
        # Create smooth crossfade effect
        scene.play(
            *[FadeOut(mob, run_time=duration*0.8) for mob in out_mobjects],
            *[FadeIn(mob.set_opacity(0), run_time=duration*0.8) for mob in in_mobjects],
            rate_func=smooth
        )
    
    @staticmethod
    def slide_transform(
        scene: Scene, 
        out_mobjects: Union[Mobject, List[Mobject]], 
        in_mobjects: Union[Mobject, List[Mobject]], 
        direction: np.ndarray = LEFT, 
        duration: float = 1.0
    ) -> None:
        # Ensure all mobjects are lists
        out_mobjects = [out_mobjects] if not isinstance(out_mobjects, list) else out_mobjects
        in_mobjects = [in_mobjects] if not isinstance(in_mobjects, list) else in_mobjects
        
        # Position incoming mobjects off-screen
        for mob in in_mobjects:
            mob.shift(-direction * scene.camera.frame_width)
        
        # Create smooth slide transition
        scene.play(
            *[mob.animate.shift(direction * scene.camera.frame_width).set_opacity(0) 
              for mob in out_mobjects],
            *[mob.animate.shift(direction * scene.camera.frame_width).set_opacity(1) 
              for mob in in_mobjects],
            rate_func=smooth,
            run_time=duration
        )
