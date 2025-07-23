"""
Centralized Text Management System for Manim Studio
Solves text fragmentation and positioning issues across 2D and 3D scenes
"""

from manim import *
from typing import Dict, List, Optional, Union, Tuple, Literal
import numpy as np
from dataclasses import dataclass
from enum import Enum

# Import existing typography system
from .visual_polish import Typography


class TextPosition(Enum):
    """Semantic positioning constants"""
    TOP_LEFT = "top_left"
    TOP_CENTER = "top_center" 
    TOP_RIGHT = "top_right"
    CENTER_LEFT = "center_left"
    CENTER = "center"
    CENTER_RIGHT = "center_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_CENTER = "bottom_center"
    BOTTOM_RIGHT = "bottom_right"


class TextLayer(Enum):
    """Text layering for different contexts"""
    BACKGROUND = 0
    CONTENT = 100
    OVERLAY = 200
    UI = 300
    FIXED_FRAME = 1000  # For 3D scenes


@dataclass
class TextStyle:
    """Complete text styling configuration"""
    font_size: int = 24
    color: str = WHITE
    font: str = "Arial"  # Use more common font
    weight: str = NORMAL
    stroke_width: float = 0
    stroke_color: str = BLACK
    fill_opacity: float = 1.0
    background: bool = False
    background_color: str = BLACK
    background_opacity: float = 0.8
    background_buff: float = 0.2


@dataclass
class TextLayout:
    """Text positioning and spacing configuration"""
    position: TextPosition = TextPosition.CENTER
    offset: np.ndarray = np.array([0, 0, 0])
    buff: float = 0.5
    layer: TextLayer = TextLayer.CONTENT
    fixed_in_frame: bool = False  # For 3D scenes
    max_width: Optional[float] = None
    alignment: str = "center"  # left, center, right


class TextManager:
    """Centralized text management system"""
    
    # Predefined styles for consistency
    STYLES = {
        'title': TextStyle(font_size=72, weight=BOLD, color=WHITE),
        'subtitle': TextStyle(font_size=48, color="#00d4ff"),
        'heading': TextStyle(font_size=36, weight=BOLD),
        'body': TextStyle(font_size=24),
        'caption': TextStyle(font_size=18, color=GRAY),
        'overlay': TextStyle(
            font_size=36, 
            background=True, 
            background_color=BLACK, 
            background_opacity=0.7
        ),
        'label_3d': TextStyle(
            font_size=28,
            background=True,
            background_color=BLACK,
            background_opacity=0.8,
            background_buff=0.3
        )
    }
    
    # Predefined layouts for common positions
    LAYOUTS = {
        'center': TextLayout(
            position=TextPosition.CENTER,
            layer=TextLayer.CONTENT
        ),
        'title': TextLayout(
            position=TextPosition.TOP_CENTER,
            offset=np.array([0, -0.5, 0]),
            layer=TextLayer.UI
        ),
        'subtitle': TextLayout(
            position=TextPosition.TOP_CENTER,
            offset=np.array([0, -1.5, 0]),
            layer=TextLayer.UI
        ),
        'bottom_label': TextLayout(
            position=TextPosition.BOTTOM_CENTER,
            layer=TextLayer.OVERLAY
        ),
        'corner_info': TextLayout(
            position=TextPosition.BOTTOM_RIGHT,
            offset=np.array([-0.5, 0.5, 0]),
            layer=TextLayer.UI
        ),
        'fixed_title_3d': TextLayout(
            position=TextPosition.TOP_CENTER,
            fixed_in_frame=True,
            layer=TextLayer.FIXED_FRAME
        ),
        'fixed_label_3d': TextLayout(
            position=TextPosition.BOTTOM_CENTER,
            fixed_in_frame=True,
            layer=TextLayer.FIXED_FRAME
        )
    }
    
    def __init__(self, scene):
        """Initialize with reference to the scene"""
        self.scene = scene
        self.active_texts: Dict[str, Mobject] = {}
        self.text_history: List[str] = []
        
    def create_text(
        self,
        text: str,
        style: Union[str, TextStyle] = 'body',
        layout: Union[str, TextLayout] = 'center',
        key: Optional[str] = None,
        **kwargs
    ) -> Mobject:
        """
        Create text with unified styling and positioning
        
        Args:
            text: Text content
            style: Style name or TextStyle object
            layout: Layout name or TextLayout object  
            key: Unique identifier for text management
            **kwargs: Override style/layout properties
        """
        # Resolve style
        if isinstance(style, str):
            text_style = self.STYLES.get(style, self.STYLES['body'])
        else:
            text_style = style
            
        # Resolve layout
        if isinstance(layout, str):
            text_layout = self.LAYOUTS.get(layout, self.LAYOUTS['center'])
        else:
            text_layout = layout
            
        # Apply kwargs overrides
        style_dict = text_style.__dict__.copy()
        layout_dict = text_layout.__dict__.copy()
        
        for k, v in kwargs.items():
            if k in style_dict:
                style_dict[k] = v
            elif k in layout_dict:
                layout_dict[k] = v
                
        # Create text object
        text_obj = self._create_text_object(text, style_dict)
        
        # Apply positioning
        positioned_text = self._apply_layout(text_obj, layout_dict)
        
        # Store reference if key provided
        if key:
            # Remove old text with same key
            if key in self.active_texts:
                self.scene.remove(self.active_texts[key])
            self.active_texts[key] = positioned_text
            
        return positioned_text
    
    def _create_text_object(self, text: str, style: Dict) -> Mobject:
        """Create the actual text mobject with styling"""
        # Create base text
        if style.get('font') == 'math':
            text_obj = MathTex(text, font_size=style['font_size'])
        else:
            text_obj = Text(
                text,
                font_size=style['font_size'],
                font=style.get('font', 'Arial'),
                weight=style.get('weight', NORMAL)
            )
        
        # Apply styling
        text_obj.set_color(style['color'])
        text_obj.set_fill(opacity=style['fill_opacity'])
        
        if style['stroke_width'] > 0:
            text_obj.set_stroke(style['stroke_color'], style['stroke_width'])
            
        # Add background if requested
        if style.get('background', False):
            bg_rect = Rectangle(
                width=text_obj.width + 2 * style['background_buff'],
                height=text_obj.height + 2 * style['background_buff'],
                fill_color=style['background_color'],
                fill_opacity=style['background_opacity'],
                stroke_width=0
            )
            bg_rect.move_to(text_obj.get_center())
            text_with_bg = VGroup(bg_rect, text_obj)
            return text_with_bg
            
        return text_obj
    
    def _apply_layout(self, text_obj: Mobject, layout: Dict) -> Mobject:
        """Apply positioning and layering to text object"""
        # Get scene dimensions - handle different camera types
        try:
            # For MovingCamera scenes
            frame = self.scene.camera.frame
            width = frame.width
            height = frame.height
        except AttributeError:
            # For regular scenes, use config dimensions
            from manim import config
            width = config.frame_width
            height = config.frame_height
        
        # Calculate position
        position = layout['position']
        offset = layout['offset']
        
        if isinstance(position, TextPosition):
            pos_map = {
                TextPosition.TOP_LEFT: np.array([-width/2, height/2, 0]),
                TextPosition.TOP_CENTER: np.array([0, height/2, 0]),
                TextPosition.TOP_RIGHT: np.array([width/2, height/2, 0]),
                TextPosition.CENTER_LEFT: np.array([-width/2, 0, 0]),
                TextPosition.CENTER: np.array([0, 0, 0]),
                TextPosition.CENTER_RIGHT: np.array([width/2, 0, 0]),
                TextPosition.BOTTOM_LEFT: np.array([-width/2, -height/2, 0]),
                TextPosition.BOTTOM_CENTER: np.array([0, -height/2, 0]),
                TextPosition.BOTTOM_RIGHT: np.array([width/2, -height/2, 0]),
            }
            base_pos = pos_map[position]
        else:
            base_pos = np.array([0, 0, 0])
            
        # Apply offset
        final_pos = base_pos + offset
        text_obj.move_to(final_pos)
        
        # Apply edge adjustments for corner positions
        buff = layout['buff']
        if position in [TextPosition.TOP_LEFT, TextPosition.CENTER_LEFT, TextPosition.BOTTOM_LEFT]:
            text_obj.to_edge(LEFT, buff=buff)
        elif position in [TextPosition.TOP_RIGHT, TextPosition.CENTER_RIGHT, TextPosition.BOTTOM_RIGHT]:
            text_obj.to_edge(RIGHT, buff=buff)
            
        if position in [TextPosition.TOP_LEFT, TextPosition.TOP_CENTER, TextPosition.TOP_RIGHT]:
            text_obj.to_edge(UP, buff=buff)
        elif position in [TextPosition.BOTTOM_LEFT, TextPosition.BOTTOM_CENTER, TextPosition.BOTTOM_RIGHT]:
            text_obj.to_edge(DOWN, buff=buff)
            
        # Apply layering
        if layout['layer'] != TextLayer.CONTENT:
            text_obj.set_z_index(layout['layer'].value)
            
        return text_obj
    
    def add_text(
        self,
        text: str,
        style: Union[str, TextStyle] = 'body',
        layout: Union[str, TextLayout] = 'center',
        key: Optional[str] = None,
        animation: Optional[Animation] = None,
        **kwargs
    ) -> Mobject:
        """Create and add text to scene with optional animation"""
        text_obj = self.create_text(text, style, layout, key, **kwargs)
        
        # Handle 3D scene fixed frame positioning
        if hasattr(self.scene, 'add_fixed_in_frame_mobjects') and \
           (layout == 'fixed_title_3d' or layout == 'fixed_label_3d' or 
            (isinstance(layout, TextLayout) and layout.fixed_in_frame)):
            self.scene.add_fixed_in_frame_mobjects(text_obj)
        else:
            self.scene.add(text_obj)
        
        # Apply animation
        if animation:
            if isinstance(animation, type):
                # If animation is a class, instantiate it with the text object
                animation_instance = animation(text_obj)
            else:
                # If it's already an animation instance
                animation_instance = animation
            self.scene.play(animation_instance)
        
        return text_obj
    
    def update_text(
        self,
        key: str,
        new_text: str,
        animation: Optional[Animation] = None,
        **kwargs
    ) -> Optional[Mobject]:
        """Update existing text by key"""
        if key not in self.active_texts:
            return None
            
        old_text = self.active_texts[key]
        
        # Create new text with same positioning
        new_text_obj = self.create_text(new_text, **kwargs)
        new_text_obj.move_to(old_text.get_center())
        
        # Handle 3D fixed frame
        if hasattr(self.scene, 'add_fixed_in_frame_mobjects'):
            self.scene.add_fixed_in_frame_mobjects(new_text_obj)
        else:
            self.scene.add(new_text_obj)
        
        # Animate transition
        if animation:
            if isinstance(animation, type):
                animation_instance = animation(old_text, new_text_obj)
            else:
                animation_instance = animation
            self.scene.play(animation_instance)
        else:
            self.scene.play(Transform(old_text, new_text_obj))
            
        self.active_texts[key] = new_text_obj
        return new_text_obj
    
    def remove_text(
        self,
        key: str,
        animation: Optional[Animation] = None
    ):
        """Remove text by key"""
        if key not in self.active_texts:
            return
            
        text_obj = self.active_texts[key]
        
        if animation:
            if isinstance(animation, type):
                animation_instance = animation(text_obj)
            else:
                animation_instance = animation
            self.scene.play(animation_instance)
        
        self.scene.remove(text_obj)
        del self.active_texts[key]
    
    def clear_all_text(self, animation: Optional[Animation] = None):
        """Remove all managed text"""
        if not self.active_texts:
            return
            
        if animation:
            if isinstance(animation, type):
                # Create animation for all text objects
                animation_instances = [animation(text_obj) for text_obj in self.active_texts.values()]
                self.scene.play(*animation_instances)
            else:
                self.scene.play(animation)
        
        for text_obj in self.active_texts.values():
            self.scene.remove(text_obj)
        
        self.active_texts.clear()
    
    def create_text_sequence(
        self,
        texts: List[Tuple[str, str, str]],  # [(text, style, layout), ...]
        duration: float = 2.0,
        transition: type = Transform
    ):
        """Create animated sequence of text changes"""
        if not texts:
            return
            
        # Create first text
        first_text, first_style, first_layout = texts[0]
        current_text = self.add_text(
            first_text, 
            first_style, 
            first_layout,
            key="sequence",
            animation=Write(self.active_texts.get("sequence"))
        )
        
        self.scene.wait(duration)
        
        # Transition through remaining texts
        for text, style, layout in texts[1:]:
            self.update_text(
                "sequence",
                text,
                animation=transition(
                    self.active_texts["sequence"],
                    self.create_text(text, style, layout)
                )
            )
            self.scene.wait(duration)


# Convenience functions for common use cases
def create_title_with_subtitle(
    scene,
    title: str,
    subtitle: str = "",
    title_style: str = 'title',
    subtitle_style: str = 'subtitle'
) -> VGroup:
    """Create title with subtitle using text manager"""
    text_manager = TextManager(scene)
    
    title_obj = text_manager.create_text(title, title_style, 'title')
    objects = [title_obj]
    
    if subtitle:
        subtitle_obj = text_manager.create_text(subtitle, subtitle_style, 'subtitle')
        objects.append(subtitle_obj)
    
    return VGroup(*objects)


def create_3d_overlay_text(
    scene,
    text: str,
    position: str = 'bottom_center'
) -> Mobject:
    """Create text overlay for 3D scenes"""
    text_manager = TextManager(scene)
    
    layout_map = {
        'top_center': 'fixed_title_3d',
        'bottom_center': 'fixed_label_3d'
    }
    
    return text_manager.add_text(
        text,
        style='label_3d',
        layout=layout_map.get(position, 'fixed_label_3d'),
        animation=FadeIn
    )


# Export all classes and functions
__all__ = [
    'TextManager', 'TextPosition', 'TextLayer', 'TextStyle', 'TextLayout',
    'create_title_with_subtitle', 'create_3d_overlay_text'
]