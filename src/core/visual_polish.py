"""
Visual Polish System - Professional video production techniques
Based on xiaoxiae's proven approaches to typography, assets, and layering
"""

from manim import *
from typing import Dict, List, Optional, Union, Tuple
import numpy as np
from pathlib import Path

# Typography System
class Typography:
    """Professional typography system with consistent hierarchy"""
    
    # Font Configuration
    FONTS = {
        'code': 'Fira Mono',
        'math': 'Latin Modern Math',  # LaTeX default
        'text': 'Source Sans Pro'
    }
    
    # Size Hierarchy (following xiaoxiae's patterns)
    SIZES = {
        'title': 56,           # \\Huge equivalent
        'subtitle': 42,        # \\Large equivalent  
        'heading': 32,         # \\large equivalent
        'body': 24,           # Default size
        'caption': 18,        # Small text
        'micro': 14           # Very small labels
    }
    
    # Spacing Constants (xiaoxiae's micro-adjustments)
    MICRO_ADJUSTMENTS = {
        'tiny': 0.02,
        'small': 0.05,
        'medium': 0.08,
        'large': 0.1
    }
    
    @staticmethod
    def create_title(text: str, size: str = 'title', **kwargs) -> Text:
        """Create consistently styled title text"""
        return Text(
            text,
            font_size=Typography.SIZES[size],
            weight=BOLD,
            **kwargs
        )
    
    @staticmethod  
    def create_math(latex: str, size: str = 'body', **kwargs) -> Tex:
        """Create mathematical notation with proper sizing"""
        size_map = {
            'title': r'\Huge',
            'subtitle': r'\Large', 
            'heading': r'\large',
            'body': r'\normalsize',
            'caption': r'\small',
            'micro': r'\tiny'
        }
        return Tex(f"{size_map[size]} {latex}", **kwargs)
    
    @staticmethod
    def create_code(
        code: str, 
        language: str = "python",
        style: str = "monokai",
        **kwargs
    ) -> Code:
        """Create code block with xiaoxiae's styling"""
        code_obj = Code(
            code_string=code,
            language=language,
            formatter_style=style,
            **kwargs
        )
        # Apply xiaoxiae's background styling
        if hasattr(code_obj, 'background_mobject') and code_obj.background_mobject:
            code_obj.background_mobject[0].set(
                stroke_color=WHITE,
                stroke_width=2.5,
                fill_opacity=0
            )
        return code_obj
    
    @staticmethod
    def create_highlighted_text(
        *text_parts: str,
        highlight_color: str = YELLOW,
        **kwargs
    ) -> VGroup:
        """Create text with alternating highlights (xiaoxiae pattern)"""
        text_objects = []
        for i, part in enumerate(text_parts):
            color = highlight_color if i % 2 == 1 else WHITE
            text_objects.append(Text(part, color=color, **kwargs))
        
        return VGroup(*text_objects).arrange(RIGHT, buff=0.1)
    
    @staticmethod
    def apply_micro_adjustment(
        mobject: Mobject,
        direction: np.ndarray,
        amount: str = 'small'
    ) -> Mobject:
        """Apply xiaoxiae-style micro-positioning adjustments"""
        offset = Typography.MICRO_ADJUSTMENTS[amount]
        return mobject.shift(direction * offset)


# Asset Management System  
class AssetManager:
    """Professional asset handling with preprocessing and optimization"""
    
    def __init__(self, asset_root: str = "assets"):
        self.asset_root = Path(asset_root)
        self.cache = {}
        
    def get_svg_symbol(self, symbol_name: str, **kwargs) -> SVGMobject:
        """Load optimized SVG symbols (like xiaoxiae's mathematical chars)"""
        svg_path = self.asset_root / "symbols" / f"{symbol_name}.svg"
        
        if symbol_name not in self.cache:
            if svg_path.exists():
                self.cache[symbol_name] = SVGMobject(str(svg_path), **kwargs)
            else:
                # Fallback to text
                self.cache[symbol_name] = Text(symbol_name, **kwargs)
                
        return self.cache[symbol_name].copy()
    
    def get_image_variant(
        self,
        image_name: str,
        variant: str = "default",
        **kwargs
    ) -> ImageMobject:
        """Get specific image variant (cropped, outline, etc.)"""
        variants = {
            "default": f"{image_name}.png",
            "cropped": f"{image_name}-cropped.png", 
            "outline": f"{image_name}-outline.png",
            "flipped": f"{image_name}-flopped.png"
        }
        
        image_path = self.asset_root / "images" / variants.get(variant, variants["default"])
        
        if image_path.exists():
            return ImageMobject(str(image_path), **kwargs)
        else:
            # Fallback to placeholder
            return Rectangle(width=2, height=1, color=GRAY, **kwargs)
    
    def create_color_fill(self, color: str, size: float = 100) -> ImageMobject:
        """Create solid color fill (xiaoxiae's black.png pattern)"""
        # In production, this would load pre-generated color PNGs
        # For now, create programmatically
        return Rectangle(
            width=size, height=size,
            fill_color=color, fill_opacity=1,
            stroke_width=0
        )


# Layering System
class LayerManager:
    """Semantic z-index management system"""
    
    # Z-Index Hierarchy (based on xiaoxiae's patterns)
    LAYERS = {
        'absolute_background': -1000,
        'background': 1,
        'content_back': 10,
        'content_main': 50, 
        'content_front': 100,
        'overlay': 150,
        'ui_elements': 200,
        'highlights': 500,
        'fade_overlay': 1000000
    }
    
    @staticmethod
    def set_layer(mobject: Mobject, layer: str) -> Mobject:
        """Set object to semantic layer"""
        if layer in LayerManager.LAYERS:
            return mobject.set_z_index(LayerManager.LAYERS[layer])
        return mobject
    
    @staticmethod
    def create_fade_overlay(
        color: str = BLACK,
        opacity: float = 0.8,
        size: float = 100
    ) -> Rectangle:
        """Create full-screen fade overlay (xiaoxiae pattern)"""
        return Rectangle(
            width=size, height=size,
            fill_color=color,
            fill_opacity=opacity,
            stroke_width=0
        ).set_z_index(LayerManager.LAYERS['fade_overlay'])
    
    @staticmethod
    def create_infinite_background(
        color: str = BLUE,
        opacity: float = 0.25,
        size: float = 100
    ) -> Square:
        """Create infinite background (xiaoxiae pattern)"""
        return Square(
            fill_color=color,
            fill_opacity=opacity,
            stroke_color=WHITE,
            side_length=size
        ).set_z_index(LayerManager.LAYERS['background'])
    
    @staticmethod
    def highlight_bring_forward(
        mobjects: List[Mobject],
        layer: str = 'highlights'
    ) -> List[Mobject]:
        """Bring objects forward for emphasis"""
        for mob in mobjects:
            mob.set_z_index(LayerManager.LAYERS[layer])
        return mobjects


# Visual Polish Presets
class PolishPresets:
    """Professional styling presets for common elements"""
    
    # Color Palettes (xiaoxiae's proven combinations)
    PALETTES = {
        'algorithm': [RED, GREEN, BLUE, PINK, ORANGE, LIGHT_BROWN],
        'emphasis': [YELLOW, WHITE, GRAY],
        'professional': [WHITE, GRAY, DARK_GRAY, BLACK]
    }
    
    # Stroke and Fill Presets
    STYLES = {
        'code_background': {
            'stroke_color': WHITE,
            'stroke_width': 2.5,
            'fill_opacity': 0
        },
        'mathematical_line': {
            'stroke_color': WHITE,
            'stroke_width': 3
        },
        'highlight_box': {
            'stroke_color': YELLOW,
            'stroke_width': 4,
            'fill_opacity': 0.1,
            'fill_color': YELLOW
        }
    }
    
    @staticmethod
    def apply_style(mobject: Mobject, style: str) -> Mobject:
        """Apply predefined style to mobject"""
        if style in PolishPresets.STYLES:
            style_dict = PolishPresets.STYLES[style]
            for attr, value in style_dict.items():
                if hasattr(mobject, f'set_{attr}'):
                    getattr(mobject, f'set_{attr}')(value)
        return mobject
    
    @staticmethod
    def create_professional_arrow(
        start: np.ndarray,
        end: np.ndarray,
        color: str = WHITE,
        **kwargs
    ) -> Arrow:
        """Create arrow with professional styling"""
        return Arrow(
            start, end,
            color=color,
            stroke_width=4,
            tip_length=0.22,
            buff=0,
            **kwargs
        )


# Scene Enhancement System
class EnhancedScene(Scene):
    """Scene class with built-in polish features"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.typography = Typography()
        self.assets = AssetManager()
        self.layers = LayerManager()
        self.polish = PolishPresets()
        
    def add_with_layer(self, *mobjects: Mobject, layer: str = 'content_main'):
        """Add objects with automatic layer assignment"""
        for mob in mobjects:
            self.layers.set_layer(mob, layer)
        self.add(*mobjects)
    
    def create_title_sequence(
        self,
        title: str,
        subtitle: str = "",
        duration: float = 3.0
    ):
        """Create professional title sequence"""
        title_obj = self.typography.create_title(title)
        
        if subtitle:
            subtitle_obj = self.typography.create_title(subtitle, 'subtitle')
            title_group = VGroup(title_obj, subtitle_obj).arrange(DOWN, buff=0.5)
        else:
            title_group = title_obj
        
        self.play(FadeIn(title_group, shift=UP))
        self.wait(duration)
        self.play(FadeOut(title_group, shift=UP))
    
    def highlight_with_layer_boost(
        self,
        *mobjects: Mobject,
        highlight_color: str = YELLOW,
        duration: float = 1.0
    ):
        """Highlight objects by boosting layer and adding effects"""
        # Boost to highlight layer
        original_z_indices = [mob.get_z_index() for mob in mobjects]
        self.layers.highlight_bring_forward(list(mobjects))
        
        # Add visual effects
        flash_anims = [Flash(mob, color=highlight_color) for mob in mobjects]
        color_anims = [mob.animate.set_color(highlight_color) for mob in mobjects]
        
        self.play(*flash_anims, *color_anims)
        self.wait(duration)
        
        # Reset layers
        for mob, original_z in zip(mobjects, original_z_indices):
            mob.set_z_index(original_z)


# Professional Utilities
def create_consistent_spacing(
    objects: List[Mobject],
    direction: np.ndarray = DOWN,
    base_buff: float = 0.5,
    micro_adjust: bool = True
) -> VGroup:
    """Create consistently spaced layout with micro-adjustments"""
    group = VGroup(*objects)
    group.arrange(direction, buff=base_buff)
    
    if micro_adjust:
        # Apply xiaoxiae-style micro-adjustments
        for i, obj in enumerate(objects):
            if i % 2 == 1:  # Every other object gets slight offset
                Typography.apply_micro_adjustment(obj, RIGHT, 'tiny')
    
    return group


def create_mathematical_layout(
    equation: str,
    explanation: str,
    code_example: str = ""
) -> VGroup:
    """Create professional mathematical presentation layout"""
    typography = Typography()
    
    # Main equation
    eq = typography.create_math(equation, 'heading')
    
    # Explanation
    exp = typography.create_title(explanation, 'body')
    
    elements = [eq, exp]
    
    # Optional code
    if code_example:
        code = typography.create_code(code_example)
        elements.append(code)
    
    return create_consistent_spacing(elements, DOWN, 0.8)


# Export all classes and functions
__all__ = [
    'Typography', 'AssetManager', 'LayerManager', 'PolishPresets',
    'EnhancedScene', 'create_consistent_spacing', 'create_mathematical_layout'
]